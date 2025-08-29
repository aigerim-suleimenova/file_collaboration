# Docker Setup for File Collaboration Project

This project includes a complete Docker setup with three services: frontend, backend, and PostgreSQL database.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (usually comes with Docker Desktop)

## Services Overview

### 1. Database Service (`db`)
- **Image**: PostgreSQL 15 Alpine
- **Port**: 5432 (host) → 5432 (container)
- **Data Persistence**: PostgreSQL data is stored in a named volume
- **Health Check**: Ensures database is ready before starting other services

### 2. Backend Service (`backend`)
- **Image**: Custom Python 3.11 with FastAPI
- **Port**: 8000 (host) → 8000 (container)
- **Dependencies**: Waits for database to be healthy
- **Hot Reload**: Development mode with auto-reload enabled
- **Volume Mounting**: Source code is mounted for live development

### 3. Frontend Service (`frontend`)
- **Image**: Custom Node.js 18 Alpine with Vue.js
- **Port**: 3000 (host) → 3000 (container)
- **Dependencies**: Waits for backend to start
- **Hot Reload**: Development mode with Vite hot reload
- **Volume Mounting**: Source code is mounted for live development

## Quick Start

### 1. Build and Start All Services
```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

### 2. View Logs
```bash
# View all services logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### 3. Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: This will delete all data)
docker-compose down -v
```

## Development Workflow

### Backend Development
- The backend service runs with hot reload enabled
- Changes to Python files will automatically restart the server
- Database migrations can be run inside the container:
  ```bash
  docker-compose exec backend alembic upgrade head
  ```

### Frontend Development
- The frontend service runs with Vite hot reload
- Changes to Vue files will automatically refresh the browser
- The development server is accessible at `http://localhost:3000`

### Database Access
- Connect to PostgreSQL using any database client:
  - Host: `localhost`
  - Port: `5432`
  - Database: `file_collaboration_db`
  - Username: `postgres`
  - Password: `12345678`

## Service Management

### Individual Service Commands
```bash
# Start only the database
docker-compose up db

# Start backend and database
docker-compose up db backend

# Rebuild and restart a specific service
docker-compose up --build backend

# Stop a specific service
docker-compose stop frontend
```

### Service Status
```bash
# Check service status
docker-compose ps

# Check service health
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
```

## Environment Variables

### Backend Environment Variables
- `POSTGRES_SERVER`: Database host (set to `db` in Docker)
- `POSTGRES_PORT`: Database port (5433)
- `POSTGRES_USER`: Database username (postgres)
- `POSTGRES_PASSWORD`: Database password (12345678)
- `POSTGRES_DB`: Database name (file_collaboration_db)
- `FRONTEND_HOST`: Frontend URL for CORS
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins
- `ENVIRONMENT`: Environment mode (local)

### Frontend Environment Variables
- `VITE_API_BASE_URL`: Backend API base URL

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :8000
   lsof -i :3000
   lsof -i :5432

   # Stop conflicting services or change ports in docker-compose.yml
   ```

2. **Database Connection Issues**
   ```bash
   # Check database logs
   docker-compose logs db

   # Check database health
   docker-compose exec db pg_isready -U postgres
   ```

3. **Build Failures**
   ```bash
   # Clean up and rebuild
   docker-compose down
   docker system prune -f
   docker-compose up --build
   ```

4. **Permission Issues**
   ```bash
   # Fix file permissions if needed
   sudo chown -R $USER:$USER .
   ```

### Reset Everything
```bash
# Stop all services and remove everything
docker-compose down -v
docker system prune -af
docker volume prune -f

# Rebuild from scratch
docker-compose up --build
```

## Production Considerations

For production deployment, consider:

1. **Security**: Change default passwords and secrets
2. **Environment Variables**: Use `.env` files or secrets management
3. **Volumes**: Use named volumes for data persistence
4. **Networks**: Restrict network access as needed
5. **Health Checks**: Implement proper health check endpoints
6. **Logging**: Configure proper logging and monitoring
7. **Backup**: Implement database backup strategies

## File Structure

```
.
├── docker-compose.yml          # Main Docker Compose file
├── backend/
│   ├── Dockerfile             # Backend service Dockerfile
│   ├── .dockerignore          # Backend Docker ignore file
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── Dockerfile             # Frontend service Dockerfile
│   ├── .dockerignore          # Frontend Docker ignore file
│   └── package.json           # Node.js dependencies
└── DOCKER_README.md           # This file
```

## Support

If you encounter issues with the Docker setup:

1. Check the service logs: `docker-compose logs [service_name]`
2. Verify Docker and Docker Compose versions
3. Ensure all required ports are available
4. Check the troubleshooting section above
