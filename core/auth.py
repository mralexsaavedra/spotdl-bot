from spotifyDownloader.auth import SpotifyOAuth

auth_manager = SpotifyOAuth(open_browser=False)
auth_manager.get_access_token()
