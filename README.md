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
   git clone https://github.com/kyler1709/NHLGoalLight.git
   cd main.py
   ```
2. **Install dependencies**
   ```sh
   pip install requirements.txt
   ```
3. **Set up your Kasa smart bulb**
   - Ensure it's connected to the same network as your PC.
   - Find its IP address using `kasa discover` or your router settings.


## 🚀 Running the Script
Run the script to check for goals and flash the bulb:
```sh
python main.py
```


## 📜 License
This project is open-source. Feel free to contribute! 🚀
