# Quick Start Guide

## 🚀 Start the Server

### Step 1: Open Terminal
Open Terminal (or your command line) and navigate to the project:
```bash
cd /Users/agrimsharma/Blog-Portfolio
```

### Step 2: Activate Virtual Environment (if using one)
```bash
source venv/bin/activate
```

### Step 3: Start Flask Server
```bash
python3 app.py
```

### Step 4: Open in Browser
You should see output like:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Then open your browser and go to:
- **Homepage:** http://127.0.0.1:5000/
- **Contact Page:** http://127.0.0.1:5000/contact
- **Resume:** http://127.0.0.1:5000/resume
- **Blog:** http://127.0.0.1:5000/blog
- **Admin Login:** http://127.0.0.1:5000/admin/login

## 🔧 Troubleshooting

### Port Already in Use?
If you see "Address already in use", run:
```bash
# Kill the process on port 5000
lsof -ti:5000 | xargs kill -9

# Then start again
python3 app.py
```

### Import Errors?
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Database Issues?
The database is created automatically. If you need to reset:
```bash
# Delete the database file
rm instance/site.db

# Restart the server (it will recreate the database)
python3 app.py
```

### Check Everything is Working
Run the health check:
```bash
python3 check_server.py
```

## ✅ What You Should See

When the server starts successfully, you'll see:
- Terminal shows "Running on http://127.0.0.1:5000"
- Browser can access all pages
- No error messages in terminal

## 🛑 To Stop the Server

Press `CTRL + C` in the terminal where the server is running.
