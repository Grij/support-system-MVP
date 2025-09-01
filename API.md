# API Documentation

Complete API reference for the Support Request Processing System.

## Base URL

\`\`\`
http://localhost:8000/api
\`\`\`

## Authentication

Currently, the API does not require authentication. In production, consider adding API key authentication.

## Content Type

All API requests should use `Content-Type: application/json` for POST/PUT requests.

## Response Format

All API responses follow this structure:

\`\`\`json
{
  "data": {},
  "status": "success|error",
  "message": "Optional message",
  "timestamp": "2024-01-15T10:30:00Z"
}
\`\`\`

## Endpoints

### 1. Health Check

Check system health and status.

**GET** `/health`

**Response:**
\`\`\`json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "service": "support-request-processor"
}
\`\`\`

**Status Codes:**
- `200`: System is healthy
- `503`: System is unhealthy

---

### 2. Create Support Request

Submit a new support request for processing.

**POST** `/api/support-requests`

**Request Body:**
\`\`\`json
{
  "customer_name": "John Doe",
  "email": "john.doe@example.com",
  "subject": "Billing question about my account",
  "description": "I have a question about the charges on my recent invoice. Can someone please review my account and explain the billing details?"
}
\`\`\`

**Response:**
\`\`\`json
{
  "id": 123,
  "customer_name": "John Doe",
  "email": "john.doe@example.com",
  "subject": "Billing question about my account",
  "description": "I have a question about the charges...",
  "category": null,
  "ai_summary": null,
  "processing_status": "pending",
  "notification_sent": "false",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "processed_at": null
}
\`\`\`

**Validation Rules:**
- `customer_name`: Required, 1-100 characters
- `email`: Required, valid email format
- `subject`: Required, 1-200 characters
- `description`: Required, 1-5000 characters

**Status Codes:**
- `200`: Request created successfully
- `422`: Validation error
- `500`: Server error

---

### 3. Get Support Request

Retrieve a specific support request by ID.

**GET** `/api/support-requests/{request_id}`

**Path Parameters:**
- `request_id` (integer): The ID of the support request

**Response:**
\`\`\`json
{
  "id": 123,
  "customer_name": "John Doe",
  "email": "john.doe@example.com",
  "subject": "Billing question about my account",
  "description": "I have a question about the charges...",
  "category": "billing",
  "ai_summary": "Customer inquiry about billing charges and account details",
  "processing_status": "completed",
  "notification_sent": "false",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:31:00Z",
  "processed_at": "2024-01-15T10:31:00Z"
}
\`\`\`

**Status Codes:**
- `200`: Request found
- `404`: Request not found
- `500`: Server error

---

### 4. List Support Requests

Retrieve a list of support requests with optional filtering and pagination.

**GET** `/api/support-requests`

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip (default: 0)
- `limit` (integer, optional): Maximum number of records to return (default: 100, max: 1000)
- `status` (string, optional): Filter by processing status

**Example:**
\`\`\`
GET /api/support-requests?skip=0&limit=50&status=completed
\`\`\`

**Response:**
\`\`\`json
[
  {
    "id": 123,
    "customer_name": "John Doe",
    "email": "john.doe@example.com",
    "subject": "Billing question",
    "description": "I have a question...",
    "category": "billing",
    "ai_summary": "Customer inquiry about billing",
    "processing_status": "completed",
    "notification_sent": "false",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:31:00Z",
    "processed_at": "2024-01-15T10:31:00Z"
  }
]
\`\`\`

**Status Codes:**
- `200`: Success
- `422`: Invalid query parameters
- `500`: Server error

---

### 5. Get Statistics

Retrieve system statistics and metrics.

**GET** `/api/stats`

**Response:**
\`\`\`json
{
  "total_requests": 1250,
  "status_breakdown": {
    "pending": 15,
    "processing": 3,
    "completed": 1200,
    "failed": 32
  },
  "category_breakdown": {
    "billing": 450,
    "technical_issue": 380,
    "cancellation_request": 125,
    "feature_request": 95,
    "complaint": 85,
    "general_inquiry": 115
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
\`\`\`

**Status Codes:**
- `200`: Success
- `500`: Server error

---

### 6. Test AI Classification

Test the AI classification system directly with sample text.

**POST** `/api/classify`

**Request Body (Form Data):**
\`\`\`
subject=Cancel my subscription
description=I want to cancel my premium subscription immediately
\`\`\`

**Response:**
\`\`\`json
{
  "status": "success",
  "classification": {
    "category": "cancellation_request",
    "summary": "Customer requesting immediate subscription cancellation",
    "confidence": 0.95,
    "method": "ollama_ai",
    "model": "llama3.1:8b",
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
\`\`\`

**Status Codes:**
- `200`: Classification successful
- `500`: Classification failed

---

### 7. Check Ollama Health

Check the health status of the Ollama AI service.

**GET** `/api/ollama/health`

**Response:**
\`\`\`json
{
  "ollama_healthy": true,
  "ollama_url": "http://ollama:11434",
  "model": "llama3.1:8b",
  "timestamp": "2024-01-15T10:30:00Z"
}
\`\`\`

**Status Codes:**
- `200`: Health check completed (check `ollama_healthy` field for actual status)
- `500`: Health check failed

---

## Data Models

### Support Request Object

\`\`\`json
{
  "id": 123,
  "customer_name": "John Doe",
  "email": "john.doe@example.com",
  "subject": "Request subject",
  "description": "Detailed description of the issue or request",
  "category": "billing|technical_issue|cancellation_request|feature_request|complaint|general_inquiry|other",
  "ai_summary": "AI-generated summary of the request",
  "processing_status": "pending|processing|completed|failed",
  "notification_sent": "true|false",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:31:00Z",
  "processed_at": "2024-01-15T10:31:00Z"
}
\`\`\`

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique identifier for the request |
| `customer_name` | string | Customer's full name |
| `email` | string | Customer's email address |
| `subject` | string | Brief subject line of the request |
| `description` | string | Detailed description of the issue |
| `category` | string | AI-classified category (null until processed) |
| `ai_summary` | string | AI-generated summary (null until processed) |
| `processing_status` | string | Current processing status |
| `notification_sent` | string | Whether Teams notification was sent |
| `created_at` | datetime | When the request was created |
| `updated_at` | datetime | When the request was last updated |
| `processed_at` | datetime | When AI processing completed (null if not processed) |

### Processing Status Values

| Status | Description |
|--------|-------------|
| `pending` | Request submitted, waiting for AI processing |
| `processing` | Currently being processed by AI classifier |
| `completed` | Successfully processed and classified |
| `failed` | Processing failed (will be retried automatically) |

### Category Values

| Category | Description | Teams Notification |
|----------|-------------|-------------------|
| `billing` | Payment issues, invoices, refunds | No |
| `technical_issue` | Bugs, crashes, performance problems | Yes |
| `cancellation_request` | Subscription cancellations, account closures | Yes |
| `feature_request` | New feature suggestions, improvements | No |
| `complaint` | Service complaints, dissatisfaction | Yes |
| `general_inquiry` | General questions, information requests | No |
| `other` | Requests that don't fit other categories | No |

---

## Error Handling

### Error Response Format

\`\`\`json
{
  "detail": "Error message",
  "status_code": 422,
  "timestamp": "2024-01-15T10:30:00Z"
}
\`\`\`

### Common Error Codes

| Code | Description |
|------|-------------|
| `400` | Bad Request - Invalid request format |
| `404` | Not Found - Resource doesn't exist |
| `422` | Validation Error - Invalid input data |
| `500` | Internal Server Error - System error |
| `503` | Service Unavailable - System maintenance |

### Validation Errors

\`\`\`json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
\`\`\`

---

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing rate limiting:

- 100 requests per minute per IP for general endpoints
- 10 requests per minute per IP for support request creation
- Higher limits for authenticated API users

---

## Examples

### Create and Monitor Request

\`\`\`bash
# 1. Create request
curl -X POST http://localhost:8000/api/support-requests \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Alice Johnson",
    "email": "alice@example.com",
    "subject": "Cancel my subscription",
    "description": "I want to cancel my premium subscription immediately. Please process this as soon as possible."
  }'

# Response: {"id": 456, "processing_status": "pending", ...}

# 2. Check processing status
curl http://localhost:8000/api/support-requests/456

# Response: {"id": 456, "processing_status": "processing", ...}

# 3. Check final result (after processing)
curl http://localhost:8000/api/support-requests/456

# Response: {
#   "id": 456,
#   "category": "cancellation_request",
#   "ai_summary": "Customer requesting immediate subscription cancellation",
#   "processing_status": "completed",
#   "notification_sent": "true",
#   ...
# }
\`\`\`

### Test AI Classification

\`\`\`bash
# Test AI classification directly
curl -X POST http://localhost:8000/api/classify \
  -d "subject=App keeps crashing" \
  -d "description=The mobile app crashes every time I try to open it"

# Response: {
#   "status": "success",
#   "classification": {
#     "category": "technical_issue",
#     "summary": "Mobile app experiencing crashes on startup",
#     "confidence": 0.92,
#     "method": "ollama_ai"
#   }
# }
\`\`\`

### Check System Health

\`\`\`bash
# Check overall system health
curl http://localhost:8000/health

# Check AI service specifically
curl http://localhost:8000/api/ollama/health

# Get system statistics
curl http://localhost:8000/api/stats
\`\`\`

### Batch Processing Monitoring

\`\`\`bash
# Create multiple requests
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/support-requests \
    -H "Content-Type: application/json" \
    -d "{\"customer_name\": \"Test User $i\", \"email\": \"test$i@example.com\", \"subject\": \"Test request $i\", \"description\": \"This is test request number $i\"}"
done

# Monitor processing
watch -n 5 'curl -s http://localhost:8000/api/stats | jq .status_breakdown'
\`\`\`

### Filter and Search

\`\`\`bash
# Get only completed requests
curl "http://localhost:8000/api/support-requests?status=completed&limit=10"

# Get recent requests (last 50)
curl "http://localhost:8000/api/support-requests?skip=0&limit=50"

# Get system statistics
curl http://localhost:8000/api/stats | jq .
\`\`\`

---

## SDK Examples

### Python SDK Example

\`\`\`python
import requests
import json
import time

class SupportSystemAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
    
    def create_request(self, customer_name, email, subject, description):
        """Create a new support request"""
        data = {
            "customer_name": customer_name,
            "email": email,
            "subject": subject,
            "description": description
        }
        
        response = requests.post(
            f"{self.api_base}/support-requests",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def get_request(self, request_id):
        """Get a specific support request"""
        response = requests.get(f"{self.api_base}/support-requests/{request_id}")
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def test_classification(self, subject, description):
        """Test AI classification directly"""
        data = {
            "subject": subject,
            "description": description
        }
        
        response = requests.post(f"{self.api_base}/classify", data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def check_ollama_health(self):
        """Check Ollama AI service health"""
        response = requests.get(f"{self.api_base}/ollama/health")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def wait_for_processing(self, request_id, timeout=300):
        """Wait for request to be processed"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            request = self.get_request(request_id)
            if request and request['processing_status'] in ['completed', 'failed']:
                return request
            time.sleep(5)
        
        raise TimeoutError(f"Request {request_id} not processed within {timeout} seconds")
    
    def get_stats(self):
        """Get system statistics"""
        response = requests.get(f"{self.api_base}/stats")
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

# Usage example
api = SupportSystemAPI()

# Check system health first
try:
    health = api.check_ollama_health()
    print(f"Ollama healthy: {health['ollama_healthy']}")
except Exception as e:
    print(f"Health check failed: {e}")

# Test classification
try:
    result = api.test_classification(
        "Cancel subscription", 
        "I want to cancel my account immediately"
    )
    print(f"Classification: {result['classification']['category']}")
except Exception as e:
    print(f"Classification test failed: {e}")

# Create request
request = api.create_request(
    customer_name="John Doe",
    email="john@example.com",
    subject="Billing issue",
    description="I was charged twice for my subscription"
)

print(f"Created request #{request['id']}")

# Wait for processing
processed_request = api.wait_for_processing(request['id'])
print(f"Request processed as: {processed_request['category']}")
print(f"AI Summary: {processed_request['ai_summary']}")
\`\`\`

### JavaScript SDK Example

\`\`\`javascript
class SupportSystemAPI {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.apiBase = `${baseUrl}/api`;
    }

    async createRequest(customerName, email, subject, description) {
        const response = await fetch(`${this.apiBase}/support-requests`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                customer_name: customerName,
                email: email,
                subject: subject,
                description: description
            })
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} - ${await response.text()}`);
        }

        return await response.json();
    }

    async getRequest(requestId) {
        const response = await fetch(`${this.apiBase}/support-requests/${requestId}`);
        
        if (response.status === 404) {
            return null;
        }
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} - ${await response.text()}`);
        }

        return await response.json();
    }

    async testClassification(subject, description) {
        const formData = new FormData();
        formData.append('subject', subject);
        formData.append('description', description);

        const response = await fetch(`${this.apiBase}/classify`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} - ${await response.text()}`);
        }

        return await response.json();
    }

    async checkOllamaHealth() {
        const response = await fetch(`${this.apiBase}/ollama/health`);
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} - ${await response.text()}`);
        }

        return await response.json();
    }

    async waitForProcessing(requestId, timeout = 300000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            const request = await this.getRequest(requestId);
            
            if (request && ['completed', 'failed'].includes(request.processing_status)) {
                return request;
            }
            
            await new Promise(resolve => setTimeout(resolve, 5000));
        }
        
        throw new Error(`Request ${requestId} not processed within ${timeout}ms`);
    }

    async getStats() {
        const response = await fetch(`${this.apiBase}/stats`);
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status} - ${await response.text()}`);
        }

        return await response.json();
    }
}

