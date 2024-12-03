import requests
import datetime


# Ваш API ключ OpenWeatherMap
API_KEY = "6a9eedc6772205944011d6cbf0b0323f"

# Список городов с их координатами
cities = [
    {'name': 'Milan', 'lat': 45.4642, 'lon': 9.1895}, 
    {'name': 'Prague', 'lat': 50.0878, 'lon': 14.4205}, 
    {'name': 'Marianske Lazne', 'lat': 49.96489, 'lon': 12.7007}, 
    {'name': 'Venezia', 'lat': 45.4944, 'lon': 12.3714}, 
    {'name': 'Minsk', 'lat': 53.9044, 'lon': 27.5614}, 
    {'name': 'Moscow', 'lat': 55.7558, 'lon': 37.6173}, 
    {'name': 'Poznan', 'lat': 52.4064, 'lon': 16.9252},      
    {'name': 'Warsaw', 'lat': 52.2297, 'lon': 21.0122},   
    {'name': 'Vilnius', 'lat': 54.6872, 'lon': 25.2797},  
]


def get_weather_day(city_name):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city_name}&appid={API_KEY}"
    
    response = requests.get(complete_url)
    
    if response.status_code == 200:
        data = response.json()
        main = data['main']
        wind = data['wind']
        weather_description = data['weather'][0]['description']
        icon_code = data['weather'][0]['icon']  # Код иконки погоды
        day = datetime.datetime.fromtimestamp(data['dt']).strftime('%A')
        
        
        # Преобразуем температуру в градусы Цельсия
        temperature_celsius = main['temp'] - 273.15
        
        # Преобразуем давление в мм рт. ст.
        pressure_mm_hg = main['pressure'] * 0.75006375541921
        
        return {
            'day': day,
            'city': city_name,
            'temperature': round(temperature_celsius),
            'pressure': round(pressure_mm_hg),
            'humidity': main['humidity'],
            'wind_speed': wind['speed'],
            'description': weather_description,
            'icon': f"http://openweathermap.org/img/wn/{icon_code}@2x.png"  # URL иконки
        }
    else:
        return None

def get_weather_week(city_name):
    geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&appid={API_KEY}"
    geo_response = requests.get(geocoding_url)

    if geo_response.status_code == 200:
        geo_data = geo_response.json()
        if len(geo_data) == 0:
            return None
        
        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        
        weather_url = f"http://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&appid={API_KEY}"
        response = requests.get(weather_url)
        
        if response.status_code == 200:
            data = response.json()
            daily_forecast = []
            
            for day in data['daily']:
                # Преобразование метки времени в день недели
                day_name = datetime.datetime.fromtimestamp(day['dt']).strftime('%A')
                # Преобразуем температуру в градусы Цельсия
                temperature_celsius = day['temp']['day'] - 273.15
                # Преобразуем давление в мм рт. ст.
                pressure_mm_hg = day['pressure'] * 0.75006375541921
                
                daily_forecast.append({
                    'day': day_name,  # Передаем уже отформатированное имя дня
                    'temperature': round(temperature_celsius),
                    'pressure': round(pressure_mm_hg),
                    'humidity': day['humidity'],
                    'wind_speed': day['wind_speed'],
                    'description': day['weather'][0]['description'],
                    'icon': f"http://openweathermap.org/img/wn/{day['weather'][0]['icon']}@2x.png"
                })
            
            return daily_forecast
        else:
            return None
    else:
        return None


