"""LED controller using rpi_ws281x. Provides an LEDController that can
send a `LightPattern` to a WS281x strip. Includes a safe mock when the
native library is not available (useful on development machines).
"""
from __future__ import annotations

from typing import Tuple
from time import sleep
from pathlib import Path

from LightPattern import LightPattern

# Try to import the real library; if it's not available provide a mock
try:
    from rpi_ws281x import PixelStrip, Color
    _HAS_WS = True
except Exception:
    _HAS_WS = False

    class Color:  # type: ignore
        def __init__(self, r: int, g: int, b: int):
            self.r = r
            self.g = g
            self.b = b

    class PixelStrip:  # type: ignore
        def __init__(self, num, pin, freq_hz=800000, dma=10, invert=False, brightness=255, channel=0, strip_type=None):
            self.num = num
            self.pin = pin
            self.brightness = brightness
            self._pixels = [Color(0, 0, 0)] * num

        def begin(self):
            print(f"[mock] PixelStrip initialized: num={self.num} pin={self.pin}")

        def setPixelColor(self, i: int, color: Color):
            if 0 <= i < self.num:
                self._pixels[i] = color

        def show(self):
            # simple textual dump for mock
            s = []
            for c in self._pixels:
                if hasattr(c, "r"):
                    s.append(f"({c.r},{c.g},{c.b})")
                else:
                    s.append(str(c))
            print("[mock] show:", " ".join(s))

        def numPixels(self):
            return self.num


class LEDController:
    """Controls a WS281x LED strip.

    Parameters
    - num_pixels: total number of LEDs on the strip
    - pin: GPIO pin number (BCM) used for data line
    - brightness: 0-255
    - channel: channel number (0 or 1)
    """

    def __init__(self, num_pixels: int, pin: int = 18, brightness: int = 255, channel: int = 0) -> None:
        self.num_pixels = int(num_pixels)
        self.pin = int(pin)
        self.brightness = int(brightness)
        self.channel = int(channel)

        # typical defaults: 800kHz, dma=10
        self.strip = PixelStrip(self.num_pixels, self.pin, brightness=self.brightness, channel=self.channel)
        self.strip.begin()

    def send_pattern(self, pattern: LightPattern, offset: int = 0, show: bool = True) -> None:
        """Send `pattern` to the strip starting at `offset`.

        Pattern semantics: `pattern.as_list()` returns Light objects with
        `color` (r,g,b) and `count` (number of LEDs). The function fills
        LEDs sequentially according to counts. Remaining LEDs are turned off.
        """
        idx = int(offset)
        for light in pattern.as_list():
            r, g, b = light.color
            for _ in range(light.count):
                if idx >= self.num_pixels:
                    break
                self.strip.setPixelColor(idx, Color(int(r), int(g), int(b)))
                idx += 1
            if idx >= self.num_pixels:
                break

        # clear remaining LEDs
        while idx < self.num_pixels:
            self.strip.setPixelColor(idx, Color(0, 0, 0))
            idx += 1

        if show:
            self.strip.show()

    def clear(self, show: bool = True) -> None:
        for i in range(self.num_pixels):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        if show:
            self.strip.show()

    def close(self) -> None:
        self.clear(True)


if __name__ == "__main__":
    # quick demo (mock friendly)
    from datetime import datetime, timedelta
    lp = LightPattern()
    lp.add_light((255, 0, 0), 3)
    lp.add_light((0, 255, 0), 2)
    lp.add_light((0, 0, 255), 1)

    ctl = LEDController(num_pixels=8)
    ctl.send_pattern(lp)
    sleep(1)
    ctl.clear()
