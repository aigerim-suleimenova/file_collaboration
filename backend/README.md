# File Collaboration Backend

A FastAPI-based backend for real-time file collaboration with WebSocket support.

## 🏗️ Architecture

```
backend/
├── app/
│   ├── api/                 # API routes and endpoints
│   │   ├── deps.py         # Dependency injection
│   │   ├── routes/         # Route handlers
│   │   │   ├── files.py    # File CRUD operations
│   │   │   ├── users.py    # User management
│   │   │   └── websocket.py # WebSocket endpoints
│   ├── core/               # Core configuration
│   │   ├── config.py       # Settings and environment
│   │   ├── db.py          # Database connection
│   │   └── security.py    # Authentication & security
│   ├── models.py           # Database models
│   ├── crud.py            # Database operations
│   └── services/          # Business logic
│       └── websocket_manager.py # WebSocket collaboration
├── alembic/                # Database migrations
├── requirements.txt        # Python dependencies
└── run.py                 # Development server script
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL
- Virtual environment

### Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your database credentials

# Initialize database
python3 init_database.py

# Run the application
python3 run.py
```

### Alternative: Use Makefile
```bash
make run        # Create venv, install deps, and run
make install    # Just install dependencies
make clean      # Remove virtual environment
```

## 🌐 API Endpoints

### Files
- `POST /files` - Create new file
- `GET /files` - List user's files
- `GET /files/{id}` - Get specific file
- `PUT /files/{id}` - Update file
- `DELETE /files/{id}` - Delete file
- `POST /files/{id}/share` - Create share token

### Users
- `POST /users/signup` - User registration
- `GET /users/me` - Get current user
- `GET /users/{id}` - Get user by ID

### WebSocket
- `WS /ws/{file_id}` - Real-time file collaboration

## 🔐 Authentication

Uses JWT tokens for authentication. Include in headers:
```
Authorization: Bearer <your_token>
```

## 🗄️ Database

- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Migrations**: Alembic
- **Database**: PostgreSQL

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 📦 Development

### Code Quality
- Use `black` for code formatting
- Use `flake8` for linting
- Use `mypy` for type checking

### Pre-commit Hooks
```bash
pip install pre-commit
pre-commit install
```

## 🚀 Production Deployment

### Docker
```bash
docker build -t file-collab-backend .
docker run -p 8000:8000 file-collab-backend
```

### Environment Variables
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key
- `API_V1_STR` - API version prefix
- `FIRST_SUPERUSER` - Initial admin email
- `FIRST_SUPERUSER_PASSWORD` - Initial admin password

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License
