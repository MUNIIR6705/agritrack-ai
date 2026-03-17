import requests

def get_dynamic_weather():
    """
    Optimized Weather Service for AgriTrack AI.
    Prioritizes speed to prevent UI 'Scanning' hangs.
    Defaults to Kutus coordinates (-0.4442, 37.3308).
    """
    # 1. DEFINE DEFAULT (KUTUS) IMMEDIATELY
    lat, lon = -0.4442, 37.3308
    location_name = "Kutus, Kirinyaga"

    try:
        # 2. ATTEMPT IP GEOLOCATION (With strict timeout)
        # We use a 1.5s timeout. If it's slower than that, we just use Kutus.
        try:
            geo_response = requests.get('http://ip-api.com/json/', timeout=1.5)
            if geo_response.status_code == 200:
                geo_data = geo_response.json()
                if geo_data.get('status') == 'success':
                    lat = geo_data['lat']
                    lon = geo_data['lon']
                    location_name = f"{geo_data['city']}, {geo_data['countryCode']}"
        except (requests.exceptions.RequestException, ValueError):
            # If IP lookup fails, location_name stays as "Kutus, Kirinyaga"
            pass

        # 3. FETCH WEATHER DATA
        # We use timezone=auto to ensure the weather matches the local time
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&"
            f"current=temperature_2m,relative_humidity_2m,weather_code&"
            f"timezone=auto"
        )
        
        weather_response = requests.get(weather_url, timeout=2.0)
        w_data = weather_response.json().get('current', {})

        if not w_data:
            raise ValueError("No weather data returned")

        # 4. MAP WEATHER CODES TO FONT-AWESOME ICONS
        code = w_data.get('weather_code', 0)
        if code == 0:
            icon = 'sun'
        elif 1 <= code <= 3:
            icon = 'cloud-sun'
        elif 45 <= code <= 48:
            icon = 'smog'
        elif 51 <= code <= 67:
            icon = 'cloud-showers-heavy'
        elif 95 <= code <= 99:
            icon = 'bolt'
        else:
            icon = 'cloud'

        return {
            'temp': int(round(w_data.get('temperature_2m', 22))),
            'humidity': w_data.get('relative_humidity_2m', 65),
            'icon': icon,
            'location': location_name,
            'recommendation': f"Conditions in {location_name} analyzed."
        }

    except Exception as e:
        print(f"Weather System Error: {e}")
        # SECURE FALLBACK: Guaranteed return so dashboard never hangs
        return {
            'temp': 22, 
            'humidity': 70, 
            'icon': 'cloud-sun', 
            'location': "Kutus, KE", 
            'recommendation': "Offline: Synchronized with Kutus baseline."
        }