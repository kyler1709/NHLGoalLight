import asyncio
import requests
from kasa.iot import IotBulb
import datetime
import pytz
import time

# Constants for the bulb IP
BULB_IP = "192.168.2.155"  # The IP address of the smart bulb
CHECK_INTERVAL = 1  # Time interval (in seconds) to check for updates (1 second)
FLASH_DURATION = 30  # Duration (in seconds) for which the bulb should flash

# NHL team colors (primary and secondary) in HSV format
# Format: [Hue (0-360), Saturation (0-100), Value (0-100)]
TEAM_COLORS = {
    "ANA": {"primary": [22, 100, 100], "secondary": [0, 0, 0]},       # Orange and Black
    "ARI": {"primary": [22, 78, 85], "secondary": [202, 100, 57]},    # Brick Red and Desert Sand
    "BOS": {"primary": [45, 100, 100], "secondary": [0, 0, 0]},       # Gold and Black
    "BUF": {"primary": [216, 100, 100], "secondary": [45, 100, 100]}, # Blue and Gold
    "CGY": {"primary": [0, 100, 100], "secondary": [45, 100, 100]},   # Red and Yellow
    "CAR": {"primary": [0, 100, 100], "secondary": [0, 0, 0]},        # Red and Black
    "CHI": {"primary": [0, 100, 100], "secondary": [0, 0, 0]},        # Red and Black
    "COL": {"primary": [215, 86, 83], "secondary": [0, 73, 86]},      # Burgundy and Blue
    "CBJ": {"primary": [216, 100, 100], "secondary": [0, 100, 100]},  # Blue and Red
    "DAL": {"primary": [120, 100, 70], "secondary": [0, 0, 20]},      # Green and Black
    "DET": {"primary": [0, 100, 100], "secondary": [0, 0, 100]},      # Red and White
    "EDM": {"primary": [216, 100, 100], "secondary": [25, 100, 100]}, # Blue and Orange
    "FLA": {"primary": [216, 100, 100], "secondary": [0, 100, 100]},  # Blue and Red
    "LAK": {"primary": [0, 0, 0], "secondary": [270, 3, 62]},         # Black and Silver
    "MIN": {"primary": [120, 100, 70], "secondary": [0, 100, 100]},   # Green and Red
    "MTL": {"primary": [0, 100, 100], "secondary": [216, 100, 100]},  # Red and Blue
    "NSH": {"primary": [45, 100, 100], "secondary": [216, 100, 100]}, # Gold and Blue
    "NJD": {"primary": [0, 100, 100], "secondary": [0, 0, 0]},        # Red and Black
    "NYI": {"primary": [216, 100, 100], "secondary": [25, 100, 100]}, # Blue and Orange
    "NYR": {"primary": [216, 100, 100], "secondary": [0, 100, 100]},  # Blue and Red
    "OTT": {"primary": [0, 100, 100], "secondary": [0, 0, 0]},        # Red and Black
    "PHI": {"primary": [25, 100, 100], "secondary": [0, 0, 0]},       # Orange and Black
    "PIT": {"primary": [0, 0, 0], "secondary": [45, 100, 100]},       # Black and Gold
    "SJS": {"primary": [180, 100, 70], "secondary": [0, 0, 20]},      # Teal and Black
    "SEA": {"primary": [180, 100, 70], "secondary": [216, 100, 100]}, # Teal and Blue
    "STL": {"primary": [216, 100, 100], "secondary": [45, 100, 100]}, # Blue and Gold
    "TBL": {"primary": [216, 100, 100], "secondary": [0, 0, 100]},    # Blue and White
    "TOR": {"primary": [216, 100, 100], "secondary": [0, 0, 100]},    # Blue and White
    "VAN": {"primary": [216, 100, 100], "secondary": [120, 100, 70]}, # Blue and Green
    "VGK": {"primary": [45, 100, 100], "secondary": [0, 0, 20]},      # Gold and Black
    "WSH": {"primary": [0, 100, 100], "secondary": [216, 100, 100]},  # Red and Blue
    "WPG": {"primary": [216, 100, 100], "secondary": [0, 0, 20]}      # Blue and Dark Blue
}

def get_todays_date():
    """Get today's date in the format required by the NHL API (YYYY-MM-DD)."""
    # Use Eastern Time since that's what NHL typically uses for scheduling
    eastern = pytz.timezone('US/Eastern')
    today = datetime.datetime.now(eastern)
    return today.strftime("%Y-%m-%d")

def fetch_todays_games():
    """Fetch the list of today's NHL games."""
    today = get_todays_date()
    schedule_url = f"https://api-web.nhle.com/v1/schedule/{today}"
    
    try:
        response = requests.get(schedule_url)
        if response.status_code == 200:
            data = response.json()
            
            # Check if there are games today
            if "gameWeek" in data and data["gameWeek"]:
                for day in data["gameWeek"]:
                    if day["date"] == today and "games" in day:
                        return day["games"]
            
            print(f"No games scheduled for today ({today})")
            return []
    except Exception as e:
        print(f"Error fetching today's games: {e}")
        return []

