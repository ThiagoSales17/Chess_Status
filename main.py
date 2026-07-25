import time
import signal
import sys
import requests
from pypresence.presence import Presence
from pypresence.exceptions import DiscordNotFound, InvalidID

username = input("Enter your chess.com account username: ").strip().lower()

profile_url = f"https://api.chess.com/pub/player/{username}"
stats_url = f"https://api.chess.com/pub/player/{username}/stats"

headers = {"User-Agent": "ChessDiscordPresence/1.0 (contact@example.com)"}

print("Checking Chess.com username...")
check_response = requests.get(profile_url, headers=headers)

if check_response.status_code == 404:
    print(f"❌ Error: The username '{username}' does not exist on Chess.com!")
    exit() 
elif check_response.status_code != 200:
    print("❌ Error: Something went wrong with Chess.com API. Try again later.")
    exit()

print("Username found!")
print("Connecting to Discord...")
app_id = input("Enter your Discord Application ID: ")

rpc = None

def cleanup(signum=None, frame=None):
    global rpc
    if rpc:
        try:
            rpc.close()
            print("🔌 RPC connection closed.")
        except Exception:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

rpc = Presence(app_id)

try:
    rpc.connect()
    print("✅ Successfully connected to Discord!")
except DiscordNotFound:
    print("❌ Error: Discord desktop app is not running! Please open Discord first.")
    exit()
except InvalidID:
    print("❌ Error: The Discord Application ID is invalid or incorrect!")
    exit()
except Exception as e:
    print(f"❌ Error: Unexpected error connecting to Discord: {e}")
    exit()

try:
    while True:
        try:
            respond_profile = requests.get(profile_url, headers=headers).json()
            respond_stats = requests.get(stats_url, headers=headers).json()

            # profile_informations
            player_username = respond_profile["username"]
            league = respond_profile.get("league", "None")

            # stats_information
            if "chess_rapid" in respond_stats:
                rapid = respond_stats["chess_rapid"]
                rating = rapid["last"]["rating"]
                wins = rapid["record"]["win"]
                losses = rapid["record"]["loss"]
                draws = rapid["record"]["draw"]
                
                state_msg = f"Wins {wins} | Losses {losses} | Draws {draws}"
                large_text_msg = f"Rating: {rating} | League = {league}"
            else:
                state_msg = "No Rapid games played yet"
                large_text_msg = f"League = {league}"

            rpc.update(
                details= "♟️ | Chess stats",
                state= state_msg,
                large_image= "chess",
                large_text= large_text_msg,
            )
            print("🔄 Discord Presence Updated successfully.")
            
        except Exception as e:
            print(f"❌ | Connection error or issue updating stats: {e}")

        time.sleep(15)
finally:
    cleanup()
