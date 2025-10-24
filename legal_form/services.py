import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

CONSULTATION_MESSAGE_TEMPLATE = """🔔 New Request For Consultation!

👤 Name: {name}
📧 Email: {email}
📱 Phone Number: {phone}
📋 Consultation: {service_type}
💬 Comments: {comment}

🕐 Time: {created_at}"""


class WhatsAppService:
    """
    Service for sending messages to WhatsApp using WhatsApp Business API
    """
    
    @staticmethod
    def format_phone_number(phone):
        """
        Format phone number for WhatsApp Cloud API
        """
        # Remove all non-digits
        cleaned = ''.join(filter(str.isdigit, str(phone)))
        return cleaned
    
    @staticmethod
    def send_consultation_request_cloud_api(consultation):
        """
        WhatsApp Cloud API (Meta)
        """
        try:
            url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
            
            # Headers
            headers = {
                'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
                'Content-Type': 'application/json'
            }
            
            # Format message
            message = CONSULTATION_MESSAGE_TEMPLATE.format(
                name=consultation.name,
                email=consultation.email,
                phone=consultation.phone,
                service_type=consultation.get_service_type_display(),
                comment=consultation.comment if consultation.comment else "No comments",
                created_at=consultation.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ).strip()
            
            # Format recipient number
            recipient_number = WhatsAppService.format_phone_number(settings.WHATSAPP_RECIPIENT_NUMBER)
            
            # Payload
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient_number,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }
            
            logger.info(f"📱 Sending WhatsApp to: {recipient_number}")
            logger.debug(f"URL: {url}")
            logger.debug(f"Payload: {payload}")
            
            # Send request
            response = requests.post(
                url, 
                headers=headers, 
                json=payload,
                timeout=10
            )
            
            logger.info(f"Status: {response.status_code}")
            logger.debug(f"Response: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                message_id = response_data.get('messages', [{}])[0].get('id', 'unknown')
                logger.info(f"✅ WhatsApp sent! Message ID: {message_id}")
                return True
            else:
                logger.error(f"❌ Failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Exception: {e}", exc_info=True)
            return False
