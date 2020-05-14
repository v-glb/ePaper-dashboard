#!/usr/bin/python
# -*- coding:utf-8 -*-

# *************************************************** 
#   This is a example program for
#   a Weather Station using Raspberry Pi B+, Waveshare ePaper Display and ProtoStax enclosure
#   --> https://www.waveshare.com/product/modules/oleds-lcds/e-paper/2.7inch-e-paper-hat-b.htm
#   --> https://www.protostax.com/products/protostax-for-raspberry-pi-b
#
#   It uses the weather API provided by Open Weather Map (https://openweathermap.org/api) to
#   query the current weather for a given location and then display it on the ePaper display.
#   It refreshes the weather information every 10 minutes and updates the display.
 
#   Written by Sridhar Rajagopal for ProtoStax.
#   BSD license. All text above must be included in any redistribution
# *

# imports
from gpiozero import Button
import sys
sys.path.append(r'lib')
import signal
import epd2in7b
import epdconfig
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import time
import datetime
import pyowm
import RPi.GPIO as GPIO

# custom files/functions imports
from get_weather import show_weather
from cleardisplay import clear_display
from coffee import display_coffee
from todo import show_todos
       
# gracefully exit without a big exception message if possible
def ctrl_c_handler(signal, frame):
    print('Goodbye!')
    # XXX : TODO
    #
    # To preserve the life of the ePaper display, it is best not to keep it powered up -
    # instead putting it to sleep when done displaying, or cutting off power to it altogether.
    #
    # epdconfig.module_exit() shuts off power to the module and calls GPIO.cleanup()
    # The latest epd library chooses to shut off power (call module_exit) even when calling epd.sleep()    
    # epd.sleep() calls epdconfig.module_exit(), which in turns calls cleanup().
    # We can therefore end up in a situation calling GPIO.cleanup twice
    # 
    # Need to cleanup Waveshare epd code to call GPIO.cleanup() only once
    # for now, calling epdconfig.module_init() to set up GPIO before calling module_exit to make sure
    # power to the ePaper display is cut off on exit
    # I have also modified epdconfig.py to initialize SPI handle in module_init() (vs. at the global scope)
    # because slepe/module_exit closes the SPI handle, which wasn't getting initialized in module_init
    epdconfig.module_init()
    epdconfig.module_exit()
    exit(0)

signal.signal(signal.SIGINT, ctrl_c_handler)

# Show on first start up: Render a help screen with key explanations
def show_help(epd):
    '''
    Given an EPD instance, and sections of text, render a help text.
    '''
    key1 = "- Key1: Clear screen"
    key2 = "- Key2: Show todos"
    key3 = "- Key3: Coffee break"
    key4 = "- Key4: Show weather"

    FONT_LARGER = ImageFont.truetype('fonts/arial.ttf', 24)
    FONT_SMALLER = ImageFont.truetype('fonts/arial.ttf', 16)

    HBlackImage = Image.new('1', (epd2in7b.EPD_HEIGHT, epd2in7b.EPD_WIDTH), 255)
    HRedImage = Image.new('1', (epd2in7b.EPD_HEIGHT, epd2in7b.EPD_WIDTH), 255)

    # render the black section
    black_draw = ImageDraw.Draw(HBlackImage)
    black_draw.text((2, 30), key1, font=FONT_LARGER, fill=0)
    black_draw.text((2, 60), key2, font=FONT_LARGER, fill=0)
    black_draw.text((2, 90), key3, font=FONT_LARGER, fill=0)
    black_draw.text((2, 120), key4, font=FONT_LARGER, fill=0)

    epd.display(epd.getbuffer(HBlackImage), epd.getbuffer(HRedImage))

# Clear ePaper display
def refresh(epd):
    epd.init()
    print("Refreshing...")
    epd.Clear()
   

def main():
    # Initial setup and clearing of epd
    epd = epd2in7b.EPD()
    refresh(epd)

    # Show help text on start up
    show_help(epd)

    # Button handling
    while True:
        GPIO.setmode(GPIO.BCM)

        key1 = 5
        key2 = 6
        key3 = 13
        key4 = 19
        
        GPIO.setup(key1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        key1state = GPIO.input(key1)
        key2state = GPIO.input(key2)
        key3state = GPIO.input(key3)
        key4state = GPIO.input(key4)
        
        if key1state == False:
            print('clear display')
            clear_display(epd)
            time.sleep(0.2)

        if key2state == False:
            print('Key2 Pressed')
            refresh(epd)
            show_todos(epd)
            time.sleep(0.2)

        if key3state == False:
            print('Key3 Pressed')
            refresh(epd)
            display_coffee(epd)
            time.sleep(0.2)

        # Weather dashboard
        if key4state == False:
            print('Weather Dashboard')
            refresh(epd)
            show_weather(epd)
            print("starting sleep...")
            time.sleep(0.2)


if __name__ == '__main__':
    main()