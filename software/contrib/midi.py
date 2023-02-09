"""
MIDI utilities
author: François Georgy (https://github.com/francoisgeorgy)
date: 2023-01-25
labels: midi

A collection of various MIDI utility data and functions.

"""
from math import log2


# NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
NOTES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
OCTAVES = list(range(11))
NOTES_IN_OCTAVE = len(NOTES)
MIDDLE_C_OCTAVE = 4  # middle C in MIDI note 60
VOLTS_PER_SEMITONE = 1 / 12

# SCALES = {
#     # scale name: list of pitch-classes in integer notation
#                   (https://en.wikipedia.org/wiki/Pitch_class#Integer_notation)
#     # note:       C     D     E  F     G     A      B   (for C major)
#     'chromatic': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],    # R b2  2 b3  3  4 b5  5 b6  6 b7  7
#     'major': [0, 2, 4, 5, 7, 9, 11],                        # R     2     3  4     5     6     7
#     'major-pentatonic': [0, 2, 4, 7, 9],                    # R     2     3        5     6
#     'minor': [0, 2, 3, 5, 7, 8, 10],                        # R     2 b3     4     5 b6    b7
#     'minor-pentatonic': [0, 3, 5, 7, 10],                   # R       b3     4     5       b7
#     # 'melodic_minor':      '1,2,b3,4,5,6,7',
#     # 'harmonic_minor':     '1,2,b3,4,5,b6,7',
#     # 'major_blues':        '1,2,b3,3,5,6',
#     # 'minor_blues':        '1,b3,4,b5,5,b7',
#     # 'pentatonic_blues':   '1,b3,4,b5,5,b7',
# }
# SCALES_NAMES = list(SCALES.keys())

# fmt: off
SCALES = (
    {
        'name': 'chromatic',
        'pitch_classes': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],    # R b2  2 b3  3  4 b5  5 b6  6 b7  7
    }, {
        'name': 'major',
        'pitch_classes': [0, 2, 4, 5, 7, 9, 11]                     # R     2     3  4     5     6     7
    }, {
        'name': 'major-pentatonic',
        'pitch_classes': [0, 2, 4, 7, 9]                            # R     2     3        5     6
    }, {
        'name': 'minor',
        'pitch_classes': [0, 2, 3, 5, 7, 8, 10]                     # R     2 b3     4     5 b6    b7
    }, {
        'name': 'minor-pentatonic',
        'pitch_classes': [0, 3, 5, 7, 10]                           # R       b3     4     5       b7
    }
)
# fmt: on

SCALES_NAMES = list(s["name"] for s in SCALES)


def pitch_classes(scale_name):
    try:
        c = next(s["pitch_classes"] for s in SCALES if s["name"] == scale_name)
        return c
    except StopIteration:
        return []


# we redefine clamp() to avoid importing europi
def clamp(value, low, high):
    """Returns a value that is no lower than 'low' and no higher than 'high'."""
    return max(min(value, high), low)


def midi_to_v(number):
    return number * VOLTS_PER_SEMITONE


def v_to_midi(v):
    return clamp(round(v / VOLTS_PER_SEMITONE), 0, 127)


def note(number):
    return NOTES[clamp(number, 0, 127) % NOTES_IN_OCTAVE]


def octave(number):
    return clamp(number, 0, 127) // NOTES_IN_OCTAVE - 5 + MIDDLE_C_OCTAVE


def note_octave(number):
    return f"{note(number)}{octave(number)}"


def quantize_down(midi_note, scale=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]):
    n = midi_note % 12
    base = midi_note - n
    while n not in scale:
        n = n - 1
    return n + base


def quantize_up(midi_note, scale=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]):
    n = midi_note % 12
    base = midi_note - n
    while n not in scale:
        n = n + 1
    return n + base


def quantize_nearest(midi_note, scale=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]):
    n = midi_note % 12
    base = midi_note - n
    d = 12
    s = n
    for i in scale:
        if abs(n - i) < d:
            d = abs(n - i)
            s = i
    return s + base


def quantize(midi_note, scale=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]):
    return quantize_nearest(midi_note, scale)
