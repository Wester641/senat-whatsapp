import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

CONSULTATION_MESSAGE_TEMPLATE = """🔔 New Request For Consultation!

👤 Имя: {name}
📧 Email: {email}
📱 Номер телефона: {phone}
📋 Тип консультации: {service_type}
💬 Комментарии: {comment}

🕐 Время: {created_at}"""


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
    def send_to_single_recipient(recipient_number, message):
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
            
            # Format recipient number
            formatted_number = WhatsAppService.format_phone_number(recipient_number)
            
            # Payload
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": formatted_number,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }
            
            logger.info(f"📱 Sending WhatsApp to: {formatted_number}")
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
                logger.info(f"✅ WhatsApp sent to {formatted_number}! Message ID: {message_id}")
                return True, formatted_number
            else:
                logger.error(f"❌ Failed to send to {formatted_number}: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False, formatted_number
            
        except Exception as e:
            logger.error(f"❌ Exception sending to {recipient_number}: {e}", exc_info=True)
            return False, recipient_number
    
    @staticmethod
    def send_consultation_request_cloud_api(consultation):
        """
        WhatsApp Cloud API (Meta) - Send to multiple recipients
        """
        try:
            message = CONSULTATION_MESSAGE_TEMPLATE.format(
                name=consultation.name,
                email=consultation.email,
                phone=consultation.phone,
                service_type=consultation.get_service_type_display(),
                comment=consultation.comment if consultation.comment else "No comments",
                created_at=consultation.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ).strip()
            
            recipient_numbers = settings.WHATSAPP_RECIPIENT_NUMBER
            
            if isinstance(recipient_numbers, str):
                recipient_numbers = [num.strip() for num in recipient_numbers.split(',')]
            
            recipient_numbers = [num for num in recipient_numbers if num]
            
            if not recipient_numbers:
                logger.error("❌ No recipient numbers configured!")
                return False
            
            logger.info(f"📤 Sending to {len(recipient_numbers)} recipient(s)")
            
            results = []
            success_count = 0
            
            for recipient in recipient_numbers:
                success, number = WhatsAppService.send_to_single_recipient(recipient, message)
                results.append({
                    'number': number,
                    'success': success
                })
                if success:
                    success_count += 1
            
            logger.info(f"📊 Summary: {success_count}/{len(recipient_numbers)} messages sent successfully")
            
            for result in results:
                status = "✅" if result['success'] else "❌"
                logger.info(f"{status} {result['number']}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Exception in send_consultation_request_cloud_api: {e}", exc_info=True)
            return False