# Deployment Guide

This guide covers production deployment of the Support Request Processing System.

## 🏗️ Production Architecture

\`\`\`
Internet → Load Balancer → Web Servers → Database
                       → Background Workers → AI Service
                       → Redis Queue
                       → Teams Integration
\`\`\`

## 🚀 Production Deployment

### Prerequisites

- Linux server with Docker & Docker Compose
- 4GB+ RAM (for AI model)
- 20GB+ disk space
- Domain name (optional)
- SSL certificate (recommended)

### 1. Server Setup

\`\`\`bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login to apply docker group
\`\`\`

### 2. Application Deployment

\`\`\`bash
# Clone repository
git clone <repository-url>
cd support-system

# Create production environment file
cp .env.example .env.production
\`\`\`

### 3. Production Configuration

Edit `.env.production`:

\`\`\`env
# Database - Use strong passwords
DATABASE_URL=postgresql://prod_user:STRONG_PASSWORD_HERE@postgres:5432/support_prod

# Redis
REDIS_URL=redis://redis:6379/0

# AI Configuration
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=llama3.1:8b

# Teams Integration
TEAMS_WEBHOOK_URL=https://your-actual-teams-webhook-url

# Production Settings
DEBUG=false
LOG_LEVEL=INFO
ENVIRONMENT=production

# Security
SECRET_KEY=your-secret-key-here
\`\`\`

### 4. Production Docker Compose

Create `docker-compose.prod.yml`:

\`\`\`yaml
version: '3.8'

services:
  web:
    build: 
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://prod_user:${DB_PASSWORD}@postgres:5432/support_prod
      - REDIS_URL=redis://redis:6379/0
      - OLLAMA_URL=http://ollama:11434
      - OLLAMA_MODEL=llama3.1:8b
      - TEAMS_WEBHOOK_URL=${TEAMS_WEBHOOK_URL}
      - DEBUG=false
      - LOG_LEVEL=INFO
    depends_on:
      - postgres
      - redis
      - ollama
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  worker:
    build: 
      context: .
      dockerfile: Dockerfile
    command: celery -A app.tasks worker --loglevel=info --concurrency=4
    environment:
      - DATABASE_URL=postgresql://prod_user:${DB_PASSWORD}@postgres:5432/support_prod
      - REDIS_URL=redis://redis:6379/0
      - OLLAMA_URL=http://ollama:11434
      - OLLAMA_MODEL=llama3.1:8b
      - TEAMS_WEBHOOK_URL=${TEAMS_WEBHOOK_URL}
      - LOG_LEVEL=INFO
    depends_on:
      - postgres
      - redis
      - ollama
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=support_prod
      - POSTGRES_USER=prod_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U prod_user -d support_prod"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_prod_data:/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_prod_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/version"]
      interval: 60s
      timeout: 30s
      retries: 3
      start_period: 120s

  # Nginx reverse proxy (optional)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_prod_data:
  redis_prod_data:
  ollama_prod_data:
\`\`\`

### 5. Deploy to Production

\`\`\`bash
# Set environment variables
export DB_PASSWORD="your-strong-database-password"
export TEAMS_WEBHOOK_URL="your-teams-webhook-url"

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Initialize AI model
docker-compose -f docker-compose.prod.yml exec ollama bash /app/scripts/init_ollama.sh

# Verify deployment
docker-compose -f docker-compose.prod.yml ps
\`\`\`

## 🔒 Security Hardening

### 1. Firewall Configuration

\`\`\`bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
\`\`\`

### 2. SSL/TLS Setup

Create `nginx.conf`:

\`\`\`nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server web:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
\`\`\`

### 3. Database Security

\`\`\`bash
# Create backup user
docker-compose exec postgres psql -U prod_user -d support_prod -c "
CREATE USER backup_user WITH PASSWORD 'backup_password';
GRANT CONNECT ON DATABASE support_prod TO backup_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;
"
\`\`\`

## 📊 Monitoring & Logging

### 1. Log Management

\`\`\`bash
# Configure log rotation
sudo tee /etc/logrotate.d/docker-support-system << EOF
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=1M
    missingok
    delaycompress
    copytruncate
}
EOF
\`\`\`

### 2. Health Monitoring

Create `monitoring/health-check.sh`:

\`\`\`bash
#!/bin/bash

# Health check script
SERVICES=("web" "worker" "postgres" "redis" "ollama")
FAILED=0

for service in "${SERVICES[@]}"; do
    if ! docker-compose -f docker-compose.prod.yml ps $service | grep -q "Up"; then
        echo "❌ $service is down"
        FAILED=1
    else
        echo "✅ $service is healthy"
    fi
done

# Check application endpoint
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Application health check failed"
    FAILED=1
else
    echo "✅ Application is responding"
fi

exit $FAILED
\`\`\`

### 3. Automated Monitoring

Add to crontab:

\`\`\`bash
# Check every 5 minutes
*/5 * * * * /path/to/monitoring/health-check.sh >> /var/log/support-system-health.log 2>&1

# Daily backup
0 2 * * * /path/to/scripts/backup.sh >> /var/log/support-system-backup.log 2>&1
\`\`\`

## 💾 Backup Strategy

### 1. Database Backup

Create `scripts/backup.sh`:

\`\`\`bash
#!/bin/bash

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="support-system_postgres_1"

# Create backup
docker exec $CONTAINER_NAME pg_dump -U prod_user support_prod > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_$DATE.sql.gz"
\`\`\`

### 2. Volume Backup

\`\`\`bash
# Backup Docker volumes
docker run --rm -v support-system_postgres_prod_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/postgres_volume_$(date +%Y%m%d).tar.gz -C /data .
\`\`\`

## 🔄 Updates & Maintenance

### 1. Application Updates

\`\`\`bash
# Pull latest code
git pull origin main

# Rebuild and deploy
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose -f docker-compose.prod.yml ps
\`\`\`

### 2. Database Migrations

\`\`\`bash
# Run migrations (if any)
docker-compose -f docker-compose.prod.yml exec web python -c "
from app.database import create_tables
create_tables()
"
\`\`\`

## 📈 Scaling

### 1. Horizontal Scaling

\`\`\`yaml
# Scale workers
worker:
  deploy:
    replicas: 4

# Scale web servers
web:
  deploy:
    replicas: 2
\`\`\`

### 2. Load Balancing

\`\`\`nginx
upstream app {
    server web_1:8000;
    server web_2:8000;
    server web_3:8000;
}
\`\`\`

## 🚨 Disaster Recovery

### 1. Recovery Procedure

\`\`\`bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Restore database
gunzip -c /backups/backup_YYYYMMDD_HHMMSS.sql.gz | docker exec -i postgres_container psql -U prod_user support_prod

# Restore volumes
docker run --rm -v support-system_postgres_prod_data:/data -v $(pwd)/backups:/backup alpine tar xzf /backup/postgres_volume_YYYYMMDD.tar.gz -C /data

# Start services
docker-compose -f docker-compose.prod.yml up -d
\`\`\`

### 2. Rollback Strategy

\`\`\`bash
# Tag current version before deployment
docker tag support-system_web:latest support-system_web:backup-$(date +%Y%m%d)

# Rollback if needed
docker tag support-system_web:backup-YYYYMMDD support-system_web:latest
docker-compose -f docker-compose.prod.yml up -d
\`\`\`

## 📞 Production Support

### Common Production Issues

1. **High Memory Usage**: Reduce Ollama model size or increase server RAM
2. **Slow AI Processing**: Scale worker replicas or optimize model
3. **Database Locks**: Monitor long-running queries and optimize
4. **Disk Space**: Implement log rotation and backup cleanup

### Performance Tuning

\`\`\`bash
# Monitor resource usage
docker stats

# Check application metrics
curl http://localhost:8000/api/stats

# Database performance
docker exec postgres_container psql -U prod_user -d support_prod -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC LIMIT 10;
"
