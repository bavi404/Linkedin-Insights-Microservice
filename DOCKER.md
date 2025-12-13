# Docker Deployment Guide

Production-ready Docker setup for LinkedIn Insights Microservice.

## Quick Start

### 1. Create Environment File

```bash
cp .docker.env.example .env
# Edit .env with your configuration
```

### 2. Build and Run

```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 3. Run Migrations

```bash
# Run migrations
docker-compose exec app alembic upgrade head
```

### 4. Check Status

```bash
# Check all services
docker-compose ps

# Check logs
docker-compose logs -f app
```

## Services

### Application Service (`app`)

- **Image**: Built from multi-stage Dockerfile
- **Port**: 8000 (configurable via `APP_PORT`)
- **Workers**: 4 uvicorn workers
- **Health Check**: `/health` endpoint

### Database Service (`db`)

- **Image**: PostgreSQL 15 Alpine
- **Port**: 5432 (configurable via `POSTGRES_PORT`)
- **Data Persistence**: `postgres_data` volume
- **Optimized**: Production-tuned PostgreSQL settings

### Redis Service (`redis`)

- **Image**: Redis 7 Alpine
- **Port**: 6379 (configurable via `REDIS_PORT`)
- **Data Persistence**: `redis_data` volume
- **Memory Policy**: `allkeys-lru` with 256MB limit

## Dockerfile Features

### Multi-Stage Build

1. **Builder Stage**: Installs Python dependencies
2. **Playwright Stage**: Installs Playwright and browsers
3. **Production Stage**: Minimal final image

### Security

- ✅ Non-root user (`appuser`)
- ✅ Minimal base image (Python slim)
- ✅ No unnecessary packages
- ✅ Proper file permissions

### Performance

- ✅ Layer caching optimization
- ✅ Virtual environment isolation
- ✅ Production uvicorn settings
- ✅ Health checks

## Environment Variables

All configuration is done via environment variables. See `.docker.env.example` for all available options.

### Required Variables

- `DATABASE_URL` (auto-generated from POSTGRES_*)
- `REDIS_URL` (auto-generated)

### Optional Variables

- `OPENAI_API_KEY` - For AI summary features
- `DEBUG` - Enable debug mode
- `LOG_LEVEL` - Logging level

## Volumes

### Application Volumes

- `./logs:/app/logs` - Application logs
- `./data:/app/data` - Application data

### Service Volumes

- `postgres_data` - PostgreSQL data persistence
- `redis_data` - Redis data persistence

## Networking

All services are on the `linkedin-insights-network` bridge network for secure internal communication.

## Health Checks

All services include health checks:

- **App**: HTTP health check on `/health`
- **Database**: `pg_isready` check
- **Redis**: `redis-cli ping` check

## Production Deployment

### Using Production Override

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Production Features

- Resource limits
- Log rotation
- Restart policies
- Multiple replicas (if using Docker Swarm)

### Scaling

```bash
# Scale app service
docker-compose up -d --scale app=3
```

## Maintenance

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f db
docker-compose logs -f redis
```

### Execute Commands

```bash
# Run migrations
docker-compose exec app alembic upgrade head

# Access database
docker-compose exec db psql -U postgres -d linkedin_insights

# Access Redis
docker-compose exec redis redis-cli

# Access app shell
docker-compose exec app /bin/bash
```

### Backup Database

```bash
# Backup
docker-compose exec db pg_dump -U postgres linkedin_insights > backup.sql

# Restore
docker-compose exec -T db psql -U postgres linkedin_insights < backup.sql
```

### Clean Up

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## Troubleshooting

### App Won't Start

1. Check database is healthy:
   ```bash
   docker-compose ps db
   ```

2. Check logs:
   ```bash
   docker-compose logs app
   ```

3. Verify environment variables:
   ```bash
   docker-compose exec app env | grep DATABASE
   ```

### Database Connection Issues

1. Verify database is running:
   ```bash
   docker-compose ps db
   ```

2. Check database logs:
   ```bash
   docker-compose logs db
   ```

3. Test connection:
   ```bash
   docker-compose exec app python -c "from linkedin_insights.db.base import engine; print('Connected')"
   ```

### Redis Connection Issues

1. Verify Redis is running:
   ```bash
   docker-compose ps redis
   ```

2. Test Redis connection:
   ```bash
   docker-compose exec redis redis-cli ping
   ```

### Playwright Issues

If Playwright browsers are missing:

```bash
# Rebuild with Playwright stage
docker-compose build --no-cache app
```

## Development

### Development Override

Create `docker-compose.dev.yml`:

```yaml
version: '3.8'
services:
  app:
    volumes:
      - .:/app
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
```

Run with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## Best Practices

1. **Never commit `.env` files** - Use `.docker.env.example`
2. **Use secrets management** - For production, use Docker secrets or external secret managers
3. **Regular backups** - Backup database volumes regularly
4. **Monitor resources** - Monitor CPU and memory usage
5. **Update regularly** - Keep base images updated
6. **Health checks** - All services should have health checks
7. **Logging** - Configure log rotation to prevent disk fill

## Security Checklist

- ✅ Non-root user in container
- ✅ Minimal base images
- ✅ No secrets in Dockerfile
- ✅ Environment-based configuration
- ✅ Network isolation
- ✅ Volume permissions
- ⚠️ Change default passwords
- ⚠️ Use secrets management in production
- ⚠️ Enable Redis password
- ⚠️ Restrict CORS origins in production

