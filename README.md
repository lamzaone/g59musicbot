# Discord YouTube Music Bot in Python - Easy Set-up
Fast and reliable music bot made in python that currently supports YouTube (more features to be added soon) - **Easy to set-up!**
You can also invite the bot to multiple servers, each having their own custom settings!


Not only this music bot can be customised to your liking, but it's very easy to self-host your own discord bot 24/7 for free! I can make a tutorial on how to host your own musicbot for free, if anyone requests it.

## Current command support:
- Queue support -- *Adds links to a queue that plays automatically*
- !prefix -- **BROKEN ATM** *Changes the prefix used for commands on the current server*
- !play <song name\youtube link> -- *Plays music from YouTube*
- !stop -- *Stops the music and clears the queue*
- !pause -- *Pause/resume the music*
- !seek <seconds> -- *Go to a specific timeframe on the current song*
- !volume opt:<0-100> -- *Sets the volume to <0-100>% / If no arguments are given, it shows the current volume*
- !ping -- *Displays the bot's ping*

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