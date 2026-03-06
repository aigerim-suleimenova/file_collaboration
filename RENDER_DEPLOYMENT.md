# Render Deployment Guide 🚀

Render is a modern cloud platform perfect for deploying Docker-based applications with generous free tier. This guide will walk you through deploying your file collaboration project to Render.

## Prerequisites

✅ GitHub account with your repository pushed
✅ Render account (free tier)
✅ Basic familiarity with environment variables

## ⚠️ IMPORTANT: Monorepo Configuration

**Your project is a monorepo with separate `backend/` and `frontend/` directories.** When creating services in Render, you MUST set:

- **Root Directory**: `backend` (for backend) or `frontend` (for frontend)
- **Dockerfile Path**: `Dockerfile.prod`

If you don't set these, you'll get error: `failed to read dockerfile: open Dockerfile: no such file or directory`

See **[Step 2.1](#21-create-web-service)** for exact configuration steps.

## Step 1: Create Render Account & Connect GitHub

1. **Go to [render.com](https://render.com)**
2. **Sign up** (click "Sign up")
3. **Choose "Sign up with GitHub"** (recommended)
4. **Authorize Render** to access your GitHub repositories
5. **Verify your email**

## Step 2: Deploy Backend Service

### 2.1 Create Web Service

1. **In Render dashboard**, click **"New +"** → **"Web Service"**
2. **Connect your GitHub repository**
   - Select: `aigerim-suleimenova/file_collaboration`
   - Click **Connect**
3. **Configure the service:**
   - **Name**: `file-collab-backend`
   - **Runtime**: `Docker`
   - **Branch**: `prod`
   - **Root Directory**: `backend` ⭐ **IMPORTANT**
   - **Dockerfile Path**: `Dockerfile.prod` ⭐ **IMPORTANT**
   - **Build Command**: (leave empty - Dockerfile handles it)
   - **Start Command**: (leave empty - Dockerfile handles it)

### 2.2 Set Environment Variables

1. **Click "Advanced"** section
2. **Add environment variables:**
   ```
   SECRET_KEY=<generate with: python3 -c "import secrets; print(secrets.token_urlsafe(32))">
   FRONTEND_HOST=https://your-render-frontend-url.onrender.com
   BACKEND_CORS_ORIGINS=https://your-render-frontend-url.onrender.com
   ENV=production
   DATABASE_URL=postgresql://...  # Will be set when PostgreSQL is added
   ```

3. **Click "Create Web Service"**
4. **Wait for deployment** (takes 5-10 minutes)

### 2.3 Verify Backend is Running

1. **Once deployed, you'll see a green "Live" status**
2. **Click the URL** to test backend health
3. **Visit**: `https://your-app-name.onrender.com/health`
   - Should return: `{"status": "ok"}`
4. **Check API docs**: `https://your-app-name.onrender.com/docs`

## Step 3: Deploy PostgreSQL Database

Render provides managed PostgreSQL databases:

### 3.1 Create Database Service

1. **In Render dashboard**, click **"New +"** → **"PostgreSQL"**
2. **Configure the database:**
   - **Name**: `file-collab-db`
   - **Database**: `file_collaboration_db`
   - **User**: `postgres`
   - **Region**: Same as backend (important for performance!)
   - **PostgreSQL Version**: 15 or latest
3. **Click "Create Database"**
4. **Wait for initialization** (takes 2-3 minutes)

### 3.2 Connect Database to Backend

1. **Copy the internal database URL** from PostgreSQL service details
2. **Go back to Web Service**
3. **Click "Environment"** tab
4. **Add/update**: `DATABASE_URL=<paste the internal URL>`
5. **Click "Save"**
6. **Backend will automatically redeploy**

### 3.3 Run Database Migrations

Once backend reconnects to database:

1. **Check backend logs** for successful connection
2. **Database migrations should run automatically**
3. **Verify in logs**: `alembic upgrade head`

## Step 4: Deploy Frontend Service

### 4.1 Create Frontend Web Service

1. **Click "New +"** → **"Web Service"** again
2. **Connect same GitHub repo**
3. **Configure the service:**
   - **Name**: `file-collab-frontend`
   - **Runtime**: `Docker`
   - **Branch**: `prod`
   - **Root Directory**: `frontend` ⭐ **IMPORTANT**
   - **Dockerfile Path**: `Dockerfile.prod` ⭐ **IMPORTANT**

### 4.2 Set Frontend Environment Variables

1. **Click "Advanced"**
2. **Add environment variables:**
   ```
   VITE_API_BASE_URL=https://your-backend-url.onrender.com/api
   VITE_COLLAB_WS=wss://your-backend-url.onrender.com/ws
   ```
3. **Click "Create Web Service"**
4. **Wait for deployment**

### 4.3 Test Frontend

1. **Once deployed, visit the frontend URL**
2. **Should load without errors**
3. **Try to register an account**
4. **Login and create a file**
5. **Test real-time collaboration**

## Step 5: Configure CORS & WebSocket

Your backend needs the correct frontend URL:

1. **Go to backend Web Service**
2. **Click "Environment"**
3. **Update these variables:**
   ```
   FRONTEND_HOST=https://file-collab-frontend.onrender.com
   BACKEND_CORS_ORIGINS=https://file-collab-frontend.onrender.com
   ```
4. **Click "Save"** (auto-redeploys)

## Step 6: Test Complete Deployment

✅ **Frontend loads**: Visit your frontend URL
✅ **Can register**: Create a new account
✅ **Can login**: Successfully authenticate
✅ **Real-time sync**: Open in 2 browser tabs, edit simultaneously
✅ **Backend health**: `https://your-backend.onrender.com/health` returns 200
✅ **API docs**: `https://your-backend.onrender.com/docs` loads

## 🆓 Render Free Tier Details

### What's Included
- **Web Services**: 1 free web service (spins down after 15 min of inactivity)
- **PostgreSQL**: 1 free database (90 days free, then $15/month)
- **Storage**: 1 GB included
- **Auto-deploys**: From GitHub pushes
- **Custom domain**: Add custom domain to free services

### Important Notes
- **Spin down**: Free web services pause after 15 minutes of no requests
- **Wake-up time**: About 30 seconds when traffic resumes
- **Database**: Free only for 90 days, then must upgrade
- **For production**: Upgrade to paid plans ($7-12/month each service)

### Upgrade Path (Optional)
```
Free → Starter ($7/month): Always-on, better performance
Sponsor: GitHub sponsors can qualify for free tiers
```

## 📊 Cost Estimation

| Component | Free Tier | Notes |
|-----------|-----------|-------|
| Backend Web Service | $0/month | Spins down after 15 min |
| Frontend Web Service | $0/month | Spins down after 15 min |
| PostgreSQL Database | $0/month (90 days) | Then $15/month |
| **Total** | **$0-15/month** | Depends on upgrades |

For always-on production:
- 2 Web Services @ $7/month = $14/month
- PostgreSQL @ $15/month = $15/month
- **Total: ~$29/month**

## 🔧 Configuration Files

Your project is ready with proper Docker configurations:

- **Backend**: `backend/Dockerfile` (for Render)
- **Frontend**: `frontend/Dockerfile` (for Render)
- **Compose**: `docker-compose.prod.yml` (for local testing)
- **Environment templates**: `env.production.example`

## 📚 Monitoring & Logs

### View Logs in Render Dashboard

1. **Select your service** (backend or frontend)
2. **Click "Logs"** tab
3. **See real-time output**
4. **Useful for debugging**

### Common Log Patterns

**Backend startup:**
```
INFO:     Uvicorn running on http://0.0.0.0:10000
```

**Database connection:**
```
SQLAlchemy connected to database
```

**Error indicators:**
```
ERROR: Failed to connect to database
CRITICAL: Missing environment variable
```

## 🆘 Troubleshooting

### ❌ Dockerfile Error: "no such file or directory: open Dockerfile"

**This is the most common issue when deploying to Render!**

**Root cause**: Render is looking for Dockerfile in the root directory, but your project is a monorepo with Dockerfiles in subdirectories (`backend/`, `frontend/`).

**Solution** (follow these exact steps):

1. **Go to your Service settings** in Render dashboard
2. **Click "Advanced"** section
3. **Set Root Directory**:
   - For backend: `backend`
   - For frontend: `frontend`
4. **Set Dockerfile Path**:
   - Use: `Dockerfile.prod` (or `Dockerfile` if only one exists)
5. **Click "Save"**
6. **Redeploy** the service
7. **Watch logs** - should build successfully now

**Screenshot flow:**
```
Service Settings
  ↓
Advanced
  ↓
Root Directory: backend (or frontend)
Dockerfile Path: Dockerfile.prod
  ↓
Save → Auto-redeploy
```

### Backend Won't Start

**Check logs for:**
- Missing environment variables
- Database connection failures
- Port binding issues

**Solution:**
```bash
# View logs in Render dashboard
# Add missing environment variables
# Redeploy service
```

### WebSocket Connection Fails

**Check:**
- Frontend `VITE_COLLAB_WS` uses `wss://` (secure)
- Backend URL is correct
- Backend is actually running

**Solution:**
```
Update environment variables:
VITE_COLLAB_WS=wss://your-backend-url/ws (with wss://)
```

### Database Connection Error

**Likely causes:**
- PostgreSQL service still initializing
- DATABASE_URL not set
- Internal URL is outdated

**Solution:**
```
1. Wait 5 minutes for database to fully initialize
2. Copy fresh internal connection URL from PostgreSQL service
3. Update DATABASE_URL in backend
4. Redeploy backend
```

### Frontend Blank Page

**Check browser console:**
- Look for 404 errors
- Look for CORS errors
- Check network requests

**Debug:**
```
Update VITE_API_BASE_URL to correct backend URL
Clear browser cache (Ctrl+Shift+R)
Redeploy frontend
```

### Service Keeps Spinning Down

**This is normal on free tier!**
- Web services pause after 15 min of inactivity
- Takes ~30 seconds to wake up
- Acceptable for development
- Upgrade to "Starter" ($7/month) for always-on

## 📈 Performance Optimization

### For Free Tier (With Spin-Down)
- Suitable for development, testing, demos
- Slight delay on first request (wake-up)
- Fine for low-traffic usage

### For Production (Upgrade to Starter)
```
Backend Starter: $7/month (always-on)
Frontend Starter: $7/month (always-on)
PostgreSQL Standard: $15/month
Total: ~$29/month (comparable to self-hosted)
```

## 🚀 Advanced Features (Optional)

### Custom Domain
1. **Buy domain** (Namecheap, Google Domains, etc.)
2. **In Render service settings**, click "Custom Domain"
3. **Add your domain**
4. **Update DNS** records (Render will show instructions)
5. **SSL certificate** automatically provisioned

### Environment-Specific Configs
```
Frontend:
- Development: .env.development (local)
- Production: VITE_API_BASE_URL (Render env var)

Backend:
- Development: .env.local (local)
- Production: Environment variables in Render
```

### GitHub Auto-Deploy
Your setup already supports this!
- Push to `prod` branch
- Render automatically redeploys
- No manual steps needed

## 📞 Support Resources

- **Render Docs**: https://render.com/docs
- **Render Support**: https://support.render.com
- **Discord Community**: https://discord.gg/render
- **Status Page**: https://status.render.com

## ✨ Next Steps

1. ✅ Create Render account
2. ✅ Deploy backend Web Service
3. ✅ Deploy PostgreSQL database
4. ✅ Deploy frontend Web Service
5. ✅ Test complete application
6. ✅ (Optional) Upgrade to paid for always-on
7. ✅ (Optional) Add custom domain

---

**Ready? Head to [render.com](https://render.com) and follow Step 1!** 🎯
