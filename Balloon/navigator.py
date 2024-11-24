import requests
import math
import time

# Бібліотеки для апаратного управління
from gpiozero import Motor  # Для керування двигунами
from smbus2 import SMBus  # Наприклад, для барометра BMP280
from adafruit_gps import GPS  # Для GPS-модуля

# Погода
def get_weather_forecast(lat, lon):
    url = f"https://nomads.ncep.noaa.gov/"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Витягування даних про вітер, напрямок і швидкість
        wind_speed = data["wind"]["speed"]
        wind_dir = data["wind"]["direction"]
        return wind_speed, wind_dir
    else:
        print("Помилка завантаження даних погоди.")
        return None, None

# Motor control
motor_left = Motor(forward=17, backward=18)  # Піни для двигунів
motor_right = Motor(forward=22, backward=23)

def control_motors(direction, speed):
    if direction == "left":
        motor_left.forward(speed)
        motor_right.backward(speed)
    elif direction == "right":
        motor_left.backward(speed)
        motor_right.forward(speed)
    elif direction == "forward":
        motor_left.forward(speed)
        motor_right.forward(speed)
    elif direction == "backward":
        motor_left.backward(speed)
        motor_right.backward(speed)
    else:
        motor_left.stop()
        motor_right.stop()

def navigate_to_target(target_lat, target_lon, current_lat, current_lon, wind_speed, wind_dir):
    # Розрахунок азимута
    delta_lon = target_lon - current_lon
    x = math.sin(math.radians(delta_lon)) * math.cos(math.radians(target_lat))
    y = math.cos(math.radians(current_lat)) * math.sin(math.radians(target_lat)) - \
        math.sin(math.radians(current_lat)) * math.cos(math.radians(target_lat)) * math.cos(math.radians(delta_lon))
    azimuth = math.degrees(math.atan2(x, y))
    
    # Врахування вітру
    adjusted_azimuth = azimuth - wind_dir
    
    # Управління
    if adjusted_azimuth < -10:
        control_motors("left", 0.5)
    elif adjusted_azimuth > 10:
        control_motors("right", 0.5)
    else:
        control_motors("forward", 0.7)

def main():
    target_lat = 50.4501  # Широта цільової точки
    target_lon = 30.5234  # Довгота цільової точки

    gps = GPS()  # Ініціалізація GPS-модуля
    gps.start()  # Почати отримувати дані GPS
    
    while True:
        # Отримати поточні координати
        current_lat, current_lon = gps.get_location()
        
        # Отримати прогноз погоди
        wind_speed, wind_dir = get_weather_forecast(current_lat, current_lon)
        
        # Навігація до цілі
        if wind_speed and wind_dir:
            navigate_to_target(target_lat, target_lon, current_lat, current_lon, wind_speed, wind_dir)
        else:
            print("Чекаємо оновлення даних погоди...")
        
        time.sleep(10)  # Затримка між оновленнями


