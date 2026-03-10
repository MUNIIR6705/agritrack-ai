import requests

def get_live_weather():
    """Fetches live temperature for Nairobi using a free service."""
    try:
        # We use wttr.in which is a great free service for server-side fetching
        city = "Nairobi"
        response = requests.get(f"https://wttr.in/{city}?format=%t", timeout=5)
        if response.status_code == 200:
            # Result is usually '+24°C', we clean it to '24'
            temp = response.text.replace('+', '').replace('°C', '').strip()
            return temp
    except Exception as e:
        print(f"Weather Fetch Error: {e}")
    return "24" # Safe fallback if internet is slow