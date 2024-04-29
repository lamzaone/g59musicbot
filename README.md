# Discord YouTube Music Bot in Python - Easy Set-up
Fast and reliable music bot made in python that currently supports YouTube, Soundcloud, Vimeo, and more! - **Easy to set-up!**
The bot doesn't currently support Spotify, but supports pretty much every other source.
You can also invite the bot to multiple servers, each having their own custom settings!


Not only this music bot can be customised to your liking, but it's very easy to self-host your own discord bot 24/7 for free! Create an account on cloud.oracle.com, start a VM instance on Ubuntu 22.04 using the Always FREE plan and follow the instructions below to install!

#### Any questions? DM me on Discord (link on my profile). Please let me know if any problems or bugs occur, thanks! 

---
### TODOs
- Implement Search function
- Handle playlist  links (add every song to the queue)
- Create custom playlists
- Add Spotify support


---
# Setup

## Windows
0. Install python310
    - https://www.python.org/downloads/release/python-3100/
    - Make sure you check "add to path" when installing

1. Clone this repository 
```
git clone https://github.com/lamzaone/g59musicplayer.git
```

2. Download ffmpeg and place `ffmpeg.exe` inside the project folder (where main.py is located)
    - https://github.com/BtbN/FFmpeg-Builds/releases


3. Install the requirements using pip, running this command inside the main folder
```
pip install -r requirements.txt
```
4. Start the bot using the following command
```
python3 main.py
```
5. Add your bot token when asked to
6. Copy the invite-url and invite the bot to your server!

---
## Linux(tested on Ubuntu)

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


4. Start the bot using the following command
```
python main.py
```
5. Add your bot token when asked to
6. Copy the invite-url and invite the bot to your server!


### OPTIONAL: Make it automatically start on reboot for your VM

An easy way to make your music bot launch on VM startup is to use crontab.
- Open your terminal and use the following command:  `crontab -e`
    - If you don't have crontab installed, install using

    ```
    sudo apt-get update
    sudo apt-get install cron
    ```

    - After installing cron, make sure to start the service

    ```
    service cron start
    ```

- Press enter, a text file should open.
- At the bottom of the file, add the following line

```
@reboot python3 path/to/musicbot/main.py
```

- Press CTRL+S, then CTRL+X to save and exit
- Reboot your VM to see if the bot boots up (it might take a couple minutes)
```
sudo reboot
```

---
---
## CHANGELOG:
### Version 0.2
- **ADDED SOUNDCLOUD SUPPORT!**
- **ADDED SLASH (/) COMMANDS SUPPORT!**
- **ADDED .GIF BANNER/AVATAR CHANGER***
- **ADDED AUTO UPDATE ON BOT LAUNCH**
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

