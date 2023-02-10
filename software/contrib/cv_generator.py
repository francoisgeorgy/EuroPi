"""
CV Generator
author: François Georgy (https://github.com/francoisgeorgy)
date: 2023-02-04
labels: cv, tuner

Output to CV1 a voltage defined by Knob1 and Knob2.

Knob-1 sets the integer part from 0 to 9.
Knob-2 sets the fractional part from 0 to 99.

This allows to output a voltage in the range 0.00 to 9.99V.

Requirements:
- contrib.largefont package.
- (optional) updated Output.voltage() method in EuroPi that return the duty value used to generate the specified voltage.
"""
from time import sleep

from europi import oled, ain, clamp, b1, cv1, k1, k2
from europi_script import EuroPiScript
from contrib.largefont import freesans20
from contrib.largefont.largefont_writer import Writer


class CvGenerator(EuroPiScript):
    @classmethod
    def display_name(cls):
        return "CV Generator"

    def __init__(self):
        super().__init__()
        self.l_font = Writer(oled, freesans20)

    def main(self):
        padding = 5  # pixels left and right
        while True:
            v1 = k1.read_position(10) + k2.read_position(100) / 100.0
            duty1 = cv1.voltage(v1)
            oled.fill(0)
            if duty1:   # compatibility with EuroPi, if the Output.voltage method does not return the duty cycle used.
                oled.text(f"{duty1}", padding, 21)
            s = f"{v1:2.2f}V"
            self.l_font.print(s, 128 - padding - self.l_font.string_len(s), 12)
            oled.show()
            sleep(0.1)


if __name__ == "__main__":
    oled.contrast(0)  # dim the display
    CvGenerator().main()
