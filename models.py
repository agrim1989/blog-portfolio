from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import event
import re

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for admin authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set password - using pbkdf2:sha256 for compatibility"""
        try:
            # Try with explicit method first (for older Python versions)
            self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        except (AttributeError, ValueError):
            # Fallback to default method if explicit method fails
            self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Profile(db.Model):
    """Personal profile information"""
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(200))
    bio = db.Column(db.Text)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    profile_image = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(255))
    github_url = db.Column(db.String(255))
    website_url = db.Column(db.String(255))
    resume_file = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    educations = db.relationship('Education', backref='profile', lazy='dynamic', cascade='all, delete-orphan')
    experiences = db.relationship('Experience', backref='profile', lazy='dynamic', cascade='all, delete-orphan')
    skills = db.relationship('Skill', backref='profile', lazy='dynamic', cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='profile', lazy='dynamic', cascade='all, delete-orphan')
    achievements = db.relationship('Achievement', backref='profile', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Profile {self.name}>'


class Education(db.Model):
    """Educational background"""
    __tablename__ = 'educations'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    institution = db.Column(db.String(200), nullable=False)
    degree = db.Column(db.String(200), nullable=False)
    field = db.Column(db.String(200))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Education {self.degree} at {self.institution}>'


class Experience(db.Model):
    """Work experience"""
    __tablename__ = 'experiences'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    position = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Experience {self.position} at {self.company}>'


class Skill(db.Model):
    """Skills"""
    __tablename__ = 'skills'
    
    SKILL_CATEGORIES = [
        ('programming', 'Programming Languages'),
        ('framework', 'Frameworks & Libraries'),
        ('database', 'Databases'),
        ('tools', 'Tools & Technologies'),
        ('soft', 'Soft Skills'),
        ('other', 'Other'),
    ]
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(20), default='other')
    proficiency_level = db.Column(db.Integer, default=50)
    order = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Skill {self.name}>'


class Project(db.Model):
    """Portfolio projects"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    url = db.Column(db.String(255))
    github_url = db.Column(db.String(255))
    technologies = db.Column(db.String(500))
    date = db.Column(db.Date)
    featured = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    
    def get_technologies_list(self):
        """Return technologies as a list"""
        if self.technologies:
            return [tech.strip() for tech in self.technologies.split(',')]
        return []
    
    def __repr__(self):
        return f'<Project {self.title}>'


class Achievement(db.Model):
    """Achievements, awards, and certifications"""
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date, nullable=False)
    issuer = db.Column(db.String(200))
    certificate_url = db.Column(db.String(255))
    order = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Achievement {self.title}>'


class Category(db.Model):
    """Blog categories"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    posts = db.relationship('Post', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Tag(db.Model):
    """Blog tags"""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Tag {self.name}>'


# Association table for many-to-many relationship between Post and Tag
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class Post(db.Model):
    """Blog posts"""
    __tablename__ = 'posts'
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(500))
    featured_image = db.Column(db.String(255))
    video_url = db.Column(db.String(500))  # For embedded videos (YouTube, Vimeo, etc.)
    video_file = db.Column(db.String(255))  # For uploaded video files
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    status = db.Column(db.String(10), default='draft')
    published_date = db.Column(db.DateTime)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    views_count = db.Column(db.Integer, default=0)
    meta_description = db.Column(db.String(160))
    meta_keywords = db.Column(db.String(255))
    
    # Many-to-many relationship with Tag
    tags = db.relationship('Tag', secondary=post_tags, lazy='subquery', backref=db.backref('posts', lazy=True))
    
    def get_reading_time(self):
        """Estimate reading time in minutes"""
        word_count = len(self.content.split())
        reading_time = max(1, round(word_count / 200))  # Average reading speed: 200 words per minute
        return reading_time
    
    def __repr__(self):
        return f'<Post {self.title}>'


def slugify(text):
    """Generate URL-friendly slug from text"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


# Event listeners to auto-generate slugs
@event.listens_for(Category, 'before_insert')
@event.listens_for(Category, 'before_update')
def generate_category_slug(mapper, connection, target):
    if not target.slug:
        target.slug = slugify(target.name)


@event.listens_for(Tag, 'before_insert')
@event.listens_for(Tag, 'before_update')
def generate_tag_slug(mapper, connection, target):
    if not target.slug:
        target.slug = slugify(target.name)


@event.listens_for(Post, 'before_insert')
@event.listens_for(Post, 'before_update')
def generate_post_slug(mapper, connection, target):
    if not target.slug:
        target.slug = slugify(target.title)

