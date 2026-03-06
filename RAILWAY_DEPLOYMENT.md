# Railway Deployment Guide 🚀

Railway is a modern cloud platform perfect for deploying Docker-based applications with a generous free tier. This guide will walk you through deploying your file collaboration project to Railway.

## Prerequisites

✅ GitHub account with your repository pushed
✅ Railway account (free tier)
✅ Basic familiarity with environment variables

## Step 1: Create Railway Account & Connect GitHub

1. **Go to [railway.app](https://railway.app)**
2. **Sign up** (click "Sign up")
3. **Choose "Create a new project"**
4. **Select "Deploy from GitHub repo"**
5. **Authorize Railway** to access your GitHub repositories
6. **Select your repository** (`file_collaboration_project`)
7. **Click "Deploy"**

Railway will automatically detect the `railway.json` file and start deploying the backend!

## Step 2: Configure Backend Service

Your backend service will be created automatically. Now let's set it up:

### 2.1 Set Environment Variables

In Railway dashboard, go to your project and click the backend service:

1. **Click "Variables"** tab
2. **Add these environment variables:**

```
SECRET_KEY=your-super-secret-random-key-here-make-it-very-long-and-random
FRONTEND_HOST=https://your-railway-backend-url.railway.app
BACKEND_CORS_ORIGINS=https://your-railway-backend-url.railway.app
DATABASE_URL=postgresql://...  # This will be auto-filled from PostgreSQL service
ENV=production
```

**To generate a secure SECRET_KEY**, run in your terminal:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.2 Enable Public Networking

1. **In the backend service settings**
2. **Click "Settings"**
3. **Scroll to "Networking"**
4. **Click "Generate Domain"** (or use the provided public URL)
5. **Copy the public URL** - this is your backend URL

## Step 3: Add PostgreSQL Database

1. **In your Railway project dashboard**
2. **Click "+ New"** button
3. **Select "PostgreSQL"**
4. **Wait for it to be created** (takes ~1 minute)

The database connection string will be automatically available to your backend service!

### Verify Database Connection

After the database is created, your backend should automatically connect. Check the backend logs:

1. **Click on backend service**
2. **Click "Logs"** tab
3. **Look for successful database connection messages**

## Step 4: Run Database Migrations

Once the backend is running and connected to the database:

1. **Go back to backend service**
2. **Click "Deploy"** → **"Redeploy"**
3. **Wait for the health check to pass**
4. **Verify with `railway logs` in your terminal:**

```bash
# Install Railway CLI if not already installed
npm install -g @railway/cli

# Login to Railway
railway login

# Link your local project
railway link

# View logs
railway logs

# Run migrations (optional if your app does it automatically)
# railway run alembic upgrade head
```

## Step 5: Deploy Frontend

You have two options:

### Option A: Deploy Frontend on Railway (Recommended for simplicity)

1. **Create a second service for frontend:**
   - Click "+ New"
   - Select "GitHub Repo"
   - Choose the same repository
   - Railway will create a new deployment

2. **Configure Frontend Service:**
   - Click "Variables"
   - Add:
   ```
   VITE_API_BASE_URL=https://your-backend-url/api
   VITE_COLLAB_WS=wss://your-backend-url/ws
   ```

3. **Create `railway.json` for frontend** (if needed):
   ```json
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "cd frontend && npm install && npm run build && npm run preview",
       "restartPolicyType": "ON_FAILURE"
     }
   }
   ```

4. **Push changes to GitHub**
5. **Railway will auto-deploy**

### Option B: Deploy Frontend to Vercel (Free & Optimized)

If you want better frontend performance:

1. **Go to [vercel.com](https://vercel.com)**
2. **Sign in with GitHub**
3. **Import your project**
4. **Set environment variables:**
   ```
   VITE_API_BASE_URL=https://your-backend-url/api
   VITE_COLLAB_WS=wss://your-backend-url/ws
   ```
5. **Deploy**

This is free and gives you a custom Vercel URL!

## Step 6: Configure CORS & WebSocket

### Update Backend Environment Variables

Your backend needs to know the frontend URL. In Railway backend service Variables:

```
FRONTEND_HOST=https://your-frontend-url
BACKEND_CORS_ORIGINS=https://your-frontend-url,https://www.your-frontend-url
```

If using Vercel: `https://your-project.vercel.app`
If using Railway: `https://your-railwayurl.railway.app`

## Step 7: Test Your Deployment

1. **Open your frontend URL** in a browser
2. **Try to register a new account** - this tests the backend connection
3. **Login** and create a file
4. **Check the health endpoint**: `https://your-backend-url/health`
5. **View API docs**: `https://your-backend-url/docs`

## Step 8: Get a Custom Domain (Optional)

Railway provides free subdomains, but if you want a custom domain:

### Option 1: Use a Free Domain Service
- **Freenom.com** - Free .tk, .ml, .ga domains
- **Google Domains** - $12/year (.com, .app, etc.)
- **Namecheap** - ~$10/year for .com

### Option 2: Connect Domain to Railway
1. **In Railway project settings**
2. **Click on backend service**
3. **Go to "Settings" → "Networking"**
4. **Add custom domain**
5. **Follow the DNS configuration steps**

## Monitoring & Logs

### View Real-time Logs
```bash
railway login
railway link
railway logs -f  # Follow logs in real-time
```

### Check Service Status
- Backend: `https://your-backend-url/health`
- Frontend: Should load without errors
- Database: Check in Railway dashboard for connectivity

## Troubleshooting

### Backend not starting?
```bash
railway logs
# Look for error messages
# Common issues:
# - Missing environment variables
# - Database not connected
# - Port already in use
```

### WebSocket connection failing?
- Ensure `wss://` is used (secure WebSocket)
- Update `VITE_COLLAB_WS` in frontend environment
- Check CORS is allowing your frontend URL

### Database connection issues?
- Verify `DATABASE_URL` is set automatically
- Check PostgreSQL service is running in Railway
- Restart both services

### Frontend showing blank page?
- Check browser console for errors
- Verify `VITE_API_BASE_URL` is correct
- Check network tab for failed requests to backend

## Cost Estimation on Railway Free Tier

✅ **Backend**: Free (5GB RAM, 512.5 GB-minutes)
✅ **Database**: Free (5GB storage, tested only)
✅ **Frontend**: Free (on Railway)
💰 **Custom Domain**: $10/year (optional, not required)

**Total: $0/month - $10/year** 🎉

## Useful Railway CLI Commands

```bash
# Login to Railway
railway login

# Link your project
railway link

# View logs (real-time)
railway logs -f

# Run commands in Railway environment
railway run python -c "import sys; print(sys.version)"

# View environment variables
railway variables

# Deploy specific service
railway deploy --service backend

# Monitor resource usage
railway logs --service backend
```

## Next Steps

1. **Custom Domain Setup** (optional) - Connect your own domain
2. **SSL/TLS Certificates** (automatic on Railway)
3. **Monitoring & Alerts** - Set up error tracking with Sentry (free tier)
4. **Backups** - Enable automatic PostgreSQL backups in Railway
5. **Auto-scaling** (premium feature)

## Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Railway CLI Docs](https://docs.railway.app/cli/cli-reference)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/concepts/)
- [Vue 3 Deployment](https://vuejs.org/guide/scaling-up/deployment.html)

---

**Need help?** Check Railway's support at [railway.app/support](https://railway.app/support)

**Happy deploying! 🚀**
