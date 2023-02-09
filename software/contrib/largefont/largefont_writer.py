import framebuf

#
# Simplified large font writer.
#
# Adapted from https://github.com/magnums/MicroPython-Oled-ssd1306-largeFont/blob/main/writer.py
#          and https://github.com/peterhinch/micropython-font-to-py/tree/master/writer
#


class Writer:

    def __init__(self, device, font, verbose=False):
        self.device = device
        self.font = font
        if font.hmap():
            self.map = framebuf.MONO_HMSB if font.reverse() else framebuf.MONO_HLSB
        else:
            raise ValueError('Font must be horizontally mapped.')
        self.screenwidth = device.width  # In pixels
        self.screenheight = device.height

    def print(self, string, x, y, invert=False):
        for char in string:
            if char == '\n':    # line breaks are ignored
                return
            glyph, char_height, char_width = self.font.get_ch(char)
            if y + char_height > self.screenheight:
                return
            if x + char_width > self.screenwidth:
                return
            buf = bytearray(glyph)
            if invert:
                for i, v in enumerate(buf):
                    buf[i] = 0xFF & ~ v
            fbc = framebuf.FrameBuffer(buf, char_width, char_height, self.map)
            self.device.blit(fbc, x, y)
            x += char_width

    def justify(self, string1, string2, y, padding=0, invert=False):
        len1 = self.string_len(string1)
        len2 = self.string_len(string2)
        self.print(string1, padding, y, invert)
        self.print(string2, 128-padding-len2, y, invert)

    def string_len(self, string):
        n = 0
        for char in string:
            n += self._char_len(char)
        return n

    def _char_len(self, char):
        if char == '\n':
            char_width = 0
        else:
            _, _, char_width = self.font.get_ch(char)
        return char_width
