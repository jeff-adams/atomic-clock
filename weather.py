import aiohttp
import asyncio

class Weather:
    
    def __init__(self, api_key, client):
        self.api_key = api_key
        self.client = client
        
    async def update(self):
        json_response = await self.call_weather_api()
        return self.create_message(json_response)
    
    async def call_weather_api(self):
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "id": "4780641",
            "appid": self.api_key,
            "units": "imperial"
        }
        
        async with self.client.get(base_url, params=params) as response:
            assert response.status == 200
            return await response.json()
    
    def create_message(self, json_response):
        description = json_response["weather"][0]["main"]
        temp = float(json_response["main"]["feels_like"])
        temp = int(round(temp,0))
        degree_symbol = u'\u00B0'
        
        return f"{temp}{degree_symbol} - {description}"     
