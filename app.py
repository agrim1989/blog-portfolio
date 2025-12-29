from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import config_dict
from models import db, User, Profile, Education, Experience, Skill, Project, Achievement, Category, Tag, Post
from forms import LoginForm, PostForm, CategoryForm, TagForm, ContactForm
from utils import save_uploaded_file, delete_file, get_video_embed_url
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_object(config_dict['default'])

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Please log in to access this page.'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Create upload directories
with app.app_context():
    os.makedirs(app.config['UPLOAD_IMAGE_FOLDER'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_VIDEO_FOLDER'], exist_ok=True)
    os.makedirs(app.config['UPLOAD_RESUME_FOLDER'], exist_ok=True)


# ==================== PORTFOLIO ROUTES ====================

@app.route('/')
def index():
    """Portfolio homepage"""
    profile = Profile.query.first()
    featured_projects = Project.query.filter_by(featured=True).order_by(Project.date.desc()).limit(3).all()
    all_skills = Skill.query.order_by(Skill.category, Skill.order, Skill.name).all()
    
    # Filter to show only the most relevant skills for homepage
    # Core frameworks: Python, Django, Flask, FastAPI
    # AI/ML: Generative AI, RAG, LLM Fine-tuning, OpenAI API
    # Databases: MySQL, SQL
    # Tools: AWS, Docker, Git
    relevant_skill_names = [
        'Python', 'Django', 'Flask', 'FastAPI',
        'Generative AI', 'RAG (Retrieval-Augmented Generation)', 'LLM Fine-tuning', 'OpenAI API',
        'MySQL', 'SQL',
        'AWS', 'Docker', 'Git'
    ]
    
    skills = [s for s in all_skills if s.name in relevant_skill_names]
    
    # Group skills by category
    skills_by_category = {}
    for skill in skills:
        category_display = dict(Skill.SKILL_CATEGORIES).get(skill.category, skill.category)
        if category_display not in skills_by_category:
            skills_by_category[category_display] = []
        skills_by_category[category_display].append(skill)
    
    return render_template('portfolio/index.html', 
                         profile=profile,
                         featured_projects=featured_projects,
                         skills_by_category=skills_by_category)


@app.route('/resume')
def resume():
    """Full resume page"""
    profile = Profile.query.first()
    educations = Education.query.order_by(Education.order.desc(), Education.start_date.desc()).all()
    experiences = Experience.query.order_by(Experience.current.desc(), Experience.start_date.desc()).all()
    skills = Skill.query.order_by(Skill.category, Skill.order, Skill.name).all()
    projects = Project.query.order_by(Project.date.desc()).all()
    all_achievements = Achievement.query.order_by(Achievement.order.asc(), Achievement.date.desc()).all()
    
    # Separate certifications (order < 10) from achievements (order >= 10)
    certifications = [a for a in all_achievements if a.order < 10]
    achievements = [a for a in all_achievements if a.order >= 10]
    
    # Get freelance work (projects with featured=False, ordered by date)
    freelance_work = [p for p in projects if not p.featured]
    freelance_work.sort(key=lambda x: x.date, reverse=True)
    
    # Group skills by category
    skills_by_category = {}
    for skill in skills:
        category_display = dict(Skill.SKILL_CATEGORIES).get(skill.category, skill.category)
        if category_display not in skills_by_category:
            skills_by_category[category_display] = []
        skills_by_category[category_display].append(skill)
    
    return render_template('portfolio/resume.html',
                         profile=profile,
                         educations=educations,
                         experiences=experiences,
                         skills_by_category=skills_by_category,
                         projects=projects,
                         certifications=certifications,
                         achievements=achievements,
                         freelance_work=freelance_work)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    profile = Profile.query.first()
    form = ContactForm()
    
    if form.validate_on_submit():
        # Create mailto link with form data
        from urllib.parse import quote
        
        name = form.name.data
        email = form.email.data
        subject = form.subject.data
        message = form.message.data
        
        # URL encode the email content
        email_body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        recipient_email = profile.email if profile and profile.email else 'your-email@example.com'
        mailto_link = f"mailto:{recipient_email}?subject={quote(subject)}&body={quote(email_body)}"
        
        # Redirect to mailto link
        return redirect(mailto_link)
    
    return render_template('portfolio/contact.html', profile=profile, form=form)


# ==================== BLOG ROUTES ====================

def check_and_publish_scheduled_posts():
    """Check for scheduled posts that should be published"""
    scheduled_posts = Post.query.filter_by(status='scheduled').all()
    now = datetime.utcnow()
    for post in scheduled_posts:
        if post.published_date and post.published_date <= now:
            post.status = 'published'
            db.session.commit()


@app.route('/blog')
def blog_list():
    """Blog post list with pagination and filters"""
    # Check and auto-publish scheduled posts
    check_and_publish_scheduled_posts()
    
    page = request.args.get('page', 1, type=int)
    category_slug = request.args.get('category')
    tag_slug = request.args.get('tag')
    search_query = request.args.get('search')
    
    # Base query for published posts
    query = Post.query.filter_by(status='published')
    
    # Filter by category
    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first_or_404()
        query = query.filter_by(category_id=category.id)
    else:
        category = None
    
    # Filter by tag
    if tag_slug:
        tag = Tag.query.filter_by(slug=tag_slug).first_or_404()
        query = query.filter(Post.tags.contains(tag))
    else:
        tag = None
    
    # Search
    if search_query:
        query = query.filter(
            db.or_(
                Post.title.contains(search_query),
                Post.content.contains(search_query),
                Post.excerpt.contains(search_query)
            )
        )
    
    # Order and paginate
    posts = query.order_by(Post.published_date.desc(), Post.created_date.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False
    )
    
    categories = Category.query.all()
    tags = Tag.query.all()
    
    return render_template('blog/post_list.html',
                         posts=posts,
                         categories=categories,
                         tags=tags,
                         selected_category=category,
                         selected_tag=tag,
                         search_query=search_query)


@app.route('/blog/<slug>')
def blog_detail(slug):
    """Individual blog post detail"""
    # Check and auto-publish scheduled posts
    check_and_publish_scheduled_posts()
    
    post = Post.query.filter_by(slug=slug, status='published').first_or_404()
    
    # Increment view count
    post.views_count += 1
    db.session.commit()
    
    # Get related posts (same category, excluding current)
    related_posts = Post.query.filter(
        Post.category_id == post.category_id,
        Post.status == 'published',
        Post.id != post.id
    ).order_by(Post.published_date.desc()).limit(3).all()
    
    # Get video embed URL if video_url exists
    video_embed_url = get_video_embed_url(post.video_url) if post.video_url else None
    
    return render_template('blog/post_detail.html',
                         post=post,
                         related_posts=related_posts,
                         video_embed_url=video_embed_url)


@app.route('/blog/category/<slug>')
def blog_category(slug):
    """Posts filtered by category"""
    category = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    posts = Post.query.filter_by(
        category_id=category.id,
        status='published'
    ).order_by(Post.published_date.desc(), Post.created_date.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False
    )
    
    categories = Category.query.all()
    tags = Tag.query.all()
    
    return render_template('blog/post_list.html',
                         posts=posts,
                         categories=categories,
                         tags=tags,
                         selected_category=category)


@app.route('/blog/tag/<slug>')
def blog_tag(slug):
    """Posts filtered by tag"""
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    
    posts = Post.query.filter(
        Post.tags.contains(tag),
        Post.status == 'published'
    ).order_by(Post.published_date.desc(), Post.created_date.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False
    )
    
    categories = Category.query.all()
    tags = Tag.query.all()
    
    return render_template('blog/post_list.html',
                         posts=posts,
                         categories=categories,
                         tags=tags,
                         selected_tag=tag)


# ==================== ADMIN ROUTES ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if user.check_password(form.password.data):
                login_user(user, remember=True)
                next_page = request.args.get('next')
                flash('Login successful!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid password. Please try again.', 'error')
        else:
            flash('User not found. Please check your username.', 'error')
    
    return render_template('admin/login.html', form=form)


@app.route('/admin/logout')
@login_required
def admin_logout():
    """Admin logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    total_posts = Post.query.count()
    published_posts = Post.query.filter_by(status='published').count()
    draft_posts = Post.query.filter_by(status='draft').count()
    total_views = db.session.query(db.func.sum(Post.views_count)).scalar() or 0
    
    return render_template('admin/dashboard.html',
                         total_posts=total_posts,
                         published_posts=published_posts,
                         draft_posts=draft_posts,
                         total_views=total_views)


@app.route('/admin/posts')
@login_required
def admin_posts():
    """List all posts (admin) with search and sorting"""
    # Check and auto-publish scheduled posts
    check_and_publish_scheduled_posts()
    
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status')
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort', 'created')
    sort_order = request.args.get('order', 'desc')
    
    query = Post.query
    
    # Apply status filter
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    # Apply search filter
    if search_query:
        query = query.filter(Post.title.ilike(f'%{search_query}%'))
    
    # Apply sorting
    if sort_by == 'title':
        if sort_order == 'asc':
            query = query.order_by(Post.title.asc())
        else:
            query = query.order_by(Post.title.desc())
    elif sort_by == 'status':
        if sort_order == 'asc':
            query = query.order_by(Post.status.asc())
        else:
            query = query.order_by(Post.status.desc())
    elif sort_by == 'views':
        if sort_order == 'asc':
            query = query.order_by(Post.views_count.asc())
        else:
            query = query.order_by(Post.views_count.desc())
    else:  # created (default)
        if sort_order == 'asc':
            query = query.order_by(Post.created_date.asc())
        else:
            query = query.order_by(Post.created_date.desc())
    
    posts = query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/post_list.html', 
                         posts=posts, 
                         status_filter=status_filter,
                         search_query=search_query,
                         sort_by=sort_by,
                         sort_order=sort_order)


@app.route('/admin/posts/new', methods=['GET', 'POST'])
@login_required
def admin_post_new():
    """Create new post"""
    form = PostForm()
    form.category_id.choices = [(0, 'No Category')] + [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        post = Post()
        post.title = form.title.data
        post.slug = form.slug.data or None  # Will be auto-generated if empty
        post.content = form.content.data
        post.excerpt = form.excerpt.data
        post.author_id = current_user.id
        post.status = form.status.data
        post.video_url = form.video_url.data
        post.meta_description = form.meta_description.data
        post.meta_keywords = form.meta_keywords.data
        
        if form.category_id.data and form.category_id.data != 0:
            post.category_id = form.category_id.data
        
        # Handle featured image upload
        if form.featured_image.data:
            filename = save_uploaded_file(form.featured_image.data, 'image')
            if filename:
                if post.featured_image:
                    delete_file(post.featured_image, 'image')
                post.featured_image = filename
        
        # Handle video file upload
        if form.video_file.data:
            filename = save_uploaded_file(form.video_file.data, 'video')
            if filename:
                if post.video_file:
                    delete_file(post.video_file, 'video')
                post.video_file = filename
        
        # Handle tags
        if form.tags.data:
            tag_names = [t.strip() for t in form.tags.data.split(',')]
            post.tags = []
            for tag_name in tag_names:
                if tag_name:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                    post.tags.append(tag)
        
        # Handle scheduled posts
        if form.status.data == 'scheduled' and form.scheduled_date.data:
            try:
                scheduled_datetime = datetime.strptime(form.scheduled_date.data, '%Y-%m-%d %H:%M:%S')
                # Only set if scheduled date is in the future
                if scheduled_datetime > datetime.utcnow():
                    post.published_date = scheduled_datetime
                else:
                    flash('Scheduled date must be in the future. Post saved as draft.', 'warning')
                    post.status = 'draft'
            except:
                flash('Invalid scheduled date format. Post saved as draft.', 'warning')
                post.status = 'draft'
        # Set published date if publishing
        elif form.status.data == 'published' and form.published_date.data:
            try:
                post.published_date = datetime.strptime(form.published_date.data, '%Y-%m-%d %H:%M:%S')
            except:
                post.published_date = datetime.utcnow()
        elif form.status.data == 'published' and not post.published_date:
            post.published_date = datetime.utcnow()
        
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('admin_posts'))
    
    return render_template('admin/post_create.html', form=form)


@app.route('/admin/posts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_post_edit(id):
    """Edit existing post"""
    post = Post.query.get_or_404(id)
    form = PostForm(obj=post)
    form.category_id.choices = [(0, 'No Category')] + [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        post.title = form.title.data
        if form.slug.data:
            post.slug = form.slug.data
        post.content = form.content.data
        post.excerpt = form.excerpt.data
        post.status = form.status.data
        post.video_url = form.video_url.data
        post.meta_description = form.meta_description.data
        post.meta_keywords = form.meta_keywords.data
        
        if form.category_id.data and form.category_id.data != 0:
            post.category_id = form.category_id.data
        else:
            post.category_id = None
        
        # Handle featured image upload
        if form.featured_image.data:
            filename = save_uploaded_file(form.featured_image.data, 'image')
            if filename:
                if post.featured_image:
                    delete_file(post.featured_image, 'image')
                post.featured_image = filename
        
        # Handle video file upload
        if form.video_file.data:
            filename = save_uploaded_file(form.video_file.data, 'video')
            if filename:
                if post.video_file:
                    delete_file(post.video_file, 'video')
                post.video_file = filename
        
        # Handle tags
        if form.tags.data:
            tag_names = [t.strip() for t in form.tags.data.split(',')]
            post.tags = []
            for tag_name in tag_names:
                if tag_name:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.session.add(tag)
                    post.tags.append(tag)
        else:
            post.tags = []
        
        # Handle scheduled posts
        if form.status.data == 'scheduled' and form.scheduled_date.data:
            try:
                scheduled_datetime = datetime.strptime(form.scheduled_date.data, '%Y-%m-%d %H:%M:%S')
                # Only set if scheduled date is in the future
                if scheduled_datetime > datetime.utcnow():
                    post.published_date = scheduled_datetime
                else:
                    flash('Scheduled date must be in the future. Post saved as draft.', 'warning')
                    post.status = 'draft'
            except:
                flash('Invalid scheduled date format. Post saved as draft.', 'warning')
                post.status = 'draft'
        # Set published date if publishing
        elif form.status.data == 'published' and form.published_date.data:
            try:
                post.published_date = datetime.strptime(form.published_date.data, '%Y-%m-%d %H:%M:%S')
            except:
                if not post.published_date:
                    post.published_date = datetime.utcnow()
        elif form.status.data == 'published' and not post.published_date:
            post.published_date = datetime.utcnow()
        
        # Handle views count
        if form.views_count.data is not None:
            post.views_count = form.views_count.data
        
        post.updated_date = datetime.utcnow()
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('admin_posts'))
    
    # Pre-populate tags
    if post.tags:
        form.tags.data = ', '.join([tag.name for tag in post.tags])
    
    # Format published date
    if post.published_date:
        form.published_date.data = post.published_date.strftime('%Y-%m-%d %H:%M:%S')
    
    # Pre-populate views count
    form.views_count.data = post.views_count
    
    return render_template('admin/post_edit.html', form=form, post=post)


@app.route('/admin/posts/<int:id>/delete', methods=['POST'])
@login_required
def admin_post_delete(id):
    """Delete post"""
    post = Post.query.get_or_404(id)
    
    # Delete associated files
    if post.featured_image:
        delete_file(post.featured_image, 'image')
    if post.video_file:
        delete_file(post.video_file, 'video')
    
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('admin_posts'))


# Serve uploaded files
@app.route('/uploads/<file_type>/<filename>')
def uploaded_file(file_type, filename):
    """Serve uploaded files"""
    if file_type == 'images':
        directory = app.config['UPLOAD_IMAGE_FOLDER']
        # Check if it's a PDF resume file (PDFs might be stored in images folder)
        if filename.endswith('.pdf'):
            # Try images folder first, then resumes folder
            if os.path.exists(os.path.join(app.config['UPLOAD_IMAGE_FOLDER'], filename)):
                directory = app.config['UPLOAD_IMAGE_FOLDER']
            elif os.path.exists(os.path.join(app.config['UPLOAD_RESUME_FOLDER'], filename)):
                directory = app.config['UPLOAD_RESUME_FOLDER']
            else:
                directory = app.config['UPLOAD_IMAGE_FOLDER']
            
            response = send_from_directory(directory, filename)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    elif file_type == 'videos':
        directory = app.config['UPLOAD_VIDEO_FOLDER']
    elif file_type == 'resumes':
        directory = app.config['UPLOAD_RESUME_FOLDER']
        if filename.endswith('.pdf'):
            response = send_from_directory(directory, filename)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    else:
        return "Invalid file type", 404
    
    return send_from_directory(directory, filename)


@app.route('/download-resume')
def download_resume():
    """Download resume PDF from root directory"""
    resume_filename = 'Agrim Resume ATS.pdf'
    resume_path = os.path.join(app.root_path, resume_filename)
    
    if os.path.exists(resume_path):
        return send_from_directory(app.root_path, resume_filename, as_attachment=True)
    else:
        flash('Resume file not found', 'error')
        return redirect(url_for('index'))


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


# Initialize database
def init_db():
    """Create database tables and default admin user"""
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: username='admin', password='admin123'")


if __name__ == '__main__':
    init_db()
    app.run(debug=True)

