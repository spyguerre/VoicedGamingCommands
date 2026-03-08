# Voiced Gaming Commands

This simple project allows you to send in-game inputs (in my case, Minecraft) just by saying so in your microphone!

## Running

- Clone this repository
- Create a venv and activate it:
```bash
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# Else:
. .venv/bin/activate
```
- Install the requirements:
```bash
pip install -r requirements.txt
```
- Unzip the vosk model
- Run the script
```bash
python main.py
```
- The script should listen to your system's default microphone for commands.
- Feel free to adapt this script as you wish, by modifying the language's dictionary and commands. This script should work for both Windows and Linux; however, I have not managed to allow the mouse to move in-game in Linux for some reason :/
