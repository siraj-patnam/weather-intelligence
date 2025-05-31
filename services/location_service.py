import requests
import streamlit as st
import re
import os
from typing import Optional, Dict
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

class LocationService:
    """Service for location and geocoding operations"""
    
    def __init__(self):
        try:
            self.google_api_key = st.secrets.get("GOOGLE_GEOCODING_API_KEY")
        except:
            # Fallback to environment variable if not in Streamlit secrets
            self.google_api_key = os.getenv('GOOGLE_GEOCODING_API_KEY')
        self.nominatim = Nominatim(user_agent="weather_intelligence_hub")
        
        # Patterns for different location formats
        self.coordinate_pattern = re.compile(r'^(-?\d+\.?\d*),\s*(-?\d+\.?\d*)$')
    
    def get_location_data(self, location_input: str) -> Optional[Dict]:
        """Get location data from various input formats"""
        if not location_input or not location_input.strip():
            return None
        
        location_input = location_input.strip()
        
        # Check if input is coordinates
        coord_match = self.coordinate_pattern.match(location_input)
        if coord_match:
            try:
                lat, lng = float(coord_match.group(1)), float(coord_match.group(2))
                if -90 <= lat <= 90 and -180 <= lng <= 180:
                    location_name = self._reverse_geocode(lat, lng)
                    return {
                        'lat': lat,
                        'lng': lng,
                        'display_name': location_name or f"Location ({lat:.4f}, {lng:.4f})"
                    }
                else:
                    st.error("❌ Invalid coordinates. Lat: -90 to 90, Lng: -180 to 180")
                    return None
            except ValueError:
                pass
        
        # Try geocoding the location name
        return self._geocode_location(location_input)
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def _geocode_location(_self, location: str) -> Optional[Dict]:
        """Geocode location using Google API or Nominatim fallback"""
        # Try Google Geocoding first
        if _self.google_api_key:
            result = _self._geocode_with_google(location)
            if result:
                return result
        
        # Fallback to Nominatim
        return _self._geocode_with_nominatim(location)
    
    def _geocode_with_google(self, location: str) -> Optional[Dict]:
        """Geocode using Google Geocoding API"""
        try:
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': location,
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                result = data['results'][0]
                geometry = result['geometry']['location']
                
                return {
                    'lat': geometry['lat'],
                    'lng': geometry['lng'],
                    'display_name': result['formatted_address']
                }
            else:
                return None
                
        except Exception as e:
            print(f"Google geocoding error: {e}")
            return None
    
    def _geocode_with_nominatim(self, location: str) -> Optional[Dict]:
        """Geocode using Nominatim (OpenStreetMap)"""
        try:
            result = self.nominatim.geocode(location, timeout=10)
            
            if result:
                return {
                    'lat': result.latitude,
                    'lng': result.longitude,
                    'display_name': result.address
                }
            else:
                st.warning(f"🔍 Location '{location}' not found")
                return None
                
        except GeocoderTimedOut:
            st.error("🔍 Geocoding service timeout. Please try again.")
            return None
        except Exception as e:
            st.error(f"❌ Geocoding error: {e}")
            return None
    
    @st.cache_data(ttl=3600)
    def _reverse_geocode(_self, lat: float, lng: float) -> Optional[str]:
        """Get location name from coordinates"""
        try:
            # Try Google reverse geocoding first
            if _self.google_api_key:
                url = "https://maps.googleapis.com/maps/api/geocode/json"
                params = {
                    'latlng': f"{lat},{lng}",
                    'key': _self.google_api_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == 'OK' and data['results']:
                        return data['results'][0]['formatted_address']
            
            # Fallback to Nominatim
            result = _self.nominatim.reverse((lat, lng), timeout=10)
            return result.address if result else None
            
        except Exception:
            return None