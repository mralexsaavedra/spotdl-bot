# from bot.telegram_bot import run_bot

from spotifyDownloader import SpotifyDownloader


if __name__ == "__main__":
    spodtl = SpotifyDownloader()
    spodtl.download(
        [
            "https://open.spotify.com/intl-es/track/2zQvtkghOHiBG48Bj0oFR9?si=0645845c6cab417f"
        ]
    )
