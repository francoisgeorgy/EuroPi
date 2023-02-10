"""
CV Tuner
author: François Georgy (https://github.com/francoisgeorgy)
date: 2023-01-25
labels: cv, tuner

Display the note corresponding to the CV value applied at the analog input.

MIDI middle-C (note #60) is C4 and correspond to 5V.

The display shows the ADC reading (top left), the MIDI note number (top right),
the Ain voltage and the corresponding MIDI note (with 5V = C4).

If the europi.AnalogueInput class includes the method read_voltage_and_sample(),
then the ADC value is also displayed.

Requirements: contrib.largefont package.

TODO: add optional quantization (B1 to toggle)
TODO: quantizer
TODO: output quantized note on CV1
TODO: transposer
TODO: copy the note (ain) to the outputs (cv1-6), on 6 different octaves
"""
from time import sleep

from europi_script import EuroPiScript
from europi import oled, ain
from contrib import midi
from contrib.largefont import freesans14
from contrib.largefont import freesans20
from contrib.largefont.largefont_writer import Writer
from contrib.midi_note_writer import MidiNoteWriter


class CvTuner(EuroPiScript):
    @classmethod
    def display_name(cls):
        return "CV Tuner"

    def __init__(self):
        super().__init__()
        self.l_font = Writer(oled, freesans20)
        self.note_writer = MidiNoteWriter(oled, freesans14, freesans20)

    def main(self):
        with_adc = "read_voltage_and_sample" in dir(ain)
        padding = 5  # pixels left and right
        while True:
            if with_adc:
                v, adc = ain.read_voltage_and_sample()
            else:
                v = ain.read_voltage()
            midi_number = midi.v_to_midi(v)
            oled.fill(0)
            if with_adc:
                oled.text(f"{adc}", padding, 0)
            oled.text(f"{midi_number}", 128 - padding - len(str(midi_number)) * 8, 0)
            self.l_font.print(f"{v:2.2f}V", padding, 12)
            self.note_writer.print_note(midi_number, 128 - padding, 12, False)
            oled.show()
            sleep(0.2)


if __name__ == "__main__":
    oled.contrast(0)  # dim the display
    CvTuner().main()
