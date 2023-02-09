Large font for the ssd1306 OLED display
---------------------------------------

The code is inspired from https://github.com/peterhinch/micropython-font-to-py/tree/master/writer

To import other fonts, use https://github.com/peterhinch/micropython-font-to-py/blob/master/font_to_py.py.

The fonts in this folder have been generated with : 

    python3 font_to_py.py FreeSans.ttf 14 freesans14.py -x
    python3 font_to_py.py FreeSans.ttf 17 freesans17.py -x
    python3 font_to_py.py FreeSans.ttf 20 freesans20.py -x
    python3 font_to_py.py FreeSans.ttf 24 freesans24.py -x

The -x option is important to have the font horizontally mapped. 
