# Deployment Guide

This guide covers various deployment options for the ArXiv Research Assistant.

## Prerequisites

- **System Requirements:**

  - 8GB+ RAM (16GB+ recommended)
  - 50GB+ storage (100GB+ for large datasets)
  - 4+ CPU cores
  - Optional: CUDA-compatible GPU

- **Software Requirements:**
  - Docker and Docker Compose
  - Python 3.10+ (for local deployment)
  - Git

## Local Development

### Quick Start

```bash
# Clone and setup
git clone https://github.com/your-username/ArXiv-Research-Assistant.git
cd ArXiv-Research-Assistant

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Start development server
python app.py web --debug
```

### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Setup Django
cd llm-integration/llmproject
python manage.py migrate
python manage.py collectstatic
python manage.py runserver
```

## Docker Deployment

### Development with Docker

```bash
# Start development environment
docker-compose --profile development up

# Access services:
# - Application: http://localhost:8000
# - Jupyter: http://localhost:8888
# - Redis: localhost:6379
```

### Production with Docker

```bash
# Build and start production services
docker-compose --profile production up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
```

### Docker Configuration

#### Environment Variables

Create a production `.env` file:

```bash
# Production environment
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
GROQ_API_KEY=your_production_groq_key
DJANGO_SECRET_KEY=your_secure_secret_key

# Database (if using external DB)
DATABASE_URL=postgresql://user:pass@db:5432/arxiv_db

# Storage
DATA_DIR=/app/data
USE_GPU=True  # If GPU available
```

#### Custom Docker Build

```bash
# Build custom image
docker build -t arxiv-assistant:custom .

# Run with custom configuration
docker run -d \
  --name arxiv-assistant \
  --env-file .env \
  -p 8000:8000 \
  -v ./data:/app/data \
  arxiv-assistant:custom
```

## Cloud Deployment

### AWS Deployment

#### Using EC2

1. **Launch EC2 Instance:**

   ```bash
   # Use Ubuntu 22.04 LTS
   # Instance type: t3.large or larger
   # Storage: 100GB+ EBS volume
   ```

2. **Setup Instance:**

   ```bash
   # Connect to instance
   ssh -i your-key.pem ubuntu@your-instance-ip

   # Install Docker
   sudo apt update
   sudo apt install docker.io docker-compose
   sudo usermod -aG docker ubuntu

   # Clone repository
   git clone https://github.com/your-username/ArXiv-Research-Assistant.git
   cd ArXiv-Research-Assistant

   # Setup environment
   cp .env.example .env
   # Edit .env with production values

   # Start services
   docker-compose --profile production up -d
   ```

3. **Configure Security Group:**
   - Allow inbound traffic on port 80 (HTTP)
   - Allow inbound traffic on port 443 (HTTPS)
   - Restrict SSH access (port 22) to your IP

#### Using ECS

1. **Build and Push Image:**

   ```bash
   # Build image
   docker build -t arxiv-assistant .

   # Tag for ECR
   docker tag arxiv-assistant:latest \
     your-account.dkr.ecr.region.amazonaws.com/arxiv-assistant:latest

   # Push to ECR
   docker push your-account.dkr.ecr.region.amazonaws.com/arxiv-assistant:latest
   ```

2. **Create ECS Task Definition:**
   ```json
   {
     "family": "arxiv-assistant",
     "cpu": "2048",
     "memory": "4096",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "arxiv-assistant",
         "image": "your-account.dkr.ecr.region.amazonaws.com/arxiv-assistant:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           { "name": "DJANGO_DEBUG", "value": "False" },
           { "name": "DJANGO_ALLOWED_HOSTS", "value": "your-domain.com" }
         ],
         "secrets": [
           {
             "name": "GROQ_API_KEY",
             "valueFrom": "arn:aws:secretsmanager:region:account:secret:groq-api-key"
           }
         ]
       }
     ]
   }
   ```

### Google Cloud Platform

#### Using Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/project-id/arxiv-assistant
gcloud run deploy arxiv-assistant \
  --image gcr.io/project-id/arxiv-assistant \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2
```

#### Using GKE

1. **Create cluster:**

   ```bash
   gcloud container clusters create arxiv-cluster \
     --num-nodes 3 \
     --machine-type n1-standard-4
   ```

2. **Deploy application:**
   ```yaml
   # kubernetes/deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: arxiv-assistant
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: arxiv-assistant
     template:
       metadata:
         labels:
           app: arxiv-assistant
       spec:
         containers:
           - name: arxiv-assistant
             image: gcr.io/project-id/arxiv-assistant
             ports:
               - containerPort: 8000
             env:
               - name: DJANGO_DEBUG
                 value: "False"
   ```

### Azure Deployment

#### Using Container Instances

```bash
# Create resource group
az group create --name arxiv-rg --location eastus

# Deploy container
az container create \
  --resource-group arxiv-rg \
  --name arxiv-assistant \
  --image your-registry/arxiv-assistant:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --environment-variables DJANGO_DEBUG=False
```

## Load Balancer and SSL

### Nginx Configuration

```nginx
# /etc/nginx/sites-available/arxiv-assistant
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/arxiv-assistant/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/arxiv-assistant/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Database Configuration

### PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE arxiv_db;
CREATE USER arxiv_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE arxiv_db TO arxiv_user;
\q

# Update .env
DATABASE_URL=postgresql://arxiv_user:secure_password@localhost/arxiv_db
```

### Redis Setup

```bash
# Install Redis
sudo apt install redis-server

# Configure Redis
sudo nano /etc/redis/redis.conf
# Set: maxmemory 512mb
# Set: maxmemory-policy allkeys-lru

# Restart Redis
sudo systemctl restart redis-server
```

## Monitoring and Logging

### Application Monitoring

```python
# Add to settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/arxiv-assistant/app.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Health Checks

```bash
# Health check endpoint
curl http://localhost:8000/health/

# Detailed status
curl http://localhost:8000/api/stats/
```

## Performance Optimization

### GPU Acceleration

```bash
# Install CUDA drivers
sudo apt install nvidia-driver-460 nvidia-cuda-toolkit

# Use GPU Docker runtime
# Edit /etc/docker/daemon.json
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}

# Restart Docker
sudo systemctl restart docker

# Run with GPU
docker run --gpus all your-image
```

### Scaling Considerations

1. **Horizontal Scaling:**

   - Use load balancer
   - Multiple app instances
   - Shared data storage

2. **Vertical Scaling:**

   - Increase CPU/memory
   - Use faster storage (SSD)
   - Optimize database queries

3. **Caching:**
   - Redis for session storage
   - CDN for static files
   - Database query caching

## Backup and Recovery

### Data Backup

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf "/backups/arxiv_data_$DATE.tar.gz" /app/data
pg_dump arxiv_db > "/backups/arxiv_db_$DATE.sql"
```

### Disaster Recovery

1. **Regular backups** of data directory and database
2. **Version control** for configuration
3. **Infrastructure as Code** for reproducible deployments
4. **Multi-region** deployment for high availability

## Troubleshooting

### Common Issues

1. **Memory issues:**

   ```bash
   # Check memory usage
   docker stats

   # Increase container memory
   docker run -m 8g your-image
   ```

2. **Permission issues:**

   ```bash
   # Fix file permissions
   sudo chown -R www-data:www-data /app/data
   sudo chmod -R 755 /app/data
   ```

3. **API key issues:**
   ```bash
   # Validate configuration
   python config/settings.py
   ```

### Logs and Debugging

```bash
# Application logs
docker-compose logs -f app

# System logs
sudo journalctl -u docker
sudo tail -f /var/log/nginx/error.log
```
