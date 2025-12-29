"""
Script to upload profile image
Usage: python3 upload_profile_image.py <image_path>
"""
import sys
import os
from app import app, db
from models import Profile
from utils import save_uploaded_file
from werkzeug.datastructures import FileStorage

def upload_profile_image(image_path):
    """Upload profile image"""
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        return False
    
    with app.app_context():
        profile = Profile.query.first()
        if not profile:
            print("Error: No profile found. Please run populate_portfolio.py first.")
            return False
        
        # Create a FileStorage object
        with open(image_path, 'rb') as f:
            file_storage = FileStorage(
                stream=f,
                filename=os.path.basename(image_path),
                content_type='image/jpeg'
            )
            
            # Save the uploaded file
            filename = save_uploaded_file(file_storage, 'image')
            
            if filename:
                # Update profile
                if profile.profile_image:
                    # Delete old image
                    from utils import delete_file
                    delete_file(profile.profile_image, 'image')
                
                profile.profile_image = filename
                db.session.commit()
                print(f"✅ Profile image uploaded successfully!")
                print(f"   Image saved as: {filename}")
                print(f"   Access at: /uploads/images/{filename}")
                return True
            else:
                print("Error: Failed to save image file")
                return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 upload_profile_image.py <image_path>")
        print(f"Example: python3 upload_profile_image.py 1712210182705.jpeg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    upload_profile_image(image_path)