def display_game_options(games):
    """Display the available games and let the user select multiple games."""
    if not games:
        print("No games available to track.")
        return []
    
    print("\nToday's NHL Games:")
    print("------------------")
    
    for i, game in enumerate(games, 1):
        away_team = game["awayTeam"]["placeName"]["default"] + " " + game["awayTeam"]["commonName"]["default"]
        home_team = game["homeTeam"]["placeName"]["default"] + " " + game["homeTeam"]["commonName"]["default"]
        
        # Convert UTC time to local time
        start_time_utc = datetime.datetime.strptime(game["startTimeUTC"], "%Y-%m-%dT%H:%M:%SZ")
        start_time_utc = pytz.utc.localize(start_time_utc)
        local_tz = datetime.datetime.now().astimezone().tzinfo
        start_time_local = start_time_utc.astimezone(local_tz)
        
        # Format the time
        time_str = start_time_local.strftime("%I:%M %p")
        
        # Get game state
        game_state = game["gameState"]
        state_display = ""
        
        if game_state == "LIVE":
            state_display = " (LIVE)"
        elif game_state == "FINAL":
            state_display = " (FINAL)"
        elif game_state == "FUT":
            state_display = f" (Starts at {time_str})"
        
        print(f"{i}. {away_team} @ {home_team}{state_display} - Game ID: {game['id']}")
    
    selected_games = []
    while True:
        try:
            selection = input("\nEnter the numbers of games to track (comma-separated, 0 to finish): ")
            if selection == "0":
                break
                
            selections = [int(x.strip()) for x in selection.split(",") if x.strip()]
            valid_selections = [s for s in selections if 1 <= s <= len(games)]
            
            if not valid_selections:
                print("No valid game numbers entered. Please try again.")
                continue
                
            for game_num in valid_selections:
                game_id = games[game_num - 1]["id"]
                start_time_utc = games[game_num - 1]["startTimeUTC"]
                away_team = games[game_num - 1]["awayTeam"]["abbrev"]
                home_team = games[game_num - 1]["homeTeam"]["abbrev"]
                
                # Parse the UTC time
                start_time = datetime.datetime.strptime(start_time_utc, "%Y-%m-%dT%H:%M:%SZ")
                start_time = pytz.utc.localize(start_time)
                
                selected_games.append({
                    "id": game_id,
                    "start_time_utc": start_time,
                    "away_team": away_team,
                    "home_team": home_team
                })
                
                # Convert to local time for display
                local_tz = datetime.datetime.now().astimezone().tzinfo
                local_start = start_time.astimezone(local_tz)
                time_str = local_start.strftime("%I:%M %p")
                
                print(f"Added: {away_team} @ {home_team} (Starts at {time_str})")
            
            # Selection complete, exit loop
            break
                
        except ValueError:
            print("Please enter valid numbers separated by commas.")
    
    return selected_games

# Function to flash the bulb with team colors
async def flash_team_colors(ip, team_abbrev, duration=30, interval=0.5):
    """Flashes the bulb with the team's colors for the specified duration."""
    bulb = IotBulb(ip)  # Create an IotBulb object to interact with the bulb
    await bulb.update()  # Update the current state of the bulb

    # Get team colors, defaulting to red and white if team not found
    team_colors = TEAM_COLORS.get(team_abbrev, {"primary": [0, 100, 100], "secondary": [0, 0, 100]})
    primary = team_colors["primary"]
    secondary = team_colors["secondary"]
    
    print(f"Flashing {team_abbrev} colors: {primary} and {secondary}")

    end_time = asyncio.get_event_loop().time() + duration  # Calculate when the flashing should stop
    while asyncio.get_event_loop().time() < end_time:  # Keep flashing until the specified duration has passed
        # Set primary color
        await bulb.set_hsv(primary[0], primary[1], primary[2], transition=100)
        await asyncio.sleep(interval)  # Wait for the specified interval before changing the color

        # Set secondary color
        await bulb.set_hsv(secondary[0], secondary[1], secondary[2], transition=100)
        await asyncio.sleep(interval)  # Wait for the specified interval before changing the color again

