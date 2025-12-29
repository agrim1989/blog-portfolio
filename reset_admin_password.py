"""
Script to reset admin password
Usage: python3 reset_admin_password.py
"""
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def reset_admin_password():
    """Reset admin password to admin123"""
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            # Create admin user if doesn't exist
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            print("Creating new admin user...")
        else:
            print("Updating existing admin user...")
        
        # Reset password using pbkdf2:sha256 method
        try:
            admin.set_password('admin123')
        except:
            # Fallback if set_password fails
            admin.password_hash = generate_password_hash('admin123', method='pbkdf2:sha256')
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Admin password reset successfully!")
        print("   Username: admin")
        print("   Password: admin123")
        print("\nYou can now login at: http://127.0.0.1:5000/admin/login")

if __name__ == '__main__':
    reset_admin_password()

