"""
Note Generator
author: François Georgy (https://github.com/francoisgeorgy)
date: 2023-02-04
labels: midi

Output to CV1 a voltage corresponding to the MIDI Note defined by knob-1 and knob-2.
Knob-1 sets the octave from 0 to 9.
Knob-2 sets the notes from C (0) to B (Ab)
This allows to output a note in the range A0..Ab9.
Scale choice with B1/B2 to navigate the scales (prev/next).

Middle C is C4 and correspond to 5V.

Requirements: contrib.largefont package.
"""
from time import sleep

from europi import oled, ain, clamp, b1, b2, k1, k2, cv1
from europi_script import EuroPiScript
from contrib.largefont import freesans14
from contrib.largefont import freesans20
from contrib.midi_note_writer import MidiNoteWriter
from contrib.midi import midi_to_v, SCALES_NAMES, SCALES, pitch_classes


class NoteGenerator(EuroPiScript):
    @classmethod
    def display_name(cls):
        return "Note Generator"

    def __init__(self):
        super().__init__()
        self.scale = 0
        self.pitches = pitch_classes(SCALES_NAMES[self.scale])
        self.note_writer = MidiNoteWriter(oled, freesans14, freesans20)
        b1.handler(self.button1)
        b2.handler(self.button2)

    def button1(self):
        self.scale = (self.scale - 1) % len(SCALES_NAMES)
        self.pitches = pitch_classes(SCALES_NAMES[self.scale])

    def button2(self):
        self.scale = (self.scale + 1) % len(SCALES_NAMES)
        self.pitches = pitch_classes(SCALES_NAMES[self.scale])

    def main(self):
        padding = 5  # pixels left and right
        while True:
            octave = k1.read_position(10)
            pitch = self.pitches[k2.read_position(len(self.pitches))]
            midi_number = octave * 12 + pitch
            v = midi_to_v(midi_number)
            cv1.voltage(v)
            oled.fill(0)
            oled.text(f"{SCALES_NAMES[self.scale]}", padding, 0)
            oled.text(f"{midi_number}", padding, 10)
            oled.text(f"{v:2.2f}V", padding, 21)
            self.note_writer.print_note(midi_number, 128 - padding, 12, False)
            oled.show()
            sleep(0.1)


if __name__ == "__main__":
    oled.contrast(0)  # dim the display
    NoteGenerator().main()
