from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, BooleanField, DateField, IntegerField, URLField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional, URL, NumberRange
from wtforms.widgets import TextArea


class LoginForm(FlaskForm):
    """Login form for admin"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])


class PostForm(FlaskForm):
    """Form for creating/editing blog posts"""
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    slug = StringField('Slug', validators=[Optional(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()], widget=TextArea())
    excerpt = TextAreaField('Excerpt', validators=[Optional(), Length(max=500)], widget=TextArea())
    featured_image = FileField('Featured Image', validators=[
        Optional(),
        FileAllowed(['png', 'jpg', 'jpeg', 'gif', 'webp'], 'Images only!')
    ])
    video_url = URLField('Video URL (YouTube/Vimeo)', validators=[Optional(), URL()])
    video_file = FileField('Upload Video', validators=[
        Optional(),
        FileAllowed(['mp4', 'webm', 'mov', 'avi'], 'Videos only!')
    ])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    tags = StringField('Tags (comma-separated)', validators=[Optional()])
    status = SelectField('Status', choices=[('draft', 'Draft'), ('published', 'Published'), ('scheduled', 'Scheduled')], default='draft')
    published_date = StringField('Published Date (YYYY-MM-DD HH:MM:SS)', validators=[Optional()])
    scheduled_date = StringField('Schedule Date & Time (YYYY-MM-DD HH:MM:SS)', validators=[Optional()], description='Set a future date/time to automatically publish this post')
    views_count = IntegerField('Views Count', validators=[Optional(), NumberRange(min=0)], default=0, description='Manually set the number of views for this post')
    meta_description = StringField('Meta Description', validators=[Optional(), Length(max=160)])
    meta_keywords = StringField('Meta Keywords', validators=[Optional(), Length(max=255)])


class CategoryForm(FlaskForm):
    """Form for creating/editing categories"""
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    slug = StringField('Slug', validators=[Optional(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()], widget=TextArea())


class TagForm(FlaskForm):
    """Form for creating/editing tags"""
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    slug = StringField('Slug', validators=[Optional(), Length(max=50)])


class ProfileForm(FlaskForm):
    """Form for profile information"""
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    title = StringField('Title', validators=[Optional(), Length(max=200)])
    bio = TextAreaField('Bio', validators=[Optional()], widget=TextArea())
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    profile_image = FileField('Profile Image', validators=[
        Optional(),
        FileAllowed(['png', 'jpg', 'jpeg', 'gif', 'webp'], 'Images only!')
    ])
    linkedin_url = URLField('LinkedIn URL', validators=[Optional(), URL()])
    github_url = URLField('GitHub URL', validators=[Optional(), URL()])
    website_url = URLField('Website URL', validators=[Optional(), URL()])
    resume_file = FileField('Resume File (PDF)', validators=[
        Optional(),
        FileAllowed(['pdf'], 'PDF files only!')
    ])


class EducationForm(FlaskForm):
    """Form for education entries"""
    institution = StringField('Institution', validators=[DataRequired(), Length(max=200)])
    degree = StringField('Degree', validators=[DataRequired(), Length(max=200)])
    field = StringField('Field', validators=[Optional(), Length(max=200)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional()], widget=TextArea())
    order = IntegerField('Order', validators=[Optional(), NumberRange(min=0)], default=0)


class ExperienceForm(FlaskForm):
    """Form for experience entries"""
    company = StringField('Company', validators=[DataRequired(), Length(max=200)])
    position = StringField('Position', validators=[DataRequired(), Length(max=200)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    current = BooleanField('Current Position')
    description = TextAreaField('Description', validators=[DataRequired()], widget=TextArea())
    order = IntegerField('Order', validators=[Optional(), NumberRange(min=0)], default=0)


class SkillForm(FlaskForm):
    """Form for skills"""
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    category = SelectField('Category', choices=[
        ('programming', 'Programming Languages'),
        ('framework', 'Frameworks & Libraries'),
        ('database', 'Databases'),
        ('tools', 'Tools & Technologies'),
        ('soft', 'Soft Skills'),
        ('other', 'Other'),
    ], default='other')
    proficiency_level = IntegerField('Proficiency Level (0-100)', validators=[
        DataRequired(), NumberRange(min=0, max=100)
    ], default=50)
    order = IntegerField('Order', validators=[Optional(), NumberRange(min=0)], default=0)


class ProjectForm(FlaskForm):
    """Form for projects"""
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()], widget=TextArea())
    image = FileField('Image', validators=[
        Optional(),
        FileAllowed(['png', 'jpg', 'jpeg', 'gif', 'webp'], 'Images only!')
    ])
    url = URLField('Project URL', validators=[Optional(), URL()])
    github_url = URLField('GitHub URL', validators=[Optional(), URL()])
    technologies = StringField('Technologies (comma-separated)', validators=[Optional(), Length(max=500)])
    date = DateField('Date', validators=[Optional()])
    featured = BooleanField('Featured')
    order = IntegerField('Order', validators=[Optional(), NumberRange(min=0)], default=0)


class AchievementForm(FlaskForm):
    """Form for achievements"""
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[Optional()], widget=TextArea())
    date = DateField('Date', validators=[DataRequired()])
    issuer = StringField('Issuer', validators=[Optional(), Length(max=200)])
    certificate_url = URLField('Certificate URL', validators=[Optional(), URL()])
    order = IntegerField('Order', validators=[Optional(), NumberRange(min=0)], default=0)


class ContactForm(FlaskForm):
    """Contact form"""
    name = StringField('Your Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Your Email', validators=[DataRequired(), Email(), Length(max=120)])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=2000)], widget=TextArea())

