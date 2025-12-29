import os
from werkzeug.utils import secure_filename
from flask import current_app
from PIL import Image


def allowed_file(filename, file_type='image'):
    """Check if file extension is allowed"""
    if file_type == 'image':
        allowed = current_app.config['ALLOWED_IMAGE_EXTENSIONS']
    elif file_type == 'video':
        allowed = current_app.config['ALLOWED_VIDEO_EXTENSIONS']
    else:
        return False
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def save_uploaded_file(file, file_type='image'):
    """Save uploaded file and return filename"""
    if file and allowed_file(file.filename, file_type):
        filename = secure_filename(file.filename)
        # Add timestamp to avoid conflicts
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        
        if file_type == 'image':
            upload_folder = current_app.config['UPLOAD_IMAGE_FOLDER']
        elif file_type == 'video':
            upload_folder = current_app.config['UPLOAD_VIDEO_FOLDER']
        else:
            return None
        
        # Ensure upload directory exists
        os.makedirs(upload_folder, exist_ok=True)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # For images, optionally create thumbnail
        if file_type == 'image':
            try:
                img = Image.open(filepath)
                # Resize if too large (max 1920px width)
                if img.width > 1920:
                    ratio = 1920 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((1920, new_height), Image.Resampling.LANCZOS)
                    img.save(filepath, optimize=True, quality=85)
            except Exception as e:
                print(f"Error processing image: {e}")
        
        return filename
    return None


def delete_file(filename, file_type='image'):
    """Delete uploaded file"""
    try:
        if file_type == 'image':
            upload_folder = current_app.config['UPLOAD_IMAGE_FOLDER']
        elif file_type == 'video':
            upload_folder = current_app.config['UPLOAD_VIDEO_FOLDER']
        else:
            return False
        
        filepath = os.path.join(upload_folder, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        print(f"Error deleting file: {e}")
    return False


def get_video_embed_url(url):
    """Convert YouTube/Vimeo URL to embed URL"""
    if not url:
        return None
    
    # YouTube
    if 'youtube.com/watch' in url or 'youtu.be' in url:
        if 'youtube.com/watch' in url:
            video_id = url.split('v=')[1].split('&')[0]
        else:  # youtu.be
            video_id = url.split('/')[-1]
        return f"https://www.youtube.com/embed/{video_id}"
    
    # Vimeo
    elif 'vimeo.com' in url:
        video_id = url.split('/')[-1]
        return f"https://player.vimeo.com/video/{video_id}"
    
    return url

