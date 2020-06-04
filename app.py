import time
import json
import asyncio
import aiohttp
from weather import Weather
from timer import Timer

async def loop(api_key):
    timer = Timer()
    w = "Loading..."
    async with aiohttp.ClientSession() as client:
        weather = Weather(api_key, client)
        while True:
            if timer.elapsed() > 60.0:
                w = await weather.update()
                timer.reset()
            time_now = clock()
            print(f"{time_now} {w}", end="\r")
            
def clock():
    current_time = time.localtime(time.time())
    time_string = f"{current_time[3]:02}:{current_time[4]:02}"
    return time_string
              
settings = json.load(open("settings.json"))
asyncio.run(loop(settings["api_key"]))