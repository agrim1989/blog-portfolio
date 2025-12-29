# Flask Portfolio & Blog Website

A modern Flask-based website featuring a portfolio/resume section and a blog with content management through an admin interface. Blog posts support text, images, and videos (both embedded URLs and file uploads).

## Features

- **Portfolio Section**: Display your professional profile, education, experience, skills, projects, and achievements
- **Blog Section**: Full-featured blog with categories, tags, pagination, and search
- **Admin Interface**: Manage all blog content through a secure admin panel
- **Video Support**: Both embedded videos (YouTube/Vimeo) and uploaded video files
- **Rich Text Editor**: TinyMCE integration for blog post content
- **Responsive Design**: Modern, mobile-friendly UI

## Installation

1. **Activate your virtual environment**:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file** in the project root:
   ```
   SECRET_KEY=your-secret-key-here-make-it-long-and-random
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

   **Note**: For production, generate a secure secret key:
   ```python
   from secrets import token_hex
   print(token_hex(32))
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

   The database will be automatically created on first run, along with a default admin user:
   - Username: `admin`
   - Password: `admin123`
   
   **⚠️ IMPORTANT: Change the default admin password in production!**

5. **Access the website**:
   - Homepage: http://127.0.0.1:5000/
   - Admin Panel: http://127.0.0.1:5000/admin/login

## Project Structure

```
Blog-Portfolio/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── forms.py              # WTForms for admin
├── utils.py              # Utility functions (file uploads, etc.)
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (create this)
├── instance/             # Instance folder (database created here)
│   └── site.db          # SQLite database
├── static/               # Static files
│   ├── css/
│   │   └── main.css    # Main stylesheet
│   └── uploads/         # User uploaded files
│       ├── images/
│       └── videos/
└── templates/            # Jinja2 templates
    ├── base.html
    ├── portfolio/
    ├── blog/
    ├── admin/
    └── errors/
```

## URL Structure

- `/` - Portfolio homepage
- `/resume` - Full resume page
- `/blog` - Blog post list
- `/blog/<slug>` - Individual blog post
- `/blog/category/<slug>` - Posts by category
- `/blog/tag/<slug>` - Posts by tag
- `/admin/login` - Admin login
- `/admin/dashboard` - Admin dashboard
- `/admin/posts` - Manage posts
- `/admin/posts/new` - Create new post
- `/admin/posts/<id>/edit` - Edit post

## Admin Features

### Creating Blog Posts

1. Log in to the admin panel
2. Click "Create New Post"
3. Fill in the form:
   - **Title**: Post title (slug auto-generated if not provided)
   - **Content**: Use the rich text editor (TinyMCE)
   - **Featured Image**: Upload an image (jpg, png, gif, webp)
   - **Video URL**: Enter YouTube or Vimeo URL for embedded videos
   - **Video File**: Upload a video file (mp4, webm, mov, avi) - Max 100MB
   - **Category**: Select or leave empty
   - **Tags**: Comma-separated list
   - **Status**: Draft or Published
4. Click "Create Post"

### Video Support

The blog supports two types of videos:

1. **Embedded Videos**: 
   - Enter a YouTube or Vimeo URL in the "Video URL" field
   - The system automatically converts it to an embed URL
   - Example: `https://www.youtube.com/watch?v=VIDEO_ID`

2. **Uploaded Videos**:
   - Upload video files directly (mp4, webm, mov, avi)
   - Maximum file size: 100MB
   - Videos are stored in `static/uploads/videos/`
   - Played using HTML5 video player

Both types can be used in the same post if needed.

## Technologies Used

- **Flask 3.0**: Web framework
- **SQLAlchemy**: ORM for database operations
- **Flask-Login**: User authentication
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation
- **Werkzeug**: Password hashing
- **Pillow**: Image processing
- **TinyMCE**: Rich text editor (via CDN)
- **SQLite**: Database (development)

## Customization

### Styling
- Main CSS file: `static/css/main.css`
- Modify CSS variables in `:root` to change color scheme

### Database Models
- Portfolio models: `models.py`
- Blog models: `models.py`

### Templates
- Base template: `templates/base.html`
- Portfolio templates: `templates/portfolio/`
- Blog templates: `templates/blog/`
- Admin templates: `templates/admin/`

## Production Deployment

Before deploying to production:

1. Set `DEBUG = False` in config or `.env`
2. Set a secure `SECRET_KEY` in environment variables
3. Configure `ALLOWED_HOSTS` properly
4. Set up a production database (PostgreSQL recommended)
5. Configure static file serving (WhiteNoise or CDN)
6. Set up media file serving
7. Use a production WSGI server (gunicorn/uwsgi)
8. Set up nginx as reverse proxy
9. Enable HTTPS with SSL certificate
10. **Change the default admin password!**

### Running with Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Security Notes

- Default admin credentials are for development only
- Change admin password before deploying
- Use strong SECRET_KEY in production
- Enable HTTPS
- Validate all file uploads (already implemented)
- Limit file sizes (configured to 100MB max)

## License

This project is open source and available for personal and commercial use.

## Support

For issues or questions, please refer to the Flask documentation or create an issue in the repository.

