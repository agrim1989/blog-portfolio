"""
WSGI entry point for production deployment
"""
from app import app, db
from populate_portfolio import populate_database

# Initialize database tables
with app.app_context():
    db.create_all()
    # Check if database is empty and populate if needed
    from models import Profile
    if not Profile.query.first():
        try:
            populate_database()
        except Exception as e:
            print(f"Error populating database: {e}")

if __name__ == "__main__":
    app.run()

