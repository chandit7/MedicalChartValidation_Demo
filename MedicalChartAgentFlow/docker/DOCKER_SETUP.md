# 🐳 Docker Setup Guide - Medical Chart Validation System

Complete guide for running the Medical Chart Validation System in Docker containers.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Volume Management](#volume-management)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)

---

## 🎯 Prerequisites

### Required Software

1. **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
   - Version: 20.10.0 or higher
   - Download: https://www.docker.com/products/docker-desktop

2. **Docker Compose**
   - Version: 2.0.0 or higher
   - Included with Docker Desktop
   - Linux: `sudo apt-get install docker-compose-plugin`

### System Requirements

- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 5GB free space
- **OS**: Windows 10/11, macOS 10.15+, or Linux

### Verify Installation

```bash
# Check Docker version
docker --version
# Expected: Docker version 20.10.0 or higher

# Check Docker Compose version
docker compose version
# Expected: Docker Compose version v2.0.0 or higher

# Test Docker installation
docker run hello-world
```

---

## 🚀 Quick Start

### Step 1: Clone and Navigate

```bash
cd Agentic_AI_Demo_Challenge
```

### Step 2: Create Environment File

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings (optional)
# For basic usage, the defaults work fine
# For AI analytics, add your Groq API key
```

### Step 3: Create Data Directory

```bash
# Create directory for persistent database
mkdir -p data
```

### Step 4: Build and Start

```bash
# Build and start the containers
docker compose up -d

# View logs
docker compose logs -f medchart-app
```

### Step 5: Access the Application

Open your browser and navigate to:
```
http://localhost:8501
```

You should see the Medical Chart Validation System interface!

### Step 6: Stop the Application

```bash
# Stop containers (keeps data)
docker compose down

# Stop and remove volumes (deletes data)
docker compose down -v
```

---

## ⚙️ Configuration

### Environment Variables

Edit `.env` file to customize:

```bash
# Required for AI Analytics (optional)
GROQ_API_KEY=your_groq_api_key_here

# Database path (inside container)
DB_PATH=/app/data/medchart.db

# Streamlit settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Port Configuration

To change the exposed port, edit `docker-compose.yml`:

```yaml
services:
  medchart-app:
    ports:
      - "8080:8501"  # Change 8080 to your desired port
```

### Resource Limits

Add resource constraints in `docker-compose.yml`:

```yaml
services:
  medchart-app:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

---

## 💾 Volume Management

### Understanding Volumes

The application uses two volume mounts:

1. **Database Volume** (`./data:/app/data`)
   - Stores `medchart.db` SQLite database
   - Persists validation results
   - Survives container restarts

2. **Sample Data Volume** (`./medchart_demo/sample_data:/app/sample_data:ro`)
   - Read-only mount of test data
   - Contains 5 sample charts and gap report

### Backup Database

```bash
# Create backup
docker compose exec medchart-app sqlite3 /app/data/medchart.db ".backup /app/data/backup.db"

# Copy backup to host
docker cp medchart-app:/app/data/backup.db ./data/backup-$(date +%Y%m%d).db
```

### Restore Database

```bash
# Copy backup to container
docker cp ./data/backup.db medchart-app:/app/data/medchart.db

# Restart container
docker compose restart medchart-app
```

### Clear All Data

```bash
# Stop containers
docker compose down

# Remove data directory
rm -rf data/

# Recreate and restart
mkdir data
docker compose up -d
```

---

## 🏭 Production Deployment

### Using Production Configuration

```bash
# Build for production
docker compose -f docker-compose.prod.yml build

# Start production stack
docker compose -f docker-compose.prod.yml up -d

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

### Production Features

- **Resource Limits**: CPU and memory constraints
- **Restart Policies**: Auto-restart on failure
- **Health Checks**: Container monitoring
- **Logging**: Structured JSON logs with rotation
- **Named Volumes**: Better data management
- **Nginx Proxy**: SSL/TLS termination (optional)

### SSL/TLS Setup (Optional)

1. Create nginx configuration directory:
```bash
mkdir -p nginx/ssl
```

2. Generate SSL certificates:
```bash
# Self-signed (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem

# Production: Use Let's Encrypt or your certificate provider
```

3. Create `nginx/nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream medchart {
        server medchart-app:8501;
    }

    server {
        listen 80;
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl;
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://medchart;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

4. Uncomment nginx service in `docker-compose.prod.yml`

---

## 🔧 Troubleshooting

### Container Won't Start

**Problem**: Container exits immediately

**Solution**:
```bash
# Check logs
docker compose logs medchart-app

# Check if port is in use
netstat -ano | findstr :8501  # Windows
lsof -i :8501                 # Mac/Linux

# Try different port
# Edit docker-compose.yml and change port mapping
```

### Database Initialization Failed

**Problem**: "Database initialization failed" in logs

**Solution**:
```bash
# Remove existing database
rm -rf data/medchart.db

# Restart container
docker compose restart medchart-app

# Check permissions
ls -la data/
```

### Sample Data Not Found

**Problem**: "Sample file not found" error

**Solution**:
```bash
# Verify sample data exists
ls -la medchart_demo/sample_data/

# Check volume mount in docker-compose.yml
docker compose config | grep sample_data

# Restart with fresh mount
docker compose down
docker compose up -d
```

### Health Check Failing

**Problem**: Container marked as unhealthy

**Solution**:
```bash
# Check health status
docker inspect medchart-app | grep -A 10 Health

# Test health endpoint manually
docker compose exec medchart-app curl http://localhost:8501/_stcore/health

# Increase start period in docker-compose.yml
healthcheck:
  start_period: 60s  # Increase if needed
```

### Out of Memory

**Problem**: Container crashes with OOM error

**Solution**:
```bash
# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G  # Increase from 2G

# Or use production config with proper limits
docker compose -f docker-compose.prod.yml up -d
```

### Permission Denied Errors

**Problem**: Cannot write to database

**Solution**:
```bash
# Fix permissions on host
chmod -R 777 data/

# Or run container as root (not recommended)
# Add to docker-compose.yml:
user: "0:0"
```

---

## 🎓 Advanced Usage

### Running Multiple Instances

```bash
# Start with custom project name
docker compose -p medchart-dev up -d

# Start another instance on different port
# Edit docker-compose.yml to use port 8502
docker compose -p medchart-test up -d
```

### Development Mode with Live Reload

```bash
# Mount source code for live editing
docker compose -f docker-compose.yml \
  -v $(pwd)/medchart_demo:/app \
  up -d
```

### Accessing Container Shell

```bash
# Open bash shell in container
docker compose exec medchart-app bash

# Run Python commands
docker compose exec medchart-app python -c "import db; print(db.get_summary())"

# Check database
docker compose exec medchart-app sqlite3 /app/data/medchart.db "SELECT COUNT(*) FROM results;"
```

### Viewing Real-time Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f medchart-app

# Last 100 lines
docker compose logs --tail=100 medchart-app

# With timestamps
docker compose logs -f -t medchart-app
```

### Building Custom Image

```bash
# Build with custom tag
docker build -t medchart:custom .

# Build with build arguments
docker build \
  --build-arg VERSION=2.0.0 \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  -t medchart:2.0.0 .

# Push to registry
docker tag medchart:2.0.0 your-registry/medchart:2.0.0
docker push your-registry/medchart:2.0.0
```

### Docker Compose Commands Reference

```bash
# Build images
docker compose build

# Start services
docker compose up -d

# Stop services
docker compose stop

# Restart services
docker compose restart

# Remove containers
docker compose down

# Remove containers and volumes
docker compose down -v

# View running containers
docker compose ps

# View logs
docker compose logs

# Execute command in container
docker compose exec medchart-app <command>

# Scale services (if configured)
docker compose up -d --scale medchart-app=3
```

---

## 📊 Monitoring and Maintenance

### Health Monitoring

```bash
# Check container health
docker compose ps

# Detailed health info
docker inspect medchart-app --format='{{json .State.Health}}' | jq

# Monitor resource usage
docker stats medchart-app
```

### Log Management

```bash
# View log size
docker compose exec medchart-app du -sh /var/log

# Rotate logs manually
docker compose exec medchart-app logrotate /etc/logrotate.conf

# Clear Docker logs
truncate -s 0 $(docker inspect --format='{{.LogPath}}' medchart-app)
```

### Database Maintenance

```bash
# Vacuum database
docker compose exec medchart-app sqlite3 /app/data/medchart.db "VACUUM;"

# Check database integrity
docker compose exec medchart-app sqlite3 /app/data/medchart.db "PRAGMA integrity_check;"

# Get database size
docker compose exec medchart-app sqlite3 /app/data/medchart.db "SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();"
```

---

## 🔐 Security Best Practices

1. **Never commit `.env` files** with real API keys
2. **Use Docker secrets** for sensitive data in production
3. **Run as non-root user** (already configured)
4. **Keep images updated**: `docker compose pull && docker compose up -d`
5. **Use SSL/TLS** in production with nginx proxy
6. **Limit resource usage** to prevent DoS
7. **Regular backups** of database volume
8. **Monitor logs** for suspicious activity

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Streamlit Docker Guide](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)
- [SQLite Docker Best Practices](https://www.sqlite.org/docker.html)

---

## 🆘 Getting Help

If you encounter issues:

1. Check this troubleshooting guide
2. Review container logs: `docker compose logs -f`
3. Verify configuration: `docker compose config`
4. Check Docker status: `docker info`
5. Consult main README.md for application-specific help

---

**Made with ❤️ for containerized deployment**