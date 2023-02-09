"""
MIDI utilities
author: François Georgy (https://github.com/francoisgeorgy)
date: 2023-01-25
labels: midi

Ad-hoc large font write to display a MIDI note with it's octave. The note
is displayed with a large font and the octave with a medium font, like
a subscript number.

Requirements: contrib.largefont package.
"""
from contrib.largefont.largefont_writer import Writer
from contrib import midi


class MidiNoteWriter:
    def __init__(self, oled, medium_font, large_font):
        self.m_font = Writer(oled, medium_font)
        self.l_font = Writer(oled, large_font)
        self.delta_y = large_font.height() - medium_font.height()

    def print_note(self, number, x, y, align_left=True):
        note = midi.note(number)
        note_width = self.l_font.string_len(note)
        octave = str(midi.octave(number))
        if align_left:
            self.l_font.print(note, x, y)
            self.m_font.print(octave, x + note_width + 1, y)
        else:
            octave_width = self.m_font.string_len(octave)
            self.l_font.print(note, x - note_width - octave_width - 1, y)
            self.m_font.print(octave, x - octave_width, y + self.delta_y - 1)
