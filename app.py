import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List

load_dotenv()



# Import services
from services.weather_service import WeatherService
from services.location_service import LocationService
from services.database_service import DatabaseService
from services.ai_assistant import WeatherAI
from utils.helpers import get_weather_emoji, format_temperature, format_date
from utils.map_utils import create_weather_map, add_weather_markers
from utils.validators import validate_coordinates, validate_date_range

# Page configuration
st.set_page_config(
    page_title="Weather Intelligence Hub",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Force light mode
st.markdown("""
<style>
    .stApp {
        color-scheme: light !important;
    }
    
    /* Force light mode colors */
    .stApp > header {
        background-color: transparent !important;
    }
    
    .main .block-container {
        background-color: white !important;
    }
    
    /* Override any dark mode settings */
    [data-theme="dark"] {
        color-scheme: light !important;
    }
    
    /* Force sidebar to light mode */
    .css-1d391kg {
        background-color: #f0f2f6 !important;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS for beautiful UI
def load_custom_css():
    st.markdown("""
    <style>
    /* Force light theme globally */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: white !important;
        color: #262730 !important;
    }
    
    /* Main app container */
    .stApp {
        background-color: white !important;
        color: #262730 !important;
    }
    
    /* Main content area */
    .main {
        padding-top: 1rem;
        background-color: white !important;
        color: #262730 !important;
    }
    
    /* Block container */
    .block-container {
        background-color: white !important;
        color: #262730 !important;
    }
    
    /* Sidebar - force light */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6 !important;
    }
    
    [data-testid="stSidebar"] .css-1lcbmhc {
        background-color: #f0f2f6 !important;
    }
    
    /* All text elements */
    .stMarkdown, .stText, p, span, div, h1, h2, h3, h4, h5, h6 {
        color: #262730 !important;
    }
    
    /* Input fields */
    .stTextInput input {
        background-color: white !important;
        color: #262730 !important;
        border: 1px solid #cccccc !important;
    }
    
    .stSelectbox select {
        background-color: white !important;
        color: #262730 !important;
        border: 1px solid #cccccc !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: white !important;
        color: #262730 !important;
        border: 1px solid #cccccc !important;
    }
    
    .stButton > button:hover {
        back

# Initialize services
@st.cache_resource
def init_services():
    """Initialize all services"""
    try:
        weather_service = WeatherService()
        location_service = LocationService()
        db_service = DatabaseService()
        ai_assistant = WeatherAI()
        
        return {
            'weather': weather_service,
            'location': location_service,
            'database': db_service,
            'ai': ai_assistant
        }
    except Exception as e:
        st.error(f"❌ Failed to initialize services: {e}")
        return None

def main():
    load_custom_css()
    
    # App header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="location-header">
            <h1>Weather Intelligence Hub</h1>
            <p>Interactive Global Weather with AI Assistant</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize services
    services = init_services()
    if not services:
        st.stop()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## 🗺️ Navigation")
        page = st.selectbox(
            "Choose Feature",
            [
                "🌍 Interactive Map", 
                "🤖 AI Weather Assistant",
                "📊 Weather Dashboard",
                "💾 Data Management",
                "📈 Analytics",
                "📤 Export Data"
            ]
        )
        
        st.markdown("---")
        
        # Quick weather lookup
        st.markdown("### ⚡ Quick Weather")
        quick_location = st.text_input("Enter location:", placeholder="New York, Paris, Tokyo...")
        
        if quick_location:
            with st.spinner("Getting weather..."):
                location_data = services['location'].get_location_data(quick_location)
                if location_data:
                    weather = services['weather'].get_current_weather(
                        location_data['lat'], location_data['lng']
                    )
                    if weather:
                        temp = weather['main']['temp']
                        condition = weather['weather'][0]['main']
                        emoji = get_weather_emoji(condition)
                        
                        st.markdown(f"""
                        <div style="text-align: center; padding: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin: 10px 0;">
                            <div style="font-size: 2rem;">{emoji}</div>
                            <div style="font-size: 1.5rem; font-weight: bold;">{temp:.1f}°C</div>
                            <div>{condition}</div>
                            <div style="font-size: 0.9rem;">{location_data['display_name']}</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📱 About PM Accelerator")
        st.markdown("""
        **Product Manager Accelerator** helps aspiring product managers 
        transition into product management roles through comprehensive 
        training and mentorship programs.
        
        [Visit LinkedIn](https://www.linkedin.com/school/pmaccelerator/)
        """)
        
        st.markdown("**Built by:** Siraj Patnam")

    # Main content routing
    if page == "🌍 Interactive Map":
        interactive_map_page(services)
    elif page == "🤖 AI Weather Assistant":
        ai_assistant_page(services)
    elif page == "📊 Weather Dashboard":
        dashboard_page(services)
    elif page == "💾 Data Management":
        data_management_page(services)
    elif page == "📈 Analytics":
        analytics_page(services)
    elif page == "📤 Export Data":
        export_page(services)

def interactive_map_page(services):
    """Interactive global map with weather data"""
    st.markdown("## 🌍 Interactive Global Weather Map")
    st.markdown("**Click anywhere on the map to get weather data for that location!**")
    
    # Initialize session state variables
    if 'map_center' not in st.session_state:
        st.session_state.map_center = [40.7128, -74.0060]  # NYC default
    
    if 'map_zoom' not in st.session_state:
        st.session_state.map_zoom = 5
    
    if 'first_click_processed' not in st.session_state:
        st.session_state.first_click_processed = False
    
    # Map controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        location_input = st.text_input(
            "🔍 Search Location", 
            placeholder="Search for cities, landmarks, coordinates..."
        )
    
    with col2:
        map_style = st.selectbox("Map Style", ["OpenStreetMap", "Satellite", "Terrain"])
    
    with col3:
        show_weather_overlay = st.checkbox("Weather Overlay", value=True)
    
    # Handle location search
    if location_input:
        location_data = services['location'].get_location_data(location_input)
        if location_data:
            st.session_state.map_center = [location_data['lat'], location_data['lng']]
            st.session_state.map_zoom = 10
    
    # Create the map
    m = create_weather_map(
        center=st.session_state.map_center,
        zoom=st.session_state.map_zoom,
        style=map_style
    )
    
    # Add weather markers if overlay is enabled
    if show_weather_overlay:
        major_cities = [
            {"name": "New York", "lat": 40.7128, "lng": -74.0060},
            {"name": "London", "lat": 51.5074, "lng": -0.1278},
            {"name": "Tokyo", "lat": 35.6762, "lng": 139.6503},
            {"name": "Paris", "lat": 48.8566, "lng": 2.3522},
            {"name": "Sydney", "lat": -33.8688, "lng": 151.2093}
        ]
        
        for city in major_cities:
            weather = services['weather'].get_current_weather(city['lat'], city['lng'])
            if weather:
                add_weather_markers(m, city, weather)
    
    # Display the map
    map_data = st_folium(m, width=700, height=500, returned_objects=["last_clicked"])
    
    # Handle map clicks with better state management
    if map_data and map_data.get('last_clicked') is not None:
        clicked_lat = map_data['last_clicked']['lat']
        clicked_lng = map_data['last_clicked']['lng']
        
        # Check if this is a new click or the same click
        current_click = f"{clicked_lat:.4f},{clicked_lng:.4f}"
        last_click = st.session_state.get('last_map_click', '')
        
        if current_click != last_click:
            # This is a new click, process it
            st.session_state.last_map_click = current_click
            
            st.markdown(f"### 📍 Weather for Clicked Location")
            st.markdown(f"**Coordinates:** {clicked_lat:.4f}, {clicked_lng:.4f}")
            
            with st.spinner("🔄 Getting weather data for selected location..."):
                # Get weather data for clicked location
                weather_data = services['weather'].get_current_weather(clicked_lat, clicked_lng)
                forecast_data = services['weather'].get_forecast(clicked_lat, clicked_lng)
                
                if weather_data:
                    # Create location data for the clicked location
                    clicked_location_data = {
                        'lat': clicked_lat,
                        'lng': clicked_lng,
                        'display_name': f"Location ({clicked_lat:.4f}, {clicked_lng:.4f})"
                    }
                    
                    # Save to session state for AI
                    st.session_state.last_weather_data = weather_data
                    st.session_state.last_location_name = clicked_location_data['display_name']
                    st.session_state.last_forecast_data = forecast_data
                    
                    # Display current weather
                    display_current_weather(weather_data, clicked_location_data)
                    
                    # Display forecast
                    if forecast_data:
                        st.markdown("### 📅 5-Day Forecast")
                        display_forecast_cards(forecast_data)
                    
                    # AI insights
                    with st.expander("🤖 AI Weather Insights"):
                        ai_insights = services['ai'].get_weather_insights(weather_data, forecast_data)
                        st.markdown(ai_insights)
                else:
                    st.error("❌ Could not retrieve weather data for this location")

def display_current_weather(weather_data, location_data):
    """Display current weather in a beautiful card format"""
    # Get location name
    location_name = f"Location ({location_data['lat']:.4f}, {location_data['lng']:.4f})"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        # Weather icon and condition
        weather_emoji = get_weather_emoji(weather_data['weather'][0]['main'])
        st.markdown(f"""
        <div class="weather-icon">
            {weather_emoji}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="text-align: center; font-size: 1.2rem; color: #666;">
            {weather_data['weather'][0]['description'].title()}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Main temperature
        temp = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        
        st.markdown(f"""
        <div class="weather-card">
            <div class="temperature-big">{temp:.1f}°C</div>
            <div style="text-align: center; font-size: 1.1rem;">
                Feels like {feels_like:.1f}°C
            </div>
            <div style="text-align: center; margin-top: 10px;">
                📍 {location_name}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # High/Low temperatures
        st.markdown(f"""
        <div class="metric-card">
            <strong>High/Low</strong><br>
            {weather_data['main']['temp_max']:.1f}° / {weather_data['main']['temp_min']:.1f}°
        </div>
        """, unsafe_allow_html=True)
    
    # Additional metrics
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("💧 Humidity", f"{weather_data['main']['humidity']}%"),
        ("🌬️ Wind", f"{weather_data['wind']['speed']} m/s"),
        ("📊 Pressure", f"{weather_data['main']['pressure']} hPa"),
        ("👁️ Visibility", f"{weather_data.get('visibility', 'N/A')} m")
    ]
    
    for i, (title, value) in enumerate(metrics):
        with [col1, col2, col3, col4][i]:
            st.markdown(f"""
            <div class="metric-card">
                <h4>{title}</h4>
                <h2>{value}</h2>
            </div>
            """, unsafe_allow_html=True)

def display_forecast_cards(forecast_data):
    """Display 5-day forecast in card format"""
    # Process forecast data into daily summaries
    daily_forecasts = {}
    for item in forecast_data['list']:
        date = datetime.fromtimestamp(item['dt']).date()
        if date not in daily_forecasts:
            daily_forecasts[date] = {
                'temp_min': item['main']['temp_min'],
                'temp_max': item['main']['temp_max'],
                'weather': item['weather'][0],
                'humidity': item['main']['humidity'],
                'wind_speed': item['wind']['speed']
            }
        else:
            daily_forecasts[date]['temp_min'] = min(
                daily_forecasts[date]['temp_min'], item['main']['temp_min']
            )
            daily_forecasts[date]['temp_max'] = max(
                daily_forecasts[date]['temp_max'], item['main']['temp_max']
            )
    
    # Display forecast cards
    cols = st.columns(5)
    for i, (date, data) in enumerate(list(daily_forecasts.items())[:5]):
        with cols[i]:
            weather_emoji = get_weather_emoji(data['weather']['main'])
            day_name = date.strftime("%A")
            date_str = date.strftime("%m/%d")
            
            st.markdown(f"""
            <div class="forecast-card">
                <h4>{day_name}</h4>
                <p>{date_str}</p>
                <div style="font-size: 2rem; margin: 10px 0;">{weather_emoji}</div>
                <h3>{data['temp_max']:.1f}°</h3>
                <p style="margin: 5px 0;">{data['temp_min']:.1f}°</p>
                <small>{data['weather']['description']}</small>
            </div>
            """, unsafe_allow_html=True)

def ai_assistant_page(services):
    """AI-powered weather assistant with fixed chat interface"""
    st.markdown("## 🤖 AI Weather Assistant")
    st.markdown("Ask me anything about weather, travel planning, or activities!")
    
    # Get current weather data from session state
    current_weather = st.session_state.get('last_weather_data')
    current_location = st.session_state.get('last_location_name')
    current_forecast = st.session_state.get('last_forecast_data')
    
    # Show current data status
    col1, col2 = st.columns([2, 1])
    with col1:
        if current_weather:
            temp = current_weather['main']['temp']
            condition = current_weather['weather'][0]['main']
            st.success(f"✅ I have current weather data for: **{current_location}** ({temp}°C, {condition})")
        else:
            st.info("💡 No current weather data loaded. Get weather data for specific advice!")
    
    with col2:
        if st.button("🔄 Refresh Weather Data"):
            if 'last_weather_data' in st.session_state:
                del st.session_state.last_weather_data
            if 'last_location_name' in st.session_state:
                del st.session_state.last_location_name
            st.info("Weather data cleared. Get new data from map or search.")
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Sample questions based on whether we have weather data
    st.markdown("### 💡 Try asking:")
    
    if current_weather:
        sample_questions = [
            f"Should I go hiking in {current_location}?",
            f"What should I wear for the weather in {current_location}?",
            f"Is it good weather for outdoor activities in {current_location}?",
            f"Should I plan an outdoor event today?",
            f"What activities do you recommend for this weather?"
        ]
    else:
        sample_questions = [
            "What should I know about hiking in different weather?",
            "How do I dress for rainy conditions?",
            "What are good indoor activities for bad weather?",
            "Tips for planning outdoor events?",
            "How to stay safe in extreme weather?"
        ]
    
    # Display sample questions as buttons
    col1, col2 = st.columns(2)
    for i, question in enumerate(sample_questions):
        with col1 if i % 2 == 0 else col2:
            if st.button(question, key=f"sample_q_{i}"):
                # Process the question immediately - NO RERUN
                process_ai_question_immediate(services, question, current_weather, current_location, current_forecast)
    
    # Chat input
    user_input = st.text_input(
        "Ask your weather question:",
        placeholder="Type your weather or planning question here...",
        key="user_question_input"
    )
    
    # Process user input when submitted
    if user_input and user_input.strip():
        # Check if this is a new question (not already processed)
        if ('last_processed_question' not in st.session_state or 
            st.session_state.last_processed_question != user_input):
            
            process_ai_question_immediate(services, user_input, current_weather, current_location, current_forecast)
            st.session_state.last_processed_question = user_input
    
    # Chat management buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            if 'last_processed_question' in st.session_state:
                del st.session_state.last_processed_question
            st.success("Chat cleared!")
    
    with col2:
        if st.session_state.chat_history:
            chat_count = len(st.session_state.chat_history)
            st.metric("Messages", chat_count)
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### 💬 Conversation")
        
        # Display messages (last 10)
        for i, chat in enumerate(st.session_state.chat_history[-10:]):
            if chat["role"] == "user":
                st.markdown(f"""
                <div style="background: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0; text-align: right; border-left: 4px solid #667eea;">
                    <strong>🙋‍♂️ You:</strong><br>
                    {chat['message']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); border-radius: 15px; padding: 20px; margin: 10px 0; color: #333; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37); border-left: 4px solid #2ecc71;">
                    <strong>🤖 AI Assistant:</strong><br><br>
                    {chat['message']}
                </div>
                """, unsafe_allow_html=True)
        
        # Show if more messages exist
        if len(st.session_state.chat_history) > 10:
            st.info(f"Showing last 10 messages. Total conversation: {len(st.session_state.chat_history)} messages.")
    
    else:
        # Welcome message when no chat history
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; padding: 20px; margin: 20px 0; color: white; text-align: center;">
            <h3>🤖 Welcome to your AI Weather Assistant!</h3>
            <p>I can help you with weather planning, activity recommendations, and travel advice.</p>
            <p><strong>Get started:</strong> Click a sample question above or type your own question!</p>
        </div>
        """, unsafe_allow_html=True)

def process_ai_question_immediate(services, user_input, weather_data, location_name, forecast_data):
    """Process AI question immediately without causing rerun loops"""
    try:
        # Add user message to chat history
        st.session_state.chat_history.append({
            "role": "user", 
            "message": user_input,
            "timestamp": datetime.now()
        })
        
        # Show processing message
        with st.spinner("🤖 AI is thinking..."):
            if weather_data:
                # Enhanced response with weather data
                ai_response = services['ai'].get_response_with_weather_data(
                    user_input,
                    weather_data=weather_data,
                    location_name=location_name,
                    forecast_data=forecast_data
                )
            else:
                # Regular response without specific weather data
                ai_response = services['ai'].get_response(user_input, st.session_state.chat_history)
            
            # Add AI response to chat history
            st.session_state.chat_history.append({
                "role": "assistant", 
                "message": ai_response,
                "timestamp": datetime.now()
            })
            
            # Show the response immediately
            st.markdown("### 🤖 Latest Response:")
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); border-radius: 15px; padding: 20px; margin: 10px 0; color: #333; box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);">
                <strong>🤖 AI Assistant:</strong><br><br>
                {ai_response}
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        error_message = f"Sorry, I encountered an error: {str(e)}"
        st.session_state.chat_history.append({
            "role": "assistant", 
            "message": error_message,
            "timestamp": datetime.now()
        })
        st.error(error_message)
def dashboard_page(services):
    """Weather dashboard with current conditions"""
    st.markdown("## 📊 Weather Dashboard")
    
    # Location input
    location_input = st.text_input(
        "📍 Enter Location for Dashboard",
        placeholder="Enter city, coordinates, or landmark..."
    )
    
    if location_input:
        with st.spinner("📊 Building dashboard..."):
            location_data = services['location'].get_location_data(location_input)
            
            if location_data:
                # Get comprehensive weather data
                current_weather = services['weather'].get_current_weather(
                    location_data['lat'], location_data['lng']
                )
                forecast_data = services['weather'].get_forecast(
                    location_data['lat'], location_data['lng']
                )
                
                if current_weather and forecast_data:
                    # Location header
                    st.markdown(f"""
                    <div class="location-header">
                        <h2>📍 {location_data['display_name']}</h2>
                        <p>Dashboard updated at {datetime.now().strftime('%H:%M:%S')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Current weather display
                    display_current_weather(current_weather, location_data)
                    
                    # Forecast chart
                    st.markdown("### 📈 Temperature Trend (5 Days)")
                    create_forecast_chart(forecast_data)
                    
                    # Weather insights
                    st.markdown("### 🧠 Weather Insights")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        insights = services['ai'].get_weather_insights(current_weather, forecast_data)
                        st.markdown(f"""
                        <div class="ai-chat-card">
                            {insights}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # Activity recommendations
                        activities = services['ai'].get_activity_recommendations(current_weather)
                        st.markdown(f"""
                        <div class="ai-chat-card">
                            <strong>🎯 Activity Recommendations:</strong><br>
                            {activities}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error("❌ Could not retrieve weather data")
            else:
                st.error("❌ Location not found")

def data_management_page(services):
    """CRUD operations for weather data"""
    st.markdown("## 💾 Data Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Create", "👁️ Read", "✏️ Update", "🗑️ Delete"])
    
    with tab1:
        st.markdown("### ➕ Save Weather Data")
        
        with st.form("save_weather"):
            location = st.text_input("📍 Location")
            notes = st.text_area("📝 Notes (optional)")
            
            if st.form_submit_button("💾 Save Current Weather"):
                if location:
                    location_data = services['location'].get_location_data(location)
                    if location_data:
                        weather_data = services['weather'].get_current_weather(
                            location_data['lat'], location_data['lng']
                        )
                        if weather_data:
                            success = save_weather_to_db(services, weather_data, 
                                                       location_data['lat'], location_data['lng'], notes)
                            if success:
                                st.success("✅ Weather data saved successfully!")
                            else:
                                st.error("❌ Failed to save weather data")
                        else:
                            st.error("❌ Could not retrieve weather data")
                    else:
                        st.error("❌ Location not found")
                else:
                    st.error("❌ Please enter a location")
    
    with tab2:
        st.markdown("### 👁️ View Saved Data")
        
        try:
            saved_data = services['database'].get_all_weather_records()
            
            if saved_data:
                df = pd.DataFrame(saved_data)
                
                # Display summary
                st.markdown(f"**Total Records:** {len(df)}")
                
                # Display data table
                st.dataframe(
                    df,
                    use_container_width=True,
                    column_config={
                        "timestamp": st.column_config.DatetimeColumn(
                            "Saved At",
                            format="MM/DD/YYYY HH:mm"
                        ),
                        "temperature": st.column_config.NumberColumn(
                            "Temperature (°C)",
                            format="%.1f"
                        ),
                        "location_name": "Location"
                    }
                )
            else:
                st.info("📭 No saved weather data found.")
                
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
    
    with tab3:
        st.markdown("### ✏️ Update Records")
        
        try:
            records = services['database'].get_all_weather_records()
            if records:
                record_options = {f"{r['location_name']} - {r['timestamp']}": r['_id'] for r in records}
                
                selected_record = st.selectbox("Select record to update", list(record_options.keys()))
                
                if selected_record:
                    record_id = record_options[selected_record]
                    
                    with st.form("update_record"):
                        new_notes = st.text_area("Update notes")
                        
                        if st.form_submit_button("💾 Update Record"):
                            success = services['database'].update_weather_record(record_id, {"notes": new_notes})
                            if success:
                                st.success("✅ Record updated!")
                            else:
                                st.error("❌ Update failed")
            else:
                st.info("📭 No records to update")
                
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    with tab4:
        st.markdown("### 🗑️ Delete Records")
        st.warning("⚠️ **Warning:** Deletion is permanent!")
        
        try:
            records = services['database'].get_all_weather_records()
            if records:
                record_options = {f"{r['location_name']} - {r['timestamp']}": r['_id'] for r in records}
                
                selected_record = st.selectbox("Select record to delete", list(record_options.keys()))
                
                if selected_record:
                    record_id = record_options[selected_record]
                    
                    confirm = st.checkbox("✅ I confirm I want to delete this record")
                    
                    if confirm and st.button("🗑️ Delete Record", type="primary"):
                        success = services['database'].delete_weather_record(record_id)
                        if success:
                            st.success("✅ Record deleted!")
                            st.rerun()
                        else:
                            st.error("❌ Delete failed")
            else:
                st.info("📭 No records to delete")
                
        except Exception as e:
            st.error(f"❌ Error: {e}")

def analytics_page(services):
    """Weather analytics and trends"""
    st.markdown("## 📈 Weather Analytics")
    
    try:
        # Get all saved weather data
        weather_records = services['database'].get_all_weather_records()
        
        if weather_records and len(weather_records) > 0:
            df = pd.DataFrame(weather_records)
            
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_records = len(df)
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📊 Total Records</h4>
                    <h2>{total_records}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                avg_temp = df['temperature'].mean() if 'temperature' in df.columns else 0
                st.markdown(f"""
                <div class="metric-card">
                    <h4>🌡️ Avg Temperature</h4>
                    <h2>{avg_temp:.1f}°C</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                unique_locations = df['location_name'].nunique() if 'location_name' in df.columns else 0
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📍 Locations</h4>
                    <h2>{unique_locations}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                latest_record = df['timestamp'].max() if 'timestamp' in df.columns else "N/A"
                st.markdown(f"""
                <div class="metric-card">
                    <h4>🕒 Latest Record</h4>
                    <h2>{latest_record.strftime("%m/%d") if latest_record != "N/A" else "N/A"}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Temperature trends
            if 'timestamp' in df.columns and 'temperature' in df.columns:
                st.markdown("### 📈 Temperature Trends")
                
                fig = px.line(
                    df,
                    x='timestamp',
                    y='temperature',
                    color='location_name' if 'location_name' in df.columns else None,
                    title="Temperature Trends by Location",
                    labels={'temperature': 'Temperature (°C)', 'timestamp': 'Date'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Location analysis
            if 'location_name' in df.columns:
                st.markdown("### 🌍 Location Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Most searched locations
                    location_counts = df['location_name'].value_counts().head(10)
                    fig = px.bar(
                        x=location_counts.values,
                        y=location_counts.index,
                        orientation='h',
                        title="Most Searched Locations"
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Temperature distribution
                    if 'temperature' in df.columns:
                        fig = px.histogram(
                            df,
                            x='temperature',
                            title="Temperature Distribution",
                            nbins=20,
                            labels={'temperature': 'Temperature (°C)', 'count': 'Frequency'}
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("📊 No weather data available for analytics. Start collecting some weather data!")
            
    except Exception as e:
        st.error(f"❌ Analytics error: {e}")

def export_page(services):
    """Export weather data in various formats"""
    st.markdown("## 📤 Export Weather Data")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); border-radius: 15px; padding: 20px; margin: 10px 0;">
        <h3>🎯 Export Options</h3>
        <p>Export your weather data for analysis, backup, or integration with other tools.</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Get data for export
        weather_records = services['database'].get_all_weather_records()
        
        if weather_records:
            st.markdown(f"**Available Records:** {len(weather_records)}")
            
            # Export format selection
            export_format = st.selectbox(
                "📋 Export Format",
                ["JSON", "CSV", "Excel"]
            )
            
            # Date range filter
            use_date_filter = st.checkbox("📅 Filter by Date Range")
            
            if use_date_filter:
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("📅 Start Date", datetime.now().date() - timedelta(days=30))
                with col2:
                    end_date = st.date_input("📅 End Date", datetime.now().date())
            
            if st.button("📥 Generate Export", type="primary"):
                try:
                    # Filter data if date range is specified
                    export_data = weather_records
                    if use_date_filter:
                        # Filter logic would go here
                        pass
                    
                    # Generate export file
                    if export_format == "JSON":
                        export_content = json.dumps(export_data, indent=2, default=str)
                        file_name = f"weather_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        mime_type = "application/json"
                        
                    elif export_format == "CSV":
                        df = pd.DataFrame(export_data)
                        export_content = df.to_csv(index=False)
                        file_name = f"weather_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                        mime_type = "text/csv"
                        
                    elif export_format == "Excel":
                        df = pd.DataFrame(export_data)
                        # For Excel, we'd need to create a BytesIO buffer
                        # Simplified for this demo
                        export_content = df.to_csv(index=False)  # Fallback to CSV
                        file_name = f"weather_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    
                    # Provide download button
                    st.download_button(
                        f"📥 Download {export_format}",
                        export_content,
                        file_name=file_name,
                        mime=mime_type
                    )
                    
                    st.success(f"✅ Export file generated successfully!")
                    
                    # Show preview
                    with st.expander("👁️ Preview Data"):
                        if export_format == "JSON":
                            st.json(export_data[:3])  # Show first 3 records
                        else:
                            df_preview = pd.DataFrame(export_data)
                            st.dataframe(df_preview.head())
                
                except Exception as e:
                    st.error(f"❌ Export failed: {e}")
        
        else:
            st.info("📭 No weather data available for export. Start collecting some weather data first!")
            
    except Exception as e:
        st.error(f"❌ Export error: {e}")

def create_forecast_chart(forecast_data):
    """Create temperature forecast chart"""
    # Process forecast data
    times = []
    temperatures = []
    descriptions = []
    
    for item in forecast_data['list'][:24]:  # Next 24 hours
        times.append(datetime.fromtimestamp(item['dt']))
        temperatures.append(item['main']['temp'])
        descriptions.append(item['weather'][0]['description'])
    
    # Create plotly chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=times,
        y=temperatures,
        mode='lines+markers',
        name='Temperature',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{y:.1f}°C</b><br>%{x}<extra></extra>'
    ))
    
    fig.update_layout(
        title="24-Hour Temperature Forecast",
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        template="plotly_white",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def save_weather_to_db(services, weather_data, lat, lng, notes=""):
    """Save weather data to database"""
    try:
        # Prepare weather record
        weather_record = {
            'location_name': f"Location ({lat:.4f}, {lng:.4f})",
            'latitude': lat,
            'longitude': lng,
            'temperature': weather_data['main']['temp'],
            'feels_like': weather_data['main']['feels_like'],
            'humidity': weather_data['main']['humidity'],
            'pressure': weather_data['main']['pressure'],
            'wind_speed': weather_data['wind']['speed'],
            'weather_condition': weather_data['weather'][0]['main'],
            'weather_description': weather_data['weather'][0]['description'],
            'timestamp': datetime.now(),
            'notes': notes
        }
        
        # Save to database
        success = services['database'].save_weather_record(weather_record)
        return success
        
    except Exception as e:
        st.error(f"❌ Error saving to database: {e}")
        return False

if __name__ == "__main__":
    main()
