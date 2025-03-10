# 🏒 DIY NHL GOAL LIGHT

## 📌 Overview
This project flashes a **Kasa smart bulb** whenever your favourite teams score a goal, using the **NHL API**.

## 🛠️ Requirements
- Python 3.9+
- A TP-Link Kasa smart bulb
- `python-kasa` library

## 📥 Installation
1. **Clone the repository**
   ```sh
   git clone https://github.com/kyler1709/NHLGoalLight
   cd nhl-goal-alert
   ```
2. **Install dependencies**
   ```sh
   pip install python-kasa requests
   ```
3. **Set up your Kasa smart bulb**
   - Ensure it's connected to the same network as your PC.
   - Find its IP address using `kasa discover` or your router settings.

## ⚙️ Configuration
1. Open `config.json` (if used) or modify the script:
   ```json
   {
       "team": "Ottawa Senators",
       "bulb_ip": "192.168.x.xxx"
   }
   ```
2. Save changes and exit.

## 🚀 Running the Script
Run the script to check for goals and flash the bulb:
```sh
python goal_alert.py
```

## 🛠️ Troubleshooting
- **Bulb not found?** Run `kasa --host 192.168.x.xxx` to verify connectivity.
- **No goal alerts?** Check NHL API status and verify the team name.

## 🎨 Customization
- Change `team` in `config.json` to another NHL team.
- Adjust the flash duration and colors in `goal_alert.py`.

## 📜 License
This project is open-source. Feel free to contribute! 🚀
