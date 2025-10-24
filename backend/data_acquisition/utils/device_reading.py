from data_acquisition.models import DeviceReading

def get_all_readings():
    return DeviceReading.objects.all()
