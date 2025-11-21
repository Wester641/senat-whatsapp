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


class TelegramService:
    """
    Service for sending messages to Telegram using Telegram Bot API
    """
    
    @staticmethod
    def send_to_chat(chat_id, message):
        """
        Send message to Telegram chat using Bot API
        """
        try:
            url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
            
            # Payload
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            logger.info(f"📱 Sending Telegram message to chat: {chat_id}")
            logger.debug(f"URL: {url}")
            logger.debug(f"Payload: {payload}")
            
            # Send request
            response = requests.post(
                url, 
                json=payload,
                timeout=10
            )
            
            logger.info(f"Status: {response.status_code}")
            logger.debug(f"Response: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('ok'):
                    message_id = response_data.get('result', {}).get('message_id', 'unknown')
                    logger.info(f"✅ Telegram message sent to {chat_id}! Message ID: {message_id}")
                    return True, chat_id
                else:
                    logger.error(f"❌ Telegram API returned ok=False: {response_data}")
                    return False, chat_id
            else:
                logger.error(f"❌ Failed to send to {chat_id}: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False, chat_id
            
        except Exception as e:
            logger.error(f"❌ Exception sending to {chat_id}: {e}", exc_info=True)
            return False, chat_id
    
    @staticmethod
    def send_consultation_request(consultation):
        """
        Send consultation request to Telegram - supports multiple chats
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
            
            chat_ids = settings.TELEGRAM_CHAT_IDS
            
            if isinstance(chat_ids, str):
                chat_ids = [chat_id.strip() for chat_id in chat_ids.split(',')]
            
            chat_ids = [chat_id for chat_id in chat_ids if chat_id]
            
            if not chat_ids:
                logger.error("❌ No chat IDs configured!")
                return False
            
            logger.info(f"📤 Sending to {len(chat_ids)} chat(s)")
            
            results = []
            success_count = 0
            
            for chat_id in chat_ids:
                success, chat = TelegramService.send_to_chat(chat_id, message)
                results.append({
                    'chat_id': chat,
                    'success': success
                })
                if success:
                    success_count += 1
            
            logger.info(f"📊 Summary: {success_count}/{len(chat_ids)} messages sent successfully")
            
            for result in results:
                status = "✅" if result['success'] else "❌"
                logger.info(f"{status} {result['chat_id']}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Exception in send_consultation_request: {e}", exc_info=True)
            return False