from models import ChessPlayer, COUNTRY_FLAGS
from datetime import datetime, timezone


MAX_HISTORY = 100


class RatingTracker:
    def __init__(self):
        self._history: dict[str, dict[str, list[int]]] = {}

    def update(self, username: str, mode: str, rating: int) -> tuple[int, int] | None:
        old = self._history.get(username, {}).get(mode, [-1])
        last = old[-1] if old else -1
        self._history.setdefault(username, {}).setdefault(mode, []).append(rating)
        history = self._history[username][mode]
        if len(history) > MAX_HISTORY:
            self._history[username][mode] = history[-MAX_HISTORY:]
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


def format_last_online(last_online: str | None) -> str:
    if not last_online:
        return ""
    try:
        dt = datetime.fromisoformat(last_online.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = now - dt
        minutes = int(diff.total_seconds() / 60)
        if minutes < 1:
            return "🟢 Online now"
        elif minutes < 60:
            return f"⏱️ {minutes}m ago"
        elif minutes < 1440:
            return f"⏱️ {minutes // 60}h ago"
        else:
            return f"⏱️ {minutes // 1440}d ago"
    except Exception:
        return ""


def format_league(league: str) -> str:
    league_icons = {
        "partner": "🤝", "admin": "👑", "moderator": "🛡️",
        "legend": "🏆", "master": "🥇", "candidate master": "🥈",
        "expert": "🥉", "class a": "🅰️", "class b": "🅱️",
        "class c": "©️", "class d": "🅳", "class e": "🅴",
        "newbie": "🆕", "provisional": "❓",
    }
    lower = league.lower() if league else ""
    icon = league_icons.get(lower, "♟️")
    return f"{icon} {league}"


def build_progress_bar(current: int, target: int, width: int = 10) -> str:
    if target <= 0:
        return ""
    ratio = min(current / target, 1.0)
    filled = int(width * ratio)
    empty = width - filled
    return f"{'█' * filled}{'░' * empty} {current}/{target}"


def build_presence_stats(player: ChessPlayer, mode: str, streamer: bool = False) -> dict:
    stats = player.get_stats(mode)
    profile = player.profile

    flag = get_country_flag(profile.country)
    name_display = f"{flag} {profile.username}" if flag else profile.username

    last_online = format_last_online(stats.last_online if stats else None)

    if stats and stats.record.total > 0:
        r = stats.record
        state_lines = [f"Wins {r.wins} | Losses {r.losses} | Draws {r.draws}"]
        state_lines.append(f"Win Rate: {r.win_rate_str} | Rating: {stats.rating}")
        if last_online:
            state_lines.append(last_online)
        state_msg = "\n".join(state_lines)
    elif stats:
        state_lines = [f"Rating: {stats.rating} | No games played yet"]
        if last_online:
            state_lines.append(last_online)
        state_msg = "\n".join(state_lines)
    else:
        state_msg = f"No {mode} games played yet"

    details = f"♟️ | {mode.title()} Chess Stats"
    large_text = f"{name_display} | League: {format_league(profile.league)}"

    small_image = ""
    small_text = ""

    if player.live_game.is_live:
        details = f"♟️ | Playing {mode.title()}"
        state_msg = f"vs {player.live_game.opponent} ({player.live_game.color})"
        large_text = f"{name_display} | Live Game"
    elif streamer:
        details = f"🔴 {mode.title()} | Streamer Mode"
        large_text = f"{name_display} | Followers: {profile.followers}"

    return {
        "details": details,
        "state": state_msg,
        "large_image": profile.avatar_url or "chess",
        "large_text": large_text,
        "small_image": small_image,
        "small_text": small_text,
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


def build_rating_chart(history: list[int], width: int = 20, height: int = 5) -> str:
    if len(history) < 2:
        return ""

    min_r = min(history)
    max_r = max(history)
    range_r = max_r - min_r if max_r != min_r else 1

    chart = []
    for row in range(height, -1, -1):
        threshold = min_r + (range_r * row / height)
        line = ""
        for val in history[::max(1, len(history) // width)]:
            if val >= threshold:
                line += "█"
            else:
                line += " "
        chart.append(f"{int(threshold):>4} │{line}")

    chart.append(f"      └{'─' * min(len(history), width)}")
    return "\n".join(chart)
