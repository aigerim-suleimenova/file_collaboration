# Render Deployment - Quick Fix Guide

If you're getting the **"no such file or directory: open Dockerfile"** error, follow these steps.

## Fix: Configure Root Directory & Dockerfile Path

### For Backend Service

1. **In Render dashboard**, select your backend service
2. **Click "Settings"** (or find Service Settings)
3. **Scroll down to "Advanced"** section
4. **Set these fields:**
   ```
   Root Directory: backend
   Dockerfile Path: Dockerfile.prod
   ```
5. **Click "Save"** button
6. **Render will automatically redeploy** (takes 5-10 minutes)
7. **Check status** - should show "Live" and build successful

### For Frontend Service

1. **In Render dashboard**, select your frontend service
2. **Click "Settings"**
3. **Scroll to "Advanced"**
4. **Set these fields:**
   ```
   Root Directory: frontend
   Dockerfile Path: Dockerfile.prod
   ```
5. **Click "Save"**
6. **Wait for auto-redeploy** (5-10 minutes)

## Why This Happens

Your project structure:
```
file_collaboration_project/
  ├── backend/
  │   ├── Dockerfile         ← For development
  │   ├── Dockerfile.prod    ← For production (Render uses this)
  │   └── ... backend files
  ├── frontend/
  │   ├── Dockerfile         ← For development
  │   ├── Dockerfile.prod    ← For production (Render uses this)
  │   └── ... frontend files
```

Render looks for Dockerfile in root by default, but your code is in subdirectories. Setting **Root Directory** tells Render where to build from.

## Verify Fix Worked

### Check Backend
1. Go to backend service
2. **Click "Logs"** tab
3. Look for: `INFO:     Uvicorn running on http://0.0.0.0:10000`
4. If you see it, backend is working! ✅

### Check Frontend
1. Go to frontend service
2. **Click "Logs"** tab
3. Look for successful build messages
4. If no errors, frontend is working! ✅

## Environment Variables Still Needed

Even after fixing Dockerfile, you still need to set:

**Backend Service Variables:**
```
SECRET_KEY=your-secret-key
ENV=production
FRONTEND_CORS_ORIGINS=https://your-frontend-url.onrender.com
DATABASE_URL=postgresql://...
```

**Frontend Service Variables:**
```
VITE_API_BASE_URL=https://your-backend-url.onrender.com/api
VITE_COLLAB_WS=wss://your-backend-url.onrender.com/ws
```

## Still Having Issues?

1. **Force reload page** in browser (Ctrl+Shift+R / Cmd+Shift+R)
2. **Check logs** - Click service → Logs tab
3. **Verify Root Directory** is set (not default)
4. **Verify Dockerfile Path** is `Dockerfile.prod`
5. **Redeploy manually** - Click service → redeploy button

---

**Once both services are Live and you see no errors in logs, you can skip to the testing section!** 🚀
