# 🎯 Render Deployment - Quick Start Guide

Your project is ready for deployment to Render! Railway trial ended, so we've switched to Render which has a better free tier.

## 📚 Documentation Created

Three deployment guides are available:

1. **`RENDER_DEPLOYMENT.md`** - Complete step-by-step guide for Render ⭐ USE THIS ONE
2. **`RENDER_DOCKERFILE_FIX.md`** - Quick fix if you get Dockerfile error ⚠️ READ IF ERRORS
3. **`RAILWAY_DEPLOYMENT.md`** - Original Railway guide (for reference)
4. **`DEPLOYMENT_CHECKLIST.md`** - Pre-deployment verification checklist

## ⚠️ CRITICAL: Monorepo Configuration

**When creating Web Services in Render, you MUST set:**
- **Root Directory**: `backend` (for backend service) or `frontend` (for frontend service)
- **Dockerfile Path**: `Dockerfile.prod`

If you skip this step, you'll get: `failed to read dockerfile: open Dockerfile: no such file or directory`

👉 **See [RENDER_DOCKERFILE_FIX.md](./RENDER_DOCKERFILE_FIX.md) for exact steps if you hit this error**

## 🚀 Next Steps

### Step 1: Verify GitHub Sync
```bash
git status
# Should show clean working directory
```

### Step 2: Go to Render.com
1. Visit https://render.com
2. Sign up with GitHub (recommended)
3. Authorize Render to access your repositories
4. You're ready to deploy!

### Step 3: Create Backend Web Service
1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select: `aigerim-suleimenova/file_collaboration`
4. **Name**: `file-collab-backend`
5. **Runtime**: Docker
6. Click **"Create Web Service"**
7. Watch Render deploy your backend (5-10 minutes)

### Step 4: Configure Environment Variables
Once backend is created:

1. Click the **backend service**
2. Go to **"Environment"** tab
3. Add these variables:
   ```
   SECRET_KEY=<generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))">
   FRONTEND_HOST=https://your-deployed-frontend-url.onrender.com
   BACKEND_CORS_ORIGINS=https://your-deployed-frontend-url.onrender.com
   ENV=production
   ```

### Step 5: Add PostgreSQL Database
1. Click **"New +"** → **"PostgreSQL"**
2. **Name**: `file-collab-db`
3. Same region as backend
4. Click **"Create Database"**
5. Copy the **Internal Database URL**
6. Add to backend **Environment**: `DATABASE_URL=<paste-url>`

### Step 6: Deploy Frontend
1. Click **"New +"** → **"Web Service"** again
2. Connect same GitHub repo
3. **Name**: `file-collab-frontend`
4. **Runtime**: Docker
5. Add environment variables:
   ```
   VITE_API_BASE_URL=https://your-backend-url.onrender.com/api
   VITE_COLLAB_WS=wss://your-backend-url.onrender.com/ws
   ```
6. Click **"Create Web Service"**

### Step 7: Test Your Deployment
1. Open frontend URL in browser
2. Register a new account
3. Login
4. Create a file and test real-time collaboration
5. Verify backend health: `https://your-backend-url.onrender.com/health`

## ⚡ Key Information

| Component | Link | Status |
|-----------|------|--------|
| GitHub Repo | https://github.com/aigerim-suleimenova/file_collaboration | ✅ Ready |
| Render Platform | https://render.com | 🔗 Set up there |
| Docs | [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) | 📖 Full guide |
| Checklist | [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) | ✓ Pre-flight check |

## 🆘 Troubleshooting Quick Reference

| Problem | Quick Fix |
|---------|-----------|
| Backend not starting | Check Render logs, verify env vars set |
| Database error | Wait for PostgreSQL to fully initialize (2-3 min) |
| WebSocket fails | Update `VITE_COLLAB_WS` env var in frontend |
| CORS errors | Set correct `BACKEND_CORS_ORIGINS` env var |
| Frontend blank | Check browser console, verify `VITE_API_BASE_URL` |

## 📞 Need Help?

- **Detailed Guide**: Read [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md)
- **Pre-flight Check**: Use [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
- **Render Docs**: https://render.com/docs
- **Render Support**: https://support.render.com

---

## 💡 Tips

✅ **Use Render's free tier** - Spins down after 15 min of inactivity (fine for testing)
✅ **Keep .env files private** - Never commit them (already in .gitignore)
✅ **Monitor with logs** - Check Render dashboard logs for debugging
✅ **Test early** - Deploy backend first, then frontend
✅ **Set correct URLs** - Most issues are wrong environment variables

## 🎉 Success Indicators

Once deployed, you should see:
- ✅ Frontend loads without errors
- ✅ Can register and login
- ✅ Can create and edit files
- ✅ Real-time collaboration works (multiple users)
- ✅ Backend shows 200 status on `/health` endpoint

---

**Ready? Open RENDER_DEPLOYMENT.md to begin! 🚀**
