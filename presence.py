import signal
import sys
from pypresence.presence import Presence
from pypresence.exceptions import DiscordNotFound, InvalidID


class DiscordPresence:
    def __init__(self, app_id: str):
        self.rpc = None
        self.app_id = app_id

    def connect(self) -> bool:
        try:
            self.rpc = Presence(self.app_id)
            self.rpc.connect()
            print("✅ Successfully connected to Discord!")
            return True
        except DiscordNotFound:
            print("❌ Error: Discord desktop app is not running! Please open Discord first.")
            return False
        except InvalidID:
            print("❌ Error: The Discord Application ID is invalid or incorrect!")
            return False
        except Exception as e:
            print(f"❌ Error: Unexpected error connecting to Discord: {e}")
            return False

    def update(self, details: str, state: str, large_image: str = "chess",
               large_text: str = "", small_image: str = "", small_text: str = ""):
        if not self.rpc:
            return
        try:
            kwargs = {
                "details": details,
                "state": state,
                "large_image": large_image,
                "large_text": large_text,
            }
            if small_image:
                kwargs["small_image"] = small_image
            if small_text:
                kwargs["small_text"] = small_text
            self.rpc.update(**kwargs)
            print("🔄 Discord Presence Updated successfully.")
        except Exception as e:
            print(f"❌ Error updating presence: {e}")

    def _cleanup(self, signum=None, frame=None):
        self.close()
        sys.exit(0)

    def close(self):
        if self.rpc:
            try:
                self.rpc.close()
                print("🔌 RPC connection closed.")
            except Exception:
                pass
            self.rpc = None

    def __enter__(self):
        if not self.connect():
            raise ConnectionError("Could not connect to Discord")
        signal.signal(signal.SIGINT, self._cleanup)
        signal.signal(signal.SIGTERM, self._cleanup)
        return self

    def __exit__(self, *args):
        self.close()
