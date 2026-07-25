import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys

from config import Config
from chess_api import ChessAPI
from presence import DiscordPresence
from utils import (
    build_presence_stats, build_leaderboard, RatingTracker,
    format_rating_change, build_rating_chart, format_last_online,
    format_league, get_country_flag
)


class ChessPresenceGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chess Discord Rich Presence")
        self.root.geometry("600x700")
        self.root.resizable(False, False)

        self.cfg = None
        self.api = ChessAPI()
        self.tracker = RatingTracker()
        self.running = False
        self.presence = None

        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(config_frame, text="Chess.com Username:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.username_entry = ttk.Entry(config_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=2)

        ttk.Label(config_frame, text="Discord App ID:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.appid_entry = ttk.Entry(config_frame, width=30)
        self.appid_entry.grid(row=1, column=1, pady=2)

        ttk.Label(config_frame, text="Game Mode:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.mode_var = tk.StringVar(value="rapid")
        mode_combo = ttk.Combobox(config_frame, textvariable=self.mode_var,
                                  values=["rapid", "blitz", "bullet", "daily"], state="readonly")
        mode_combo.grid(row=2, column=1, pady=2)

        ttk.Label(config_frame, text="Update Interval (s):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.interval_var = tk.StringVar(value="15")
        ttk.Entry(config_frame, textvariable=self.interval_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=2)

        self.streamer_var = tk.BooleanVar()
        ttk.Checkbutton(config_frame, text="Streamer Mode", variable=self.streamer_var).grid(
            row=4, column=0, columnspan=2, sticky=tk.W, pady=2)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        self.start_btn = ttk.Button(btn_frame, text="▶ Start", command=self._start)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.stop_btn = ttk.Button(btn_frame, text="⏹ Stop", command=self._stop, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

        self.refresh_btn = ttk.Button(btn_frame, text="🔄 Refresh", command=self._refresh)
        self.refresh_btn.pack(side=tk.RIGHT)

        info_frame = ttk.LabelFrame(main_frame, text="Player Info", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.info_text = tk.Text(info_frame, height=15, width=60, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X)

        self.status_var = tk.StringVar(value="Status: Ready")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)

        self.live_label = ttk.Label(status_frame, text="", foreground="red")
        self.live_label.pack(side=tk.RIGHT)

    def _update_info(self, text: str):
        self.info_text.configure(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, text)
        self.info_text.configure(state=tk.DISABLED)

    def _start(self):
        username = self.username_entry.get().strip().lower()
        appid = self.appid_entry.get().strip()

        if not username:
            messagebox.showerror("Error", "Enter Chess.com username")
            return
        if not appid:
            messagebox.showerror("Error", "Enter Discord App ID")
            return

        self.cfg = Config()
        self.cfg.username = username
        self.cfg.app_id = appid
        self.cfg.game_mode = self.mode_var.get()
        self.cfg.interval = int(self.interval_var.get() or 15)
        self.cfg.streamer = self.streamer_var.get()

        if not self.api.check_username(username):
            messagebox.showerror("Error", f"Username '{username}' not found")
            return

        self.running = True
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self.status_var.set("Status: Connecting...")

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _stop(self):
        self.running = False
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
        self.status_var.set("Status: Stopped")
        self.live_label.config(text="")

    def _refresh(self):
        if not self.running:
            return
        try:
            player = self.api.get_player(self.cfg.username)
            info = self._format_player_info(player)
            self._update_info(info)
        except Exception as e:
            self._update_info(f"Error: {e}")

    def _format_player_info(self, player) -> str:
        lines = []
        profile = player.profile
        flag = get_country_flag(profile.country)

        lines.append(f"{'='*50}")
        lines.append(f"👤 {profile.username} {flag}")
        lines.append(f"🔗 {profile.url or 'N/A'}")

        if profile.avatar_url:
            lines.append(f"🖼️  Avatar: {profile.avatar_url}")

        lines.append(f"🏆 League: {format_league(profile.league)}")
        lines.append(f"👥 Followers: {profile.followers}")

        stats = player.get_stats(self.cfg.game_mode)
        if stats:
            last_online = format_last_online(stats.last_online)
            if last_online:
                lines.append(f"⏰ {last_online}")

            lines.append(f"\n📊 {self.cfg.game_mode.title()} Stats:")
            lines.append(f"   Rating: {stats.rating}")
            r = stats.record
            lines.append(f"   W/L/D: {r.wins}/{r.losses}/{r.draws}")
            lines.append(f"   Win Rate: {r.win_rate_str}")

            history = self.tracker.get_history(profile.username, self.cfg.game_mode)
            if len(history) >= 2:
                lines.append(f"\n📈 Rating History:")
                lines.append(build_rating_chart(history))
        else:
            lines.append(f"\n📊 No {self.cfg.game_mode} stats available")

        if player.live_game.is_live:
            lines.append(f"\n🔴 LIVE GAME!")
            lines.append(f"   vs {player.live_game.opponent} ({player.live_game.color})")
            lines.append(f"   Time: {player.live_game.time_control}")
            lines.append(f"   Link: {player.live_game.url}")

        lines.append(f"{'='*50}")
        return "\n".join(lines)

    def _run(self):
        try:
            self.presence = DiscordPresence(self.cfg.app_id)
            if not self.presence.connect():
                self.root.after(0, lambda: self._update_info("Could not connect to Discord"))
                self.root.after(0, self._stop)
                return

            self.root.after(0, lambda: self.status_var.set("Status: Connected"))
            self.root.after(0, lambda: self._update_info("Connected! Fetching data..."))

            while self.running:
                try:
                    player = self.api.get_player(self.cfg.username)

                    stats = player.get_stats(self.cfg.game_mode)
                    new_rating = stats.rating if stats else 0
                    change = self.tracker.update(self.cfg.username, self.cfg.game_mode, new_rating)

                    info = self._format_player_info(player)
                    self.root.after(0, lambda i=info: self._update_info(i))

                    if player.live_game.is_live:
                        self.root.after(0, lambda: self.live_label.config(text="🔴 LIVE GAME!"))
                    else:
                        self.root.after(0, lambda: self.live_label.config(text=""))

                    stats_data = build_presence_stats(player, self.cfg.game_mode, self.cfg.streamer)
                    self.presence.update(**stats_data)

                except Exception as e:
                    self.root.after(0, lambda err=e: self._update_info(f"Error: {err}"))

                time.sleep(self.cfg.interval)

        except Exception as e:
            self.root.after(0, lambda err=e: self._update_info(f"Connection error: {err}"))
        finally:
            if self.presence:
                self.presence.close()
            self.root.after(0, self._stop)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ChessPresenceGUI()
    app.run()
