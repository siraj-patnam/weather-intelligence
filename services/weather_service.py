import requests
import streamlit as st
import os
from typing import Optional, Dict
from datetime import datetime

import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import requests
import streamlit as st
from typing import Optional, Dict


class WeatherService:
    """Service for OpenWeather API integration"""
    
    def __init__(self):
        try:
            self.openai_api_key = st.secrets.get("OPENAI_API_KEY")
        except:
            self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
        if not self.api_key:
            st.warning("⚠️ OpenWeather API key not found. Please set OPENWEATHER_API_KEY in your environment.")
    
    @st.cache_data(ttl=1800)  # Cache for 30 minutes
    def get_current_weather(_self, lat: float, lon: float) -> Optional[Dict]:
        """Get current weather for coordinates"""
        if not _self.api_key:
            return _self._get_mock_weather_data(lat, lon)
        
        try:
            url = f"{_self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': _self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Weather API error: {e}")
            return _self._get_mock_weather_data(lat, lon)
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            return None
    
    @st.cache_data(ttl=1800)
    def get_forecast(_self, lat: float, lon: float) -> Optional[Dict]:
        """Get 5-day forecast for coordinates"""
        if not _self.api_key:
            return _self._get_mock_forecast_data(lat, lon)
        
        try:
            url = f"{_self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': _self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Forecast API error: {e}")
            return _self._get_mock_forecast_data(lat, lon)
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")
            return None
    
    def _get_mock_weather_data(self, lat: float, lon: float) -> Dict:
        """Generate realistic mock weather data for demo purposes"""
        import random
        
        # Generate temperature based on latitude (very simplified)
        base_temp = 20 - abs(lat) * 0.5 + random.uniform(-10, 10)
        
        conditions = [
            {'main': 'Clear', 'description': 'clear sky', 'icon': '01d'},
            {'main': 'Clouds', 'description': 'few clouds', 'icon': '02d'},
            {'main': 'Clouds', 'description': 'scattered clouds', 'icon': '03d'},
            {'main': 'Rain', 'description': 'light rain', 'icon': '10d'},
            {'main': 'Snow', 'description': 'light snow', 'icon': '13d'}
        ]
        
        condition = random.choice(conditions)
        
        return {
            'coord': {'lon': lon, 'lat': lat},
            'weather': [condition],
            'main': {
                'temp': round(base_temp, 1),
                'feels_like': round(base_temp + random.uniform(-3, 3), 1),
                'temp_min': round(base_temp - random.uniform(2, 5), 1),
                'temp_max': round(base_temp + random.uniform(2, 5), 1),
                'pressure': random.randint(1000, 1030),
                'humidity': random.randint(30, 90)
            },
            'wind': {
                'speed': round(random.uniform(0, 15), 1),
                'deg': random.randint(0, 360)
            },
            'visibility': random.randint(5000, 10000),
            'dt': int(datetime.now().timestamp()),
            'name': f"Location ({lat:.2f}, {lon:.2f})"
        }
    
    def _get_mock_forecast_data(self, lat: float, lon: float) -> Dict:
        """Generate mock forecast data"""
        import random
        from datetime import timedelta
        
        forecast_list = []
        base_temp = 20 - abs(lat) * 0.5
        
        for i in range(40):  # 5 days * 8 (3-hour intervals)
            dt = datetime.now() + timedelta(hours=i * 3)
            temp = base_temp + random.uniform(-8, 8)
            
            conditions = ['Clear', 'Clouds', 'Rain']
            condition = random.choice(conditions)
            
            forecast_list.append({
                'dt': int(dt.timestamp()),
                'main': {
                    'temp': round(temp, 1),
                    'feels_like': round(temp + random.uniform(-2, 2), 1),
                    'temp_min': round(temp - random.uniform(1, 3), 1),
                    'temp_max': round(temp + random.uniform(1, 3), 1),
                    'pressure': random.randint(1000, 1030),
                    'humidity': random.randint(30, 90)
                },
                'weather': [{
                    'main': condition,
                    'description': f'{condition.lower()} sky',
                    'icon': '01d'
                }],
                'wind': {
                    'speed': round(random.uniform(0, 10), 1),
                    'deg': random.randint(0, 360)
                }
            })
        
        return {
            'list': forecast_list,
            'city': {
                'name': f"Location ({lat:.2f}, {lon:.2f})",
                'coord': {'lat': lat, 'lon': lon}
            }
        }