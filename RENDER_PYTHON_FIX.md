# Fix Python 3.13 Error on Render

## Problem
Render is using Python 3.13.4, but `psycopg2-binary` doesn't have proper wheels for Python 3.13, causing import errors.

## Solution: Force Python 3.12.7

### Option 1: Manual Configuration (Recommended)

1. Go to your **Web Service** in Render Dashboard
2. Click **"Settings"** tab
3. Scroll down to **"Build & Deploy"** section
4. Find **"Python Version"** dropdown
5. **Select: `3.12.7`** (or `3.12` if 3.12.7 is not available)
6. Click **"Save Changes"**
7. Click **"Manual Deploy"** → **"Deploy latest commit"**

### Option 2: Use Dockerfile (Alternative)

If Option 1 doesn't work, Render will automatically use the `Dockerfile` we created, which forces Python 3.12.7.

1. In Render Dashboard → Web Service → Settings
2. Under **"Build & Deploy"**, set:
   - **Environment**: `Docker`
3. Save and redeploy

### Option 3: Update render.yaml (If using Blueprint)

The `render.yaml` file specifies Python 3.12.7, but you may need to manually set it in the dashboard.

## Verify Python Version

After deployment, check the build logs. You should see:
```
==> Installing Python version 3.12.7...
```

NOT:
```
==> Installing Python version 3.13.4...
```

## Why This Works

- `psycopg2-binary==2.9.9` has pre-built wheels for Python 3.12
- Python 3.12.7 is stable and well-supported
- SQLAlchemy works perfectly with psycopg2-binary on Python 3.12

## Files Added

- `runtime.txt` - Specifies Python 3.12.7
- `.python-version` - Additional Python version hint
- `Dockerfile` - Forces Python 3.12.7 if using Docker
- `render.yaml` - Updated with Python version

After setting Python 3.12.7 in Render dashboard, your deployment should succeed!

