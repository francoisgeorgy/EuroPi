"""
CV Monitor
author: François Georgy (https://github.com/francoisgeorgy)
date: 2023-01-25
labels: cv, tuner

Display the voltage applied to the analog input.

Copy this voltage to the CV1 output.

If the europi.AnalogueInput class includes the method read_voltage_and_sample(),
then the ADC value is also displayed.

Requirements: contrib.largefont package.
"""
from time import sleep

from europi import oled, ain, b1, cv1
from europi_script import EuroPiScript
from contrib.largefont import freesans20
from contrib.largefont.largefont_writer import Writer

VOLTS_PER_SEMITONE = 1 / 12


class VoltageMonitor(EuroPiScript):
    @classmethod
    def display_name(cls):
        return "Voltage Monitor"

    def __init__(self):
        super().__init__()
        self.v_min = 100000
        self.v_max = -100
        self.midi_min = 128
        self.midi_max = -1
        self.l_font = Writer(oled, freesans20)
        b1.handler(self.reset_min_max)

    def reset_min_max(self):
        self.v_min = 100000
        self.v_max = -100
        self.midi_min = 128
        self.midi_max = -1

    def main(self):
        with_adc = "read_voltage_and_sample" in dir(ain)
        padding = 5  # pixels left and right
        while True:
            if with_adc:
                v, adc = ain.read_voltage_and_sample()
            else:
                v = ain.read_voltage()
            if v < self.v_min:
                self.v_min = v
            if v > self.v_max:
                self.v_max = v
            oled.fill(0)
            oled.text(f"{self.v_max:2.2f}", padding, 0)
            if with_adc:
                oled.text(f"{adc}", 128 - padding - 8 * len(str(adc)), 0)
            oled.text(f"{self.v_min:2.2f}", padding, 21)
            s = f"{v:2.2f}V"
            self.l_font.print(s, 128 - padding - self.l_font.string_len(s), 12)
            oled.show()
            cv1.voltage(v)  # copy Ain to CV1
            sleep(0.2)


if __name__ == "__main__":
    oled.contrast(0)  # dim the display
    VoltageMonitor().main()
