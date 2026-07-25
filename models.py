from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GameRecord:
    wins: int = 0
    losses: int = 0
    draws: int = 0

    @property
    def total(self) -> int:
        return self.wins + self.losses + self.draws

    @property
    def win_rate(self) -> float:
        return (self.wins / self.total * 100) if self.total > 0 else 0.0

    @property
    def win_rate_str(self) -> str:
        return f"{self.win_rate:.1f}%"


@dataclass
class GameStats:
    rating: int = 0
    record: GameRecord = field(default_factory=GameRecord)
    last_online: Optional[str] = None
    is_online: bool = False


@dataclass
class PlayerProfile:
    username: str = ""
    avatar_url: Optional[str] = None
    country: Optional[str] = None
    league: str = "None"
    followers: int = 0
    url: Optional[str] = None


@dataclass
class LiveGame:
    is_live: bool = False
    opponent: Optional[str] = None
    time_control: Optional[str] = None
    color: Optional[str] = None
    url: Optional[str] = None


@dataclass
class ChessPlayer:
    profile: PlayerProfile = field(default_factory=PlayerProfile)
    rapid: Optional[GameStats] = None
    blitz: Optional[GameStats] = None
    bullet: Optional[GameStats] = None
    daily: Optional[GameStats] = None
    live_game: LiveGame = field(default_factory=LiveGame)

    def get_stats(self, mode: str) -> Optional[GameStats]:
        return getattr(self, mode, None)

    def get_best_rating(self) -> tuple[str, int]:
        ratings = {}
        if self.rapid and self.rapid.rating > 0:
            ratings["rapid"] = self.rapid.rating
        if self.blitz and self.blitz.rating > 0:
            ratings["blitz"] = self.blitz.rating
        if self.bullet and self.bullet.rating > 0:
            ratings["bullet"] = self.bullet.rating
        if self.daily and self.daily.rating > 0:
            ratings["daily"] = self.daily.rating
        if not ratings:
            return ("N/A", 0)
        best = max(ratings, key=ratings.get)
        return (best, ratings[best])


COUNTRY_FLAGS = {
    "BR": "🇧🇷", "US": "🇺🇸", "GB": "🇬🇧", "DE": "🇩🇪", "FR": "🇫🇷",
    "ES": "🇪🇸", "IT": "🇮🇹", "RU": "🇷🇺", "CN": "🇨🇳", "JP": "🇯🇵",
    "KR": "🇰🇷", "IN": "🇮🇳", "CA": "🇨🇦", "AU": "🇦🇺", "MX": "🇲🇽",
    "AR": "🇦🇷", "CL": "🇨🇱", "CO": "🇨🇴", "PT": "🇵🇹", "NL": "🇳🇱",
    "SE": "🇸🇪", "NO": "🇳🇴", "DK": "🇩🇰", "FI": "🇫🇮", "PL": "🇵🇱",
    "UA": "🇺🇦", "TR": "🇹🇷", "SA": "🇸🇦", "EG": "🇪🇬", "ZA": "🇿🇦",
    "NG": "🇳🇬", "KE": "🇰🇪", "PH": "🇵🇭", "ID": "🇮🇩", "TH": "🇹🇭",
    "VN": "🇻🇳", "MY": "🇲🇾", "SG": "🇸🇬", "NZ": "🇳🇿", "IE": "🇮🇪",
}