# Function to fetch the current game data
async def get_game_data(game_id):
    """Fetches the current game data (team names and scores)."""
    boxscore_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore"
    try:
        response = requests.get(boxscore_url)  # Make a GET request to fetch the game data
        if response.status_code == 200:  # Check if the response status is successful (200 OK)
            data = response.json()  # Parse the response JSON data
            
            game_data = {
                "away_team": data["awayTeam"]["abbrev"],  # Away team abbreviation (e.g., "OTT")
                "home_team": data["homeTeam"]["abbrev"],  # Home team abbreviation (e.g., "CHI")
                "game_state": data.get("gameState", ""),  # Current game state
            }
            
            # Only include scores if the game has started
            if "score" in data["awayTeam"] and "score" in data["homeTeam"]:
                game_data["away_score"] = data["awayTeam"]["score"]
                game_data["home_score"] = data["homeTeam"]["score"]
            
            return game_data
    except Exception as e:
        # Don't print errors for games that haven't started yet
        pass
    return None  # Return None if no data could be fetched or an error occurred

# Function to monitor a single game and flash the bulb on goals
async def monitor_game(game_info, bulb_lock):
    """Monitor a single game for goals and flash the bulb when a goal is scored."""
    game_id = game_info["id"]
    away_team = game_info["away_team"]
    home_team = game_info["home_team"]
    start_time_utc = game_info["start_time_utc"]
    
    # Convert to local time for display
    local_tz = datetime.datetime.now().astimezone().tzinfo
    local_start = start_time_utc.astimezone(local_tz)
    time_str = local_start.strftime("%I:%M %p")
    
    # Check if game is in the future
    now = datetime.datetime.now(pytz.utc)
    if start_time_utc > now:
        time_until_start = (start_time_utc - now).total_seconds()
        print(f"Game {away_team} @ {home_team} starts at {time_str} (in {int(time_until_start/60)} minutes)")
        
        # If game starts more than 5 minutes from now, wait until closer to game time
        if time_until_start > 300:  # More than 5 minutes
            wait_time = time_until_start - 300  # Wait until 5 minutes before game
            await asyncio.sleep(wait_time)
            print(f"Getting ready for {away_team} @ {home_team} game (starts in 5 minutes)")
    
    # Initialize scores to None, indicating game hasn't started
    last_away_score = None
    last_home_score = None
    game_started = False
    game_ended = False
    
    # Keep checking until the game ends
    while not game_ended:
        game_data = await get_game_data(game_id)
        
        if game_data:
            game_state = game_data.get("game_state", "")
            
            # Check if game has ended
            if game_state in ["FINAL", "OFF"]:
                if "away_score" in game_data and "home_score" in game_data:
                    final_away = game_data["away_score"]
                    final_home = game_data["home_score"]
                    print(f"Game has ended: {away_team} {final_away} - {home_team} {final_home}")
                else:
                    print(f"Game has ended: {away_team} @ {home_team}")
                game_ended = True
                break
                
            # Check if game has scores (has started)
            if "away_score" in game_data and "home_score" in game_data:
                away_score = game_data["away_score"]
                home_score = game_data["home_score"]
                
                # Announce game start if this is the first time we see scores
                if not game_started:
                    print(f"Game started: {away_team} vs {home_team}")
                    print(f"Initial score: {away_team} {away_score} - {home_team} {home_score}")
                    game_started = True
                    last_away_score = away_score
                    last_home_score = home_score
                else:
                    # Check for goals
                    if away_score > last_away_score:
                        print(f"GOAL! {away_team} scored! Score: {away_team} {away_score} - {home_team} {home_score}")
                        async with bulb_lock:
                            await flash_team_colors(BULB_IP, away_team, FLASH_DURATION)
                    elif home_score > last_home_score:
                        print(f"GOAL! {home_team} scored! Score: {away_team} {away_score} - {home_team} {home_score}")
                        async with bulb_lock:
                            await flash_team_colors(BULB_IP, home_team, FLASH_DURATION)
                    
                    # Update scores
                    last_away_score = away_score
                    last_home_score = home_score
            else:
                # Game hasn't started yet
                if not game_started:
                    # Check if we're close to game time
                    now = datetime.datetime.now(pytz.utc)
                    if start_time_utc <= now:
                        print(f"Waiting for {away_team} @ {home_team} game to start...")
        
        # Wait before checking again
        await asyncio.sleep(CHECK_INTERVAL)

async def main():
    """Main function to run the NHL goal light program."""
    print("NHL Goal Light - Fetching today's games...")
    
    # Fetch today's games and let the user select multiple games
    games = fetch_todays_games()
    selected_games = display_game_options(games)
    
    if not selected_games:
        print("No games selected. Exiting program.")
        return
    
    print(f"\nTracking {len(selected_games)} games.")
    
    # Create a lock to ensure only one task flashes the bulb at a time
    bulb_lock = asyncio.Lock()
    
    # Create tasks for monitoring each selected game
    tasks = []
    for game_info in selected_games:
        task = asyncio.create_task(monitor_game(game_info, bulb_lock))
        tasks.append(task)
    
    # Wait for all monitoring tasks to complete
    await asyncio.gather(*tasks)
    
    print("All games have ended. Exiting program.")

# Run the main function to start the application
if __name__ == "__main__":
    asyncio.run(main())