# File Collaboration System

##  Features

### Core Functionality
- **Real-time Collaboration**: Multiple users can edit the same document simultaneously
- **Live Synchronization**: Changes appear instantly across all connected users
- **Conflict Resolution**: CRDT-based system automatically resolves editing conflicts
- **Rich Text Editing**: Full-featured Quill editor with formatting options (Fixed corruption issues)
- **User Authentication**: Secure JWT-based authentication system
- **File Management**: Create, read, update, and manage collaborative documents
- **Content Integrity**: Robust content validation and corruption prevention

##  Tech Stack

### Backend
- **Framework**: FastAPI (Python) - High-performance async web framework
- **Database**: PostgreSQL with SQLAlchemy 2.0 ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **Real-time**: WebSocket + Yjs CRDT framework
- **Migrations**: Alembic for database schema management
- **Validation**: Pydantic for data validation and serialization

### Frontend
- **Framework**: Vue 3 with Composition API
- **State Management**: Pinia for reactive state management
- **Rich Text Editor**: Quill.js with custom Vue 3 integration
- **Styling**: Tailwind CSS for utility-first styling
- **Build Tool**: Vite for lightning-fast development and building
- **Routing**: Vue Router for SPA navigation

### DevOps & Infrastructure
- **Containerization**: Docker + Docker Compose (Development & Production)
- **Database Admin**: pgAdmin for PostgreSQL management
- **Monitoring**: Health checks, structured logging, and deployment monitoring
- **Environment**: Configurable environment variables with validation
- **Networking**: Custom network configuration with security isolation
- **CI/CD**: GitHub Actions for automated deployment
- **Cloud Deployment**: GitHub Actions CI/CD with Docker deployment options

## 📋 Prerequisites

- Docker and Docker Compose
- Node.js 18+ and npm
- Python 3.9+
- Git


### Real-time Collaboration Flow
1. **User connects** to WebSocket endpoint
2. **Document changes** are captured by Quill editor
3. **Yjs CRDT** processes and transforms operations
4. **WebSocket** broadcasts changes to all connected users
5. **Automatic conflict resolution** ensures consistency
6. **Database persistence** maintains document state

### CI/CD Workflow
1. **Developer pushes code** to `main` branch
2. **GitHub Actions automatically triggers**:
   - Frontend build and test
   - Backend build and test
   - Docker image validation
3. **Build artifacts are stored** for 7 days
4. **Quality gates ensure** only working code passes
5. **Developer deploys locally** using Docker
6. **Application runs** on chosen infrastructure

##  Development

### Backend Development
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "description"
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Start collaboration server
npm run collab:server
```

### Database Operations
```bash
# Connect to database
docker exec -it file_collaboration_db psql -U postgres -d file_collaboration_db

# View logs
docker-compose logs db
docker-compose logs backend
```

### Infrastructure Options
```bash
# Local Development
docker-compose up -d

# Local Production
docker-compose -f docker-compose.prod.yml up -d

# Remote Server/VPS
ssh user@your-server
git clone <your-repo>
docker-compose -f docker-compose.prod.yml up -d

# Cloud Platform
# Deploy to AWS, GCP, Azure, or DigitalOcean using the same Docker images
```

## 🔐 Authentication

The system uses JWT-based authentication with the following flow:

1. **User Registration**: POST `/api/register` with email/password
2. **User Login**: POST `/api/login` to receive JWT token
3. **Token Validation**: Automatic validation on protected endpoints
4. **Password Security**: bcrypt hashing with salt rounds

## 📊 API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User authentication
- `GET /api/users/me` - Get current user info

### Files
- `GET /api/files` - List user's files
- `POST /api/files` - Create new file
- `GET /api/files/{id}` - Get file content
- `PUT /api/files/{id}` - Update file content
- `DELETE /api/files/{id}` - Delete file

### WebSocket
- `ws://localhost:8000/ws` - Real-time collaboration endpoint

## 🧪 Testing

### Backend Testing
```bash
cd backend
# Run tests (when implemented)
pytest

# Check database connection
python check_db.py

# Verify configuration
python check_config.py
```

### Frontend Testing
```bash
cd frontend
# Lint code
npm run lint

# Build verification
npm run build
```

## 🚀 Deployment Options

### Option 1: GitHub Actions + Local Docker (Recommended)

#### What GitHub Actions Does
- **Automated Testing**: Runs tests on every push
- **Build Validation**: Ensures code compiles correctly
- **Docker Testing**: Validates Docker image builds
- **Artifact Storage**: Stores build outputs for 7 days
- **Quality Gates**: Prevents broken code from being deployed

#### Local Docker Deployment
```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.prod.yml up -d

# Or use the automated deployment script
./deploy.sh
```

### Option 2: Self-Hosted Server/VPS

#### Production Considerations
- **Environment Variables**: Configure production database credentials
- **SSL/TLS**: Enable HTTPS for production
- **Database Backups**: Implement regular PostgreSQL backups
- **Monitoring**: Add Sentry or similar error tracking
- **Load Balancing**: Consider reverse proxy for multiple instances

