import requests
import base64
from datetime import datetime
from django.conf import settings

class MpesaClient:
    def __init__(self):
        # Standard Safaricom Sandbox Credentials
        self.consumer_key = 'QGMx3AcyyFcGVak4ra4UMAQpA6Isv9arqU0VR7em9WdG7rXF'
        self.consumer_secret = 'QMlsZXHiclPuiehFi6WMLbSObvMifnL7A9j5JzGbr83BE09kyzrRyag1gV8cLUnN'
        self.business_shortcode = '174379'
        self.passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        self.base_url = "https://sandbox.safaricom.co.ke"

    def get_access_token(self):
        """Fetches the OAuth2 Token from Safaricom"""
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(url, auth=(self.consumer_key, self.consumer_secret))
        
        # Ensures it fails loudly if Safaricom rejects the credentials
        response.raise_for_status() 
        return response.json().get('access_token')

    def stk_push(self, phone_number, amount, description, callback_url):
        """Triggers the STK Push to the user's phone"""
        token = self.get_access_token()
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Generate Password: base64(shortcode + passkey + timestamp)
        password_str = f"{self.business_shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode('utf-8')

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Strip spaces and ensure format is 2547XXXXXXXX
        clean_phone = str(phone_number).replace(" ", "").replace("+", "")
        formatted_phone = f"254{clean_phone[-9:]}"

        payload = {
            "BusinessShortCode": self.business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(float(amount)), # Safaricom strictly requires whole numbers
            "PartyA": formatted_phone,
            "PartyB": self.business_shortcode,
            "PhoneNumber": formatted_phone,
            "CallBackURL": callback_url, # CRITICAL: Safaricom sends the receipt here!
            "AccountReference": "AgriTrack AI",
            "TransactionDesc": description[:13] # Max 13 characters allowed by Daraja API
        }

        # The actual endpoint to trigger the STK Push
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        response = requests.post(url, json=payload, headers=headers)
        
        return response.json()