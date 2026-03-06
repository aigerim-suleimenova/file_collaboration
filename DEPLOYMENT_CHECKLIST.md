# 🚀 Pre-Deployment Checklist

Before deploying to Railway, run through this checklist to ensure everything is ready:

## ✅ Code & Git Setup

- [ ] **Push code to GitHub**
  ```bash
  git add .
  git commit -m "Ready for Railway deployment"
  git push origin main
  ```

- [ ] **Verify `.gitignore`** includes:
  - `.env`, `.env.local`, `.env.*.local`
  - `node_modules/`, `venv/`, `.venv/`
  - `__pycache__/`, `.pytest_cache/`
  - `.DS_Store` (macOS), `*.log`

- [ ] **Check no secrets are committed**
  ```bash
  git log --all -p | grep -i "password\|secret\|key" || echo "✓ No secrets found"
  ```

## ✅ Backend Setup

- [ ] **Backend runs locally**
  ```bash
  cd backend
  pip install -r requirements.txt
  uvicorn app.main:app --reload
  # Should run on http://localhost:8000
  ```

- [ ] **Health endpoint works**
  - Visit `http://localhost:8000/health`
  - Should return `{"status": "ok"}`

- [ ] **Database migrations are correct**
  ```bash
  cd backend
  alembic current  # Check current schema version
  ```

- [ ] **Environment variables defined**
  - Check `env.production.example` for all required vars
  - Example in comments

## ✅ Frontend Setup

- [ ] **Frontend builds successfully**
  ```bash
  cd frontend
  npm install
  npm run build
  # Check `dist/` folder is created
  ```

- [ ] **Frontend runs locally**
  ```bash
  npm run dev
  # Should run on http://localhost:5173
  ```

- [ ] **Frontend connects to backend**
  - Check `frontend/src/services/api.js` for correct API URL
  - WebSocket should connect to backend

## ✅ Docker Setup (Optional for Railway, but good to verify)

- [ ] **Docker services start**
  ```bash
  docker-compose up -d
  # All services should start without errors
  # Check: docker-compose ps
  ```

- [ ] **Health checks pass**
  ```bash
  # Backend health
  curl http://localhost:8000/health
  
  # Frontend loads
  curl http://localhost:3000
  
  # Database connection
  docker exec file_collaboration_db psql -U postgres -d file_collaboration_db -c "SELECT 1"
  ```

## ✅ Configuration Files

- [ ] **`railway.json` exists** in root directory
  ```bash
  ls -la railway.json
  # Should show the file
  ```

- [ ] **`env.production.example` is complete**
  - All required environment variables listed
  - Example values provided
  - Comments explain each variable

## ✅ Documentation

- [ ] **`RAILWAY_DEPLOYMENT.md` reviewed**
  - Understand each deployment step
  - Know where to find your URLs

- [ ] **`README.md` has deployment section**
  - Clear instructions for users
  - Troubleshooting guide included

## 🚀 Railway Deployment Checklist

Once code is pushed to GitHub:

- [ ] **Create Railway account** (if not exists)
  - https://railway.app

- [ ] **Connect GitHub account**
  - Authorize Railway to access your repos

- [ ] **Create new project**
  - Select your GitHub repository

- [ ] **Configure environment variables**
  - Generate secure `SECRET_KEY`
  - Set `FRONTEND_HOST` (will update after frontend deployed)
  - Set `BACKEND_CORS_ORIGINS`

- [ ] **Add PostgreSQL service**
  - Database will auto-connect to backend

- [ ] **Verify logs**
  ```bash
  railway logs -f
  # Should show successful startup
  ```

- [ ] **Test backend endpoint**
  - Visit: `https://your-backend-url/health`
  - Should return JSON success

- [ ] **Deploy frontend** (Option A: Railway or Option B: Vercel)
  - Follow RAILWAY_DEPLOYMENT.md Step 5

- [ ] **Update CORS settings**
  - Set `FRONTEND_HOST` and `BACKEND_CORS_ORIGINS` to frontend URL
  - Restart backend service

- [ ] **End-to-end testing**
  - Load frontend URL
  - Register new account
  - Login
  - Create/edit files with real-time collaboration
  - Test WebSocket connection

## 🆘 Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| Backend won't start | Check `railway logs`, verify environment variables |
| Database connection fails | Verify PostgreSQL service created, check DATABASE_URL |
| WebSocket fails | Check `wss://` protocol, verify CORS settings |
| Frontend blank page | Check browser console, verify API_BASE_URL env var |
| Static files 404 | Ensure frontend build completes, check Nginx config |

## 📞 Getting Help

1. **Check logs first**
   ```bash
   railway logs -f
   ```

2. **Review RAILWAY_DEPLOYMENT.md** troubleshooting section

3. **Check Railway docs**
   - https://docs.railway.app

4. **Contact Railway support**
   - https://railway.app/support

---

**Ready to deploy? Follow RAILWAY_DEPLOYMENT.md next!** 🎯
