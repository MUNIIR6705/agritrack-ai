import requests
import base64
from datetime import datetime
from django.conf import settings

class MpesaClient:
    def __init__(self):
        self.consumer_key = 'QGMx3AcyyFcGVak4ra4UMAQpA6Isv9arqU0VR7em9WdG7rXF'
        self.consumer_secret = 'QMlsZXHiclPuiehFi6WMLbSObvMifnL7A9j5JzGbr83BE09kyzrRyag1gV8cLUnN'
        self.business_shortcode = '174379'  # Standard Sandbox Shortcode
        self.passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919' # Standard Sandbox Passkey
        self.base_url = "https://sandbox.safaricom.co.ke"

    def get_access_token(self):
        """Fetches the OAuth2 Token from Safaricom"""
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(url, auth=(self.consumer_key, self.consumer_secret))
        return response.json().get('access_token')

    def stk_push(self, phone_number, amount, description):
        """Triggers the STK Push to the user's phone"""
        token = self.get_access_token()
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # Generate Password: base64(shortcode + passkey + timestamp)
        password_str = f"{self.business_shortcode}{self.passkey}{timestamp}"
        password = base64.b64encode(password_str.encode()).decode('utf-8')

        headers = {"Authorization": f"Bearer {token}"}
        
        # Note: Phone must be in 2547XXXXXXXX format
        formatted_phone = f"254{phone_number[-9:]}"

        payload = {
            "BusinessShortCode": self.business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(float(amount)),
            "PartyA": formatted_phone,
            "PartyB": self.business_shortcode,
            "PhoneNumber": formatted_phone,
            "CallBackURL": "https://mydomain.com/path", # Placeholder for Sandbox
            "AccountReference": "AgriTrackAI",
            "TransactionDesc": description
        }

        url = f"{self.base_url}/mpesa/stkpush/v1/query" # For sandbox STK Push
        # Note: In production the endpoint is /mpesa/stkpush/v1/processrequest
        response = requests.post(f"{self.base_url}/mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
        return response.json()