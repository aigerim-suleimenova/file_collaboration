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

##  Authentication

The system uses JWT-based authentication with the following flow:

1. **User Registration**: POST `/api/register` with email/password
2. **User Login**: POST `/api/login` to receive JWT token
3. **Token Validation**: Automatic validation on protected endpoints
4. **Password Security**: bcrypt hashing with salt rounds

##  API Endpoints

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


### Option 3: Cloud Platforms (Optional)

#### If you want cloud hosting later
- **AWS**: ECS, EKS, or EC2 with RDS
- **GCP**: Cloud Run or GKE
- **Azure**: Container Instances or AKS
- **DigitalOcean**: App Platform or Droplets

## Performance & Scalability

### Current Optimizations
- **Async/await patterns** in FastAPI for concurrent requests
- **Connection pooling** for database connections
- **CRDT efficiency** for real-time collaboration
- **Vite build optimization** for frontend assets
- **Content validation** prevents data corruption and improves reliability
- **Efficient WebSocket handling** with proper connection management


## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- **Yjs team** for the excellent CRDT framework
- **FastAPI community** for the high-performance web framework
- **Vue.js team** for the progressive JavaScript framework
- **Quill.js** for the rich text editor


