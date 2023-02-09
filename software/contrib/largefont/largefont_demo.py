import time

from europi_script import EuroPiScript
from europi import oled, b2
from contrib.largefont import freesans14
from contrib.largefont import freesans17
from contrib.largefont import freesans20
from contrib.largefont import freesans24
from contrib.largefont.largefont_writer import Writer


class LargeFontDemo(EuroPiScript):

    @classmethod
    def display_name(cls):
        return "Large font demo"

    def __init__(self):
        super().__init__()
        self.font14 = Writer(oled, freesans14)
        self.font17 = Writer(oled, freesans17)
        self.font20 = Writer(oled, freesans20)
        self.font24 = Writer(oled, freesans24)
        self.demo = 0
        b2.handler(self.button2)

    def update_demo(self):
        self.demo = (self.demo + 1) % 4
        oled.fill(0)
        if self.demo == 0:
            s = 'FreeSans14'
            self.font14.print(s, (128 - self.font14.string_len(s)) // 2, (32 - freesans14.height()) // 2)
        elif self.demo == 1:
            s = 'FreeSans17'
            self.font17.print(s, (128 - self.font17.string_len(s)) // 2, (32 - freesans17.height()) // 2)
        elif self.demo == 2:
            s = 'FreeSans20'
            self.font20.print(s, (128 - self.font20.string_len(s)) // 2, (32 - freesans20.height()) // 2)
        elif self.demo == 3:
            s = 'Sans24'
            self.font24.print(s, (128 - self.font24.string_len(s)) // 2, (32 - freesans24.height()) // 2)
        oled.show()
        
    def button2(self):
        self.update_demo()

    def main(self):
        self.update_demo()
        t = time.time()        
        while True:
            if (time.time() - t) >= 0.5:
                self.update_demo()
                t = time.time()                    
            time.sleep(0.1)


if __name__ == "__main__":
    oled.contrast(0)  # dim the display
    LargeFontDemo().main()
