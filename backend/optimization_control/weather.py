import requests

LATITUDE = 51.7687323
LONGITUDE = 19.4569911

class weather_connection():
    def __init__(self) -> None:
        self.stats = {}

    def connect(self):
        try:
            with requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&daily=temperature_2m_min") as weather:
                weather.raise_for_status()
                self.stats = weather.json()
        except:
            self.stats = {"error": "Could not fetch weather data"}
        else:
            self.stats["error"] = None

    def get_tomorrow_temp(self):
        if self.stats["error"] is None:
            daily = self.stats["daily"]
            return self.stats["daily"]["time"][1], self.stats["daily"]["temperature_2m_min"][1]
        else:
            return "Error", "Error"
