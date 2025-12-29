# Quick Render.com Deployment Guide

## 🚀 Step-by-Step Deployment

### 1. Sign Up for Render
- Go to **https://render.com**
- Click **"Get Started for Free"**
- Sign up with your **GitHub account** (recommended)

### 2. Create PostgreSQL Database (Do this first!)

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `blog-portfolio-db`
   - **Database**: `blog_portfolio`
   - **User**: `blog_portfolio_user`
   - **Region**: Choose closest to you
   - **Plan**: **Free**
3. Click **"Create Database"**
4. **IMPORTANT**: Copy the **"Internal Database URL"** (you'll need this!)

### 3. Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub account if not already connected
3. Select repository: **`agrim1989/blog-portfolio`**
4. Click **"Connect"**

### 4. Configure Web Service

**Basic Settings:**
- **Name**: `blog-portfolio` (or your preferred name)
- **Environment**: **Docker** (or Python 3 - but ensure Python 3.12 is selected)
- **Region**: Same as database
- **Branch**: `main`
- **Root Directory**: (leave empty)

**Build & Start:**
- **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Python Version**: Make sure to select **Python 3.12.7** (not 3.13)

### 5. Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add:

1. **FLASK_ENV** = `production`
2. **SECRET_KEY** = (Generate one using: `python -c "import secrets; print(secrets.token_hex(32))"`)
3. **DATABASE_URL** = (Paste the Internal Database URL from step 2)

### 6. Deploy!

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for the first build
3. Your site will be live at: `https://blog-portfolio.onrender.com` (or your chosen name)

### 7. Initialize Database (Automatic!)

The app will automatically:
- Create all database tables
- Populate with your portfolio data
- Create admin user (username: `admin`, password: `admin123`)

**Note**: First deployment may take longer. After that, deployments are faster.

---

## 🔧 Troubleshooting

### App won't start?
- Check **Logs** tab in Render dashboard
- Verify all environment variables are set
- Ensure `gunicorn` is in requirements.txt ✅ (it is!)

### Database errors?
- Verify `DATABASE_URL` is correctly set
- Check PostgreSQL service is running
- Database auto-initializes on first run

### Can't access admin?
- Default credentials: `admin` / `admin123`
- Change password immediately after first login!

### Static files not loading?
- All static files are in Git ✅
- Check file paths in templates

---

## 📝 Important Notes

### Free Tier Limitations:
- ⏰ **Spins down after 15 minutes** of inactivity
- 🚀 First request after inactivity takes ~30 seconds
- 💾 **750 hours/month** free (enough for personal use)
- 🗄️ **PostgreSQL**: 1GB storage, 90-day retention

### Security:
- ✅ Change admin password immediately
- ✅ Use strong SECRET_KEY (32+ characters)
- ✅ HTTPS is automatic on Render

### Custom Domain (Optional):
1. Go to Web Service → **Settings** → **Custom Domains**
2. Add your domain
3. Update DNS records as instructed

---

## 🎉 You're Done!

Your portfolio is now live! Share your URL: `https://your-app-name.onrender.com`

**Admin Panel**: `https://your-app-name.onrender.com/admin/login`

---

## Need Help?

- Check Render logs for errors
- Verify environment variables
- Test locally first: `python app.py`
- Render Status: https://status.render.com

Happy deploying! 🚀

