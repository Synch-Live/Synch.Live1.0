#!/usr/bin/python3

import importlib
import logging
import random
import time
from math import floor
from typing import List, Tuple

# hardware controllers
import Adafruit_WS2801 as LED
import Adafruit_GPIO.SPI as SPI
import RPi.GPIO as GPIO

# initialise logging to file
import leds.logger

# import abstract headset class
from leds.headset import Headset

"""
Class implementing the behaviour of a LED headset on an actual RaspberryPi
using the WS2801 LEDs
"""
class WS2801Headset(Headset):
    """
    The characteristic values for the first version of the headset are hardcoded
    here. If you're building a new type of headset make sure to update.
    """
    COUNT = 30
    CROWN_RANGE = list(range(26))
    PILOT_RANGE = [ 28 ]

    def __init__(self,
            crown_col: Tuple[int, int, int], pilot_col: Tuple[int, int, int],
            on_delay: float, off_delay: float,
            count: int = COUNT,
            crown_range: List[int] = CROWN_RANGE,
            pilot_range: List[int] = PILOT_RANGE,
        ) -> None:
        """
        Initialise WS2801 pixel array. The array is split into two parts, the 'crown'
        which will blink and the 'pilot' light which must be always on and pure green.

        Params
        ------
        crown_col, pilot_col
            (r, g, b) values for the colour of the crown and pilot lights respectively

        on_delay, off_delay
            time (in seconds) the crown lights should be on, and off, respectively

        count
            total number of LEDs on the headset

        crown_range, pilot_range
            a list of indexes for the LEDS used in the crown (blinking) or as pilot
            lights (not blinking) respectively

        """
        super().__init__(crown_col, pilot_col, on_delay, off_delay, pilot_turnon = False)

        self.CROWN_RANGE = crown_range
        self.PILOT_RANGE = pilot_range
        self.CROWN_COUNT = len(crown_range)

        SPI_PORT = 0
        SPI_DEVICE = 0
        self.pixels = LED.WS2801Pixels(count, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)

        logging.info('Initialisation of WS2801 LEDs complete')

        self.pilot()

        
    def all_off(self) -> None:
        """
        Turn off all LEDs in the headset
        """
        self.pixels.clear()
        self.pixels.show()
        super().all_off()

        
    def pilot(self) -> None:
        """
        Turn on all LEDs in the pilot range in the headset
        """
        for i in self.PILOT_RANGE:
            self.pixels.set_pixel(i, LED.RGB_to_color(*self.pilot_col))
        self.pixels.show()
        super().pilot()

        
    def crown_on(self, col: Tuple[int, int, int] = None) -> None:
        """
        Turn on all LEDS in the crown range in the headset. A specified colour can be passed in as a parameter.
        """
        for i in self.CROWN_RANGE:
            if col is not None:
                self.pixels.set_pixel(i, LED.RGB_to_color(*col))
            else:
                self.pixels.set_pixel(i, LED.RGB_to_color(*self.crown_col))
        self.pixels.show()
        super().crown_on()

        
    def crown_off(self) -> None:
        """
        Turn off all LEDS in the crown range in the headset
        """
        for i in self.CROWN_RANGE:
            self.pixels.set_pixel(i, LED.RGB_to_color(0, 0, 0))
        self.pixels.show()
        super().crown_off()

        
    def crown_blink(self) -> None:
        """
        All LEDs in the crown should turn on for ON_DELAY time, then turn off
        """
        self.crown_on()
        time.sleep(self.ON_DELAY)
        self.crown_off()

        
    def crown_blink_wait(self, rand: float) -> None:
        """
        All LEDs in the crown should be on for ON_DELAY time, then off for
        OFF_DELAY.

        This function must be called by a periodic timer with a period equal
        to ON_DELAY + OFF_DELAY.

        When the headsets are not synchronised, the lights may not blink on the
        clock, but instead incur a random delay, controlled by the rand param.

        The amount of time delay is chosen uniformly at random from a range
        given by the parameter.
        """
        if rand > 0:
            r = random.uniform(0, rand)
        else:
            r = 0

        logging.info(f'Waiting {round(r, 3)}')

        time.sleep(r)
        self.crown_on()
        time.sleep(self.ON_DELAY)
        self.crown_off()
        

    def crown_fadein_colour(self,
            dt: float = 0.01, col: Tuple[int, int, int] = (0, 0, 0)
        ) -> None:
        """
        All leds in the crown should fade in to the `col` param or, if that is
        not specified, to the `crown_col` set in the constructor in `dt` second
        increments
        """
        super().crown_fadein_colour(dt, col)

        self.crown_off()
        sleep_duration = float((dur - 1.5) / 100)
        if col is None or not (col[0] and col[1] and col[2]):
            col = self.crown_col
        r, g, b = col
        for j in range(100):
            for i in self.CROWN_RANGE:
                self.pixels.set_pixel(i, LED.RGB_to_color(
                    int(r * j / 100), int(g * j / 100), int(b * j / 100)))
            self.pixels.show()
            if dt:
                time.sleep(sleep_duration)

                
    def crown_fade_between_colours(self,
            dt: float = 0.03, col1: Tuple[int, int, int] = (255, 255, 255),
            col2: Tuple[int, int, int] = (0, 0, 255), dur: float = 5.0
        ) -> None:
        """
        All leds in the crown should fade in to the `col` param or, if that is
        not specified, to the `crown_col` set in the constructor in `dt` second
        increments
        """
        super().crown_fade_between_colours(dt, col1, col2)
        sleep_duration = float((dur - 1.5) / 100)
        r1, g1, b1 = col1
        r2, g2, b2 = col2
        WS2801Headset((r1, g1, b1), (r1, g1, b1), 0.5, 1.5).crown_on()

        for j in range(100):
            for i in self.CROWN_RANGE:
                self.pixels.set_pixel(i, LED.RGB_to_color(
                    int(r1 + ((r2 - r1) * j / 100)), int(g1 + ((g2 - g1) * j / 100)), int(b1 + ((b2 - b1) * j / 100))))
            self.pixels.show()
            time.sleep(sleep_duration)

            
    def crown_fadeout(self, dt: float = 0.01) -> None:
        """
        All leds in the crown should fade out from the current colour to black,
        going from full brightness to none in `dt` second increments
        """
        super().crown_fadeout(dt)

        for j in range(100):
            for i in self.CROWN_RANGE:
                r, g, b = self.pixels.get_pixel_rgb(i)
                r = int(r * (100 - j) / 100)
                g = int(g * (100 - j) / 100)
                b = int(b * (100 - j) / 100)
                self.pixels.set_pixel(i, LED.RGB_to_color(r, g, b))
            self.pixels.show()
            if dt:
                time.sleep(dt)
                

    def crown_breathe(self,
            dt: float = 0.01, delay: float = 0, col: Tuple[int, int, int] = (0, 0, 0)
        ) -> None:
        """
        All leds in the crown should fade in to colour specified in `col` param,
        or the `crown_col` set in the constructor if that is not set, in `dt`
        second increents. Then, after `delay` seconds, fade out in `dt` second
        increments
        """
        super().crown_breathe(dt, delay, col)


    def crown_rainbow(self, dt: float = 0.01) -> None:
        """
        All leds in the crown cycle for `dt` seconds through the 256 possible
        colours, starting from consecutive colours
        """
        super().crown_rainbow(dt)
        for j in range(256):
            for i in self.CROWN_RANGE:
                col = (0, 0, 0)
                pos = ((i * 256 // self.CROWN_COUNT) + j) % 256
                if pos < 85:
                    col = (pos * 3, 255 - pos * 3, 0)
                elif pos < 170:
                    pos -= 85
                    col = (255 - pos * 3, 0, pos * 3)
                else:
                    pos -= 170
                    col = (0, pos * 3, 255 - pos * 3)
                self.pixels.set_pixel(i, LED.RGB_to_color(*col))
            self.pixels.show()
            time.sleep(dt)


    def crown_rainbow_repeat(self,
            dt: float = 0.01, duration: float = 2
        ) -> None:
        """
        All leds in the crown cycle for `dt` seconds through the 256 possible
        colours for a total time of `duration` seconds
        """
        super().crown_rainbow_repeat(dt, duration)


    def crown_police(self, dt: float = 0.9) -> None:
        """
        All leds in the crown flash alternative colours for `dt` seconds through either blue
        or red, starting from alternate colours
        """
        super().crown_police(dt)
        switcher = 0
        for j in range(8):
            for i in self.CROWN_RANGE:
                col = (0, 0, 0)
                if switcher == 0:
                    if i % 2 == 0:
                        # Blue
                        col = (0, 0, 255)
                    else:
                        # Red
                        col = (255, 0, 0)
                if switcher == 1:
                    if i % 2 == 1:
                        # Blue
                        col = (0, 0, 255)
                    else:
                        # Red
                        col = (255, 0, 0)

                self.pixels.set_pixel(i, LED.RGB_to_color(*col))
            self.pixels.show()
            time.sleep(dt)
            # Mechanism to switch alternate colours between red and blue
            if switcher == 0:
                switcher = 1
            else:
                switcher = 0
        self.crown_off()
        

    def crown_fire(self, dt: float = 0.2) -> None:
        """
        All leds change between varying shades of red, orange and yellow randomly.
        """
        super().crown_fire(dt)
        for j in range(20):
            for i in self.CROWN_RANGE:
                col = (0, 0, 0)
                random_number = random.randint(0, 40)
                if random_number <= 10:
                    # Dark red
                    col = (102, 0, 0)
                elif random_number <= 20:
                    # Relatively lighter red
                    col = (255, 51, 51)
                elif random_number <= 30:
                    # Orange
                    col = (255, 128, 0)
                else:
                    # Orange
                    col = (255, 128, 0)
                self.pixels.set_pixel(i, LED.RGB_to_color(*col))
            self.pixels.show()
            time.sleep(dt)
        self.crown_off()

        
    def crown_party(self, dt: float = 0.2) -> None:
        """
        All leds change between varying disco-esque colours.
        """
        super().crown_party(dt)
        for j in range(20):
            for i in self.CROWN_RANGE:
                col = (0, 0, 0)
                random_number = random.randint(0, 100)
                if random_number <= 10:
                    # Dark red
                    col = (148, 27, 27)
                elif random_number <= 20:
                    col = (171, 32, 32)
                elif random_number <= 30:
                    col = (222, 10, 10)
                elif random_number <= 40:
                    # Dark Orange
                    col = (204, 102, 0)
                elif random_number <= 50:
                    col = (255, 128, 0)
                elif random_number <= 60:
                    col = (255, 128, 0)
                elif random_number <= 70:
                    # Light Orange
                    col = (255, 153, 51)
                elif random_number <= 80:
                    # Dark yellow
                    col = (204, 204, 0)
                elif random_number <= 90:
                    # Medium yellow
                    col = (255, 255, 0)
                else:
                    # Orange
                    col = (255, 128, 0)
                self.pixels.set_pixel(i, LED.RGB_to_color(*col))
            self.pixels.show()
            time.sleep(dt)
        self.crown_off()

        
    def crown_paparazzi(self) -> None:
        """
        Some leds in the crown flash white randomly while others stay black.
        """
        super().crown_paparazzi()
        for j in range(20):
            for i in self.CROWN_RANGE:
                col = (0, 0, 0)
                random_number = random.randint(0, 100)
                if random_number <= 40:
                    # White
                    col = (255, 255, 255)
                else:
                    # Black
                    col = (0, 0, 0)
                self.pixels.set_pixel(i, LED.RGB_to_color(*col))
            self.pixels.show()
            time.sleep(random.uniform(0.05, 0.25))
        self.crown_off()
        

    def crown_trial_config(self, r=255, g=255, b=255, blink_freq=1, effect_dur=1) -> None:
        """
         Set the colour, blink frequency and effect duration to the custom configuration, and run for 5 seconds.
        """
        super().crown_trial_config_log()

        # Limit loop (effect) run-time to 10 seconds.
        t_end_10 = time.time() + 10

        if effect_dur > 10:
            t_end = t_end_10
        else:
            t_end = time.time() + effect_dur

        if blink_freq is 0:
            WS2801Headset((r, g, b), (r, g, b), 0.5, 1.5).crown_on()
            return

        if blink_freq is not 0:
            sleep_duration = (float(60 / blink_freq)) / 2

            # Blinking effect for effect_dur seconds
            while time.time() < t_end:
                for i in self.CROWN_RANGE:
                    col = (r, g, b)
                    self.pixels.set_pixel(i, LED.RGB_to_color(*col))
                self.pixels.show()
                time.sleep(sleep_duration)
                self.crown_off()
                time.sleep(sleep_duration)

        if time.time() < t_end_10:
            WS2801Headset((r, g, b), (r, g, b), 0.5, 1.5).crown_on()
            while time.time() < t_end_10:
                time.sleep(0)

        self.crown_off()


    def crown_run_config(self, r=43, g=67, b=220, blink_freq=1, effect_dur=5) -> None:
        """
         Set the colour, blink frequency and effect duration to the custom configuration, and run effect for
         effect_dur seconds. Then the crown lights stay solidly on at the same colour.
        """
        super().crown_run_config()
        if blink_freq is 0:
            WS2801Headset((r, g, b), (r, g, b), 0.5, 1.5).crown_on()
            return

        if blink_freq is not 0:
            sleep_duration = (float(60 / blink_freq)) / 2
            t_end = time.time() + effect_dur

            # Blinking effect for effect_dur seconds
            while time.time() < t_end:
                for i in self.CROWN_RANGE:
                    col = (r, g, b)
                    self.pixels.set_pixel(i, LED.RGB_to_color(*col))
                self.pixels.show()
                time.sleep(sleep_duration)
                self.crown_off()
                time.sleep(sleep_duration)

        WS2801Headset((r, g, b), (r, g, b), 0.5, 1.5).crown_on()

