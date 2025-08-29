# 🚀 Deployment Setup Guide

## Overview
This guide will help you deploy your file collaboration app using:
- **Frontend**: Docker (Vue.js)
- **Backend**: Railway (FastAPI + PostgreSQL)
- **CI/CD**: GitHub Actions

## 🎯 Step-by-Step Setup

### 1. Frontend Setup (Docker)

#### A. Docker Setup
1. Install Docker and Docker Compose
2. Ensure Docker daemon is running
3. Test with: `docker --version && docker-compose --version`

#### B. Deploy Frontend
1. **Build and run with Docker**:
   ```bash
   cd frontend
   docker build -t frontend-app .
   docker run -p 3000:80 frontend-app
   ```
2. **Or use Docker Compose**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

#### C. Configure Environment Variables
In your environment configuration, add:
```
VITE_API_BASE_URL=https://your-backend-url.railway.app
VITE_COLLAB_WS=wss://your-backend-url.railway.app/ws
```

### 2. Backend Setup (Railway)

#### A. Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create new project

#### B. Deploy Backend
1. **Connect your repository**
2. **Add PostgreSQL service**:
   - Service: `PostgreSQL`
   - Name: `file-collab-db`
3. **Add backend service**:
   - Service: `GitHub Repo`
   - Repository: Your repo
   - Branch: `main`

#### C. Configure Environment Variables
In Railway dashboard, add:
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=your-super-secret-key-here
FRONTEND_HOST=http://localhost:3000
BACKEND_CORS_ORIGINS=http://localhost:3000
```

### 3. GitHub Actions Setup

#### A. Add Repository Secrets
Go to your GitHub repo → Settings → Secrets and variables → Actions

Add these secrets:
```
# Docker deployment doesn't require these tokens
# VERCEL_TOKEN=your-vercel-token
# VERCEL_ORG_ID=your-vercel-org-id
# VERCEL_PROJECT_ID=your-vercel-project-id
RAILWAY_TOKEN=your-railway-token
RAILWAY_SERVICE_NAME=your-railway-service-name
DATABASE_URL=your-railway-database-url
VITE_API_BASE_URL=https://your-backend-url.railway.app
VITE_COLLAB_WS=wss://your-backend-url.railway.app/ws
```

#### B. Docker Configuration
1. Ensure Docker is running and accessible
2. Check Docker Compose version: `docker-compose --version`
3. Verify network connectivity for external services

#### C. Get Railway Tokens
1. In Railway dashboard → Account → Tokens
2. Create new token
3. Copy token and service name
4. Install Railway CLI: `npm install -g @railway/cli`

### 4. Database Setup

#### A. Run Migrations
The GitHub Action will automatically run migrations, or manually:
```bash
# In Railway dashboard terminal
cd backend
alembic upgrade head
```

#### B. Create Test User
```bash
# In Railway dashboard terminal
cd backend
python create_test_user.py
```

## 🔄 Deployment Flow

1. **Push to main branch** → Triggers GitHub Actions
2. **Frontend builds** → Creates Docker images
3. **Backend builds** → Deploys to Railway
4. **Database migrates** → Updates schema
5. **Health checks** → Verifies deployment

## 🌐 URLs After Deployment

- **Frontend**: `http://localhost:3000` (Docker)
- **Backend**: `https://your-app.railway.app`
- **API Docs**: `https://your-app.railway.app/docs`

## 📊 Monitoring

### Docker
- Container logs
- Resource usage
- Performance metrics

### Railway
- Service logs
- Database metrics
- Resource usage

### GitHub Actions
- Deployment status
- Build logs
- Error notifications

## 🚨 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check GitHub Actions logs
   - Verify environment variables
   - Check dependency versions

2. **Database Connection**
   - Verify DATABASE_URL in Railway
   - Check PostgreSQL service status
   - Run migrations manually

3. **CORS Issues**
   - Verify BACKEND_CORS_ORIGINS
   - Check frontend URL in backend config
   - Test API endpoints

### Debug Commands

```bash
# Check Railway logs
railway logs

# Check Docker deployment
docker ps

# Test backend locally
cd backend
uvicorn app.main:app --reload
```

## 💰 Cost Estimation

### Docker (Frontend)
- **Local**: $0/month
- **VPS/Cloud**: $5-20/month (depending on provider)

### Railway (Backend + Database)
- **Free Tier**: $5/month credit
- **Paid**: ~$10-20/month (depending on usage)

### Total Estimated Cost
- **Development**: $0-5/month
- **Production**: $10-25/month

## 🎉 Success!

After following these steps:
1. ✅ Frontend deployed with Docker
2. ✅ Backend deployed to Railway
3. ✅ Database connected and migrated
4. ✅ GitHub Actions automated
5. ✅ App accessible globally

Your file collaboration app is now live and automatically deploying on every push to main!
