"""
Validation utilities for Weather Intelligence Hub
"""

import re
from datetime import datetime, date
from typing import Tuple, Optional, Union

def validate_coordinates(lat: float, lng: float) -> Tuple[bool, str]:
    """
    Validate latitude and longitude coordinates
    
    Args:
        lat: Latitude value
        lng: Longitude value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check if values are numeric
        lat = float(lat)
        lng = float(lng)
        
        # Validate latitude range (-90 to 90)
        if not (-90 <= lat <= 90):
            return False, f"Latitude must be between -90 and 90, got {lat}"
        
        # Validate longitude range (-180 to 180)
        if not (-180 <= lng <= 180):
            return False, f"Longitude must be between -180 and 180, got {lng}"
        
        return True, "Valid coordinates"
        
    except (ValueError, TypeError):
        return False, "Coordinates must be numeric values"

def validate_date_range(start_date: Union[date, datetime], end_date: Union[date, datetime]) -> Tuple[bool, str]:
    """
    Validate date range
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Convert to date objects if they're datetime
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime):
            end_date = end_date.date()
        
        # Check if start date is before or equal to end date
        if start_date > end_date:
            return False, "Start date must be before or equal to end date"
        
        # Check if dates are not too far in the future (optional constraint)
        today = date.today()
        max_future_days = 365  # 1 year
        
        if (start_date - today).days > max_future_days:
            return False, f"Start date cannot be more than {max_future_days} days in the future"
        
        if (end_date - today).days > max_future_days:
            return False, f"End date cannot be more than {max_future_days} days in the future"
        
        return True, "Valid date range"
        
    except (ValueError, TypeError, AttributeError) as e:
        return False, f"Invalid date format: {str(e)}"

def validate_location_input(location: str) -> Tuple[bool, str]:
    """
    Validate location input string
    
    Args:
        location: Location string (city, coordinates, etc.)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not location or not location.strip():
        return False, "Location cannot be empty"
    
    location = location.strip()
    
    # Check length
    if len(location) > 200:
        return False, "Location input too long (max 200 characters)"
    
    if len(location) < 2:
        return False, "Location input too short (min 2 characters)"
    
    # Check for obviously invalid patterns
    if location.count(',') > 3:
        return False, "Too many commas in location"
    
    # Check for coordinate pattern
    coord_pattern = r'^-?\d+\.?\d*,\s*-?\d+\.?\d*$'
    if re.match(coord_pattern, location):
        # Parse and validate coordinates
        try:
            lat_str, lng_str = location.split(',')
            lat = float(lat_str.strip())
            lng = float(lng_str.strip())
            return validate_coordinates(lat, lng)
        except ValueError:
            return False, "Invalid coordinate format"
    
    return True, "Valid location input"

def validate_api_key(api_key: str, service_name: str = "API") -> Tuple[bool, str]:
    """
    Validate API key format
    
    Args:
        api_key: API key string
        service_name: Name of the service for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not api_key or not api_key.strip():
        return False, f"{service_name} key cannot be empty"
    
    api_key = api_key.strip()
    
    # Basic length check
    if len(api_key) < 10:
        return False, f"{service_name} key seems too short"
    
    if len(api_key) > 200:
        return False, f"{service_name} key seems too long"
    
    # Check for whitespace (most API keys shouldn't have spaces)
    if ' ' in api_key:
        return False, f"{service_name} key should not contain spaces"
    
    return True, f"Valid {service_name} key format"

def validate_temperature(temp: float, unit: str = "C") -> Tuple[bool, str]:
    """
    Validate temperature value
    
    Args:
        temp: Temperature value
        unit: Temperature unit (C, F, K)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        temp = float(temp)
        unit = unit.upper()
        
        # Define reasonable ranges for each unit
        ranges = {
            'C': (-100, 60),    # Celsius: extreme cold to extreme hot
            'F': (-148, 140),   # Fahrenheit equivalent
            'K': (173, 333)     # Kelvin equivalent
        }
        
        if unit not in ranges:
            return False, f"Invalid temperature unit: {unit}. Use C, F, or K"
        
        min_temp, max_temp = ranges[unit]
        
        if not (min_temp <= temp <= max_temp):
            return False, f"Temperature {temp}°{unit} is outside reasonable range ({min_temp}°{unit} to {max_temp}°{unit})"
        
        return True, f"Valid temperature: {temp}°{unit}"
        
    except (ValueError, TypeError):
        return False, "Temperature must be a numeric value"

def validate_humidity(humidity: Union[int, float]) -> Tuple[bool, str]:
    """
    Validate humidity percentage
    
    Args:
        humidity: Humidity value (0-100%)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        humidity = float(humidity)
        
        if not (0 <= humidity <= 100):
            return False, f"Humidity must be between 0 and 100%, got {humidity}%"
        
        return True, f"Valid humidity: {humidity}%"
        
    except (ValueError, TypeError):
        return False, "Humidity must be a numeric value"

def validate_wind_speed(speed: Union[int, float], unit: str = "ms") -> Tuple[bool, str]:
    """
    Validate wind speed
    
    Args:
        speed: Wind speed value
        unit: Unit (ms for m/s, mph for miles per hour, kmh for km/h)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        speed = float(speed)
        unit = unit.lower()
        
        if speed < 0:
            return False, "Wind speed cannot be negative"
        
        # Define maximum reasonable speeds for each unit
        max_speeds = {
            'ms': 150,    # m/s (hurricane force ~75 m/s)
            'mph': 300,   # mph
            'kmh': 500    # km/h
        }
        
        if unit not in max_speeds:
            return False, f"Invalid wind speed unit: {unit}. Use ms, mph, or kmh"
        
        if speed > max_speeds[unit]:
            return False, f"Wind speed {speed} {unit} seems unreasonably high"
        
        return True, f"Valid wind speed: {speed} {unit}"
        
    except (ValueError, TypeError):
        return False, "Wind speed must be a numeric value"