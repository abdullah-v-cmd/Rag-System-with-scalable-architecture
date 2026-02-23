# 🚀 Deployment Guide

## Quick Start with Docker

### 1. Prerequisites
- Docker and Docker Compose installed
- OpenAI API key

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/abdullah-v-cmd/Rag-System-with-scalable-architecture.git
cd Rag-System-with-scalable-architecture

# Setup environment
./scripts/setup.sh

# Edit .env and add your OpenAI API key
nano .env
# or
vim .env
```

### 3. Start Services
```bash
./scripts/start.sh
```

### 4. Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## GitHub Actions CI/CD

The `.github/workflows/ci-cd.yml` file is included in the repository but may need manual addition to your GitHub repo due to workflow permissions.

**To add the workflow manually:**
1. Go to your GitHub repository
2. Navigate to `.github/workflows/`
3. Create a new file `ci-cd.yml`
4. Copy the contents from `.github/workflows/ci-cd.yml` in this repo

**Required GitHub Secrets:**
- `OPENAI_API_KEY` - Your OpenAI API key for testing
- `DOCKER_USERNAME` - Docker Hub username (optional, for image publishing)
- `DOCKER_PASSWORD` - Docker Hub password (optional, for image publishing)

## Environment Variables

### Required
```env
OPENAI_API_KEY=your-api-key-here
```

### Optional (defaults provided)
```env
DATABASE_URL=postgresql://raguser:ragpassword@postgres:5432/ragdb
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
MAX_UPLOAD_SIZE_MB=50
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Production Deployment

### Option 1: Docker on VPS/Cloud Server

1. **Provision a server** (AWS EC2, DigitalOcean, etc.)
2. **Install Docker and Docker Compose**
3. **Clone repository and setup**
4. **Update environment variables for production**
5. **Start services**

### Option 2: Kubernetes

A Kubernetes deployment configuration can be created with:
- Deployments for backend, frontend, celery workers
- Services for backend, frontend
- StatefulSets for PostgreSQL, Redis
- ConfigMaps for configuration
- Secrets for sensitive data

### Option 3: Cloud Platforms

**AWS:**
- ECS/Fargate with ECR
- RDS for PostgreSQL
- ElastiCache for Redis
- Application Load Balancer

**Google Cloud:**
- Cloud Run for containers
- Cloud SQL for PostgreSQL
- Memorystore for Redis

**Azure:**
- Container Instances
- Azure Database for PostgreSQL
- Azure Cache for Redis

## Monitoring

### Logs
```bash
# View all logs
./scripts/logs.sh

# View specific service logs
./scripts/logs.sh backend
./scripts/logs.sh frontend
./scripts/logs.sh postgres
./scripts/logs.sh redis
./scripts/logs.sh celery_worker
```

### Health Check
```bash
curl http://localhost:8000/health
```

### Statistics
```bash
curl http://localhost:8000/stats
```

## Scaling

### Horizontal Scaling
```bash
# Scale Celery workers
docker-compose up -d --scale celery_worker=3
```

### Vertical Scaling
Update Docker Compose resource limits:
```yaml
celery_worker:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
```

## Backup

### Database Backup
```bash
docker-compose exec postgres pg_dump -U raguser ragdb > backup.sql
```

### Restore Database
```bash
docker-compose exec -T postgres psql -U raguser ragdb < backup.sql
```

## Security Checklist

- [ ] Change default database passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS in production
- [ ] Use environment-specific .env files
- [ ] Enable firewall rules
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Implement rate limiting (already included)
- [ ] Add authentication (future feature)

## Troubleshooting

### Services won't start
```bash
docker-compose down -v
docker-compose up -d
```

### Port conflicts
Check if ports 3000, 8000, 5432, 6379 are available:
```bash
lsof -i :3000
lsof -i :8000
lsof -i :5432
lsof -i :6379
```

### Database connection issues
```bash
docker-compose logs postgres
docker-compose exec postgres psql -U raguser -d ragdb
```

### OpenAI API errors
- Verify API key in .env
- Check API quota and billing
- Review backend logs

## Performance Tuning

### PostgreSQL
- Increase `shared_buffers`
- Adjust `work_mem`
- Tune `effective_cache_size`

### Redis
- Set `maxmemory` policy
- Enable persistence if needed

### Celery
- Adjust worker concurrency
- Configure task time limits
- Set up multiple queues for different task types

## Cost Optimization

1. **OpenAI API**: Use caching (already implemented) to reduce API calls
2. **Infrastructure**: Right-size your servers
3. **Database**: Use connection pooling (already implemented)
4. **Redis**: Set appropriate TTL for cached data

## Support

- GitHub Issues: https://github.com/abdullah-v-cmd/Rag-System-with-scalable-architecture/issues
- API Documentation: http://localhost:8000/docs
