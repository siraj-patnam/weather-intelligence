import folium
from folium import plugins
from typing import List, Tuple, Dict, Any
from utils.helpers import get_weather_emoji, format_temperature

def create_weather_map(center: List[float] = [40.7128, -74.0060], zoom: int = 5, style: str = "OpenStreetMap") -> folium.Map:
    """Create a base weather map with custom styling"""
    
    # Map tile options
    tile_options = {
        "OpenStreetMap": "OpenStreetMap",
        "Satellite": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/MapServer/tile/{z}/{y}/{x}",
        "Terrain": "https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}{r}.png"
    }
    
    # Create base map
    if style == "OpenStreetMap":
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles="OpenStreetMap"
        )
    else:
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles=tile_options.get(style, "OpenStreetMap"),
            attr="Weather Intelligence Hub"
        )
    
    # Add custom CSS styling
    map_css = """
    <style>
    .weather-marker {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        border: 2px solid white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    .weather-popup {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        border-radius: 10px;
    }
    </style>
    """
    
    m.get_root().html.add_child(folium.Element(map_css))
    
    # Add fullscreen button
    plugins.Fullscreen(
        position="topright",
        title="Fullscreen",
        title_cancel="Exit fullscreen",
        force_separate_button=True
    ).add_to(m)
    
    # Add measure control
    plugins.MeasureControl(
        position="bottomleft",
        primary_length_unit="kilometers",
        secondary_length_unit="miles",
        primary_area_unit="sqkilometers",
        secondary_area_unit="acres"
    ).add_to(m)
    
    return m

def add_weather_markers(map_obj: folium.Map, location_data: Dict, weather_data: Dict) -> None:
    """Add weather markers to the map"""
    try:
        lat = location_data['lat']
        lng = location_data['lng']
        name = location_data['name']
        
        # Extract weather information
        temp = weather_data['main']['temp']
        condition = weather_data['weather'][0]['main']
        description = weather_data['weather'][0]['description']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']
        
        # Get weather emoji
        weather_emoji = get_weather_emoji(condition)
        
        # Create popup content
        popup_html = f"""
        <div class="weather-popup" style="width: 250px; padding: 10px;">
            <h4 style="margin: 0 0 10px 0; color: #333; text-align: center;">
                {weather_emoji} {name}
            </h4>
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                <div style="font-size: 24px; font-weight: bold; text-align: center; margin-bottom: 5px;">
                    {temp:.1f}°C
                </div>
                <div style="text-align: center; font-size: 14px; margin-bottom: 10px;">
                    {description.title()}
                </div>
                <div style="font-size: 12px;">
                    <div>💧 Humidity: {humidity}%</div>
                    <div>🌬️ Wind: {wind_speed} m/s</div>
                    <div>📍 Coordinates: {lat:.4f}, {lng:.4f}</div>
                </div>
            </div>
        </div>
        """
        
        # Create custom icon based on temperature
        icon_color = get_temperature_color(temp)
        
        # Add marker to map
        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{name}: {temp:.1f}°C - {description}",
            icon=folium.Icon(
                color=icon_color,
                icon='thermometer-half',
                prefix='fa'
            )
        ).add_to(map_obj)
        
        # Add temperature label
        folium.map.Marker(
            location=[lat, lng],
            icon=folium.DivIcon(
                html=f"""
                <div style="background: {get_temperature_bg_color(temp)}; 
                           color: white; padding: 4px 8px; border-radius: 20px; 
                           font-weight: bold; font-size: 12px; text-align: center;
                           border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                           transform: translate(-50%, -100%);">
                    {temp:.0f}°C
                </div>
                """,
                icon_size=(60, 25),
                icon_anchor=(30, 35)
            )
        ).add_to(map_obj)
        
    except Exception as e:
        print(f"Error adding weather marker: {e}")

def get_temperature_color(temp: float) -> str:
    """Get marker color based on temperature"""
    if temp < 0:
        return 'purple'
    elif temp < 10:
        return 'blue'
    elif temp < 20:
        return 'green'
    elif temp < 30:
        return 'orange'
    else:
        return 'red'

def get_temperature_bg_color(temp: float) -> str:
    """Get background color for temperature labels"""
    if temp < 0:
        return '#4a0e4e'  # Dark purple
    elif temp < 10:
        return '#2e5984'  # Dark blue
    elif temp < 20:
        return '#2d5016'  # Dark green
    elif temp < 30:
        return '#cc6600'  # Orange
    else:
        return '#cc2936'  # Red

def add_weather_layer(map_obj: folium.Map, weather_data_points: List[Dict]) -> None:
    """Add weather overlay layer to the map"""
    try:
        # Create feature group for weather layer
        weather_layer = folium.FeatureGroup(name="Weather Data")
        
        for point in weather_data_points:
            lat = point['lat']
            lng = point['lng']
            temp = point['temperature']
            
            # Add circle marker for temperature
            folium.CircleMarker(
                location=[lat, lng],
                radius=10,
                popup=f"Temperature: {temp:.1f}°C",
                color=get_temperature_color(temp),
                fill=True,
                fillColor=get_temperature_color(temp),
                fillOpacity=0.6,
                weight=2
            ).add_to(weather_layer)
        
        weather_layer.add_to(map_obj)
        
        # Add layer control
        folium.LayerControl().add_to(map_obj)
        
    except Exception as e:
        print(f"Error adding weather layer: {e}")

