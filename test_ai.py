import requests
import json

# Your NEW API Key
API_KEY = 'AIzaSyBy4cI9__cPVfaN0to2cEzcNNs9z_R08xU' 

def raw_api_test():
    print("Bypassing SDK... Sending raw HTTP request directly to Google API...")
    print("-" * 50)
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    
    try:
        response = requests.get(url)
        print(f"HTTP Status Code: {response.status_code}")
        print("-" * 50)
        
        # Parse the raw response from Google
        data = response.json()
        
        if 'models' in data:
            models = [m['name'] for m in data['models'] if 'generateContent' in m.get('supportedGenerationMethods', [])]
            print(f"✅ SUCCESS! Found {len(models)} working models.")
            for m in models:
                print(f" - {m}")
        else:
            print("❌ GOOGLE API ERROR RESPONSE:")
            print(json.dumps(data, indent=2))
            
    except Exception as e:
        print(f"Critical Network Error: {e}")

if __name__ == "__main__":
    raw_api_test()