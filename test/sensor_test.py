import psutil


def get_first_sensor_temperature():
    try:
        temps = psutil.sensors_temperatures()
        temp = temps[next(iter(temps))][0].current
        print(f"温度:{temp}°C")
    except Exception as e:
        print(f"获取温度失败: {e}")


get_first_sensor_temperature()
