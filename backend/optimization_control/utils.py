from .models import Device
from weather import weather_connection


NORMAL_PRIZES = 0.6212
NIGHT_PRIZES = 0.5536

class optimizationAlgorithm:
    def __init__(self):
        self.devices = Device.objects.all()

    def optimize(self):
        stats_after_optimalization = []
        for device in self.devices:
            best_hours = ""
            if device.priority == 1:
                if device.worktime <= 120:
                    cost = device.power * device.worktime/60 * NIGHT_PRIZES
                    best_hours = f"Godziny pracy: 16:00-{16+int(device.worktime/60)}:{"0" if (device.worktime%60) < 10 else ""}{device.worktime%60}"
                    stats_after_optimalization.append({
                        "device": device.name,
                        "cost": cost,
                        "workhour": best_hours
                    })
                else:
                    cost = device.power * device.worktime/60 * NIGHT_PRIZES
                    best_hours = f"Godziny pracy: 22:00-{(22+int(device.worktime/60))%24}:{"0" if (device.worktime%60) < 10 else ""}{device.worktime%60}"
        
                    stats_after_optimalization.append({
                        "device": device.name,
                        "cost": cost,
                        "workhour": best_hours
                    })
            elif device.priority == 2:
                cost = device.power * device.worktime/60 * NIGHT_PRIZES
                best_hours = f"Godziny pracy: 22:00-{(22+int(device.worktime/60))%24}:{"0" if (device.worktime%60) < 10 else ""}{device.worktime%60}"
                stats_after_optimalization.append({
                    "device": device.name,
                    "cost": cost,
                    "workhour": best_hours
                })
        return stats_after_optimalization
    
class temperature_control(weather_connection):
    def __init__(self):
        super().__init__()
    
    def temperature_set(self):
        self.connect()
        date, temp = self.get_tomorrow_temp()
        if date != "error" and temp != "error":
            if float(temp) < 17:
                temp_devices = Device.objects.filter(is_temp=True)
                for device in temp_devices:
                    device.status = True
                    device.save()
                

def run_my_code(param):
    opt = optimizationAlgorithm()
    # opt.setlist()
    results = opt.optimize()
    if not results:
        return "<p>Brak optymalizacji do wyświetlenia.</p>"
    html = "<h2>Wyniki optymalizacji:</h2><ul>"
    for r in results:
        html += f"<li>{r['device']}: koszt = {r['cost']:.2f} zł, {r['workhour']}</li>"
    html += "</ul>"
    return html


