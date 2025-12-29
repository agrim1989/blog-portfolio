#!/usr/bin/env python3
"""
Quick check script to verify the Flask app can start
"""
import sys
import os

print("=" * 50)
print("Flask App Health Check")
print("=" * 50)

# Check Python version
print(f"\n✓ Python version: {sys.version.split()[0]}")

# Check if we're in the right directory
if not os.path.exists('app.py'):
    print("\n❌ ERROR: app.py not found!")
    print("   Make sure you're in the Blog-Portfolio directory")
    sys.exit(1)
print("\n✓ Found app.py")

# Check dependencies
print("\nChecking dependencies...")
required_modules = ['flask', 'flask_sqlalchemy', 'flask_login', 'flask_wtf', 'werkzeug']
missing = []
for module in required_modules:
    try:
        __import__(module)
        print(f"  ✓ {module}")
    except ImportError:
        print(f"  ❌ {module} - MISSING")
        missing.append(module)

if missing:
    print(f"\n❌ Missing modules: {', '.join(missing)}")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

# Try to import the app
print("\nChecking app imports...")
try:
    from app import app
    print("  ✓ App imports successfully")
except Exception as e:
    print(f"  ❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check database
print("\nChecking database...")
try:
    with app.app_context():
        from models import Profile, db
        # Try to query
        profile = Profile.query.first()
        if profile:
            print(f"  ✓ Database connected - Profile found: {profile.name}")
        else:
            print("  ⚠ Database connected but no profile found")
            print("     Run: python3 populate_portfolio.py")
except Exception as e:
    print(f"  ❌ Database error: {e}")
    import traceback
    traceback.print_exc()

# Check templates
print("\nChecking templates...")
template_files = [
    'templates/base.html',
    'templates/portfolio/index.html',
    'templates/portfolio/contact.html',
    'templates/portfolio/resume.html'
]
for template in template_files:
    if os.path.exists(template):
        print(f"  ✓ {template}")
    else:
        print(f"  ❌ {template} - MISSING")

# Check static files
print("\nChecking static files...")
static_files = [
    'static/css/main.css',
    'static/js/main.js'
]
for static_file in static_files:
    if os.path.exists(static_file):
        print(f"  ✓ {static_file}")
    else:
        print(f"  ❌ {static_file} - MISSING")

print("\n" + "=" * 50)
print("✓ All checks passed! You can start the server with:")
print("  python3 app.py")
print("=" * 50)