def create_heat_map(map_obj: folium.Map, temperature_data: List[Tuple[float, float, float]]) -> None:
    """Create temperature heat map overlay"""
    try:
        from folium.plugins import HeatMap
        
        # Add heat map layer
        HeatMap(
            temperature_data,
            min_opacity=0.2,
            max_zoom=18,
            radius=25,
            blur=15,
            gradient={
                0.0: 'blue',
                0.2: 'cyan',
                0.4: 'lime',
                0.6: 'yellow',
                0.8: 'orange',
                1.0: 'red'
            }
        ).add_to(map_obj)
        
    except ImportError:
        print("HeatMap plugin not available")
    except Exception as e:
        print(f"Error creating heat map: {e}")

def add_map_legends(map_obj: folium.Map) -> None:
    """Add legends and controls to the map"""
    try:
        # Temperature legend
        legend_html = """
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 150px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h5 style="margin: 0 0 10px 0; text-align: center;">Temperature Scale</h5>
        <div><span style="color: purple;">●</span> < 0°C (Freezing)</div>
        <div><span style="color: blue;">●</span> 0-10°C (Cold)</div>
        <div><span style="color: green;">●</span> 10-20°C (Cool)</div>
        <div><span style="color: orange;">●</span> 20-30°C (Warm)</div>
        <div><span style="color: red;">●</span> > 30°C (Hot)</div>
        </div>
        """
        
        map_obj.get_root().html.add_child(folium.Element(legend_html))
        
    except Exception as e:
        print(f"Error adding map legends: {e}")

def add_weather_controls(map_obj: folium.Map) -> None:
    """Add weather-specific controls to the map"""
    try:
        # Add draw plugin for user interaction
        from folium.plugins import Draw
        
        Draw(
            export=True,
            filename='weather_locations.geojson',
            position='topleft',
            draw_options={
                'polyline': False,
                'polygon': False,
                'circle': False,
                'rectangle': False,
                'marker': True,
                'circlemarker': False
            },
            edit_options={'edit': False}
        ).add_to(map_obj)
        
    except ImportError:
        print("Draw plugin not available")
    except Exception as e:
        print(f"Error adding weather controls: {e}")

def create_weather_cluster_map(map_obj: folium.Map, weather_locations: List[Dict]) -> None:
    """Create clustered weather markers for better performance"""
    try:
        from folium.plugins import MarkerCluster
        
        # Create marker cluster
        marker_cluster = MarkerCluster(
            name="Weather Locations",
            overlay=True,
            control=True,
            show=True
        )
        
        for location in weather_locations:
            lat = location['lat']
            lng = location['lng']
            name = location.get('name', f"Location ({lat:.2f}, {lng:.2f})")
            
            if 'weather' in location:
                weather = location['weather']
                temp = weather['main']['temp']
                condition = weather['weather'][0]['main']
                emoji = get_weather_emoji(condition)
                
                popup_content = f"""
                <b>{emoji} {name}</b><br>
                Temperature: {temp:.1f}°C<br>
                Condition: {condition}
                """
                
                folium.Marker(
                    location=[lat, lng],
                    popup=popup_content,
                    tooltip=f"{name}: {temp:.1f}°C",
                    icon=folium.Icon(
                        color=get_temperature_color(temp),
                        icon='thermometer-half',
                        prefix='fa'
                    )
                ).add_to(marker_cluster)
        
        marker_cluster.add_to(map_obj)
        
    except ImportError:
        print("MarkerCluster plugin not available")
    except Exception as e:
        print(f"Error creating weather cluster map: {e}")

def add_map_search(map_obj: folium.Map) -> None:
    """Add search functionality to the map"""
    try:
        from folium.plugins import Search
        
        # This would typically search through marker data
        # For now, we'll add a placeholder
        search_html = """
        <div style="position: fixed; 
                    top: 80px; left: 10px; 
                    background-color: white; 
                    padding: 10px; 
                    border-radius: 5px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    z-index: 9999;">
            <input type="text" 
                   placeholder="Search locations..." 
                   style="width: 200px; padding: 5px; border: 1px solid #ccc; border-radius: 3px;">
        </div>
        """
        
        map_obj.get_root().html.add_child(folium.Element(search_html))
        
    except Exception as e:
        print(f"Error adding map search: {e}")

def style_map_for_weather(map_obj: folium.Map) -> None:
    """Apply weather-specific styling to the map"""
    try:
        # Add custom CSS for weather map
        weather_css = """
        <style>
        .leaflet-popup-content-wrapper {
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .leaflet-popup-tip {
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .leaflet-control-zoom a {
            border-radius: 5px;
        }
        
        .weather-marker-label {
            background: rgba(255,255,255,0.9);
            border: 2px solid #333;
            border-radius: 15px;
            padding: 4px 8px;
            font-weight: bold;
            font-size: 12px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        </style>
        """
        
        map_obj.get_root().html.add_child(folium.Element(weather_css))
        
    except Exception as e:
        print(f"Error styling map for weather: {e}")