# Support Request Processing System

A production-ready, self-hosted support request processing system with AI-powered classification and Microsoft Teams integration.

## 🚀 Features

- **Web Form Interface**: Clean, responsive form for customers to submit support requests
- **AI-Powered Classification**: Automatic categorization using self-hosted Ollama (no SaaS dependencies)
- **Asynchronous Processing**: Redis + Celery for scalable background task processing
- **Teams Integration**: Automatic notifications for critical requests (cancellations, complaints)
- **PostgreSQL Database**: Reliable data storage with proper indexing
- **Docker Deployment**: Complete containerized setup with health checks
- **REST API**: Full API for programmatic access
- **Admin Interface**: Web-based request viewing and management
- **Production Ready**: Comprehensive logging, error handling, and monitoring

## 🏗️ Architecture

\`\`\`
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Form      │    │   FastAPI App    │    │   PostgreSQL    │
│   (Customer)    │───▶│   (API Server)   │───▶│   (Database)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Redis Queue    │    │   Celery Worker │
                       │   (Task Broker)  │───▶│   (Background)  │
                       └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Ollama AI      │    │  Teams Webhook  │
                       │   (Classification)│    │  (Notifications)│
                       └──────────────────┘    └─────────────────┘
\`\`\`

## 🎯 Complete System Demonstration

### Quick Setup & Test
\`\`\`bash
# 1. Start all services
docker-compose up -d

# 2. Initialize AI model (first time only - takes 10-15 minutes)
chmod +x scripts/init_ollama.sh
./scripts/init_ollama.sh

# 3. Run complete system demonstration
python3 scripts/task_demonstration.py
\`\`\`

### Expected Demo Output
\`\`\`
🚀 Customer Support Automation System Demo
==========================================

✅ System Health Check
- Web Service: ✅ Healthy (200)
- Database: ✅ Connected
- Redis: ✅ Connected  
- Ollama AI: ✅ Ready (llama3.1:8b loaded)

📝 Testing Support Request Workflow

1️⃣ BILLING REQUEST
   Customer: Sarah Johnson (sarah@company.com)
   Subject: "Refund request for overcharge"
   → Status: completed
   → AI Category: billing
   → AI Summary: Customer requesting refund for billing overcharge
   → Teams Notification: Not sent (billing category)

2️⃣ TECHNICAL ISSUE  
   Customer: Mike Chen (mike@techcorp.com)
   Subject: "Application crashes on startup"
   → Status: completed
   → AI Category: technical_issue
   → AI Summary: Application experiencing startup crashes
   → Teams Notification: Sent ✅

3️⃣ CANCELLATION REQUEST
   Customer: Lisa Brown (lisa@startup.io)
   Subject: "Cancel my subscription immediately"
   → Status: completed
   → AI Category: cancellation_request
   → AI Summary: Customer requesting immediate subscription cancellation
   → Teams Notification: Sent ✅ (Critical Request)

4️⃣ GENERAL INQUIRY
   Customer: David Wilson (david@example.com)
   Subject: "How to use advanced features?"
   → Status: completed
   → AI Category: general_inquiry
   → AI Summary: Customer inquiry about advanced feature usage
   → Teams Notification: Not sent

📊 Final Statistics:
- Total Requests: 4
- Successfully Processed: 4 (100%)
- AI Classifications: 4/4 successful
- Teams Notifications: 2/4 sent (for critical categories)

🎉 Demo Complete! All systems working perfectly.
\`\`\`

## 📋 Requirements

- Docker & Docker Compose
- 4GB+ RAM (for Ollama AI model)
- Microsoft Teams webhook URL (optional)

## 🚀 Quick Start

### 1. Clone and Setup

\`\`\`bash
git clone <repository-url>
cd support-system
\`\`\`

### 2. Deploy with Docker

\`\`\`bash
# Start all services
docker-compose up -d

# Initialize Ollama AI model (first time only)
chmod +x scripts/init_ollama.sh
./scripts/init_ollama.sh

# Check service health
docker-compose ps
\`\`\`

### 3. Configure Teams (Optional)

\`\`\`bash
# Set your Teams webhook URL
export TEAMS_WEBHOOK_URL="https://your-teams-webhook-url"
docker-compose restart web worker
\`\`\`

### 4. Test the System

\`\`\`bash
# Run complete demonstration
python3 scripts/task_demonstration.py

# Or test manually
curl http://localhost:8000/health
\`\`\`

## 🌐 Usage

### Web Interface

- **Customer Form**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin/requests/{id}
- **API Documentation**: http://localhost:8000/docs

### API Examples

\`\`\`bash
# Submit support request
curl -X POST http://localhost:8000/api/support-requests \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "John Doe",
    "email": "john@example.com", 
    "subject": "Need help with billing",
    "description": "I have a question about my recent invoice..."
  }'

# Response:
{
  "id": 1,
  "customer_name": "John Doe",
  "email": "john@example.com",
  "subject": "Need help with billing", 
  "description": "I have a question about my recent invoice...",
  "processing_status": "pending",
  "created_at": "2024-01-15T10:30:00Z"
}

# Get request status (after AI processing)
curl http://localhost:8000/api/support-requests/1

# Response:
{
  "id": 1,
  "customer_name": "John Doe",
  "email": "john@example.com",
  "subject": "Need help with billing",
  "description": "I have a question about my recent invoice...",
  "category": "billing",
  "ai_summary": "Customer inquiry about billing charges and invoice details",
  "processing_status": "completed",
  "notification_sent": false,
  "created_at": "2024-01-15T10:30:00Z",
  "processed_at": "2024-01-15T10:31:00Z"
}

# List all requests
curl http://localhost:8000/api/support-requests

# Get system statistics
curl http://localhost:8000/api/stats
\`\`\`

## 🤖 AI Classification Categories

The system automatically classifies requests into:

- **cancellation_request**: Subscription cancellations, account closures → **Teams notification sent**
- **billing**: Payment issues, invoice questions, refunds
- **technical_issue**: Bugs, crashes, performance problems → **Teams notification sent**
- **feature_request**: New feature suggestions, improvements
- **complaint**: Service complaints, dissatisfaction → **Teams notification sent**
- **general_inquiry**: General questions, information requests

### Teams Integration

Critical requests (cancellations, complaints, technical issues) automatically trigger Teams notifications:

\`\`\`json
{
  "@type": "MessageCard",
  "@context": "http://schema.org/extensions",
  "summary": "🚨 Critical Support Request",
  "themeColor": "FF6B6B",
  "sections": [{
    "activityTitle": "🚨 Critical Support Request - cancellation_request",
    "activitySubtitle": "Customer: Lisa Brown (lisa@startup.io)",
    "facts": [
      {"name": "Subject", "value": "Cancel my subscription immediately"},
      {"name": "Category", "value": "cancellation_request"},
      {"name": "AI Summary", "value": "Customer requesting immediate subscription cancellation"},
      {"name": "Request ID", "value": "3"}
    ]
  }]
}
\`\`\`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | Required |
| `OLLAMA_URL` | Ollama API endpoint | `http://ollama:11434` |
| `OLLAMA_MODEL` | AI model to use | `llama3.1:8b` |
| `TEAMS_WEBHOOK_URL` | Teams webhook URL | Optional |
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Scaling Configuration

