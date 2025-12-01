import winsound
import time
from enum import IntEnum
import threading

# Frequencies for Note C4 to C5 (Middle C)
notes = {
    'Do': 262,
    'Re': 294,
    'Mi': 330,
    'Fa': 349,
    'Sol': 392, # "Son"
    'La': 440,
    'Ti': 494,
    'Do_High': 523
}

def _beep_thread(freq, duration):
    # This runs in the background
    winsound.Beep(freq, duration)

def play_note_threaded(note_name):
    if note_name in notes:
        freq = notes[note_name]
        # Create a new worker for this specific beep
        t = threading.Thread(target=_beep_thread, args=(freq, 200)) # 200ms is snappy
        t.daemon = True # Kills sound if program closes
        t.start()

# Play the scale
scale = ['Do', 'Re', 'Mi', 'Fa', 'Sol', 'La', 'Ti', 'Do_High']

for note in scale:
    play_note_threaded(note)