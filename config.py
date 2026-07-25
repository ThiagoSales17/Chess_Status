import argparse
from pathlib import Path


class Config:
    def __init__(self):
        self._last_mtime = 0
        self._env_path = Path(".env")
        self._cli_args = self._parse_cli()
        self._env = self._load_env(self._env_path)
        self._apply()

    def _parse_cli(self):
        parser = argparse.ArgumentParser(description="Chess Discord Rich Presence")
        parser.add_argument("--username", "-u", help="Chess.com username")
        parser.add_argument("--appid", "-a", help="Discord Application ID")
        parser.add_argument("--game-mode", "-g", default="rapid",
                          choices=["rapid", "blitz", "bullet", "daily"],
                          help="Game mode to display (default: rapid)")
        parser.add_argument("--interval", "-i", type=int, default=15,
                          help="Update interval in seconds (default: 15)")
        parser.add_argument("--multi-account", "-m", nargs="+",
                          help="Additional Chess.com usernames to track")
        parser.add_argument("--streamer", "-s", action="store_true",
                          help="Enable streamer mode (extra info)")
        parser.add_argument("--env-file", "-e", default=".env",
                          help="Path to .env file (default: .env)")
        args, _ = parser.parse_known_args()
        return args

    def _load_env(self, env_path):
        env = {}
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env[key.strip()] = value.strip().strip('"').strip("'")
        return env

    def _apply(self):
        args = self._cli_args
        env = self._env

        self.username = args.username or env.get("CHESS_USERNAME", "")
        self.app_id = args.appid or env.get("DISCORD_APP_ID", "")
        self.game_mode = env.get("GAME_MODE", args.game_mode)

        try:
            self.interval = int(env.get("UPDATE_INTERVAL", args.interval))
        except ValueError:
            self.interval = 15

        if args.multi_account:
            self.multi_account = args.multi_account
        elif env.get("MULTI_ACCOUNT"):
            self.multi_account = [u.strip() for u in env["MULTI_ACCOUNT"].split(",") if u.strip()]
        else:
            self.multi_account = []

        self.streamer = args.streamer or env.get("STREAMER_MODE", "").lower() == "true"

    def needs_reload(self):
        if self._env_path.exists():
            mtime = self._env_path.stat().st_mtime
            if mtime > self._last_mtime:
                self._last_mtime = mtime
                return True
        return False

    def reload_if_needed(self):
        if self.needs_reload():
            self._env = self._load_env(self._env_path)
            self._apply()
            return True
        return False

    def validate(self):
        errors = []
        if not self.username:
            errors.append("Username is required (--username or CHESS_USERNAME in .env)")
        if not self.app_id:
            errors.append("Discord App ID is required (--appid or DISCORD_APP_ID in .env)")
        return errors
