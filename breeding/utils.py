import africastalking
from django.conf import settings

# Initialize Africa's Talking
africastalking.initialize(settings.AT_USERNAME, settings.AT_API_KEY)
sms = africastalking.SMS

def send_breeding_alert(phone_number, message):
    """Sends a professional SMS alert to the farmer"""
    try:
        # Note: phone_number must be in international format (e.g., +254...)
        response = sms.send(message, [phone_number])
        print(f"SMS Sent: {response}")
    except Exception as e:
        print(f"SMS Error: {str(e)}")