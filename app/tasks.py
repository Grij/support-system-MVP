import os
import asyncio
import logging
from celery import Celery
from datetime import datetime
from app.database import SessionLocal
from app.models import SupportRequest
from app.services.ai_classifier import AIClassifier
from app.services.teams_notifier import TeamsNotifier

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Створення Celery app
celery_app = Celery(
    'support_processor',
    broker=os.getenv('REDIS_URL', 'redis://redis:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://redis:6379/0')
)

# Конфігурація Celery
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    task_routes={
        'app.tasks.process_support_request': {'queue': 'support_processing'},
        'app.tasks.send_teams_notification': {'queue': 'notifications'}
    }
)

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def process_support_request(self, request_id: int):
    """Основне завдання для обробки запиту підтримки з AI класифікацією"""
    
    logger.info(f"Starting processing for request {request_id}")
    
    db = SessionLocal()
    try:
        # Отримуємо запит з бази даних
        request = db.query(SupportRequest).filter(SupportRequest.id == request_id).first()
        if not request:
            raise ValueError(f"Request {request_id} not found")
        
        # Перевіряємо чи не обробляється вже
        if request.processing_status == 'completed':
            logger.info(f"Request {request_id} already processed, skipping")
            return
        
        # Оновлюємо статус на "в обробці"
        request.processing_status = 'processing'
        db.commit()
        
        # AI класифікація
        classifier = AIClassifier()
        
        # Використовуємо синхронний виклик для Celery
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ai_result = loop.run_until_complete(
            classifier.classify_request(request.subject, request.description)
        )
        loop.close()
        
        # Оновлюємо запит з результатами AI
        request.category = ai_result['category']
        request.ai_summary = ai_result['summary']
        request.processed_at = datetime.utcnow()
        request.processing_status = 'completed'
        
        db.commit()
        
        logger.info(f"Successfully processed request {request_id} as {ai_result['category']}")
        
        # Якщо це запит на скасування, відправляємо сповіщення в Teams
        if ai_result['category'] == 'cancellation_request':
            send_teams_notification.delay(request_id)
        
        return {
            "request_id": request_id,
            "category": ai_result['category'],
            "summary": ai_result['summary']
        }
        
    except Exception as e:
        logger.error(f"Error processing request {request_id}: {e}")
        
        # Оновлюємо статус на помилку
        if 'request' in locals():
            request.processing_status = 'failed'
            db.commit()
        
        raise
    finally:
        db.close()

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 30})
def send_teams_notification(self, request_id: int):
    """Відправляє сповіщення в Teams для запитів на скасування"""
    
    logger.info(f"Sending Teams notification for request {request_id}")
    
    db = SessionLocal()
    try:
        request = db.query(SupportRequest).filter(SupportRequest.id == request_id).first()
        if not request:
            raise ValueError(f"Request {request_id} not found")
        
        # Перевіряємо чи не відправлено вже сповіщення
        if request.notification_sent == "true":
            logger.info(f"Teams notification already sent for request {request_id}")
            return
        
        # Відправляємо сповіщення
        notifier = TeamsNotifier()
        
        # Використовуємо синхронний виклик для Celery
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        notification_id = loop.run_until_complete(
            notifier.send_cancellation_alert(request)
        )
        loop.close()
        
        # Оновлюємо статус сповіщення
        request.notification_sent = "true"
        db.commit()
        
        logger.info(f"Teams notification sent successfully for request {request_id}")
        
        return {"request_id": request_id, "notification_id": notification_id}
        
    except Exception as e:
        logger.error(f"Failed to send Teams notification for request {request_id}: {e}")
        raise
    finally:
        db.close()
