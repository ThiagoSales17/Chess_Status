import time
import signal
import sys
import requests

from config import Config
from chess_api import ChessAPI
from presence import DiscordPresence
from utils import build_presence_stats, build_leaderboard, RatingTracker


GAME_MODES = ["rapid", "blitz", "bullet", "daily"]
GAME_MODE_ICONS = {
    "rapid": "⏱️", "blitz": "⚡", "bullet": "🔫", "daily": "📅"
}


def select_game_mode(api: ChessAPI, username: str, current_mode: str) -> str:
    available = []
    for mode in GAME_MODES:
        stats = api.get_stats(username)
        if mode in stats and stats[mode].rating > 0:
            available.append(mode)

    if not available:
        return current_mode

    print("\n🎮 Available game modes:")
    for i, mode in enumerate(available, 1):
        icon = GAME_MODE_ICONS.get(mode, "")
        marker = " ✓" if mode == current_mode else ""
        print(f"  {i}. {icon} {mode.title()}{marker}")

    print(f"\n  0. Keep current ({current_mode})")

    try:
        choice = input(f"\nSelect mode [0-{len(available)}]: ").strip()
        if choice == "" or choice == "0":
            return current_mode
        idx = int(choice) - 1
        if 0 <= idx < len(available):
            return available[idx]
    except (ValueError, EOFError):
        pass

    return current_mode


def main():
    cfg = Config()
    errors = cfg.validate()
    if errors:
        for e in errors:
            print(f"❌ {e}")
        sys.exit(1)

    api = ChessAPI()
    print(f"Checking Chess.com username '{cfg.username}'...")
    if not api.check_username(cfg.username):
        print(f"❌ Error: The username '{cfg.username}' does not exist on Chess.com!")
        sys.exit(1)
    print("Username found!")

    print("\n🎮 Select game mode:")
    cfg.game_mode = select_game_mode(api, cfg.username, cfg.game_mode)
    print(f"✅ Using: {GAME_MODE_ICONS.get(cfg.game_mode, '')} {cfg.game_mode.title()}")

    all_usernames = [cfg.username] + [u for u in cfg.multi_account if u]
    players = {}
    tracker = RatingTracker()

    print("Connecting to Discord...")
    with DiscordPresence(cfg.app_id) as presence:
        print(f"🔄 Update interval: {cfg.interval}s")
        if cfg.multi_account:
            print(f"👥 Tracking: {', '.join(all_usernames)}")

        try:
            while True:
                cfg.reload_if_needed()

                for username in all_usernames:
                    try:
                        player = api.get_player(username)
                        players[username] = player

                        stats = player.get_stats(cfg.game_mode)
                        new_rating = stats.rating if stats else 0

                        change = tracker.update(username, cfg.game_mode, new_rating)
                        if change:
                            old_rating, new_rating = change
                            diff = new_rating - old_rating
                            emoji = "📈" if diff > 0 else "📉"
                            print(f"{emoji} {username}: {old_rating} → {new_rating} ({'+' if diff > 0 else ''}{diff})")
                    except Exception as e:
                        print(f"❌ Error fetching data for {username}: {e}")

                if cfg.username in players:
                    player = players[cfg.username]

                    if cfg.multi_account and len(players) > 1:
                        lb = build_leaderboard(list(players.values()), cfg.game_mode)
                        print(f"\n{lb}\n")

                    stats_data = build_presence_stats(player, cfg.game_mode)
                    presence.update(**stats_data)

                time.sleep(cfg.interval)
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")


if __name__ == "__main__":
    main()
