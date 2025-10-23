from .models import Device

NORMAL_PRIZES = 0.6212
NIGHT_PRIZES = 0.5536

class OptimizationAlgorithm:
    def __init__(self):
        self.devices = Device.objects.all()

    def optimize(self):
        stats_after_optimalization = []
        for device in self.devices:
            best_hours = ""
            if device.priority == 1:
                if device.worktime <= 120:
                    cost = device.power * device.worktime/60 * NIGHT_PRIZES
                    if cost < device.current_cost:
                        best_hours = f"Godziny pracy: 16:00-{16+int(device.worktime/60)}:{device.worktime%60}"
                        stats_after_optimalization.append({
                            "device": device.name,
                            "cost": cost,
                            "workhour": best_hours
                        })
                else:
                    cost = device.power * device.worktime/60 * NIGHT_PRIZES
                    if cost < device.current_cost:
                        best_hours = f"Godziny pracy: 22:00-{(22+int(device.worktime/60))%24}:{device.worktime%60}"
                        stats_after_optimalization.append({
                            "device": device.name,
                            "cost": cost,
                            "workhour": best_hours
                        })
            elif device.priority == 2:
                cost = device.power * device.worktime/60 * NIGHT_PRIZES
                if cost < device.current_cost:
                    best_hours = f"Godziny pracy: 22:00-{(22+int(device.worktime/60))%24}:{device.worktime%60}"
                    stats_after_optimalization.append({
                        "device": device.name,
                        "cost": cost,
                        "workhour": best_hours
                    })
        return stats_after_optimalization

def run_my_code(param):
    opt = OptimizationAlgorithm()
    results = opt.optimize()
    if not results:
        return "<p>Brak optymalizacji do wyświetlenia.</p>"
    html = "<h2>Wyniki optymalizacji:</h2><ul>"
    for r in results:
        html += f"<li>{r['device']}: koszt = {r['cost']:.2f} zł, {r['workhour']}</li>"
    html += "</ul>"
    return html
