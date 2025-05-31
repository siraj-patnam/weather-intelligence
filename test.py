#!/usr/bin/env python3
"""
API Keys Test Script
Tests all your API connections using keys from .env file
"""

import os
import requests
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables from .env file
load_dotenv()

def show_loaded_keys():
    """Display what keys were loaded (masked for security)"""
    print("🔑 Loading API keys from .env file...")
    
    openweather = os.getenv('OPENWEATHER_API_KEY')
    mongodb = os.getenv('MONGODB_URI')
    google = os.getenv('GOOGLE_GEOCODING_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print(f"   OpenWeather: {'✅ Found' if openweather else '❌ Missing'} {openweather[:10] + '...' if openweather else ''}")
    print(f"   MongoDB: {'✅ Found' if mongodb else '❌ Missing'} {mongodb[:20] + '...' if mongodb else ''}")
    print(f"   Google: {'✅ Found' if google else '❌ Missing'} {google[:10] + '...' if google else ''}")
    print(f"   OpenAI: {'✅ Found' if openai_key else '❌ Missing'} {openai_key[:10] + '...' if openai_key else ''}")
    print()

def test_openweather_api():
    """Test OpenWeather API"""
    print("\n🌤️  Testing OpenWeather API...")
    
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        print("❌ OpenWeather API key not found in .env")
        return False
    
    try:
        # Test with New York coordinates
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': 40.7128,
            'lon': -74.0060,
            'appid': api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            city = data['name']
            condition = data['weather'][0]['description']
            print(f"✅ OpenWeather API working!")
            print(f"   📍 {city}: {temp}°C, {condition}")
            return True
        else:
            print(f"❌ OpenWeather API error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ OpenWeather API connection failed: {e}")
        return False

def test_mongodb():
    """Test MongoDB connection"""
    print("\n🍃 Testing MongoDB connection...")
    
    mongodb_uri = os.getenv('MONGODB_URI')
    if not mongodb_uri:
        print("❌ MongoDB URI not found in .env")
        return False
    
    try:
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        
        # Test database access
        db = client[os.getenv('DATABASE_NAME', 'weather_app')]
        collection = db['test_collection']
        
        # Insert test document
        test_doc = {'test': True, 'message': 'API test successful'}
        result = collection.insert_one(test_doc)
        
        # Clean up test document
        collection.delete_one({'_id': result.inserted_id})
        
        print("✅ MongoDB connection working!")
        print(f"   📊 Database: {db.name}")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def test_google_geocoding():
    """Test Google Geocoding API"""
    print("\n🗺️  Testing Google Geocoding API...")
    
    api_key = os.getenv('GOOGLE_GEOCODING_API_KEY')
    if not api_key:
        print("❌ Google Geocoding API key not found in .env")
        return False
    
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': 'New York City',
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK' and data['results']:
                location = data['results'][0]
                address = location['formatted_address']
                coords = location['geometry']['location']
                print(f"✅ Google Geocoding API working!")
                print(f"   📍 {address}")
                print(f"   🌍 Coordinates: {coords['lat']}, {coords['lng']}")
                return True
            else:
                print(f"❌ Google Geocoding API error: {data.get('status', 'Unknown error')}")
                return False
        else:
            print(f"❌ Google Geocoding API HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Google Geocoding API connection failed: {e}")
        return False

def test_openai_api():
    """Test OpenAI API"""
    print("\n🤖 Testing OpenAI API...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not found in .env")
        return False
    
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'API test successful' if you can read this."}
            ],
            max_tokens=10
        )
        
        message = response.choices[0].message.content
        print("✅ OpenAI API working!")
        print(f"   🤖 Response: {message}")
        return True
        
    except ImportError:
        print("❌ OpenAI package not installed. Run: pip install openai")
        return False
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        return False

def test_all_apis():
    """Test all APIs and provide summary"""
    print("🚀 Weather Intelligence Hub - API Test Suite")
    print("=" * 50)
    
    # Show what keys were loaded first
    show_loaded_keys()
    
    results = {
        'OpenWeather': test_openweather_api(),
        'MongoDB': test_mongodb(),
        'Google Geocoding': test_google_geocoding(),
        'OpenAI': test_openai_api()
    }
    
    print("\n" + "=" * 50)
    print("📊 API Test Summary:")
    print("=" * 50)
    
    working_count = 0
    for service, status in results.items():
        status_icon = "✅" if status else "❌"
        status_text = "Working" if status else "Failed"
        print(f"{status_icon} {service:<20} {status_text}")
        if status:
            working_count += 1
    
    print(f"\n🎯 Result: {working_count}/{len(results)} APIs working")
    
    if working_count == len(results):
        print("🎉 All APIs are working! Your Weather Intelligence Hub is ready!")
        print("🚀 You can now run: streamlit run app.py")
    elif working_count >= 2:
        print("⚠️  Some APIs working. App will run with limited functionality.")
        print("🔧 Check the failed APIs above and verify your keys.")
    else:
        print("🔧 Most APIs failed. Check your API keys and network connection.")
        print("💡 The app will still work with fallback/mock data.")
    
    print("\n📝 Next steps:")
    print("1. Fix any failed API connections above")
    print("2. Run: streamlit run app.py")
    print("3. Test the interactive map and AI assistant!")
    
    return results

if __name__ == "__main__":
    test_all_apis()