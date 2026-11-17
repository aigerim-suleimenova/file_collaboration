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
1. **The editor connects** to `WS /api/v1/collab/{file_id}` on the FastAPI backend (the same service as the REST API). It passes `?token=<access token>` for the owner, or `?share_token=<share link token>` for a guest.
2. **The backend checks access before sending any document data.** The owner's access token or a matching, unexpired share token is accepted. Anything else is closed with `4001` (missing or invalid credentials), `4003` (no access to this file) or `4004` (no such file).
3. **Yjs CRDT sync** (`pycrdt-websocket` on the server, `y-websocket` + `y-quill` in the browser) merges concurrent edits with formatting intact. Yjs awareness shows each collaborator's labelled cursor.
4. **Saving:** the server saves the Yjs document state to Postgres (`file.yjs_state`) at most every 2 s while it is being edited, when the last editor leaves, and on shutdown. Reloads and restarts keep edits.
5. **First open:** a document with no collaborative state is filled once from its stored HTML, after the first sync.
6. **Safety:** typed markup stays text, and stored HTML is sanitized with DOMPurify before it is displayed.

### Known Limitations
- **Single backend process:** collaboration rooms live in memory, so the backend runs one uvicorn worker. Scaling out would need a shared message bus (for example Redis).
- **Share links grant edit access** until they expire (4 h by default). Access is checked when a connection opens, and there are no viewer/editor roles yet.
- **View mode shows the last saved HTML:** guest edits appear in the editor straight away, but in view mode only after the owner saves.
- **Two first openers:** if two people open a never-edited document at the same moment, its initial content can be loaded twice. This can only happen once per document.
- **Tokens travel in the WebSocket URL** (browsers can't set headers on WebSockets). They are redacted from server logs.

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
```

Real-time collaboration needs no separate server. The Vite dev server proxies `/api/v1/collab` to the backend. In production, set `VITE_COLLAB_WS=wss://<backend-host>/api/v1/collab` when the frontend is hosted separately from the backend.

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

### Real-time
- `WS /api/v1/collab/{file_id}?token=...|share_token=...` - Yjs document sync and presence (see Real-time Collaboration Flow)


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


