import os
import streamlit as st
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class WeatherAI:
    """Simple, intelligent weather assistant that lets AI do the thinking"""
    
    def __init__(self):
        try:
            self.openai_api_key = st.secrets.get("OPENAI_API_KEY")
        except:
            self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.use_openai = self.openai_api_key is not None
        
        if self.use_openai:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.openai_api_key)
                self.model = "gpt-3.5-turbo"
            except ImportError:
                st.warning("⚠️ OpenAI package not installed. Using simple fallback.")
                self.use_openai = False
            except Exception as e:
                st.warning(f"⚠️ OpenAI error: {e}. Using simple fallback.")
                self.use_openai = False
    
    def get_response(self, user_question: str, chat_history: List[Dict] = None) -> str:
        """Simple response method for backward compatibility"""
        return self.get_response_with_weather_data(user_question)
    
    def get_response_with_weather_data(self, user_question: str, weather_data: Dict = None, 
                                     location_name: str = None, forecast_data: Dict = None) -> str:
        """Get AI response with real weather data - let AI do the thinking"""
        
        if self.use_openai:
            return self._get_smart_ai_response(user_question, weather_data, location_name, forecast_data)
        else:
            return self._get_simple_fallback(user_question, weather_data, location_name)
    
    def _get_smart_ai_response(self, user_question: str, weather_data: Dict = None, 
                              location_name: str = None, forecast_data: Dict = None) -> str:
        """Let GPT analyze the weather data and respond naturally"""
        
        # Build weather context for AI
        weather_info = ""
        
        if weather_data:
            try:
                current = weather_data['main']
                weather = weather_data['weather'][0]
                wind = weather_data.get('wind', {})
                
                weather_info = f"""
CURRENT WEATHER DATA for {location_name}:
- Temperature: {current['temp']}°C (feels like {current['feels_like']}°C)
- Condition: {weather['main']} - {weather['description']}
- Humidity: {current['humidity']}%
- Wind: {wind.get('speed', 0)} m/s
- Pressure: {current['pressure']} hPa
- High/Low: {current['temp_max']}°C / {current['temp_min']}°C
"""
            except Exception as e:
                weather_info = f"Weather data available but parsing error: {e}"
        
        if forecast_data:
            try:
                forecast_info = "\nUPCOMING FORECAST:\n"
                for item in forecast_data.get('list', [])[:8]:  # Next 24 hours
                    dt = datetime.fromtimestamp(item['dt']).strftime('%m/%d %H:%M')
                    temp = item['main']['temp']
                    condition = item['weather'][0]['main']
                    forecast_info += f"- {dt}: {temp}°C, {condition}\n"
                weather_info += forecast_info
            except:
                weather_info += "\nForecast data available but parsing error occurred."
        
        # Simple, direct prompt - let AI think
        system_prompt = f"""You are a helpful weather assistant. You have access to current, real weather data.

Current weather information:
{weather_info if weather_info else "No current weather data available."}

Instructions:
- Use the actual weather data provided to give specific, helpful advice
- Be conversational and helpful
- Reference the real temperature, conditions, and location when relevant
- Give practical recommendations based on the actual conditions
- If no weather data is provided, let the user know you need weather data for specific advice
- Keep responses concise but helpful
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"AI Error: {str(e)}. Here's what I can tell you from the weather data: {weather_info[:200]}..."
    
    def _get_simple_fallback(self, user_question: str, weather_data: Dict = None, location_name: str = None) -> str:
        """Simple fallback when OpenAI isn't available"""
        
        if weather_data:
            try:
                temp = weather_data['main']['temp']
                condition = weather_data['weather'][0]['description']
                humidity = weather_data['main']['humidity']
                
                return f"""🤖 **Weather Assistant** (Simple Mode)

**Current conditions for {location_name}:**
- Temperature: {temp}°C
- Conditions: {condition}
- Humidity: {humidity}%

**Your question:** {user_question}

**Basic advice:** Based on {temp}°C and {condition}, I can see the current conditions. For detailed analysis and recommendations, add your OpenAI API key to get intelligent responses!

**Current weather summary:** The temperature of {temp}°C with {condition} conditions should help you plan your activities accordingly."""

            except Exception as e:
                return f"Weather data available but couldn't parse it. Error: {e}"
        else:
            return f"""🤖 **Weather Assistant** 

**Your question:** {user_question}

I don't currently have weather data to analyze. To get specific weather advice:

1. 🗺️ Click on the Interactive Map to get weather for any location
2. 🔍 Use the Quick Weather search in the sidebar
3. Then ask me your question again!

I'll analyze the real weather conditions and give you helpful advice."""
    
    def get_weather_insights(self, current_weather: Dict, forecast_data: Dict = None) -> str:
        """Generate quick insights about weather conditions"""
        if not current_weather:
            return "No weather data available for insights."
        
        if self.use_openai:
            weather_context = f"""
Temperature: {current_weather['main']['temp']}°C
Condition: {current_weather['weather'][0]['description']}
Humidity: {current_weather['main']['humidity']}%
Wind: {current_weather.get('wind', {}).get('speed', 0)} m/s
"""
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Provide 2-3 brief weather insights based on the data provided. Be concise and practical."},
                        {"role": "user", "content": f"Give insights about this weather: {weather_context}"}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except:
                pass
        
        # Simple fallback
        temp = current_weather['main']['temp']
        condition = current_weather['weather'][0]['main']
        
        if temp < 10:
            return "❄️ Cold conditions - dress warmly and consider indoor activities."
        elif temp > 25:
            return "🌞 Warm weather - great for outdoor activities, stay hydrated."
        elif 'rain' in condition.lower():
            return "🌧️ Rainy conditions - plan indoor activities or bring waterproof gear."
        else:
            return f"🌤️ Pleasant {temp}°C with {condition.lower()} conditions - good for most activities."
    
    def get_activity_recommendations(self, weather_data: Dict) -> str:
        """Get activity recommendations"""
        if not weather_data:
            return "No weather data available for recommendations."
        
        if self.use_openai:
            weather_context = f"""
Temperature: {weather_data['main']['temp']}°C
Condition: {weather_data['weather'][0]['description']}
Humidity: {weather_data['main']['humidity']}%
Wind: {weather_data.get('wind', {}).get('speed', 0)} m/s
"""
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "Recommend 3-4 specific activities based on the weather conditions. Be practical and specific."},
                        {"role": "user", "content": f"What activities would you recommend for this weather: {weather_context}"}
                    ],
                    max_tokens=200,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except:
                pass
        
        # Simple fallback
        temp = weather_data['main']['temp']
        condition = weather_data['weather'][0]['main'].lower()
        
        if 'rain' in condition:
            return "☔ Rainy weather activities:\n• Indoor museums\n• Shopping centers\n• Cozy cafés\n• Movie theaters"
        elif temp > 25:
            return "🌞 Hot weather activities:\n• Swimming\n• Shaded parks\n• Early morning walks\n• Air-conditioned venues"
        elif temp < 10:
            return "❄️ Cold weather activities:\n• Indoor attractions\n• Hot drink venues\n• Museums\n• Shopping malls"
        else:
            return "🌤️ Great weather for:\n• Walking or hiking\n• Outdoor dining\n• Parks and recreation\n• Cycling"