# app/services/ai_classifier.py
import json
import logging
import httpx
import asyncio
from typing import Dict, Any, Optional
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class SelfHostedAIClassifier:
    """Self-hosted AI classifier using Ollama instead of OpenAI SaaS"""
    
    def __init__(self):
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://ollama:11434')
        self.model = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
        self.timeout = 60
        
        # Fallback categories for offline mode
        self.fallback_categories = {
            'cancel': 'cancellation_request',
            'refund': 'cancellation_request', 
            'stop': 'cancellation_request',
            'billing': 'billing',
            'payment': 'billing',
            'invoice': 'billing',
            'technical': 'technical_issue',
            'bug': 'technical_issue',
            'error': 'technical_issue',
            'crash': 'technical_issue',
            'feature': 'feature_request',
            'suggestion': 'feature_request',
            'complaint': 'complaint',
            'problem': 'complaint'
        }
    
    async def check_ollama_health(self) -> bool:
        """Check if Ollama service is available"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.ollama_url}/api/version")
                return response.status_code == 200
        except:
            return False
    
    def fallback_classify(self, subject: str, description: str) -> Dict[str, Any]:
        """Fallback classification when AI is unavailable"""
        logger.warning("Using fallback classification - AI service unavailable")
        
        text = f"{subject} {description}".lower()
        
        # Simple keyword-based classification
        for keyword, category in self.fallback_categories.items():
            if keyword in text:
                return {
                    'category': category,
                    'summary': f"Fallback classification: {category} (keyword: {keyword})",
                    'confidence': 0.6,
                    'method': 'fallback'
                }
        
        return {
            'category': 'general_inquiry',
            'summary': 'General inquiry - requires manual review',
            'confidence': 0.5,
            'method': 'fallback'
        }
    
    async def classify_request(self, subject: str, description: str) -> Dict[str, Any]:
        """Main classification method using self-hosted Ollama"""
        
        # Check if Ollama is available
        if not await self.check_ollama_health():
            logger.error("Ollama service unavailable, using fallback")
            return self.fallback_classify(subject, description)
        
        # Create detailed prompt for classification
        prompt = f"""You are a customer support classification system. Analyze this support request and classify it into ONE of these exact categories:
- billing
- technical_issue  
- cancellation_request
- feature_request
- complaint
- general_inquiry
- other

Support Request:
Subject: {subject}
Description: {description}

Respond with ONLY a JSON object in this exact format:
{{
    "category": "one_of_the_categories_above",
    "summary": "Brief 1-2 sentence summary of the issue",
    "confidence": 0.95
}}

Do not include any other text or explanations."""

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Call Ollama API
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "top_p": 0.9,
                            "num_predict": 200
                        }
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Ollama API error: {response.status_code}")
                    return self.fallback_classify(subject, description)
                
                # Parse Ollama response
                ollama_result = response.json()
                ai_response = ollama_result.get('response', '')
                
                # Extract JSON from AI response
                result = self.parse_ai_response(ai_response)
                
                # Validate and clean result
                return self.validate_classification_result(result, subject, description)
                
        except asyncio.TimeoutError:
            logger.error("Ollama request timeout")
            return self.fallback_classify(subject, description)
        except Exception as e:
            logger.error(f"Ollama classification error: {e}")
            return self.fallback_classify(subject, description)
    
    def parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse JSON from AI response, handling various formats"""
        
        # Try to find JSON in the response
        try:
            # First, try direct JSON parsing
            return json.loads(ai_response.strip())
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from text
        import re
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, ai_response)
        
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
        
        # If no valid JSON found, create default response
        logger.warning(f"Could not parse AI response: {ai_response}")
        return {
            "category": "general_inquiry",
            "summary": "AI parsing failed - manual review needed",
            "confidence": 0.3
        }
    
    def validate_classification_result(self, result: Dict[str, Any], subject: str, description: str) -> Dict[str, Any]:
        """Validate and clean AI classification result"""
        
        valid_categories = [
            'billing', 'technical_issue', 'cancellation_request',
            'feature_request', 'complaint', 'general_inquiry', 'other'
        ]
        
        # Ensure category is valid
        category = result.get('category', 'general_inquiry')
        if category not in valid_categories:
            logger.warning(f"Invalid category '{category}', defaulting to general_inquiry")
            category = 'general_inquiry'
        
        # Ensure summary exists and is reasonable length
        summary = result.get('summary', 'No summary provided')
        if len(summary) > 500:
            summary = summary[:497] + "..."
        
        # Ensure confidence is reasonable
        confidence = result.get('confidence', 0.7)
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            confidence = 0.7
        
        return {
            'category': category,
            'summary': summary,
            'confidence': confidence,
            'method': 'ollama_ai',
            'model': self.model,
            'timestamp': datetime.utcnow().isoformat()
        }

# Backward compatibility alias
AIClassifier = SelfHostedAIClassifier
