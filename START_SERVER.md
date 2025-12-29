# How to Start the Flask Server

## Quick Start

1. **Activate Virtual Environment** (if using one):
   ```bash
   source venv/bin/activate
   ```

2. **Start the Flask Server**:
   ```bash
   python3 app.py
   ```

3. **Open in Browser**:
   - Homepage: http://127.0.0.1:5000/
   - Contact Page: http://127.0.0.1:5000/contact
   - Resume: http://127.0.0.1:5000/resume
   - Blog: http://127.0.0.1:5000/blog
   - Admin: http://127.0.0.1:5000/admin/login

## Troubleshooting

### If you see "Port already in use":
```bash
# Find and kill the process using port 5000
lsof -ti:5000 | xargs kill -9

# Or use a different port
python3 app.py --port 5001
```

### If you see import errors:
```bash
# Make sure you're in the project directory
cd /Users/agrimsharma/Blog-Portfolio

# Install dependencies
pip install -r requirements.txt
```

### If database errors occur:
```bash
# The database will be created automatically on first run
# If you need to reset it, delete instance/site.db and restart
```

## Expected Output

When you run `python3 app.py`, you should see:
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

Then open http://127.0.0.1:5000 in your browser!