// Usage example
const api = new SupportSystemAPI();

async function example() {
    try {
        // Check system health
        const health = await api.checkOllamaHealth();
        console.log(`Ollama healthy: ${health.ollama_healthy}`);
        
        // Test classification
        const classificationResult = await api.testClassification(
            'Feature request',
            'Please add dark mode to the application'
        );
        console.log(`Test classification: ${classificationResult.classification.category}`);
        
        // Create request
        const request = await api.createRequest(
            'Jane Smith',
            'jane@example.com',
            'Feature request',
            'Please add dark mode to the application'
        );
        
        console.log(`Created request #${request.id}`);
        
        // Wait for processing
        const processedRequest = await api.waitForProcessing(request.id);
        console.log(`Request processed as: ${processedRequest.category}`);
        console.log(`AI Summary: ${processedRequest.ai_summary}`);
        
    } catch (error) {
        console.error('Error:', error.message);
    }
}

example();
\`\`\`

---

## Webhooks (Future Enhancement)

The API could be extended to support webhooks for real-time notifications:

\`\`\`json
{
  "webhook_url": "https://your-app.com/webhooks/support",
  "events": ["request.created", "request.processed", "request.failed"],
  "secret": "your-webhook-secret"
}
\`\`\`

This would allow external systems to receive real-time updates when support requests are processed.
