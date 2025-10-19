# Deployment Guide

This guide covers deploying the Project Management System to a production VM.

## 🎯 Target Environment

- **VM IP**: 18.234.41.103
- **Backend Port**: 8010
- **Frontend Port**: 3000
- **Protocol**: HTTP

## 📋 Prerequisites

- VM with Docker and Docker Compose installed
- SSH access to the VM
- Supabase project with credentials
- Git access to the repository

## 🚀 Deployment Steps

### 1. Connect to VM

```bash
# SSH into your VM
ssh user@18.234.41.103

# Or if using a specific key
ssh -i /path/to/your/key.pem user@18.234.41.103
```

### 2. Clone Repository

```bash
# Clone the project repository
git clone https://github.com/Gabriel-Kelvin/Project-Management.git
cd Project-Management
```

### 3. Environment Configuration

```bash
# Copy environment example files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Edit backend environment file
nano backend/.env
```

Add your Supabase credentials to `backend/.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
BACKEND_PORT=8010
BACKEND_HOST=0.0.0.0
CORS_ORIGINS=http://18.234.41.103:3000,http://localhost:3000
```

### 4. Deploy Application

```bash
# Build and start all services
docker-compose up --build -d

# Check if containers are running
docker-compose ps

# View logs if needed
docker-compose logs -f
```

### 5. Verify Deployment

```bash
# Test backend health endpoint
curl http://18.234.41.103:8010/health

# Expected response:
# {"status": "healthy", "api": "project_management", "version": "1.0.0"}

# Test frontend health endpoint
curl http://18.234.41.103:3000/health

# Expected response:
# healthy
```

### 6. Access Application

- **Frontend**: http://18.234.41.103:3000
- **Backend API**: http://18.234.41.103:8010
- **API Documentation**: http://18.234.41.103:8010/docs
- **ReDoc Documentation**: http://18.234.41.103:8010/redoc

## 🔧 Docker Commands

### Basic Operations

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Development Commands

```bash
# Rebuild and start
docker-compose up --build -d

# Force rebuild without cache
docker-compose build --no-cache
docker-compose up -d

# Scale services (if needed)
docker-compose up -d --scale backend=2
```

### Debugging Commands

```bash
# Execute commands in running container
docker-compose exec backend bash
docker-compose exec frontend sh

# Check container status
docker-compose ps

# View resource usage
docker stats

# Check container logs
docker logs project-management-backend
docker logs project-management-frontend
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
sudo netstat -tulpn | grep :8010
sudo netstat -tulpn | grep :3000

# Kill process if needed
sudo kill -9 <PID>
```

#### 2. Container Won't Start
```bash
# Check container logs
docker-compose logs backend
docker-compose logs frontend

# Check if environment variables are set
docker-compose exec backend env | grep SUPABASE
```

#### 3. Database Connection Issues
```bash
# Verify Supabase credentials
curl -H "apikey: YOUR_SUPABASE_KEY" \
     -H "Authorization: Bearer YOUR_SUPABASE_KEY" \
     https://your-project.supabase.co/rest/v1/
```

#### 4. CORS Issues
- Ensure `CORS_ORIGINS` includes your frontend URL
- Check that frontend is using the correct API URL
- Verify both services are running on the correct ports

### Health Check Failures

```bash
# Manual health checks
curl -f http://localhost:8010/health
curl -f http://localhost:3000/health

# Check if services are responding
docker-compose exec backend curl localhost:8010/health
docker-compose exec frontend curl localhost:3000/health
```

## 🔄 Updates and Maintenance

### Updating Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d
```

### Backup and Restore

```bash
# Backup environment files
cp backend/.env backend/.env.backup
cp frontend/.env frontend/.env.backup

# Backup logs (if needed)
docker-compose exec backend tar -czf /tmp/logs-backup.tar.gz /app/logs
```

### Monitoring

```bash
# Monitor resource usage
docker stats

# Monitor logs in real-time
docker-compose logs -f

# Check service health
watch -n 5 'curl -s http://18.234.41.103:8010/health'
```

## 🔒 Security Considerations

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 3000  # Frontend
sudo ufw allow 8010  # Backend
sudo ufw enable
```

### SSL/HTTPS Setup (Optional)

For production, consider setting up SSL certificates:

```bash
# Install certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Configure nginx with SSL (requires additional setup)
```

## 📊 Performance Optimization

### Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
  frontend:
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.25'
```

### Log Rotation

```bash
# Configure log rotation
sudo nano /etc/logrotate.d/docker-compose

# Add:
/var/lib/docker/containers/*/*.log {
  rotate 7
  daily
  compress
  size=1M
  missingok
  delaycompress
  copytruncate
}
```

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify environment variables are set correctly
3. Ensure all required ports are open
4. Check Supabase connection and credentials
5. Review the troubleshooting section above

For additional help, create an issue on the GitHub repository.

---

**Deployment completed successfully! 🎉**

Your Project Management System is now running at:
- Frontend: http://18.234.41.103:3000
- Backend: http://18.234.41.103:8010