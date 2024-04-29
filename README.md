# Discord YouTube Music Bot in Python - Easy Set-up
Fast and reliable music bot made in python that currently supports YouTube and Soundcloud(more features to be added soon) - **Easy to set-up!**
You can also invite the bot to multiple servers, each having their own custom settings!


Not only this music bot can be customised to your liking, but it's very easy to self-host your own discord bot 24/7 for free! I can make a tutorial on how to host your own musicbot for free, if anyone requests it.

---

## Setup

### Windows
0. Install python310
1. Clone this repository 
```
git clone https://github.com/lamzaone/g59musicplayer.git
```
2. Download ffmpeg and place `ffmpeg.exe` inside the project folder (where main.py is located)
3. Install the requirements using pip, running this command inside the main folder
```
pip install -r requirements.txt
```
4. Place your  Discord Bot Token insie config/config.py
5. Start the bot using the following command
```
python3 main.py
```

---
### Linux(tested on Ubuntu)

0. Install python310 if you haven't already
1. Clone this repository 
```
git clone https://github.com/lamzaone/g59musicplayer.git
```
2. Install ffmpeg
```
sudo apt install ffmpeg
```
3. Install the requirements using pip, running this command inside the main folder
```
pip install -r requirements.txt
```
4. Place your  Discord Bot Token insie config/config.py
5. Start the bot using the following command
```
python3 main.py
```


---
---
## CHANGELOG:
### Version 0.2
- **ADDED SOUNDCLOUD SUPPORT!**
- **ADDED SLASH (/) COMMANDS SUPPORT!**
- **ADDED .GIF BANNER/AVATAR CHANGER***
- Rebuild the logic behind the musicplayer to improve stability
- fixed a bug where queue would break sometimes
- Improved code readability
- *Added !sync command to sync the command tree **(bot owner only)***

### Version 0.1:
- Implemented queues
- Implemented !play command (supports YouTube currently)
- Implemented !skip command - **skips current song**
- Implemented !seek command - **set current song timeframe to x**
- Implemented !pause command - **pause/resume**
- Implemented !volume command - **change volume to <0-100>%
- Implemented !stop command - **stops music and clears queue**
- Implemented !prefix command - **change command prefix**
