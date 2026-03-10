import africastalking
from django.conf import settings

class SMSHandler:
    def __init__(self):
        # 1. Credentials
        self.username = getattr(settings, 'AT_USERNAME', 'sandbox')
        self.api_key = getattr(settings, 'AT_API_KEY', 'TEST_KEY')
        
        # Initialize SDK (Uncomment these 2 lines for REAL SMS)
        # africastalking.initialize(self.username, self.api_key)
        # self.sms = africastalking.SMS

    def send_alert(self, phone, animal_tag, condition, severity):
        """
        Sends an emergency SMS to the farmer.
        """
        message = f"⚠️ ALERT: {animal_tag} is marked as {severity}! Condition: {condition}. Please isolate immediately."
        
        try:
            # --- REAL SMS SENDING CODE (Commented out for Safety) ---
            # response = self.sms.send(message, [phone])
            # print(f"✅ SMS SENT to {phone}: {response}")
            # return response
            
            # --- SIMULATION MODE (Prints to Console) ---
            print("=========================================")
            print(f"📲 SMS SIMULATION TO: {phone}")
            print(f"📩 MESSAGE: {message}")
            print("=========================================")
            return {"status": "success", "message": "Simulated"}
            
        except Exception as e:
            print(f"❌ SMS FAILED: {str(e)}")
            return {"status": "error", "error": str(e)}