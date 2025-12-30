"""
Migration script to add previous_post_id column to posts table
"""
import sqlite3
import os
from config import config_dict

# Get database URI
env = os.getenv('FLASK_ENV', 'development')
config = config_dict[env]
db_uri = config.SQLALCHEMY_DATABASE_URI

# Extract database path from SQLite URI
if db_uri.startswith('sqlite:///'):
    db_path = db_uri.replace('sqlite:///', '')
    # Handle absolute paths
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.path.dirname(__file__), db_path)
else:
    print(f"Database URI: {db_uri}")
    print("This migration script only works with SQLite databases.")
    exit(1)

print(f"Database path: {db_path}")

if not os.path.exists(db_path):
    print(f"Database file not found at: {db_path}")
    print("Creating database with new schema...")
    # Import app to trigger database creation
    from app import app, db
    with app.app_context():
        db.create_all()
    print("Database created successfully!")
    exit(0)

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if column already exists
    cursor.execute("PRAGMA table_info(posts)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'previous_post_id' in columns:
        print("Column 'previous_post_id' already exists. No migration needed.")
    else:
        print("Adding 'previous_post_id' column to posts table...")
        # Add the column
        cursor.execute("""
            ALTER TABLE posts 
            ADD COLUMN previous_post_id INTEGER 
            REFERENCES posts(id)
        """)
        conn.commit()
        print("Migration completed successfully!")
        print("Column 'previous_post_id' added to posts table.")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(posts)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'previous_post_id' in columns:
            print("✓ Verification: Column exists in database.")
        else:
            print("✗ Warning: Column may not have been added correctly.")
            
except sqlite3.Error as e:
    print(f"Error during migration: {e}")
    conn.rollback()
    exit(1)
finally:
    conn.close()

print("\nMigration script completed. You can now run populate_portfolio.py")

