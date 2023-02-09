from europi import OLED_HEIGHT, OLED_WIDTH, k2, oled
import random


starCount = 384
maxDepth = 32
stars = [[0 for x in range(3)] for y in range(starCount)]


def draw_stars():
    """A simple starfield, adapted from https://github.com/sinoia/oled-starfield/blob/master/src/starfield.cpp"""
    origin_x = OLED_WIDTH / 2
    origin_y = OLED_HEIGHT / 2
    for i in range(starCount):
        stars[i][2] -= 0.19
        if stars[i][2] <= 0:
            stars[i][0] = random.randrange(-25, 25)
            stars[i][1] = random.randrange(-25, 25)
            stars[i][2] = maxDepth
        k = OLED_WIDTH / stars[i][2]
        x = int(stars[i][0] * k + origin_x)
        y = int(stars[i][1] * k + origin_y)
        if (0 <= x < OLED_WIDTH) and (0 <= y < OLED_HEIGHT):
            size = int((1 - stars[i][2] / maxDepth) * 4)
            oled.fill_rect(x, y, size, size, 1)


def screen_saver():
    """Display the screen saver until B1 is pressed."""
    oled.contrast(0)  # dim the screen
    oled.fill(0)
    oled.show()
    for i in range(starCount):
        stars[i][0] = random.randrange(-25, 25)
        stars[i][1] = random.randrange(-25, 25)
        stars[i][2] = random.randrange(0, maxDepth)
    p = k2.read_position(10)
    while True:
        oled.fill(0)
        draw_stars()
        oled.show()
        # move knob2 to exit the screensaver
        if k2.read_position(10) != p:
            break
    oled.fill(0)
    oled.show()


if __name__ == "__main__":
    screen_saver()