\`\`\`yaml
# docker-compose.yml
worker:
  command: celery -A app.tasks worker --loglevel=info --concurrency=4
  deploy:
    replicas: 2
\`\`\`

## 📊 Monitoring

### Health Checks

\`\`\`bash
# Application health
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready -U support_user

# Redis health  
docker-compose exec redis redis-cli ping

# Ollama health
curl http://localhost:11434/api/version
\`\`\`

### Logs

\`\`\`bash
# Application logs
docker-compose logs -f web

# Worker logs
docker-compose logs -f worker

# All services
docker-compose logs -f
\`\`\`

### Statistics

The system provides real-time statistics at `/api/stats`:

\`\`\`json
{
  "total_requests": 150,
  "status_breakdown": {
    "pending": 5,
    "processing": 2,
    "completed": 140,
    "failed": 3
  },
  "category_breakdown": {
    "billing": 45,
    "technical_issue": 38,
    "cancellation_request": 25,
    "general_inquiry": 32
  }
}
\`\`\`

## 🛠️ Development

### Local Development

\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Start services (database, redis, ollama)
docker-compose up -d postgres redis ollama

# Run application locally
export DATABASE_URL="postgresql://support_user:support_pass@localhost:5432/support_db"
export REDIS_URL="redis://localhost:6379/0"
uvicorn app.main:app --reload

# Run worker locally
celery -A app.tasks worker --loglevel=info
\`\`\`

### Testing

\`\`\`bash
# Run demo test
python scripts/demo_test.py

# Manual API testing
curl -X POST http://localhost:8000/api/support-requests \
  -H "Content-Type: application/json" \
  -d @test_request.json
\`\`\`

## 🚨 Troubleshooting

### Common Issues

**AI Processing Timeouts**
\`\`\`bash
# Check Ollama status
curl http://localhost:11434/api/version

# Restart Ollama service
docker-compose restart ollama

# Check worker logs
docker-compose logs worker
\`\`\`

**Database Connection Issues**
\`\`\`bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready -U support_user

# Reset database
docker-compose down -v
docker-compose up -d postgres
\`\`\`

**Teams Notifications Not Working**
\`\`\`bash
# Verify webhook URL
echo $TEAMS_WEBHOOK_URL

# Test webhook manually
curl -X POST $TEAMS_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{"text": "Test message"}'
\`\`\`

### Performance Tuning

**For High Volume**
\`\`\`yaml
# Increase worker concurrency
worker:
  command: celery -A app.tasks worker --loglevel=info --concurrency=8

# Scale workers
worker:
  deploy:
    replicas: 4
\`\`\`

**For Limited Resources**
\`\`\`yaml
# Reduce Ollama memory
ollama:
  deploy:
    resources:
      limits:
        memory: 2G
\`\`\`

## 📚 API Reference

### Support Request Object

\`\`\`json
{
  "id": 1,
  "customer_name": "John Doe",
  "email": "john@example.com",
  "subject": "Billing question",
  "description": "I have a question about my invoice...",
  "category": "billing",
  "ai_summary": "Customer inquiry about billing charges",
  "processing_status": "completed",
  "notification_sent": "false",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:31:00Z",
  "processed_at": "2024-01-15T10:31:00Z"
}
\`\`\`

### Status Values

- `pending`: Request submitted, waiting for processing
- `processing`: Currently being processed by AI
- `completed`: Successfully processed and classified
- `failed`: Processing failed (will retry automatically)

## 🔒 Security

- No external SaaS dependencies (fully self-hosted)
- Environment variable configuration
- Input validation and sanitization
- SQL injection protection via SQLAlchemy ORM
- Rate limiting ready (add nginx proxy)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs
3. Run the demo test script
4. Create an issue with detailed logs and configuration
