import json
from urllib import request

LATITUDE = 51.7687323
LONGITUDE = 19.4569911

class weather_connection:
    def __init__(self) -> None:
        self.stats = {}

    def connect(self):
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={LATITUDE}&longitude={LONGITUDE}&"
            f"daily=wind_speed_10m_max,shortwave_radiation_sum,temperature_2m_max,"
            f"temperature_2m_min,temperature_2m_mean&"
            f"hourly=temperature_2m,wind_speed_10m,cloud_cover,shortwave_radiation&"
            f"timezone=Europe/Warsaw"
        )
        try:
            with request.urlopen(url) as response:
                if response.status != 200:
                    raise Exception(f"HTTP error: {response.status}")
                data = response.read()
                self.stats = json.loads(data)
        except Exception as e:
            self.stats = {"error": f"Could not fetch weather data: {e}"}
        else:
            self.stats["error"] = None

    def get_tomorrow_temp(self):
        if self.stats.get("error") is None:
            daily = self.stats["daily"]
            return daily["time"][1], daily["temperature_2m_min"][1]
        else:
            return "Error", "Error"
        
    def return_for_simulation(self):
        if self.stats.get("error") is None:
            daily = self.stats["daily"]
            return {
                "time": daily["time"],
                "wind_speed_10m_max": daily["wind_speed_10m_max"],
                "shortwave_radiation_sum": daily["shortwave_radiation_sum"],
                "temperature_2m_max": daily["temperature_2m_max"],
                "temperature_2m_min": daily["temperature_2m_min"],
                "temperature_2m_mean": daily["temperature_2m_mean"],
            }
        