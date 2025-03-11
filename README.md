# Discord YouTube Music Bot in Python - Easy Set-up
Fast and reliable music bot made in python that currently supports YouTube, Soundcloud, Vimeo, and more! - **Easy to set-up!**
The bot doesn't currently support Spotify, but supports pretty much every other source.
You can also invite the bot to multiple servers, each having their own custom settings!


Not only this music bot can be customised to your liking, but it's very easy to self-host your own discord bot 24/7 for free! Create an account on cloud.oracle.com, start a VM instance on Ubuntu 22.04 using the Always FREE plan and follow the instructions below to install!

#### Any questions? DM me on Discord (link on my profile). Please let me know if any problems or bugs occur, thanks! 

---
### TODOs
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
python main.py
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
python3 main.py
```
5. Add your bot token when asked to
6. Copy the invite-url and invite the bot to your server!

## FOR VPS HOSTED BOTS!
Lately, youtube has been actively combatting bots, so your VPS ip is most likely blacklisted, therefore it asks you to login. Here is how to bypass this for the bot!

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
### Version 0.3.3
- HOTFIX:
  - Fixed configs Linux systems being unable to play music
  - Added youtube bot detection bypass method
### Version 0.3.2
- Tweaked updater
  - Update message set to no timeout
- Tweaked playlists
  - Better error handling
  - Using `!playlist <partial_name>` or `/playlist list <partial_name>` will now show results if your query matches an existing playlist by a certain threshold
- **Added Avatar/Banner changer!**
  - You can now change your bot's avatar and banner by simply executing a command!
  - You can use animated .GIF files!
  - `!avatar, !banner` and `/avatar, /banner`
  - You can use both URLs and local files (attachments)
  - MAX 10MB
### Version 0.3.1
- Improved playlists
    - Better playlist display (`/playlist list` or `!playlist`)
        - Can now display the whole playlist (with pages)
        - Can now shuffle the playlist before loading into queue
        - Can now load into queue straight form this embed
    - Can now load a YouTube playlist into your custom playlist all at once! just use `/playlist add <playlist_name / index> <playlist url>`
- Improved Queue
    - Better queue display
        - Can now see the whole queue on pages of 20
        - Can shuffle the queue
        - `/queue` or `!queue`
    - Can load a whole YouTube playlist into the queue!
        - Just use `/play <playlist url>` or `!play <playlist_url>?`
### Version 0.3
- **Music player now supports most sources (excluding Spotify)**
- **Added Playlists - you can now create custom playlists, that can be loaded at any time into the queue**
- **`/play` now can load youtube playlists into the queue**
- **Improved updater**
    - Now checks for updates every hour
    - Sends a message to the Bot owner that allows you to update the bot
- **Added `/queue` to display the queue**
- **Added `/shuffle` to shuffle the queue**

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

