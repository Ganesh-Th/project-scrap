# Production Deployment Guide

This guide covers deploying the AI Review Intelligence System to production.

## Prerequisites

- Linux server (Ubuntu 20.04+ recommended)
- Docker and Docker Compose installed
- Domain name (optional, for HTTPS)
- At least 2GB RAM, 2 CPU cores

## Quick Deployment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Ganesh-Th/project-scrap.git
   cd project-scrap
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   nano .env  # Edit with production values
   ```

3. **Start services**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

## Production Configuration

### Environment Variables

Create a `.env` file with production values:

```bash
# SerpAPI - Get from https://serpapi.com/
SERPAPI_KEY=your_production_key

# Database - Use strong passwords
POSTGRES_DB=review_intelligence
POSTGRES_USER=postgres
POSTGRES_PASSWORD=strong_secure_password_here

# Ports (if customizing)
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

### Docker Compose Production Override

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    restart: always
    environment:
      - DEBUG=false
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

  celery_worker:
    restart: always
    command: celery -A app.celery_app worker --concurrency=4 --loglevel=warning

  frontend:
    restart: always
    command: npm start

  postgres:
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups

  redis:
    restart: always
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Nginx Reverse Proxy

Install and configure Nginx:

```bash
sudo apt-get install nginx
```

Create `/etc/nginx/sites-available/review-intelligence`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # API Docs
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/review-intelligence /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL/HTTPS with Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Systemd Service

Create `/etc/systemd/system/review-intelligence.service`:

```ini
[Unit]
Description=AI Review Intelligence System
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/project-scrap
ExecStart=/usr/local/bin/docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose down
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable review-intelligence
sudo systemctl start review-intelligence
sudo systemctl status review-intelligence
```

## Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Service status
docker-compose ps

# Logs
docker-compose logs -f --tail=100
```

### Log Rotation

Create `/etc/logrotate.d/review-intelligence`:

```
/var/lib/docker/containers/*/*.log {
  rotate 7
  daily
  compress
  size=50M
  missingok
  delaycompress
  copytruncate
}
```

## Backup

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres review_intelligence > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U postgres review_intelligence < backup.sql
```

### Automated Backups

Add to crontab (`crontab -e`):

```bash
# Daily database backup at 2 AM
0 2 * * * cd /path/to/project-scrap && docker-compose exec -T postgres pg_dump -U postgres review_intelligence > /backups/db-$(date +\%Y\%m\%d).sql
```

## Security

### Firewall

```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### Environment Variables

- Never commit `.env` to version control
- Use strong passwords
- Rotate API keys regularly

### Database

- Use strong PostgreSQL password
- Don't expose port 5432 externally
- Regular backups

## Performance Tuning

### Database

```sql
-- PostgreSQL tuning (in postgresql.conf)
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
```

### Redis

```bash
# In redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
```

### Celery Workers

Scale workers based on load:

```bash
docker-compose up -d --scale celery_worker=4
```

## Troubleshooting

### Services won't start

```bash
# Check logs
docker-compose logs

# Restart specific service
docker-compose restart backend
```

### High memory usage

```bash
# Check resource usage
docker stats

# Reduce workers if needed
docker-compose up -d --scale celery_worker=2
```

### Database connection errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
docker-compose exec postgres psql -U postgres -c "SELECT 1"
```

## Scaling

### Horizontal Scaling

For high traffic:

1. **Load Balancer**: Use Nginx or HAProxy
2. **Multiple Backend Instances**: Scale FastAPI
3. **Multiple Workers**: Scale Celery workers
4. **Database**: PostgreSQL replication
5. **Redis**: Redis Cluster

### Monitoring Tools

- **Prometheus + Grafana**: Metrics
- **Sentry**: Error tracking
- **ELK Stack**: Log aggregation

## Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

## Maintenance

### Regular Tasks

- Monitor disk space
- Review logs for errors
- Update dependencies
- Backup database
- Test disaster recovery

### Health Monitoring

Set up monitoring with:
- Uptime monitoring (UptimeRobot, Pingdom)
- Application Performance Monitoring (New Relic, DataDog)
- Log aggregation (Papertrail, Loggly)
