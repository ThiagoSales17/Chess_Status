import time
import requests
from models import ChessPlayer, GameStats, GameRecord, PlayerProfile, LiveGame

BASE_URL = "https://api.chess.com/pub"
HEADERS = {"User-Agent": "ChessDiscordPresence/2.0 (github.com/ThiagoSales17/Chess_Status)"}

MAX_RETRIES = 3
BASE_DELAY = 2
CACHE_TTL = 30


def fetch_with_retry(url: str, headers: dict, max_retries: int = MAX_RETRIES) -> dict:
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            delay = BASE_DELAY * (2 ** attempt)
            print(f"⚠️ Request failed (attempt {attempt + 1}/{max_retries}): {e}")
            print(f"   Retrying in {delay}s...")
            time.sleep(delay)


class ChessAPI:
    def __init__(self):
        self._cache = {}
        self._cache_times = {}

    def _cached_fetch(self, url: str) -> dict:
        now = time.time()
        if url in self._cache and (now - self._cache_times.get(url, 0)) < CACHE_TTL:
            return self._cache[url]
        data = fetch_with_retry(url, headers=HEADERS)
        self._cache[url] = data
        self._cache_times[url] = now
        return data

    def check_username(self, username: str) -> bool:
        try:
            data = self._cached_fetch(f"{BASE_URL}/player/{username}")
            return "username" in data
        except Exception:
            return False

    def get_profile(self, username: str) -> PlayerProfile:
        data = self._cached_fetch(f"{BASE_URL}/player/{username}")
        country_url = data.get("country", "")
        country_code = country_url.split("/")[-1] if country_url else None
        return PlayerProfile(
            username=data.get("username", username),
            avatar_url=data.get("avatar"),
            country=country_code,
            league=data.get("league", "None"),
            followers=data.get("followers", 0),
            url=data.get("url"),
        )

    def get_stats(self, username: str) -> dict[str, GameStats]:
        data = self._cached_fetch(f"{BASE_URL}/player/{username}/stats")
        stats = {}
        for mode in ["chess_rapid", "chess_blitz", "chess_bullet", "chess_daily"]:
            mode_name = mode.replace("chess_", "")
            if mode in data and "last" in data[mode]:
                record_data = data[mode].get("record", {})
                stats[mode_name] = GameStats(
                    rating=data[mode]["last"]["rating"],
                    record=GameRecord(
                        wins=record_data.get("win", 0),
                        losses=record_data.get("loss", 0),
                        draws=record_data.get("draw", 0),
                    ),
                )
        return stats

    def get_live_game(self, username: str) -> LiveGame:
        try:
            data = self._cached_fetch(f"{BASE_URL}/games/live/{username}")
            games = data.get("games", [])
            for game in games:
                if game.get("status") == "active":
                    white = game.get("white", {})
                    black = game.get("black", {})
                    current = white if white.get("username", "").lower() == username.lower() else black
                    opponent = black if current == white else white
                    return LiveGame(
                        is_live=True,
                        opponent=opponent.get("username"),
                        time_control=game.get("time_control"),
                        color="white" if current == white else "black",
                        url=game.get("url"),
                    )
        except Exception as e:
            print(f"⚠️ Error checking live game: {e}")
        return LiveGame()

    def get_player(self, username: str) -> ChessPlayer:
        profile = self.get_profile(username)
        stats = self.get_stats(username)
        live = self.get_live_game(username)
        return ChessPlayer(
            profile=profile,
            rapid=stats.get("rapid"),
            blitz=stats.get("blitz"),
            bullet=stats.get("bullet"),
            daily=stats.get("daily"),
            live_game=live,
        )
