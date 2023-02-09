from machine import Pin, ADC, PWM, reset
from time import sleep

from simple_state_machine import SimpleStateMachine
from europi import oled, b1, b2, k1, k2
from europi_script import EuroPiScript


# fmt: off
CALIBRATION_SERIES = [
    [0, 10],
    [0, 2.5, 5, 7.5, 10],
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
]
# fmt: on

ain = None
usb = None
cv1 = None


def change_decimal(n, position, digit):
    s = list(f"{(n * 10**position):0.4f}")
    s[-6] = str(digit)  # -6 is the digit at the left of the dot (xxx.xxxx)
    return float("".join(s)) / (10**position)


def change_10th_bipolar(n, delta):
    return n + (delta - 5) / 10


def centered(line1, line2="", line3=""):
    oled.centre_text("\n".join([line1, line2, line3]))


def sample():
    """Sample the input 256 times and returns the average value."""
    value = 0
    for _ in range(256):
        value += ain.read_u16() & 0xFF80  # mask the 7 low bits because they are just noise
    return round(value / 256)


class Calibrate(EuroPiScript):
    @classmethod
    def display_name(cls):
        """Push this script to the end of the menu."""
        return "~Calibrate"

    def __init__(self):
        super().__init__()

        state = self.load_state_json()

        self.m = SimpleStateMachine()

        # fmt: off
        self.m.state("start") \
            .when("B1").do(self.display_start_menu).goto("start") \
            .when("B2").do(self.do_init_input_calibration).goto("power_reminder", self.display_power_reminder)\
            .when("K1").do(self.do_select_serie)

        self.m.state("power_reminder")\
            .when("B1").goto("start")\
            .when("B2").goto("current_point", self.display_current_point)

        self.m.state("current_point") \
            .when("B1").do(self.display_start_menu).goto("start") \
            .when("B2").do(self.do_calibrate_point).goto("result", self.display_result) \
            .when("K1").do(self.do_adjust10th).do(self.display_current_point) \
            .when("K2").do(self.do_adjust100th).do(self.display_current_point) \
            .when("refresh_display").do(self.display_current_point)

        self.m.state("result") \
            .when("B1").do(self.do_retry).goto("current_point", self.display_current_point) \
            .when("B2").do(self.do_select_next_point_or_save)

        self.m.state("input_done") \
            .when("B2").do(self.do_prepare_output_calibration)  # .goto("start_output", self.display_connect_output)

        self.m.state("start_output") \
            .when("B2").do(self.do_calibrate_output).goto("all_done", self.display_output_done)

        self.m.state("all_done") \
            .when("B2").do(self.do_reset)

        self.m.state("error") \
            .when("B2").do(self.do_reset)
        # fmt: on

        self.serie = state.get("serie", 0)

        self.points = CALIBRATION_SERIES[self.serie].copy()
        self.readings = []
        self.current_point = 0
        self.current_reading = 0
        # self.calibration_values = []
        self.ain_gradients = []
        b1.handler(self.button1)
        b2.handler(self.button2)

    def save_state(self):
        """Save the current state variables as JSON."""
        if self.last_saved() < 500:
            return
        state = {"serie": self.serie}
        self.save_state_json(state)

    def button1(self):
        self.m.do_action("B1")

    def button2(self):
        self.m.do_action("B2")

    def knob1(self):
        self.m.do_action("K1")

    def knob2(self):
        self.m.do_action("K2")

    def compute_ain_gradients(self):
        self.ain_gradients = []
        for index, value in enumerate(self.readings[:-1]):
            try:
                self.ain_gradients.append(
                    (self.points[index + 1] - self.points[index])
                    / (self.readings[index + 1] - value)
                )
            except ZeroDivisionError:
                # TODO: review error message
                raise Exception(
                    "The input calibration process did not complete properly. Please complete again with rack power turned on."
                )
        self.ain_gradients.append(self.ain_gradients[-1])

    def reading_to_voltage(self, reading):
        # reading = self._sample_adc(samples)
        try:
            index = next(index for index, v in enumerate(self.readings) if v >= reading) - 1
        except StopIteration:
            index = len(self.readings) - 1
        if index < 0:
            cv = 0
        else:
            cv = self.points[index] + self.ain_gradients[index] * (reading - self.readings[index])
        return max(min(cv, 12), 0)

    def cv_to_reading(self, cv):
        try:
            index = next(index for index, v in enumerate(self.points) if v >= cv) - 1
        except StopIteration:
            index = len(self.points) - 1
        if index < 0:
            return self.readings[0]
        else:
            return int(self.readings[index] + (cv - self.points[index]) / self.ain_gradients[index])

    def save_on_disk(self):
        oled.centre_text("Saving values...")
        with open(f"lib/calibration_values.py", "w") as file:
            file.write(f"INPUT_CALIBRATION_POINTS={self.points}")
            file.write(f"\nINPUT_CALIBRATION_VALUES={self.readings}")
        centered("Saving done.", "Press B2 to", "calib. outputs")

    def execute_outputs_calibration(self):
        global cv1

        centered("Calibrating", f"0 V", "please wait...")
        duty = 0
        output_duties = [duty]
        cv1.duty_u16(duty)
        sleep(0.5)
        reading = sample()
        centered(f"Cal 0 V", f"adc: {reading}", f"ain: {self.reading_to_voltage(reading):0.3} V")
        for v in range(1, 11):
            expected_reading = self.cv_to_reading(v)
            while abs(reading - expected_reading) > 0.002 and reading < expected_reading:
                wait = 0
                if reading / expected_reading < 0.5:
                    duty += 1000
                elif reading / expected_reading < 0.8:
                    duty += 200
                elif reading / expected_reading < 0.95:
                    duty += 100
                elif reading / expected_reading < 0.99:
                    duty += 20
                    wait = 0.1
                else:
                    duty += 10
                    wait = 0.2
                cv1.duty_u16(duty)
                if wait:
                    sleep(wait)  # wait for the output to stabilize
                reading = sample()
                centered(
                    f"Cal {v} V",
                    f"{duty} {(reading/expected_reading*100):0.1f}%",
                    f"ain: {self.reading_to_voltage(reading):0.2f} V",
                )
            output_duties.append(duty)
            # Display the result before continuing with the next calibration point :
            centered(
                f"Cal {v} V", f"duty = {duty}", f"ain: {self.reading_to_voltage(reading):0.2f} V"
            )
            sleep(1)

        oled.centre_text("Saving values...")
        with open(f"lib/calibration_values.py", "a+") as file:
            values = ", ".join(map(str, output_duties))
            file.write(f"\nOUTPUT_CALIBRATION_VALUES=[{values}]")
        oled.centre_text("Saving done")
        sleep(1)

    # --------------------------------------------------------------------------
    # STATES

    def display_power_reminder(self, action=None):
        if usb.value() == 1:
            centered("Confirm rack", "power is ON", "Back   Confirm")
        else:
            centered("Rack power", "is ON.", "       Continue")

    def display_start_menu(self, action=None):
        centered(
            f"Input calib.", f"{len(CALIBRATION_SERIES[self.serie])} points", "K1:points B2:go"
        )

    def display_current_point(self, action=None):
        v = sample()
        centered(f"Apply {self.points[self.current_point]:0.2f} V", f"adc: {v}", "Abort        OK")

    def display_result(self, action=None):
        centered(
            f"{self.points[self.current_point]}V = {self.current_reading}", " ", "Retry   Confirm"
        )

    def display_output_calibration(self, action=None):
        centered("Values saved", "B2 to", "calib. outputs")

    def display_connect_output(self, action=None):
        centered("Plug CV1 into", "analogue in.", "             OK")

    def display_output_done(self, action=None):
        centered("All done!", " ", "B2 to restart")

    def display_error(self, action=None):
        centered("ERROR", "Invalid data", "B2 to restart")

    # --------------------------------------------------------------------------
    # TRANSITIONS

    # def do_abort(self):
    #     pass

    def do_select_serie(self, action=None):
        n = k1.read_position(len(CALIBRATION_SERIES))
        if n != self.serie and n < len(CALIBRATION_SERIES):
            self.serie = n
            self.points = CALIBRATION_SERIES[n].copy()
            self.readings = []
            self.save_state()
            self.display_start_menu()

    def do_init_input_calibration(self, action):
        self.current_point = 0
        self.current_reading = 0

    def do_adjust10th(self, action=None):
        self.points[self.current_point] = change_10th_bipolar(
            CALIBRATION_SERIES[self.serie][self.current_point], k1.read_position(10)
        )

    def do_adjust100th(self, action=None):
        self.points[self.current_point] = change_decimal(
            self.points[self.current_point], 2, int(k2.read_position(10))
        )

    def do_calibrate_point(self, action):
        self.current_reading = sample()

    def do_retry(self, action):
        # TODO: discard last result
        # self.display_current_point()
        pass

    def do_select_next_point_or_save(self, action=None):
        # save current reading _
        self.readings.append(self.current_reading)
        # select next calibration point :
        self.current_point += 1
        if self.current_point == len(self.points):
            self.save_on_disk()  # FIXME: should be in do_save_result()
            self.display_output_calibration()
            return "input_done"
        else:
            self.display_current_point()
            return "current_point"

    def do_prepare_output_calibration(self, action):
        # print("do_prepare_output_calibration")
        try:
            self.compute_ain_gradients()
            self.display_connect_output()
            return "start_output"
        except Exception:
            self.display_error()
            return "error"

    def do_calibrate_output(self, action):
        self.execute_outputs_calibration()

    def do_reset(self, action):
        oled.fill(0)
        oled.show()
        reset()

    def main(self):
        global ain
        ain = ADC(Pin(26, Pin.IN, Pin.PULL_DOWN))
        global cv1
        cv1 = PWM(Pin(21))
        global usb
        usb = Pin(24, Pin.IN)

        k1prev = k1.read_position(10)
        k2prev = k2.read_position(10)

        self.display_start_menu()
        self.m.start("start")
        while True:
            self.m.execute()
            # The simple state machine is only able to handle one action at a time.
            # This is why we use if..elif below.
            if k1.read_position(10) != k1prev:
                k1prev = k1.read_position(10)
                self.knob1()
            elif k2.read_position(10) != k2prev:
                k2prev = k2.read_position(10)
                self.knob2()
            elif self.m.in_state("current_point"):
                self.m.do_action("refresh_display")
                sleep(0.2)  # TODO: is this delay necessary?


if __name__ == "__main__":
    oled.contrast(0)  # dim the display
    Calibrate().main()
