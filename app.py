import time
import argparse
import json
import asyncio
import aiohttp
from weather import Weather
from timer import Timer
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

class App:
    
    def __init__(self, *args, **kwargs):
        self.parser = argparse.ArgumentParser()

        self.parser.add_argument("-r", "--led-rows", action="store", help="Display rows. 16 for 16x32, 32 for 32x32. Default: 16", default=16, type=int)
        self.parser.add_argument("--led-cols", action="store", help="Panel columns. Typically 32 or 64. (Default: 32)", default=32, type=int)
        self.parser.add_argument("-c", "--led-chain", action="store", help="Daisy-chained boards. Default: 1.", default=1, type=int)
        self.parser.add_argument("-P", "--led-parallel", action="store", help="For Plus-models or RPi2: parallel chains. 1..3. Default: 1", default=1, type=int)
        self.parser.add_argument("-p", "--led-pwm-bits", action="store", help="Bits used for PWM. Something between 1..11. Default: 11", default=11, type=int)
        self.parser.add_argument("-b", "--led-brightness", action="store", help="Sets brightness level. Default: 25. Range: 1..100", default=25, type=int)
        self.parser.add_argument("-m", "--led-gpio-mapping", help="Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm" , choices=['regular', 'adafruit-hat', 'adafruit-hat-pwm'], type=str)
        self.parser.add_argument("--led-scan-mode", action="store", help="Progressive or interlaced scan. 0 Progressive, 1 Interlaced (default)", default=1, choices=range(2), type=int)
        self.parser.add_argument("--led-pwm-lsb-nanoseconds", action="store", help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. Default: 130", default=130, type=int)
        self.parser.add_argument("--led-show-refresh", action="store_true", help="Shows the current refresh rate of the LED panel")
        self.parser.add_argument("--led-slowdown-gpio", action="store", help="Slow down writing to GPIO. Range: 0..4. Default: 1", default=1, type=int)
        self.parser.add_argument("--led-no-hardware-pulse", action="store", help="Don't use hardware pin-pulse generation")
        self.parser.add_argument("--led-rgb-sequence", action="store", help="Switch if your matrix has led colors swapped. Default: RGB", default="RGB", type=str)
        self.parser.add_argument("--led-pixel-mapper", action="store", help="Apply pixel mappers. e.g \"Rotate:90\"", default="", type=str)
        self.parser.add_argument("--led-row-addr-type", action="store", help="0 = default; 1=AB-addressed panels; 2=row direct; 3=ABC-addressed panels; 4 = ABC Shift + DE direct", default=0, type=int, choices=[0,1,2,3,4])
        self.parser.add_argument("--led-multiplexing", action="store", help="Multiplexing type: 0=direct; 1=strip; 2=checker; 3=spiral; 4=ZStripe; 5=ZnMirrorZStripe; 6=coreman; 7=Kaler2Scan; 8=ZStripeUneven (Default: 0)", default=0, type=int)
        self.parser.add_argument("--led-panel-type", action="store", help="Needed to initialize special panels. Supported: 'FM6126A'", default="", type=str)

        self.settings = json.load(open("settings.json"))
        self.api_key = self.settings["api_key"]
        
        font = graphics.Font()
        self.time_font = font.LoadFont("fontfile")
        self.weather_font = font.LoadFont("fontfile")
        
        self.timer = Timer()

    async def loop(self):
        matrix = self.init_matrix()
        canvas = matrix.CreateFrameCanvas()
        weather_now = "Loading..."
        async with aiohttp.ClientSession() as client:
            weather_api = Weather(self.api_key, client)
            while True:
                weather_now = self.get_weather(weather_api, weather_now)
                time_now = self.get_time()
                
                # 
                print(f"{time_now} {weather_now}", end="\r")
                
    def get_time(self):
        current_time = time.localtime(time.time())
        time_string = f"{current_time[3]:02}:{current_time[4]:02}"
        return time_string
    
    def init_matrix(self):
        args = self.parser.parse_args()

        options = RGBMatrixOptions()

        if args.led_gpio_mapping != None:
          options.hardware_mapping = args.led_gpio_mapping
        options.rows = args.led_rows
        options.cols = args.led_cols
        options.chain_length = args.led_chain
        options.parallel = args.led_parallel
        options.row_address_type = args.led_row_addr_type
        options.multiplexing = args.led_multiplexing
        options.pwm_bits = args.led_pwm_bits
        options.brightness = args.led_brightness
        options.pwm_lsb_nanoseconds = args.led_pwm_lsb_nanoseconds
        options.led_rgb_sequence = args.led_rgb_sequence
        options.pixel_mapper_config = args.led_pixel_mapper
        options.panel_type = args.led_panel_type

        if args.led_show_refresh:
          options.show_refresh_rate = 1

        if args.led_slowdown_gpio != None:
            options.gpio_slowdown = args.led_slowdown_gpio
        if args.led_no_hardware_pulse:
          options.disable_hardware_pulsing = True

        return RGBMatrix(options = options)
    
    def get_weather(self, weather_api, weather_then):
        weather = weather_then
        if self.timer.elapsed() > 60.0 * 5:
            weather = weather_api.update()
        return weather

if __name__ == "__main__":
    app = App()
    asyncio.run(app.loop())