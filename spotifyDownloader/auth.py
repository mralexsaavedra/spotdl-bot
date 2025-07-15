import base64
import time
import urllib.parse as urllibparse
import warnings
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from config.config import (
    CACHE_DIR,
    SPOTIFY_CLIENT_ID,
    SPOTIFY_CLIENT_SECRET,
    SPOTIFY_REDIRECT_URI,
)
from core.locale import get_text
from core.utils import send_message
from urllib.parse import parse_qsl, urlparse
from loguru import logger
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from spotipy.cache_handler import CacheFileHandler, MemoryCacheHandler
from spotipy.exceptions import SpotifyOauthError, SpotifyStateError
from spotipy.oauth2 import SpotifyAuthBase
from spotipy.util import get_host_port
from spotdl.utils.config import DEFAULT_CONFIG


class SpotifyOAuth(SpotifyAuthBase):
    """
    Implements Authorization Code Flow for Spotify's OAuth implementation.
    """

    OAUTH_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
    OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(
        self,
        state=None,
        proxies=None,
        requests_session=True,
        requests_timeout=None,
    ):
        """
        Creates a SpotifyOAuth object

        Parameters:
             * state: Optional, no verification is performed
             * proxies: Optional, proxy for the requests library to route through
             * requests_session: A Requests session
             * requests_timeout: Optional, tell Requests to stop waiting for a response after
                                 a given number of seconds
        """

        super().__init__(requests_session)

        self.client_id = SPOTIFY_CLIENT_ID
        self.client_secret = SPOTIFY_CLIENT_SECRET
        self.redirect_uri = SPOTIFY_REDIRECT_URI
        self.scope = self._normalize_scope(
            "playlist-read-private user-follow-read user-library-read"
        )
        cache_handler = (
            CacheFileHandler(f"{CACHE_DIR}/.spotipy")
            if not DEFAULT_CONFIG["no_cache"]
            else MemoryCacheHandler()
        )
        self.cache_handler = cache_handler
        self.state = state
        self.proxies = proxies
        self.requests_timeout = requests_timeout

    def validate_token(self, token_info):
        if token_info is None:
            return None

        # if scopes don't match, then bail
        if "scope" not in token_info or not self._is_scope_subset(
            self.scope, token_info["scope"]
        ):
            return None

        if self.is_token_expired(token_info):
            token_info = self.refresh_access_token(token_info["refresh_token"])

        return token_info

    def get_authorize_url(self, state=None):
        """Gets the URL to use to authorize this app"""
        payload = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
        }
        if self.scope:
            payload["scope"] = self.scope
        if state is None:
            state = self.state
        if state is not None:
            payload["state"] = state

        urlparams = urllibparse.urlencode(payload)

        return f"{self.OAUTH_AUTHORIZE_URL}?{urlparams}"

    def parse_response_code(self, url):
        """Parse the response code in the given response url

        Parameters:
            - url - the response url
        """
        _, code = self.parse_auth_response_url(url)
        if code is None:
            return url
        else:
            return code

    @staticmethod
    def parse_auth_response_url(url):
        query_s = urlparse(url).query
        form = dict(parse_qsl(query_s))
        if "error" in form:
            raise SpotifyOauthError(
                f"Received error from auth server: {form['error']}", error=form["error"]
            )
        return tuple(form.get(param) for param in ["state", "code"])

    def _make_authorization_headers(self):
        auth_header = base64.b64encode(
            str(self.client_id + ":" + self.client_secret).encode("ascii")
        )
        return {"Authorization": f"Basic {auth_header.decode('ascii')}"}

    def _open_auth_url(self, bot):
        auth_url = self.get_authorize_url()
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton(get_text("auth_button_label"), url=auth_url))
        send_message(
            bot=bot,
            message=get_text("auth_request"),
            reply_markup=markup,
        )
        logger.info(f"Opened {auth_url} in your browser")

    def _get_auth_response_interactive(self, bot):
        self._open_auth_url(bot=bot)
        prompt = "Enter the URL you were redirected to: "
        response = self._get_user_input(prompt)
        state, code = SpotifyOAuth.parse_auth_response_url(response)
        if self.state is not None and self.state != state:
            raise SpotifyStateError(self.state, state)
        return code

    def _get_auth_response_local_server(self, bot, redirect_port):
        server = start_local_http_server(redirect_port)
        self._open_auth_url(bot=bot)
        server.handle_request()

        if server.error is not None:
            raise server.error
        elif self.state is not None and server.state != self.state:
            raise SpotifyStateError(self.state, server.state)
        elif server.auth_code is not None:
            return server.auth_code
        else:
            raise SpotifyOauthError(
                "Server listening on localhost has not been accessed"
            )

    def get_auth_response(self, bot):
        logger.info(
            "User authentication requires interaction with your "
            "web browser. Once you enter your credentials and "
            "give authorization, you will be redirected to "
            "a url.  Paste that url you were directed to to "
            "complete the authorization."
        )

        redirect_info = urlparse(self.redirect_uri)
        redirect_host, redirect_port = get_host_port(redirect_info.netloc)

        if redirect_host == "localhost":
            logger.warning(
                "Using 'localhost' as a redirect URI is being deprecated. "
                "Use a loopback IP address such as 127.0.0.1 "
                "to ensure your app remains functional."
            )

        if redirect_info.scheme == "http" and redirect_host not in (
            "127.0.0.1",
            "localhost",
        ):
            logger.warning(
                "Redirect URIs using HTTP are being deprecated. "
                "To ensure your app remains functional, use HTTPS instead."
            )

        if (
            redirect_host in ("127.0.0.1", "localhost")
            and redirect_info.scheme == "http"
        ):
            # Only start a local http server if a port is specified
            if redirect_port:
                return self._get_auth_response_local_server(
                    bot=bot, redirect_port=redirect_port
                )
            else:
                logger.warning(
                    f"Using `{redirect_host}` as redirect URI without a port. "
                    f"Specify a port (e.g. `{redirect_host}:8080`) to allow "
                    "automatic retrieval of authentication code "
                    "instead of having to copy and paste "
                    "the URL your browser is redirected to."
                )

        return self._get_auth_response_interactive(bot=bot)

    def get_access_token(self, bot, code=None, check_cache=True):
        """Gets the access token for the app given the code

        Parameters:
            - bot: the bot instance to send messages
            - code: the response code
            - check_cache: a boolean indicating if cached token should be used
        """
        if check_cache:
            token_info = self.validate_token(self.cache_handler.get_cached_token())
            if token_info is not None:
                if self.is_token_expired(token_info):
                    token_info = self.refresh_access_token(token_info["refresh_token"])
                send_message(
                    bot=bot,
                    message=get_text("auth_already_authorized"),
                )
                return token_info

        payload = {
            "redirect_uri": self.redirect_uri,
            "code": code or self.get_auth_response(bot=bot),
            "grant_type": "authorization_code",
        }
        if self.scope:
            payload["scope"] = self.scope
        if self.state:
            payload["state"] = self.state

        headers = self._make_authorization_headers()

        logger.debug(
            f"Sending POST request to {self.OAUTH_TOKEN_URL} with Headers: "
            f"{headers} and Body: {payload}"
        )

        try:
            response = self._session.post(
                self.OAUTH_TOKEN_URL,
                data=payload,
                headers=headers,
                verify=True,
                proxies=self.proxies,
                timeout=self.requests_timeout,
            )
            response.raise_for_status()
            token_info = response.json()
            token_info = self._add_custom_values_to_token_info(token_info)
            self.cache_handler.save_token_to_cache(token_info)
            send_message(
                bot=bot,
                message=get_text("auth_success"),
            )
            return token_info
        except requests.exceptions.HTTPError as http_error:
            send_message(
                bot=bot,
                message=get_text("error_auth_failed"),
            )
            self._handle_oauth_error(http_error)

    def refresh_access_token(self, refresh_token):
        payload = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        headers = self._make_authorization_headers()

        logger.debug(
            f"Sending POST request to {self.OAUTH_TOKEN_URL} with Headers: "
            f"{headers} and Body: {payload}"
        )

        try:
            response = self._session.post(
                self.OAUTH_TOKEN_URL,
                data=payload,
                headers=headers,
                proxies=self.proxies,
                timeout=self.requests_timeout,
            )
            response.raise_for_status()
            token_info = response.json()
            token_info = self._add_custom_values_to_token_info(token_info)
            if "refresh_token" not in token_info:
                token_info["refresh_token"] = refresh_token
            self.cache_handler.save_token_to_cache(token_info)
            return token_info
        except requests.exceptions.HTTPError as http_error:
            self._handle_oauth_error(http_error)

    def _add_custom_values_to_token_info(self, token_info):
        """
        Store some values that aren't directly provided by a Web API
        response.
        """
        token_info["expires_at"] = int(time.time()) + token_info["expires_in"]
        token_info["scope"] = self.scope
        return token_info

    def get_cached_token(self):
        """Gets the cached token for the app

        .. deprecated::
        This method is deprecated and may be removed in a future version.
        """
        warnings.warn(
            "Calling get_cached_token directly on the SpotifyOAuth object will be "
            + "deprecated. Instead, please specify a CacheFileHandler instance as "
            + "the cache_handler in SpotifyOAuth and use the CacheFileHandler's "
            + "get_cached_token method. You can replace:\n\tsp.get_cached_token()"
            + "\n\nWith:\n\tsp.validate_token(sp.cache_handler.get_cached_token())",
            DeprecationWarning,
        )
        return self.validate_token(self.cache_handler.get_cached_token())

    def _save_token_info(self, token_info):
        warnings.warn(
            "Calling _save_token_info directly on the SpotifyOAuth object will be "
            + "deprecated. Instead, please specify a CacheFileHandler instance as "
            + "the cache_handler in SpotifyOAuth and use the CacheFileHandler's "
            + "save_token_to_cache method.",
            DeprecationWarning,
        )
        self.cache_handler.save_token_to_cache(token_info)
        return None


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.auth_code = self.server.error = None
        try:
            state, auth_code = SpotifyOAuth.parse_auth_response_url(self.path)
            self.server.state = state
            self.server.auth_code = auth_code
        except SpotifyOauthError as error:
            self.server.error = error

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        if self.server.auth_code:
            status = "successful"
        elif self.server.error:
            status = f"failed ({self.server.error})"
        else:
            self._write("<html><body><h1>Invalid request</h1></body></html>")
            return

        self._write(
            f"""<html>
<script>
window.close()
</script>
<body>
<h1>Authentication status: {status}</h1>
This window can be closed.
<script>
window.close()
</script>
<button class="closeButton" style="cursor: pointer" onclick="window.close();">
Close Window
</button>
</body>
</html>"""
        )

    def _write(self, text):
        return self.wfile.write(text.encode("utf-8"))

    def log_message(self, format, *args):
        return


def start_local_http_server(port, handler=RequestHandler):
    server = HTTPServer(("127.0.0.1", port), handler)
    server.allow_reuse_address = True
    server.auth_code = None
    server.auth_token_form = None
    server.error = None
    return server
