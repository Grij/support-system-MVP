# app/services/teams_notifier.py
import os
import json
import logging
import httpx
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TeamsNotifier:
    """Microsoft Teams notification service for support requests"""
    
    def __init__(self):
        self.webhook_url = os.getenv('TEAMS_WEBHOOK_URL')
        self.timeout = 30
        
        if not self.webhook_url or self.webhook_url == "https://your-teams-webhook-url-here":
            logger.warning("Teams webhook URL not configured properly")
    
    async def send_cancellation_alert(self, support_request) -> Optional[str]:
        """Send cancellation request alert to Teams"""
        
        if not self.webhook_url or self.webhook_url == "https://your-teams-webhook-url-here":
            logger.warning("Teams webhook not configured, skipping notification")
            return None
        
        # Create Teams message card
        message_card = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "FF6B35",  # Orange for cancellation alerts
            "summary": f"Cancellation Request #{support_request.id}",
            "sections": [
                {
                    "activityTitle": "🚨 Cancellation Request Alert",
                    "activitySubtitle": f"Request #{support_request.id}",
                    "facts": [
                        {
                            "name": "Customer",
                            "value": support_request.customer_name
                        },
                        {
                            "name": "Email",
                            "value": support_request.email
                        },
                        {
                            "name": "Subject",
                            "value": support_request.subject
                        },
                        {
                            "name": "Category",
                            "value": support_request.category or "Not classified"
                        },
                        {
                            "name": "Created",
                            "value": support_request.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                        }
                    ],
                    "markdown": True
                },
                {
                    "activityTitle": "Description",
                    "text": support_request.description[:500] + ("..." if len(support_request.description) > 500 else "")
                }
            ],
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "View Request",
                    "targets": [
                        {
                            "os": "default",
                            "uri": f"http://localhost:8000/admin/requests/{support_request.id}"
                        }
                    ]
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.webhook_url,
                    json=message_card,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    logger.info(f"Teams notification sent successfully for request {support_request.id}")
                    return f"teams_notification_{support_request.id}_{datetime.utcnow().timestamp()}"
                else:
                    logger.error(f"Teams notification failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error sending Teams notification: {e}")
            return None
    
    async def send_notification(self, support_request, classification_result: Dict[str, Any]) -> bool:
        """Generic notification method for backward compatibility"""
        result = await self.send_cancellation_alert(support_request)
        return result is not None
