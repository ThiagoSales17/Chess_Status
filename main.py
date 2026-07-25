import time
import sys

from config import Config
from chess_api import ChessAPI
from presence import DiscordPresence
from utils import (
    build_presence_stats, build_leaderboard, RatingTracker,
    format_rating_change, build_rating_chart, format_last_online,
    format_league, build_progress_bar
)


GAME_MODES = ["rapid", "blitz", "bullet", "daily"]
GAME_MODE_ICONS = {
    "rapid": "⏱️", "blitz": "⚡", "bullet": "🔫", "daily": "📅"
}


def select_game_mode(api: ChessAPI, username: str, current_mode: str) -> str:
    all_stats = api.get_stats(username)
    available = [m for m in GAME_MODES if m in all_stats and all_stats[m].rating > 0]

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


def print_player_info(player, mode: str):
    profile = player.profile
    stats = player.get_stats(mode)

    flag = ""
    if profile.country:
        from models import COUNTRY_FLAGS
        flag = COUNTRY_FLAGS.get(profile.country, "")

    print(f"\n{'='*50}")
    print(f"👤 {profile.username} {flag}")
    print(f"🔗 {profile.url or 'N/A'}")

    if profile.avatar_url:
        print(f"🖼️  Avatar: {profile.avatar_url}")

    print(f"🏆 League: {format_league(profile.league)}")
    print(f"👥 Followers: {profile.followers}")

    if stats:
        last_online = format_last_online(stats.last_online)
        if last_online:
            print(f"⏰ {last_online}")

        print(f"\n📊 {mode.title()} Stats:")
        print(f"   Rating: {stats.rating}")
        r = stats.record
        print(f"   W/L/D: {r.wins}/{r.losses}/{r.draws}")
        print(f"   Win Rate: {r.win_rate_str}")
    else:
        print(f"\n📊 No {mode} stats available")

    if player.live_game.is_live:
        print(f"\n🔴 LIVE GAME!")
        print(f"   vs {player.live_game.opponent} ({player.live_game.color})")
        print(f"   Time: {player.live_game.time_control}")
        print(f"   Link: {player.live_game.url}")

    print(f"{'='*50}")


def main():
    cfg = Config()

    if not cfg.username:
        cfg.username = input("Enter your chess.com account username: ").strip().lower()
    if not cfg.app_id:
        cfg.app_id = input("Enter your Discord Application ID: ").strip()

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
        if cfg.streamer:
            print("🔴 Streamer mode enabled")

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
                            print(f"{username}: {format_rating_change(old_rating, new_rating)}")

                            history = tracker.get_history(username, cfg.game_mode)
                            if len(history) >= 2:
                                print(build_rating_chart(history))
                    except Exception as e:
                        print(f"❌ Error fetching data for {username}: {e}")

                if cfg.username in players:
                    player = players[cfg.username]

                    print_player_info(player, cfg.game_mode)

                    if cfg.multi_account and len(players) > 1:
                        lb = build_leaderboard(list(players.values()), cfg.game_mode)
                        print(f"\n{lb}\n")

                    stats_data = build_presence_stats(player, cfg.game_mode, cfg.streamer)
                    presence.update(**stats_data)

                time.sleep(cfg.interval)
        except KeyboardInterrupt:
            print("\n👋 Shutting down...")


if __name__ == "__main__":
    main()
