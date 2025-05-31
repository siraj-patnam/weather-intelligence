from datetime import datetime
from typing import Dict, Any

def get_weather_emoji(condition: str) -> str:
    """Get emoji representation of weather condition"""
    condition = condition.lower()
    
    emoji_map = {
        'clear': '☀️',
        'sunny': '☀️',
        'clouds': '☁️',
        'partly cloudy': '⛅',
        'overcast': '☁️',
        'rain': '🌧️',
        'drizzle': '🌦️',
        'shower': '🌧️',
        'thunderstorm': '⛈️',
        'snow': '❄️',
        'mist': '🌫️',
        'fog': '🌫️',
        'haze': '🌫️',
        'dust': '🌪️',
        'sand': '🌪️',
        'tornado': '🌪️',
        'hurricane': '🌀',
        'hot': '🔥',
        'cold': '🥶',
        'windy': '💨'
    }
    
    # Try to find a match
    for key, emoji in emoji_map.items():
        if key in condition:
            return emoji
    
    # Default fallback
    return '🌤️'

def format_temperature(temp: float, unit: str = 'C') -> str:
    """Format temperature with appropriate unit"""
    if unit.upper() == 'F':
        temp_f = (temp * 9/5) + 32
        return f"{temp_f:.1f}°F"
    elif unit.upper() == 'K':
        temp_k = temp + 273.15
        return f"{temp_k:.1f}K"
    else:
        return f"{temp:.1f}°C"

def format_date(date_obj: datetime, format_type: str = 'standard') -> str:
    """Format date according to specified type"""
    if not date_obj:
        return 'N/A'
    
    formats = {
        'standard': '%Y-%m-%d %H:%M:%S',
        'date_only': '%Y-%m-%d',
        'time_only': '%H:%M:%S',
        'readable': '%B %d, %Y at %I:%M %p',
        'short': '%m/%d/%Y',
        'iso': '%Y-%m-%dT%H:%M:%SZ'
    }
    
    return date_obj.strftime(formats.get(format_type, formats['standard']))

def get_comfort_level(temp: float, humidity: int) -> str:
    """Determine comfort level based on temperature and humidity"""
    if temp < 0:
        return "🥶 Very Cold"
    elif temp < 10:
        return "❄️ Cold"
    elif temp < 20:
        return "😐 Cool"
    elif temp <= 25 and humidity <= 60:
        return "😊 Comfortable"
    elif temp <= 30 and humidity <= 70:
        return "😅 Warm"
    elif temp <= 35:
        return "🥵 Hot"
    else:
        return "🔥 Very Hot"

def get_wind_description(speed: float) -> str:
    """Get wind description based on speed (m/s)"""
    if speed < 0.3:
        return "🍃 Calm"
    elif speed < 1.6:
        return "🍃 Light air"
    elif speed < 3.4:
        return "🍃 Light breeze"
    elif speed < 5.5:
        return "💨 Gentle breeze"
    elif speed < 8.0:
        return "💨 Moderate breeze"
    elif speed < 10.8:
        return "💨 Fresh breeze"
    elif speed < 13.9:
        return "💨 Strong breeze"
    elif speed < 17.2:
        return "🌬️ High wind"
    elif speed < 20.8:
        return "🌬️ Gale"
    else:
        return "🌪️ Storm"

def calculate_heat_index(temp_c: float, humidity: int) -> float:
    """Calculate heat index (feels like temperature)"""
    # Convert to Fahrenheit for calculation
    temp_f = (temp_c * 9/5) + 32
    
    # Heat index formula (only applicable when temp >= 80°F)
    if temp_f < 80:
        return temp_c
    
    hi = -42.379 + 2.04901523 * temp_f + 10.14333127 * humidity
    hi -= 0.22475541 * temp_f * humidity
    hi -= 6.83783e-3 * temp_f * temp_f
    hi -= 5.481717e-2 * humidity * humidity
    hi += 1.22874e-3 * temp_f * temp_f * humidity
    hi += 8.5282e-4 * temp_f * humidity * humidity
    hi -= 1.99e-6 * temp_f * temp_f * humidity * humidity
    
    # Convert back to Celsius
    return (hi - 32) * 5/9

def get_uv_description(uv_index: float) -> str:
    """Get UV index description"""
    if uv_index <= 2:
        return "🟢 Low - Minimal protection needed"
    elif uv_index <= 5:
        return "🟡 Moderate - Seek shade during midday"
    elif uv_index <= 7:
        return "🟠 High - Protection essential"
    elif uv_index <= 10:
        return "🔴 Very High - Extra protection required"
    else:
        return "🟣 Extreme - Avoid sun exposure"

def format_weather_summary(weather_data: Dict[str, Any]) -> str:
    """Format weather data into a readable summary"""
    if not weather_data:
        return "Weather data not available"
    
    try:
        main = weather_data['main']
        weather = weather_data['weather'][0]
        wind = weather_data.get('wind', {})
        
        emoji = get_weather_emoji(weather['main'])
        comfort = get_comfort_level(main['temp'], main['humidity'])
        wind_desc = get_wind_description(wind.get('speed', 0))
        
        summary = f"""
{emoji} **{weather['description'].title()}**
🌡️ **Temperature:** {main['temp']:.1f}°C (feels like {main['feels_like']:.1f}°C)
💧 **Humidity:** {main['humidity']}%
{wind_desc} **Wind:** {wind.get('speed', 0):.1f} m/s
📊 **Pressure:** {main['pressure']} hPa
😊 **Comfort:** {comfort}
        """
        
        return summary.strip()
        
    except Exception as e:
        return f"Error formatting weather summary: {e}"