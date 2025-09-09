# CVFlow Deployment Guide

## Overview

CVFlow is a comprehensive CV management and HR process automation system built with Python FastAPI backend and React frontend. This guide covers deployment options, configuration, and maintenance.

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows 10+

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 50GB+ SSD
- **OS**: Linux (Ubuntu 22.04+)

## Prerequisites

### Required Software
- Docker 20.10+
- Docker Compose 2.0+
- Git
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### Optional Software
- Nginx (for production reverse proxy)
- SSL certificates (for HTTPS)
- Monitoring tools (Prometheus, Grafana)

## Quick Start with Docker

### 1. Clone Repository
```bash
git clone <repository-url>
cd cvflow
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

### 3. Start Services
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Initialize Database
```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Create admin user (optional)
docker-compose exec backend python -m app.scripts.create_admin
```

### 5. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Production Deployment

### 1. Server Setup

#### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt install nginx -y
```

#### CentOS/RHEL
```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install docker-ce docker-ce-cli containerd.io -y
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Application Configuration

#### Environment Variables
```bash
# Production environment file
cat > .env.production << EOF
# Database
DATABASE_URL=postgresql://cvflow:secure_password@db:5432/cvflow_prod
POSTGRES_DB=cvflow_prod
POSTGRES_USER=cvflow
POSTGRES_PASSWORD=secure_password

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
ALLOWED_ORIGINS=["https://yourdomain.com"]
ALLOWED_HOSTS=["yourdomain.com", "www.yourdomain.com"]

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_TLS=true

# Redis (optional, for caching)
REDIS_URL=redis://redis:6379/0

# Monitoring
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
EOF
```

#### Docker Compose Production
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    networks:
      - cvflow-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ALGORITHM=${ALGORITHM}
      - ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}
      - REFRESH_TOKEN_EXPIRE_DAYS=${REFRESH_TOKEN_EXPIRE_DAYS}
      - BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS}
      - LOG_LEVEL=${LOG_LEVEL}
    volumes:
      - ./logs:/app/logs
    depends_on:
      - db
    restart: unless-stopped
    networks:
      - cvflow-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      - REACT_APP_API_URL=https://api.yourdomain.com
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - cvflow-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
    networks:
      - cvflow-network

volumes:
  postgres_data:

networks:
  cvflow-network:
    driver: bridge
```

### 3. Nginx Configuration

#### Main Configuration
```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    # Upstream servers
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # Main HTTPS server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Login rate limiting
        location /api/v1/auth/login {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend routes
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files
        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

### 4. SSL Certificate Setup

#### Using Let's Encrypt
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### Using Custom Certificate
```bash
# Create SSL directory
sudo mkdir -p /etc/nginx/ssl

# Copy your certificates
sudo cp your-cert.pem /etc/nginx/ssl/cert.pem
sudo cp your-key.pem /etc/nginx/ssl/key.pem
sudo chmod 600 /etc/nginx/ssl/key.pem
```

### 5. Database Setup

#### PostgreSQL Configuration
```bash
# Create database user
sudo -u postgres psql
CREATE USER cvflow WITH PASSWORD 'secure_password';
CREATE DATABASE cvflow_prod OWNER cvflow;
GRANT ALL PRIVILEGES ON DATABASE cvflow_prod TO cvflow;
\q

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

#### Database Backup
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="cvflow_backup_$DATE.sql"

docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U cvflow cvflow_prod > $BACKUP_DIR/$BACKUP_FILE

# Compress backup
gzip $BACKUP_DIR/$BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
EOF

chmod +x backup.sh

# Schedule backups
crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

### 6. Monitoring and Logging

#### Log Configuration
```bash
# Create log directory
sudo mkdir -p /var/log/cvflow
sudo chown -R $USER:$USER /var/log/cvflow

# Log rotation
sudo cat > /etc/logrotate.d/cvflow << 'EOF'
/var/log/cvflow/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF
```

#### Health Check Script
```bash
# Create health check script
cat > health_check.sh << 'EOF'
#!/bin/bash
API_URL="https://yourdomain.com/api/v1/auth/me"
HEALTH_URL="https://yourdomain.com/health"

# Check API health
if curl -f -s $HEALTH_URL > /dev/null; then
    echo "API is healthy"
else
    echo "API is down"
    # Send alert email
    echo "CVFlow API is down" | mail -s "API Alert" admin@yourdomain.com
fi
EOF

chmod +x health_check.sh

# Schedule health checks
crontab -e
# Add: */5 * * * * /path/to/health_check.sh
```

## Development Setup

### 1. Backend Development
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://cvflow:password@localhost:5432/cvflow_dev"
export SECRET_KEY="dev-secret-key"

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Development
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set environment variables
export REACT_APP_API_URL="http://localhost:8000/api/v1"

# Start development server
npm start
```

### 3. Database Development
```bash
# Start PostgreSQL with Docker
docker run --name cvflow-db -e POSTGRES_DB=cvflow_dev -e POSTGRES_USER=cvflow -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15-alpine

# Connect to database
docker exec -it cvflow-db psql -U cvflow -d cvflow_dev
```

## Testing

### 1. Backend Tests
```bash
# Run all tests
cd backend
python -m pytest

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/test_auth.py -v
```

### 2. Frontend Tests
```bash
# Run all tests
cd frontend
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- --testPathPattern=auth.test.js
```

### 3. Integration Tests
```bash
# Run integration tests
cd backend
python -m pytest tests/test_integration_*.py -v

# Run with Docker
docker-compose exec backend python -m pytest tests/test_integration_*.py -v
```

## Maintenance

### 1. Regular Updates
```bash
# Update dependencies
cd backend
pip install --upgrade -r requirements.txt

cd frontend
npm update

# Update Docker images
docker-compose pull
docker-compose up -d
```

### 2. Database Maintenance
```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Rollback migration
docker-compose exec backend alembic downgrade -1
```

### 3. Log Management
```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Clean old logs
docker system prune -f
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check database status
docker-compose ps db

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

#### 2. Authentication Issues
```bash
# Check JWT secret key
echo $SECRET_KEY

# Verify token expiration settings
grep -r "ACCESS_TOKEN_EXPIRE" backend/

# Test authentication endpoint
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

#### 3. CORS Issues
```bash
# Check CORS configuration
grep -r "CORS" backend/app/core/

# Verify allowed origins
echo $BACKEND_CORS_ORIGINS
```

#### 4. Performance Issues
```bash
# Check resource usage
docker stats

# Check database performance
docker-compose exec db psql -U cvflow -d cvflow_prod -c "SELECT * FROM pg_stat_activity;"

# Check application logs
tail -f logs/backend.log
```

### Support

For additional support:
- Check the project documentation
- Review the API documentation
- Contact the development team
- Create an issue in the project repository

## Security Considerations

### 1. Environment Variables
- Never commit `.env` files to version control
- Use strong, unique passwords
- Rotate secrets regularly
- Use environment-specific configurations

### 2. Database Security
- Use strong database passwords
- Enable SSL connections
- Regular backups
- Monitor database access

### 3. Application Security
- Keep dependencies updated
- Use HTTPS in production
- Implement rate limiting
- Monitor for security vulnerabilities

### 4. Server Security
- Keep OS updated
- Use firewall rules
- Monitor system logs
- Regular security audits









