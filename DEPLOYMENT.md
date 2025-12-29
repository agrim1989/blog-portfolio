# Deployment Guide - Free Hosting on Render

This guide will help you deploy your Blog Portfolio to Render.com for free.

## Prerequisites

1. GitHub account (your code is already pushed)
2. Render account (sign up at https://render.com - it's free)

## Step-by-Step Deployment

### Option 1: Using Render Dashboard (Recommended)

1. **Sign up/Login to Render**
   - Go to https://render.com
   - Sign up with your GitHub account

2. **Create a New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub account if not already connected
   - Select repository: `agrim1989/blog-portfolio`
   - Click "Connect"

3. **Configure the Service**
   - **Name**: `blog-portfolio` (or any name you prefer)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: (leave empty)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

4. **Add Environment Variables**
   - Click "Advanced" → "Add Environment Variable"
   - Add:
     - `FLASK_ENV` = `production`
     - `SECRET_KEY` = (generate a random string, e.g., use: `python -c "import secrets; print(secrets.token_hex(32))"`)

5. **Create PostgreSQL Database (Free)**
   - Click "New +" → "PostgreSQL"
   - **Name**: `blog-portfolio-db`
   - **Database**: `blog_portfolio`
   - **User**: `blog_portfolio_user`
   - **Plan**: Free
   - Click "Create Database"
   - Copy the **Internal Database URL**

6. **Link Database to Web Service**
   - Go back to your Web Service settings
   - Add Environment Variable:
     - `DATABASE_URL` = (paste the Internal Database URL from step 5)

7. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app
   - Wait 5-10 minutes for the first deployment

8. **Initialize Database**
   - Once deployed, your app will be live at: `https://your-app-name.onrender.com`
   - SSH into the service or use Render's shell to run:
     ```bash
     python populate_portfolio.py
     ```
   - Or add this to your app startup (see below)

### Option 2: Using render.yaml (Automatic)

The `render.yaml` file is already created. You can:

1. Go to Render Dashboard
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically detect `render.yaml` and create all services

## Post-Deployment Steps

### 1. Initialize Database

After first deployment, you need to populate the database:

**Option A: Using Render Shell**
1. Go to your Web Service on Render
2. Click "Shell" tab
3. Run: `python populate_portfolio.py`

**Option B: Add to app.py (Automatic)**
Add this to your `app.py` after database initialization to auto-populate on first run.

### 2. Access Your Site

- Your site will be live at: `https://your-app-name.onrender.com`
- Admin login: `/admin/login`
- Default credentials: `admin` / `admin123` (change this in production!)

### 3. Update Admin Password

For security, change the admin password:
1. SSH into Render shell
2. Run: `python reset_admin_password.py`
3. Or manually update through the database

## Important Notes

### Free Tier Limitations

- **Spins down after 15 minutes of inactivity** - First request after inactivity takes ~30 seconds
- **750 hours/month free** - Enough for always-on if you're the only user
- **512MB RAM** - Should be sufficient for this app
- **PostgreSQL**: 1GB storage, 90-day retention

### Custom Domain (Optional)

1. Go to your Web Service settings
2. Click "Custom Domains"
3. Add your domain
4. Update DNS records as instructed

### Environment Variables

Make sure these are set in Render:
- `FLASK_ENV` = `production`
- `SECRET_KEY` = (random secure string)
- `DATABASE_URL` = (from PostgreSQL service)

## Troubleshooting

### App won't start
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure `gunicorn` is in requirements.txt

### Database errors
- Verify `DATABASE_URL` is correctly set
- Check PostgreSQL service is running
- Run migrations: `python populate_portfolio.py`

### Static files not loading
- Ensure `static/` folder is committed to Git
- Check file paths in templates

## Alternative Free Hosting Options

### 1. Railway (railway.app)
- Free $5 credit/month
- Similar to Render
- Easy deployment from GitHub

### 2. Fly.io (fly.io)
- Free tier available
- Global edge deployment
- More complex setup

### 3. PythonAnywhere (pythonanywhere.com)
- Free tier for Python apps
- Limited to one app
- Good for learning

## Security Recommendations

1. **Change default admin password** immediately
2. **Use strong SECRET_KEY** (32+ characters)
3. **Enable HTTPS** (automatic on Render)
4. **Regular backups** of database
5. **Update dependencies** regularly

## Support

If you encounter issues:
1. Check Render logs
2. Verify all environment variables
3. Test locally first
4. Check Render status page

Happy deploying! 🚀

