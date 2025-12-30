"""
WSGI entry point for production deployment
"""
from app import app, db
from populate_portfolio import populate_database

# Initialize database tables and populate on startup
with app.app_context():
    try:
        # Create all tables
        db.create_all()
        print("Database tables created/verified")
        
        # Always run populate_database to ensure data is up to date
        # This will update existing records and add new ones
        try:
            populate_database()
            print("Database populated/updated successfully!")
        except Exception as e:
            print(f"Error populating database: {e}")
            import traceback
            traceback.print_exc()
    except Exception as e:
        print(f"Database initialization error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    app.run()