#### Server Deployment
1. **Choose your server**: DigitalOcean ($5/month), AWS EC2, GCP Compute Engine
2. **Install Docker**: `curl -fsSL https://get.docker.com | sh`
3. **Clone your repo**: `git clone <your-repo>`
4. **Deploy**: `docker-compose -f docker-compose.prod.yml up -d`

### Option 3: Cloud Platforms (Optional)

#### If you want cloud hosting later
- **AWS**: ECS, EKS, or EC2 with RDS
- **GCP**: Cloud Run or GKE
- **Azure**: Container Instances or AKS
- **DigitalOcean**: App Platform or Droplets

## 💰 Cost Estimation

### GitHub Actions + Local Docker (Recommended)
- **GitHub Actions**: $0/month (2000 minutes free)
- **Local Docker**: $0/month (runs on your machine)
- **Total**: $0/month

### Self-Hosted Server/VPS
- **VPS/Server**: $5-50/month (DigitalOcean, AWS, GCP)
- **Domain + SSL**: $10-20/year
- **Total**: $5-50/month

### Cloud Platforms (Optional)
- **AWS/GCP/Azure**: $10-100/month (depending on usage)
- **Managed Services**: $20-200/month (depending on scale)


## 🔍 Troubleshooting

### Common Issues

#### 1. **Database Connection Failed**
   - Check if PostgreSQL container is running
   - Verify environment variables
   - Check container logs: `docker-compose logs db`

#### 2. **WebSocket Connection Issues**
   - Ensure backend is running on port 8000
   - Check CORS configuration
   - Verify WebSocket endpoint in frontend

#### 3. **Frontend Build Errors**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility
   - Verify Vite configuration

#### 4. **QuillEditor Content Issues** (Fixed in Latest Version)
   - Content corruption and duplication issues have been resolved
   - HTML entities are now properly cleaned
   - Content validation prevents corrupted data

#### 5. **Deployment Issues**
   - Check GitHub Actions logs for deployment failures
   - Verify environment variables in your deployment platform
   - Check service health endpoints

### Debug Commands

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f [service_name]

# Check GitHub Actions
# Go to Actions tab in your GitHub repository

# Check deployment status
echo "Check GitHub Actions workflow status"

# Check Railway deployment
railway logs
```

## 📈 Performance & Scalability

### Current Optimizations
- **Async/await patterns** in FastAPI for concurrent requests
- **Connection pooling** for database connections
- **CRDT efficiency** for real-time collaboration
- **Vite build optimization** for frontend assets
- **Content validation** prevents data corruption and improves reliability
- **Efficient WebSocket handling** with proper connection management

### Future Improvements
- **Redis caching** for session management
- **CDN integration** for static assets
- **Horizontal scaling** with multiple backend instances
- **Database read replicas** for improved read performance
- **Edge computing** for global collaboration performance
- **Advanced monitoring** with Prometheus and Grafana

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Yjs team** for the excellent CRDT framework
- **FastAPI community** for the high-performance web framework
- **Vue.js team** for the progressive JavaScript framework
- **Quill.js** for the rich text editor

## 📚 Additional Resources

### Documentation
- **API Documentation**: Available at `/docs` endpoint when running
- **Deployment Guide**: See `DEPLOYMENT_SETUP.md` for detailed setup
- **Docker Guide**: See `DOCKER_README.md` for Docker-specific instructions
- **Testing Guide**: See `TESTING_README.md` for testing procedures

### Configuration Files
- **Frontend**: `frontend/Dockerfile.prod` for Docker deployment
- **Backend**: `railway.json` for Railway deployment
- **Production**: `docker-compose.prod.yml` for production Docker setup
- **Nginx**: `nginx.conf` for reverse proxy configuration

## 📞 Support

For questions or support:
- **Create an issue** in the repository
- **Check the troubleshooting section** above
- **Review the API documentation** at `/docs` endpoint
- **Check deployment logs** in GitHub Actions
- **Verify service health** at health check endpoints

## 🎯 Project Status

- **✅ Core Features**: Complete and stable
- **✅ Real-time Collaboration**: Working with Yjs CRDT
- **✅ QuillEditor**: Fixed content corruption issues
- **✅ Authentication**: JWT-based with security best practices
- **✅ Deployment**: Multiple options available
- **✅ Documentation**: Comprehensive guides included
- **🔄 Continuous Improvement**: Regular updates and bug fixes

---

**Built with ❤️ using modern web technologies for real-time collaboration**

**Latest Update**: QuillEditor content corruption fixed, multiple deployment options added, production-ready configurations implemented.

## 📋 Table of Contents

- [✨ What's New](#-whats-new-latest-updates)
- [🚀 Features](#-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [📋 Prerequisites](#-prerequisites)
- [🚀 Quick Start](#-quick-start)
- [🏗️ Architecture](#️-architecture)
- [🔧 Development](#-development)
- [🔐 Authentication](#-authentication)
- [📊 API Endpoints](#-api-endpoints)
- [🧪 Testing](#-testing)
- [🚀 Deployment Options](#-deployment-options)
- [🔍 Troubleshooting](#-troubleshooting)
- [📈 Performance & Scalability](#-performance--scalability)
- [🤝 Contributing](#-contributing)
- [📝 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)
- [📚 Additional Resources](#-additional-resources)
- [📞 Support](#-support)
- [🎯 Project Status](#-project-status)
