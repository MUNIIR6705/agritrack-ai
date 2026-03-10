import requests
import json
import base64
from datetime import datetime
from django.conf import settings

class MpesaHandler:
    def __init__(self):
        # --- YOUR SPECIFIC SANDBOX KEYS ---
        self.consumer_key = 'QGMx3AcyyFcGVak4ra4UMAQpA6Isv9arqU0VR7em9WdG7rXF'
        self.consumer_secret = 'QMlsZXHiclPuiehFi6WMLbSObvMifnL7A9j5JzGbr83BE09kyzrRyag1gV8cLUnN'
        
        # --- STANDARD SAFARICOM SANDBOX CONFIG ---
        # Do not change these, they are standard for all sandbox tests
        self.shortcode = '174379'
        self.passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        self.base_url = 'https://sandbox.safaricom.co.ke'

    def get_access_token(self):
        """Generates a fresh token from Safaricom"""
        url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
        try:
            r = requests.get(url, auth=(self.consumer_key, self.consumer_secret))
            r.raise_for_status() # Check for errors
            
            # The API returns a JSON like {'access_token': '...', 'expires_in': '...'}
            token = r.json()['access_token']
            return token
        except Exception as e:
            print(f"❌ TOKEN ERROR: {e}")
            return None

    def lipa_na_mpesa_password(self):
        """Generates the timestamp and password required for the transaction"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        data_to_encode = self.shortcode + self.passkey + timestamp
        encoded_string = base64.b64encode(data_to_encode.encode())
        return encoded_string.decode('utf-8'), timestamp

    def stk_push(self, phone_number, amount, account_reference="AgriTrack"):
        """Sends the actual request to the phone"""
        
        # 1. Get Token
        access_token = self.get_access_token()
        if not access_token:
            return {"ResponseCode": "1", "ResponseDescription": "Failed to get Token (Check Keys)"}

        # 2. Format Phone Number (Must be 2547...)
        # Remove spaces, dashes, or leading '+'
        phone_number = str(phone_number).replace(" ", "").replace("-", "").replace("+", "")
        
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
            
        # 3. Prepare Payload
        password, timestamp = self.lipa_na_mpesa_password()
        headers = { 
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json' 
        }
        
        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount), 
            "PartyA": phone_number, # The phone paying
            "PartyB": self.shortcode, # The business receiving (Sandbox Shortcode)
            "PhoneNumber": phone_number,
            "CallBackURL": "https://mydomain.com/path", # Callback URL (Dummy for localhost)
            "AccountReference": account_reference,
            "TransactionDesc": "Payment for Livestock"
        }
        
        # 4. Send Request
        try:
            url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'
            response = requests.post(url, headers=headers, json=payload)
            
            # Print result to console for debugging
            print("--- SAFARICOM RESPONSE ---")
            print(response.json())
            print("--------------------------")
            
            return response.json()
        except Exception as e:
            print(f"❌ REQUEST ERROR: {e}")
            return {"ResponseCode": "1", "ResponseDescription": str(e)}