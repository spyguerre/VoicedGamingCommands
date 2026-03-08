import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import pyautogui
import time
import win32api, win32con

MODEL_PATH = "vosk-model-small-en-us-0.15"
SAMPLE_RATE = 16000

q = queue.Queue()

commands = [
    "run", "forward", "back",
    "left", "right", "up", "down",
    "jump", "drop", "use", "view",
    "using", "jumping",
    "sneak", "stand", "inventory", "escape",
    "click", "mine",
    "look", "keep", "pause", "resume",
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "hand",
    "stop"
]

def callback(indata, frames, time, status):
    q.put(bytes(indata))

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, SAMPLE_RATE, json.dumps(commands))

look = False
lookmod = 1
keep = False
paused = False

def handle_command(cmd):
    global look, lookmod, keep, paused

    print("Command: " if not paused else "(Paused): ", cmd)

    if cmd == "pause":
        paused = True
    elif cmd == "resume":
        paused = False

    if not paused:
        if look:
            if cmd == "down":
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 32*lookmod)
                lookmod = 1
                look = False

            elif cmd == "up":
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, -32*lookmod)
                lookmod = 1
                look = False

            elif cmd == "left":
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, -32*lookmod, 0)
                lookmod = 1
                look = False

            elif cmd == "right":
                win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 32*lookmod, 0)
                lookmod = 1
                look = False
            
            elif cmd == "one":
                lookmod = 1
            
            elif cmd == "two":
                lookmod = 2

            elif cmd == "three":
                lookmod = 3
            
            elif cmd == "four":
                lookmod = 4
            
            elif cmd == "five":
                lookmod = 5
            
            elif cmd == "six":
                lookmod = 6
            
            elif cmd == "seven":
                lookmod = 7
            
            elif cmd == "eight":
                lookmod = 8
            
            elif cmd == "nine":
                lookmod = 9

        elif keep:
            if cmd == "using":
                pyautogui.mouseDown(button="right")
                keep = False
            
            elif cmd == "jumping":
                pyautogui.keyDown("space")
                keep = False

        else:
            if cmd == "run":
                pyautogui.keyDown('z')
                pyautogui.keyDown('capslock')
                pyautogui.keyUp('capslock')
                pyautogui.keyUp('s')

            elif cmd == "forward":
                pyautogui.keyDown('z')
                pyautogui.keyUp('s')

            elif cmd == "back":
                pyautogui.keyDown('s')
                pyautogui.keyUp('z')

            if cmd == "left":
                pyautogui.keyDown('q')
                pyautogui.keyUp('d')

            if cmd == "right":
                pyautogui.keyDown('d')
                pyautogui.keyUp('q')

            elif cmd == "jump":
                pyautogui.keyDown('space')
                pyautogui.keyUp('space')

            elif cmd == "drop":
                pyautogui.keyDown('g')
                pyautogui.keyUp('g')

            elif cmd == "sneak":
                pyautogui.keyDown("ctrlleft")
            
            elif cmd == "stand":
                pyautogui.keyUp("ctrlleft")

            elif cmd == "inventory":
                pyautogui.keyDown('e')
                pyautogui.keyUp('e')

            elif cmd == "escape":
                pyautogui.keyDown('esc')
                pyautogui.keyUp('esc')

            elif cmd == "click":
                pyautogui.mouseDown()
                pyautogui.mouseUp()
            
            elif cmd == "mine":
                pyautogui.mouseDown()
            
            elif cmd == "use":
                pyautogui.rightClick()

            elif cmd == "one":
                pyautogui.keyDown('num1')
                pyautogui.keyUp('num1')
            
            elif cmd == "two":
                pyautogui.keyDown('num2')
                pyautogui.keyUp('num2')

            elif cmd == "three":
                pyautogui.keyDown('num3')
                pyautogui.keyUp('num3')
            
            elif cmd == "four":
                pyautogui.keyDown('num4')
                pyautogui.keyUp('num4')
            
            elif cmd == "five":
                pyautogui.keyDown('num5')
                pyautogui.keyUp('num5')
            
            elif cmd == "six":
                pyautogui.keyDown('num6')
                pyautogui.keyUp('num6')
            
            elif cmd == "seven":
                pyautogui.keyDown('num7')
                pyautogui.keyUp('num7')
            
            elif cmd == "eight":
                pyautogui.keyDown('num8')
                pyautogui.keyUp('num8')
            
            elif cmd == "nine":
                pyautogui.keyDown('num9')
                pyautogui.keyUp('num9')

            elif cmd == "hand":
                pyautogui.keyDown('f')
                pyautogui.keyUp('f')
            
            elif cmd == "view":
                pyautogui.keyDown('f5')
                pyautogui.keyUp('f5')

            elif cmd == "look":
                look = True

            elif cmd == "keep":
                keep = True
        
        if cmd == "stop":
            pyautogui.keyUp('z')
            pyautogui.keyUp('q')
            pyautogui.keyUp('s')
            pyautogui.keyUp('d')
            pyautogui.keyUp('space')
            pyautogui.mouseUp()
            pyautogui.mouseUp(button="right")
            lookmod = 1
            look = False
            keep = False

def handle_debounced(cmd, last_command, last_time):
    import time
    now = int(time.time() * 1000)  # current time in milliseconds
    if cmd != last_command or (now - last_time) > DEBOUNCE_MS:
        handle_command(cmd)
        return cmd, now
    return last_command, last_time


last_command_time = {}  # Tracks last time each command was executed
DEBOUNCE_MS = 300       # Minimum delay between repeated triggers

with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        dtype='int16',
        channels=1,
        callback=callback):

    print("Listening for commands...")

    triggered_commands = set()  # Commands already triggered in current waveform

    while True:
        data = q.get()

        # --- Final result ---
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            if text:
                words = text.split()
                for cmd in words:
                    if cmd in commands and cmd not in triggered_commands:
                        handle_command(cmd)
                        triggered_commands.add(cmd)

            # Reset for the next waveform
            triggered_commands.clear()

        # --- Partial result ---
        else:
            partial = json.loads(recognizer.PartialResult())
            partial_text = partial.get("partial", "")
            if partial_text:
                for cmd in commands:
                    if cmd in partial_text and cmd not in triggered_commands:
                        handle_command(cmd)
                        triggered_commands.add(cmd)
