from models import ChessPlayer, COUNTRY_FLAGS


class RatingTracker:
    def __init__(self):
        self._history: dict[str, dict[str, list[int]]] = {}

    def update(self, username: str, mode: str, rating: int) -> tuple[int, int] | None:
        old = self._history.get(username, {}).get(mode, [-1])
        last = old[-1] if old else -1
        self._history.setdefault(username, {}).setdefault(mode, []).append(rating)
        if last >= 0 and last != rating:
            return (last, rating)
        return None

    def get_history(self, username: str, mode: str) -> list[int]:
        return self._history.get(username, {}).get(mode, [])


def format_rating_change(old_rating: int, new_rating: int) -> str:
    diff = new_rating - old_rating
    if diff > 0:
        return f"📈 +{diff}"
    elif diff < 0:
        return f"📉 {diff}"
    return "➡️ 0"


def format_win_rate(wins: int, losses: int, draws: int) -> str:
    total = wins + losses + draws
    if total == 0:
        return "N/A"
    rate = wins / total * 100
    return f"{rate:.1f}%"


def get_country_flag(country_code: str | None) -> str:
    if not country_code:
        return ""
    return COUNTRY_FLAGS.get(country_code.upper(), f"🏁 {country_code}")


def format_followers(count: int) -> str:
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)


def format_last_online(is_online: bool) -> str:
    if is_online:
        return "🟢 Online"
    return "🔴 Offline"


def build_presence_stats(player: ChessPlayer, mode: str) -> dict:
    stats = player.get_stats(mode)
    profile = player.profile

    flag = get_country_flag(profile.country)
    name_display = f"{flag} {profile.username}" if flag else profile.username

    if stats and stats.record.total > 0:
        r = stats.record
        state_msg = (
            f"Wins {r.wins} | Losses {r.losses} | Draws {r.draws}\n"
            f"Win Rate: {r.win_rate_str} | Rating: {stats.rating}"
        )
    elif stats:
        state_msg = f"Rating: {stats.rating} | No games played yet"
    else:
        state_msg = f"No {mode} games played yet"

    details = f"♟️ | {mode.title()} Chess Stats"
    large_text = f"{name_display} | League: {profile.league}"

    if player.live_game.is_live:
        details = f"♟️ | Playing {mode.title()}"
        state_msg = f"vs {player.live_game.opponent} ({player.live_game.color})"
        large_text = f"{name_display} | Live Game"

    return {
        "details": details,
        "state": state_msg,
        "large_image": "chess",
        "large_text": large_text,
    }


def build_leaderboard(players: list[ChessPlayer], mode: str) -> str:
    ranked = []
    for p in players:
        stats = p.get_stats(mode)
        if stats and stats.record.total > 0:
            ranked.append((p.profile.username, stats.rating, stats.record.win_rate))
    ranked.sort(key=lambda x: x[1], reverse=True)

    if not ranked:
        return f"🏆 {mode.title()} Leaderboard\n   No games played yet"

    lines = [f"🏆 {mode.title()} Leaderboard"]
    for i, (name, rating, wr) in enumerate(ranked, 1):
        medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"#{i}"
        lines.append(f"{medal} {name}: {rating} ({wr:.1f}%)")
    return "\n".join(lines)
