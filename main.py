import time
import signal
import sys
import requests

from config import Config
from chess_api import ChessAPI
from presence import DiscordPresence
from utils import build_presence_stats, build_leaderboard


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

    all_usernames = [cfg.username] + [u for u in cfg.multi_account if u]
    players = {}
    ratings = {}

    print("Connecting to Discord...")
    with DiscordPresence(cfg.app_id) as presence:
        print(f"🎮 Game mode: {cfg.game_mode}")
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

                        old_rating = ratings.get(username, {}).get(cfg.game_mode, 0)
                        stats = player.get_stats(cfg.game_mode)
                        new_rating = stats.rating if stats else 0

                        if old_rating > 0 and new_rating != old_rating:
                            diff = new_rating - old_rating
                            emoji = "📈" if diff > 0 else "📉"
                            print(f"{emoji} {username}: {old_rating} → {new_rating} ({'+' if diff > 0 else ''}{diff})")

                        ratings.setdefault(username, {})[cfg.game_mode] = new_rating
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
