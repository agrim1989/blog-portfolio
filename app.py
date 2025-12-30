from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import config_dict
from models import db, User, Profile, Education, Experience, Skill, Project, Achievement, Category, Tag, Post, Course, CourseVideo, CourseSubscription
from forms import LoginForm, PostForm, CategoryForm, TagForm, ContactForm
from utils import save_uploaded_file, delete_file, get_video_embed_url
from datetime import datetime
import os
import razorpay
import hmac
import hashlib

app = Flask(__name__)
# Use production config if FLASK_ENV is set to production
env = os.getenv('FLASK_ENV', 'development')
if env == 'production':
    app.config.from_object(config_dict['production'])
else:
    app.config.from_object(config_dict['default'])

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()

# Initialize database on startup (for production)
def init_database():
    """Initialize database tables and populate on startup"""
    try:
        with app.app_context():
            # Test database connection first
            db.engine.connect()
            print(f"Database connected: {app.config['SQLALCHEMY_DATABASE_URI'][:20]}...")
            
            db.create_all()
            print("Database tables created/verified")
            
            # Always run populate_database to ensure data is up to date
            # This will update existing records and add new ones
            try:
                from populate_portfolio import populate_database
                populate_database()
                print("Database populated/updated successfully!")
            except Exception as e:
                print(f"Error populating database: {e}")
                import traceback
                traceback.print_exc()
    except Exception as e:
        print(f"Database initialization error: {e}")
        print(f"Database URL: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')[:50]}...")
        import traceback
        traceback.print_exc()

# Initialize database when app starts (only in production)
if os.getenv('FLASK_ENV') == 'production':
    init_database()
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


@app.route('/course/payment/create-order', methods=['POST'])
def create_payment_order():
    """Create Razorpay order for course payment"""
    try:
        data = request.get_json()
        course_id = data.get('course_id')
        email = data.get('email')
        name = data.get('name')
        phone = data.get('phone', '')
        
        if not course_id or not email or not name:
            return jsonify({'error': 'Missing required fields'}), 400
        
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Initialize Razorpay client
        razorpay_key_id = app.config.get('RAZORPAY_KEY_ID')
        razorpay_key_secret = app.config.get('RAZORPAY_KEY_SECRET')
        
        if not razorpay_key_id or not razorpay_key_secret:
            return jsonify({'error': 'Payment gateway not configured'}), 500
        
        client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))
        
        # Create order
        amount = int(course.price * 100)  # Convert to paise
        order_data = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'course_{course_id}_{datetime.utcnow().timestamp()}',
            'notes': {
                'course_id': course_id,
                'course_name': course.title,
                'email': email,
                'name': name
            }
        }
        
        order = client.order.create(data=order_data)
        
        # Create subscription record
        subscription = CourseSubscription(
            course_id=course_id,
            email=email,
            name=name,
            phone=phone,
            order_id=order['id'],
            amount=course.price,
            currency='INR',
            status='pending'
        )
        db.session.add(subscription)
        db.session.commit()
        
        return jsonify({
            'order_id': order['id'],
            'amount': amount,
            'currency': 'INR',
            'key_id': razorpay_key_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/course/payment/verify', methods=['POST'])
def verify_payment():
    """Verify Razorpay payment signature"""
    try:
        data = request.get_json()
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        
        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return jsonify({'error': 'Missing payment details'}), 400
        
        # Find subscription
        subscription = CourseSubscription.query.filter_by(order_id=razorpay_order_id).first()
        if not subscription:
            return jsonify({'error': 'Order not found'}), 404
        
        # Verify signature
        razorpay_key_secret = app.config.get('RAZORPAY_KEY_SECRET')
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            razorpay_key_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature != razorpay_signature:
            subscription.status = 'failed'
            db.session.commit()
            return jsonify({'error': 'Invalid payment signature'}), 400
        
        # Payment verified - update subscription
        subscription.payment_id = razorpay_payment_id
        subscription.status = 'completed'
        subscription.payment_method = data.get('payment_method', 'unknown')
        db.session.commit()
        
        # Set cookie to remember user
        response = make_response(jsonify({
            'success': True,
            'message': 'Payment successful! You now have access to all course videos.'
        }))
        response.set_cookie('user_email', subscription.email, max_age=31536000)  # 1 year
        
        return response
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/course/check-subscription', methods=['POST'])
def check_subscription():
    """Check if user has active subscription"""
    try:
        data = request.get_json()
        email = data.get('email')
        course_id = data.get('course_id')
        
        if not email or not course_id:
            return jsonify({'has_subscription': False})
        
        subscription = CourseSubscription.query.filter_by(
            course_id=course_id,
            email=email,
            status='completed'
        ).first()
        
        return jsonify({'has_subscription': subscription is not None})
    
    except Exception as e:
        return jsonify({'has_subscription': False, 'error': str(e)})


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
    
    # Get previous post if this is a continuation
    previous_post = None
    if post.previous_post_id:
        previous_post = Post.query.filter_by(id=post.previous_post_id, status='published').first()
    
    # Also check for prev query parameter (for navigation from other posts)
    prev_slug = request.args.get('prev')
    if prev_slug and not previous_post:
        previous_post = Post.query.filter_by(slug=prev_slug, status='published').first()
    
    # Get video embed URL if video_url exists
    video_embed_url = get_video_embed_url(post.video_url) if post.video_url else None
    
    return render_template('blog/post_detail.html',
                         post=post,
                         related_posts=related_posts,
                         previous_post=previous_post,
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


@app.route('/blog/topic/<topic_slug>')
def topic_detail(topic_slug):
    """Topic detail page"""
    # Get the Python Learning blog post for back navigation
    python_learning_post = Post.query.filter_by(slug='python-learning', status='published').first()
    
    # Define topic details
    topics_data = {
        # Python Basic Topics
        'introduction-to-python': {
            'title': 'Introduction to Python',
            'category': 'Python Basics',
            'image': 'https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=800&h=400&fit=crop&q=80',
            'content': '''
            <h2>What is Python?</h2>
            <p>Python is a high-level, interpreted programming language known for its simplicity and readability. Created by Guido van Rossum and first released in 1991, Python has become one of the most popular programming languages in the world.</p>
            
            <h3>Why Learn Python?</h3>
            <ul>
                <li><strong>Easy to Learn:</strong> Python has a simple syntax that is easy to read and write, making it perfect for beginners.</li>
                <li><strong>Versatile:</strong> Python can be used for web development, data science, artificial intelligence, automation, and more.</li>
                <li><strong>Large Community:</strong> Python has a huge community of developers who contribute to libraries and provide support.</li>
                <li><strong>High Demand:</strong> Python developers are in high demand across various industries.</li>
            </ul>
            
            <h3>Python's History</h3>
            <p>Python was conceived in the late 1980s and its implementation began in December 1989. The name "Python" comes from the British comedy group Monty Python, not from the snake.</p>
            
            <h3>Python Versions</h3>
            <p>Currently, Python 3.x is the recommended version. Python 2.x reached end-of-life in 2020. Always use Python 3 for new projects.</p>
            
            <h3>Your First Python Program</h3>
            <p>Let's write a simple "Hello, World!" program:</p>
            <pre><code class="language-python"># Hello, World! in Python
print("Hello, World!")

# Variables and basic operations
name = "Python"
version = 3.11
print(f"Welcome to {name} {version}!")</code></pre>
            '''
        },
        'variables-and-data-types': {
            'title': 'Variables and Data Types',
            'category': 'Python Basics',
            'image': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800&h=400&fit=crop&q=80',
            'content': '''
            <h2>Variables in Python</h2>
            <p>Variables are containers for storing data values. Unlike other programming languages, Python has no command for declaring a variable. A variable is created the moment you first assign a value to it.</p>
            
            <h3>Naming Variables</h3>
            <ul>
                <li>Variable names must start with a letter or underscore</li>
                <li>Can contain letters, numbers, and underscores</li>
                <li>Case-sensitive (age, Age, and AGE are different)</li>
                <li>Cannot use Python keywords as variable names</li>
            </ul>
            
            <h3>Data Types</h3>
            <p>Python has several built-in data types:</p>
            <ul>
                <li><strong>Numbers:</strong> int, float, complex</li>
                <li><strong>Strings:</strong> Text data enclosed in quotes</li>
                <li><strong>Booleans:</strong> True or False</li>
                <li><strong>Lists:</strong> Ordered, mutable collections</li>
                <li><strong>Tuples:</strong> Ordered, immutable collections</li>
                <li><strong>Dictionaries:</strong> Key-value pairs</li>
                <li><strong>Sets:</strong> Unordered collections of unique elements</li>
            </ul>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python"># Variables
name = "Alice"
age = 25
height = 5.9
is_student = True

# Data types
print(type(name))      # &lt;class 'str'&gt;
print(type(age))       # &lt;class 'int'&gt;
print(type(height))    # &lt;class 'float'&gt;
print(type(is_student)) # &lt;class 'bool'&gt;

# Type conversion
num_str = "42"
num_int = int(num_str)
num_float = float(num_str)
print(f"String: {num_str}, Integer: {num_int}, Float: {num_float}")</code></pre>
            '''
        },
        'operators-and-expressions': {
            'title': 'Operators and Expressions',
            'category': 'Python Basics',
            'image': None,
            'content': '''
            <h2>Operators in Python</h2>
            <p>Operators are special symbols that perform operations on variables and values. Python supports various types of operators.</p>
            
            <h3>Arithmetic Operators</h3>
            <ul>
                <li><strong>+</strong> Addition</li>
                <li><strong>-</strong> Subtraction</li>
                <li><strong>*</strong> Multiplication</li>
                <li><strong>/</strong> Division</li>
                <li><strong>%</strong> Modulus (remainder)</li>
                <li><strong>**</strong> Exponentiation</li>
                <li><strong>//</strong> Floor division</li>
            </ul>
            
            <h3>Comparison Operators</h3>
            <ul>
                <li><strong>==</strong> Equal to</li>
                <li><strong>!=</strong> Not equal to</li>
                <li><strong>&lt;</strong> Less than</li>
                <li><strong>&gt;</strong> Greater than</li>
                <li><strong>&lt;=</strong> Less than or equal to</li>
                <li><strong>&gt;=</strong> Greater than or equal to</li>
            </ul>
            
            <h3>Logical Operators</h3>
            <ul>
                <li><strong>and</strong> Returns True if both conditions are true</li>
                <li><strong>or</strong> Returns True if at least one condition is true</li>
                <li><strong>not</strong> Reverses the boolean value</li>
            </ul>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python"># Arithmetic operators
a, b = 10, 3
print(f"Addition: {a + b}")        # 13
print(f"Subtraction: {a - b}")     # 7
print(f"Multiplication: {a * b}")  # 30
print(f"Division: {a / b}")        # 3.333...
print(f"Floor division: {a // b}") # 3
print(f"Modulus: {a % b}")         # 1
print(f"Exponentiation: {a ** b}") # 1000

# Comparison operators
x, y = 5, 10
print(x == y)  # False
print(x != y)  # True
print(x &lt; y)   # True
print(x &gt; y)   # False

# Logical operators
age = 25
has_license = True
if age &gt;= 18 and has_license:
    print("Can drive")
else:
    print("Cannot drive")</code></pre>
            '''
        },
        'control-flow': {
            'title': 'Control Flow: If-Else Statements',
            'category': 'Python Basics',
            'image': 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&h=400&fit=crop&q=80',
            'content': '''
            <h2>Conditional Statements</h2>
            <p>Control flow allows you to make decisions in your code. Python uses if, elif, and else statements for conditional execution.</p>
            
            <h3>If Statement</h3>
            <p>The if statement is used to test a condition. If the condition is true, the code block is executed.</p>
            
            <h3>If-Else Statement</h3>
            <p>The else statement is used to execute code when the if condition is false.</p>
            
            <h3>If-Elif-Else Statement</h3>
            <p>The elif statement allows you to check multiple conditions. It stands for "else if".</p>
            
            <h3>Nested Conditionals</h3>
            <p>You can nest if statements inside other if statements to create complex decision trees.</p>
            
            <h3>Logical Operators</h3>
            <ul>
                <li><strong>and:</strong> Returns True if both conditions are true</li>
                <li><strong>or:</strong> Returns True if at least one condition is true</li>
                <li><strong>not:</strong> Reverses the boolean value</li>
            </ul>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python"># Simple if statement
age = 20
if age &gt;= 18:
    print("You are an adult")

# If-else statement
score = 75
if score &gt;= 60:
    print("You passed!")
else:
    print("You failed!")

# If-elif-else statement
grade = 85
if grade &gt;= 90:
    print("Grade: A")
elif grade &gt;= 80:
    print("Grade: B")
elif grade &gt;= 70:
    print("Grade: C")
else:
    print("Grade: F")

# Nested conditionals
age = 20
has_license = True
if age &gt;= 18:
    if has_license:
        print("You can drive")
    else:
        print("You need a license")
else:
    print("You're too young to drive")</code></pre>
            '''
        },
        'loops': {
            'title': 'Loops: For and While',
            'category': 'Python Basics',
            'image': None,
            'content': '''
            <h2>Loops in Python</h2>
            <p>Loops allow you to execute a block of code repeatedly. Python has two main types of loops: for loops and while loops.</p>
            
            <h3>For Loops</h3>
            <p>For loops are used to iterate over a sequence (list, tuple, string, etc.) or other iterable objects.</p>
            
            <h3>While Loops</h3>
            <p>While loops execute a block of code as long as a condition is true.</p>
            
            <h3>Loop Control Statements</h3>
            <ul>
                <li><strong>break:</strong> Exits the loop immediately</li>
                <li><strong>continue:</strong> Skips the rest of the current iteration</li>
                <li><strong>pass:</strong> Does nothing, used as a placeholder</li>
            </ul>
            
            <h3>Nested Loops</h3>
            <p>You can have loops inside loops. This is useful for working with multi-dimensional data structures.</p>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python"># For loop with list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# For loop with range
for i in range(5):
    print(i)  # Prints 0, 1, 2, 3, 4

# While loop
count = 0
while count &lt; 5:
    print(f"Count: {count}")
    count += 1

# Loop control: break
for i in range(10):
    if i == 5:
        break
    print(i)  # Prints 0, 1, 2, 3, 4

# Loop control: continue
for i in range(5):
    if i == 2:
        continue
    print(i)  # Prints 0, 1, 3, 4

# Nested loops
for i in range(3):
    for j in range(2):
        print(f"({i}, {j})")</code></pre>
            '''
        },
        'lists-and-tuples': {
            'title': 'Lists and Tuples',
            'category': 'Python Basics',
            'image': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&h=400&fit=crop&q=80',
            'content': '''
            <h2>Lists in Python</h2>
            <p>Lists are ordered, mutable collections of items. They are one of the most versatile data types in Python.</p>
            
            <h3>Creating Lists</h3>
            <p>Lists are created using square brackets []. Items are separated by commas.</p>
            
            <h3>List Operations</h3>
            <ul>
                <li><strong>Accessing items:</strong> Use index to access list items</li>
                <li><strong>Slicing:</strong> Extract portions of a list</li>
                <li><strong>Modifying:</strong> Lists are mutable, so you can change their elements</li>
                <li><strong>Adding items:</strong> Use append(), insert(), or extend()</li>
                <li><strong>Removing items:</strong> Use remove(), pop(), or del</li>
            </ul>
            
            <h2>Tuples in Python</h2>
            <p>Tuples are ordered, immutable collections of items. Once created, tuples cannot be modified.</p>
            
            <h3>Creating Tuples</h3>
            <p>Tuples are created using parentheses () or just commas. Items are separated by commas.</p>
            
            <h3>When to Use Tuples</h3>
            <ul>
                <li>When you want to ensure data integrity</li>
                <li>For fixed collections of items</li>
                <li>As dictionary keys (since they're immutable)</li>
                <li>For returning multiple values from functions</li>
            </ul>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python"># Lists (mutable)
my_list = [1, 2, 3, 4, 5]
print(my_list[0])        # 1
print(my_list[-1])       # 5 (last element)
print(my_list[1:3])     # [2, 3] (slicing)

# List operations
my_list.append(6)        # Add to end
my_list.insert(0, 0)     # Insert at index
my_list.remove(3)       # Remove value
print(my_list)           # [0, 1, 2, 4, 5, 6]

# Tuples (immutable)
my_tuple = (1, 2, 3, 4, 5)
print(my_tuple[0])       # 1
# my_tuple[0] = 10       # Error! Tuples are immutable

# Tuple unpacking
x, y, z = (1, 2, 3)
print(f"x={x}, y={y}, z={z}")  # x=1, y=2, z=3

# Returning multiple values
def get_name_age():
    return "Alice", 25

name, age = get_name_age()
print(f"{name} is {age} years old")</code></pre>
            '''
        },
        'dictionaries-and-sets': {
            'title': 'Dictionaries and Sets',
            'category': 'Python Basics',
            'image': None,
            'content': '''
            <h2>Dictionaries in Python</h2>
            <p>Dictionaries are unordered collections of key-value pairs. They are extremely useful for storing and retrieving data efficiently.</p>
            
            <h3>Creating Dictionaries</h3>
            <p>Dictionaries are created using curly braces {} with key-value pairs separated by colons.</p>
            
            <h3>Dictionary Operations</h3>
            <ul>
                <li><strong>Accessing values:</strong> Use keys to access values</li>
                <li><strong>Adding items:</strong> Assign new key-value pairs</li>
                <li><strong>Modifying items:</strong> Update existing key-value pairs</li>
                <li><strong>Removing items:</strong> Use del, pop(), or popitem()</li>
                <li><strong>Dictionary methods:</strong> keys(), values(), items(), get(), update()</li>
            </ul>
            
            <h2>Sets in Python</h2>
            <p>Sets are unordered collections of unique elements. They are useful for membership testing and eliminating duplicates.</p>
            
            <h3>Creating Sets</h3>
            <p>Sets are created using curly braces {} or the set() function. Duplicate values are automatically removed.</p>
            
            <h3>Set Operations</h3>
            <ul>
                <li><strong>Adding items:</strong> Use add() or update()</li>
                <li><strong>Removing items:</strong> Use remove(), discard(), or pop()</li>
                <li><strong>Set operations:</strong> union(), intersection(), difference(), symmetric_difference()</li>
                <li><strong>Membership testing:</strong> Use 'in' keyword</li>
            </ul>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python"># Dictionaries
student = {
    "name": "Alice",
    "age": 20,
    "grade": "A"
}
print(student["name"])           # Alice
print(student.get("age"))        # 20
print(student.get("city", "N/A")) # N/A (default value)

# Dictionary operations
student["city"] = "New York"     # Add new key-value
student["age"] = 21             # Update value
del student["grade"]            # Delete key
print(student.keys())            # dict_keys(['name', 'age', 'city'])
print(student.values())          # dict_values(['Alice', 21, 'New York'])

# Sets
my_set = {1, 2, 3, 4, 5}
my_set.add(6)                   # Add element
my_set.remove(3)                # Remove element
print(my_set)                    # {1, 2, 4, 5, 6}

# Set operations
set1 = {1, 2, 3}
set2 = {3, 4, 5}
print(set1.union(set2))          # {1, 2, 3, 4, 5}
print(set1.intersection(set2))  # {3}
print(set1.difference(set2))    # {1, 2}</code></pre>
            '''
        },
        'functions': {
            'title': 'Functions in Python',
            'category': 'Python Basics',
            'image': 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&h=400&fit=crop&q=80',
            'content': '''
            <h2>Functions</h2>
            <p>Functions are reusable blocks of code that perform a specific task. They help organize code and avoid repetition.</p>
            
            <h3>Defining Functions</h3>
            <p>Functions are defined using the def keyword followed by the function name and parentheses.</p>
            
            <h3>Parameters and Arguments</h3>
            <p>Functions can accept parameters (inputs) and return values (outputs).</p>
            
            <h3>Return Statement</h3>
            <p>The return statement is used to exit a function and return a value. If no return statement is specified, the function returns None.</p>
            
            <h3>Scope</h3>
            <p>Variables defined inside a function have local scope and are not accessible outside the function.</p>
            
            <h3>Default Arguments</h3>
            <p>You can provide default values for function parameters, making them optional when calling the function.</p>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python"># Basic function
def greet(name):
    return f"Hello, {name}!"

print(greet("Alice"))  # Hello, Alice!

# Function with multiple parameters
def add(a, b):
    return a + b

print(add(5, 3))  # 8

# Function with default arguments
def greet_person(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet_person("Bob"))              # Hello, Bob!
print(greet_person("Bob", "Hi"))        # Hi, Bob!

# Function with *args
def sum_all(*numbers):
    return sum(numbers)

print(sum_all(1, 2, 3, 4, 5))  # 15

# Function with **kwargs
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Alice", age=25, city="NYC")

# Lambda function
square = lambda x: x ** 2
print(square(5))  # 25</code></pre>
            '''
        },
        'file-handling': {
            'title': 'File Handling',
            'category': 'Python Basics',
            'image': None,
            'content': '''
            <h2>File Handling in Python</h2>
            <p>File handling allows you to read from and write to files on your system. Python provides built-in functions for file operations.</p>
            
            <h3>Opening Files</h3>
            <p>Use the open() function to open a file. You need to specify the file path and the mode (read, write, append, etc.).</p>
            
            <h3>File Modes</h3>
            <ul>
                <li><strong>'r'</strong> Read mode (default)</li>
                <li><strong>'w'</strong> Write mode (overwrites existing file)</li>
                <li><strong>'a'</strong> Append mode (adds to existing file)</li>
                <li><strong>'x'</strong> Exclusive creation (fails if file exists)</li>
                <li><strong>'b'</strong> Binary mode</li>
                <li><strong>'t'</strong> Text mode (default)</li>
            </ul>
            
            <h3>Reading Files</h3>
            <p>Use read(), readline(), or readlines() methods to read file content.</p>
            
            <h3>Writing to Files</h3>
            <p>Use write() or writelines() methods to write content to files.</p>
            
            <h3>Closing Files</h3>
            <p>Always close files using close() method or use the 'with' statement for automatic file closure.</p>
            
            <h3>Best Practices</h3>
            <ul>
                <li>Always use 'with' statement for file operations</li>
                <li>Handle file exceptions properly</li>
                <li>Check if file exists before operations</li>
                <li>Use appropriate file modes</li>
            </ul>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python"># Reading a file
with open("example.txt", "r") as file:
    content = file.read()
    print(content)

# Reading line by line
with open("example.txt", "r") as file:
    for line in file:
        print(line.strip())

# Writing to a file
with open("output.txt", "w") as file:
    file.write("Hello, World!\\n")
    file.write("This is a new line.")

# Appending to a file
with open("output.txt", "a") as file:
    file.write("\\nThis is appended text.")

# Reading all lines
with open("example.txt", "r") as file:
    lines = file.readlines()
    for line in lines:
        print(line)</code></pre>
            '''
        },
        # Python Advanced Topics
        'object-oriented-programming': {
            'title': 'Object-Oriented Programming',
            'category': 'Python Intermediate',
            'content': '''
            <h2>OOP in Python</h2>
            <p>Object-Oriented Programming (OOP) is a programming paradigm that uses objects and classes to organize code. Python is an object-oriented language.</p>
            
            <h3>Classes and Objects</h3>
            <p>A class is a blueprint for creating objects. An object is an instance of a class.</p>
            
            <h3>Inheritance</h3>
            <p>Inheritance allows a class to inherit attributes and methods from another class. This promotes code reuse.</p>
            
            <h3>Polymorphism</h3>
            <p>Polymorphism allows objects of different classes to be treated as objects of a common base class.</p>
            
            <h3>Encapsulation</h3>
            <p>Encapsulation is the bundling of data and methods that operate on that data within a single unit (class).</p>
            
            <h3>Abstraction</h3>
            <p>Abstraction hides complex implementation details and shows only the essential features of an object.</p>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python"># Class definition
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def bark(self):
        return f"{self.name} says Woof!"
    
    def get_info(self):
        return f"{self.name} is {self.age} years old"

# Creating objects
my_dog = Dog("Buddy", 3)
print(my_dog.bark())      # Buddy says Woof!
print(my_dog.get_info())   # Buddy is 3 years old

# Inheritance
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

dog = Dog()
cat = Cat()
print(dog.speak())  # Woof!
print(cat.speak())  # Meow!</code></pre>
            '''
        },
        'decorators-and-generators': {
            'title': 'Decorators and Generators',
            'category': 'Python Advanced',
            'image': 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&h=400&fit=crop&q=80',
            'content': '''
            <h2>Decorators</h2>
            <p>Decorators are a powerful feature in Python that allow you to modify the behavior of functions or classes without changing their source code.</p>
            
            <h3>Function Decorators</h3>
            <p>Decorators are functions that wrap other functions to extend their behavior.</p>
            
            <h2>Generators</h2>
            <p>Generators are a special type of iterator that generate values on-the-fly using the yield keyword. They are memory-efficient for large datasets.</p>
            
            <h3>Generator Functions</h3>
            <p>Generator functions use yield instead of return. They return a generator object that can be iterated over.</p>
            
            <h3>Generator Expressions</h3>
            <p>Similar to list comprehensions, but use parentheses and create generator objects instead of lists.</p>
            
            <h3>Benefits of Generators</h3>
            <ul>
                <li>Memory efficient</li>
                <li>Lazy evaluation</li>
                <li>Can represent infinite sequences</li>
            </ul>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python"># Decorator example
def my_decorator(func):
    def wrapper():
        print("Before function call")
        func()
        print("After function call")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()

# Generator example
def count_up_to(max):
    count = 1
    while count &lt;= max:
        yield count
        count += 1

for num in count_up_to(5):
    print(num)  # 1, 2, 3, 4, 5

# Generator expression
squares = (x*x for x in range(10))
for square in squares:
    print(square)</code></pre>
            '''
        },
        'exception-handling': {
            'title': 'Exception Handling',
            'category': 'Python Intermediate',
            'image': None,
            'content': '''
            <h2>Exception Handling</h2>
            <p>Exception handling allows you to gracefully handle errors and prevent your program from crashing.</p>
            
            <h3>Try-Except Blocks</h3>
            <p>The try block contains code that might raise an exception. The except block handles the exception.</p>
            
            <h3>Multiple Exceptions</h3>
            <p>You can handle multiple exceptions in a single except block or use multiple except blocks for different exceptions.</p>
            
            <h3>Finally Block</h3>
            <p>The finally block is executed regardless of whether an exception occurs. It's useful for cleanup operations.</p>
            
            <h3>Custom Exceptions</h3>
            <p>You can create custom exception classes by inheriting from the Exception class.</p>
            
            <h3>Raising Exceptions</h3>
            <p>You can raise exceptions manually using the raise keyword when certain conditions are met.</p>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python"># Basic try-except
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")

# Multiple exceptions
try:
    num = int(input("Enter a number: "))
    result = 10 / num
except ValueError:
    print("Invalid input. Please enter an integer.")
except ZeroDivisionError:
    print("Cannot divide by zero!")

# Finally block
try:
    file = open("data.txt", "r")
    content = file.read()
except FileNotFoundError:
    print("File not found!")
finally:
    file.close()
    print("File closed.")

# Custom exception
class CustomError(Exception):
    pass

raise CustomError("This is a custom error")</code></pre>
            '''
        },
        'modules-and-packages': {
            'title': 'Modules and Packages',
            'category': 'Python Intermediate',
            'image': None,
            'content': '''
            <h2>Modules in Python</h2>
            <p>Modules are files containing Python code. They allow you to organize code into logical units and reuse code across different programs.</p>
            
            <h3>Creating Modules</h3>
            <p>Any Python file (.py) can be used as a module. Simply save your code in a .py file and import it in other files.</p>
            
            <h3>Importing Modules</h3>
            <ul>
                <li><strong>import module_name:</strong> Import entire module</li>
                <li><strong>from module import function:</strong> Import specific function</li>
                <li><strong>from module import *:</strong> Import all (not recommended)</li>
                <li><strong>import module as alias:</strong> Import with alias</li>
            </ul>
            
            <h2>Packages in Python</h2>
            <p>Packages are collections of modules organized in directories. They help organize related modules together.</p>
            
            <h3>Creating Packages</h3>
            <p>Create a directory with an __init__.py file. This file makes the directory a Python package.</p>
            
            <h3>Package Structure</h3>
            <p>Packages can contain sub-packages and modules. Use dot notation to access nested packages.</p>
            
            <h3>Standard Library</h3>
            <p>Python comes with a large standard library of modules and packages for common tasks like file I/O, networking, data structures, and more.</p>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python"># Importing modules
import math
print(math.pi)  # 3.141592653589793

# Import specific function
from math import sqrt
print(sqrt(16))  # 4.0

# Import with alias
import datetime as dt
now = dt.datetime.now()
print(now)

# Creating a module (save as mymodule.py)
# def greet(name):
#     return f"Hello, {name}!"

# Using the module
# import mymodule
# print(mymodule.greet("Alice"))</code></pre>
            '''
        },
        'list-comprehensions': {
            'title': 'List Comprehensions',
            'category': 'Python Intermediate',
            'image': None,
            'content': '''
            <h2>List Comprehensions</h2>
            <p>List comprehensions provide a concise way to create lists in Python. They are more readable and often faster than traditional loops.</p>
            
            <h3>Basic Syntax</h3>
            <p>The basic syntax is: [expression for item in iterable]</p>
            
            <h3>Benefits</h3>
            <ul>
                <li>More concise and readable</li>
                <li>Often faster than traditional loops</li>
                <li>Can include conditional statements</li>
                <li>Can be nested for complex operations</li>
            </ul>
            
            <h3>Dictionary and Set Comprehensions</h3>
            <p>Similar syntax can be used for dictionaries and sets, making them powerful tools for data transformation.</p>
            
            <h3>When to Use</h3>
            <p>Use list comprehensions when you need to create a new list by transforming or filtering an existing iterable. They're perfect for simple transformations but should be avoided for complex logic.</p>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python"># Basic list comprehension
squares = [x**2 for x in range(10)]
print(squares)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# With condition
evens = [x for x in range(20) if x % 2 == 0]
print(evens)  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# Dictionary comprehension
squares_dict = {x: x**2 for x in range(5)}
print(squares_dict)  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

# Set comprehension
unique_squares = {x**2 for x in range(10)}
print(unique_squares)</code></pre>
            '''
        },
        'lambda-functions': {
            'title': 'Lambda Functions',
            'category': 'Python Intermediate',
            'image': None,
            'content': '''
            <h2>Lambda Functions</h2>
            <p>Lambda functions are small anonymous functions that can have any number of arguments, but can only have one expression.</p>
            
            <h3>Syntax</h3>
            <p>The syntax is: lambda arguments: expression</p>
            
            <h3>When to Use Lambda</h3>
            <ul>
                <li>For simple, one-line functions</li>
                <li>As arguments to higher-order functions (map, filter, reduce)</li>
                <li>When you need a function temporarily</li>
            </ul>
            
            <h3>Common Use Cases</h3>
            <ul>
                <li>Sorting with custom keys</li>
                <li>Filtering data</li>
                <li>Mapping transformations</li>
                <li>Event handlers</li>
            </ul>
            
            <h3>Limitations</h3>
            <p>Lambda functions are limited to a single expression and cannot contain statements. For complex logic, use regular functions.</p>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python"># Basic lambda
square = lambda x: x ** 2
print(square(5))  # 25

# Lambda with map
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, numbers))
print(squared)  # [1, 4, 9, 16, 25]

# Lambda with filter
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # [2, 4]

# Lambda with sorted
students = [("Alice", 25), ("Bob", 20), ("Charlie", 30)]
sorted_by_age = sorted(students, key=lambda x: x[1])
print(sorted_by_age)</code></pre>
            '''
        },
        'working-with-json': {
            'title': 'Working with JSON',
            'category': 'Python Intermediate',
            'image': None,
            'content': '''
            <h2>Working with JSON in Python</h2>
            <p>JSON (JavaScript Object Notation) is a lightweight data interchange format. Python's json module makes it easy to work with JSON data.</p>
            
            <h3>JSON Module</h3>
            <p>Python's built-in json module provides methods to encode and decode JSON data.</p>
            
            <h3>Encoding (Python to JSON)</h3>
            <p>Use json.dumps() to convert Python objects to JSON strings, and json.dump() to write JSON to files.</p>
            
            <h3>Decoding (JSON to Python)</h3>
            <p>Use json.loads() to parse JSON strings into Python objects, and json.load() to read JSON from files.</p>
            
            <h3>Common Use Cases</h3>
            <ul>
                <li>API responses</li>
                <li>Configuration files</li>
                <li>Data storage</li>
                <li>Inter-service communication</li>
            </ul>
            
            <h3>Best Practices</h3>
            <ul>
                <li>Handle JSON parsing errors</li>
                <li>Validate JSON structure</li>
                <li>Use proper encoding/decoding methods</li>
                <li>Consider using json.dumps() with indent for readability</li>
            </ul>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python">import json

# Python to JSON
data = {
    "name": "Alice",
    "age": 25,
    "city": "New York"
}
json_string = json.dumps(data)
print(json_string)

# JSON to Python
json_data = '{"name": "Bob", "age": 30}'
parsed = json.loads(json_data)
print(parsed["name"])  # Bob

# Reading from file
with open("data.json", "r") as f:
    data = json.load(f)

# Writing to file
with open("output.json", "w") as f:
    json.dump(data, f, indent=4)</code></pre>
            '''
        },
        'regular-expressions': {
            'title': 'Regular Expressions',
            'category': 'Python Intermediate',
            'image': None,
            'content': '''
            <h2>Regular Expressions in Python</h2>
            <p>Regular expressions (regex) are powerful tools for pattern matching and text manipulation. Python's re module provides regex functionality.</p>
            
            <h3>Common Patterns</h3>
            <ul>
                <li><strong>.</strong> Matches any character</li>
                <li><strong>^</strong> Matches start of string</li>
                <li><strong>$</strong> Matches end of string</li>
                <li><strong>*</strong> Zero or more occurrences</li>
                <li><strong>+</strong> One or more occurrences</li>
                <li><strong>?</strong> Zero or one occurrence</li>
                <li><strong>\\d</strong> Matches digits</li>
                <li><strong>\\w</strong> Matches word characters</li>
            </ul>
            
            <h3>Common Functions</h3>
            <ul>
                <li><strong>re.search():</strong> Find first match</li>
                <li><strong>re.findall():</strong> Find all matches</li>
                <li><strong>re.sub():</strong> Replace matches</li>
                <li><strong>re.match():</strong> Match at start of string</li>
            </ul>
            
            <h3>Use Cases</h3>
            <ul>
                <li>Email validation</li>
                <li>Phone number formatting</li>
                <li>Text extraction</li>
                <li>Data cleaning</li>
                <li>URL parsing</li>
            </ul>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python">import re

# Search for pattern
text = "Contact me at email@example.com"
match = re.search(r'\\w+@\\w+\\.\\w+', text)
if match:
    print(match.group())  # email@example.com

# Find all matches
text = "Call 123-456-7890 or 987-654-3210"
phones = re.findall(r'\\d{3}-\\d{3}-\\d{4}', text)
print(phones)  # ['123-456-7890', '987-654-3210']

# Replace
text = "Hello World"
new_text = re.sub(r'World', 'Python', text)
print(new_text)  # Hello Python

# Email validation
email = "user@example.com"
pattern = r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$'
if re.match(pattern, email):
    print("Valid email")</code></pre>
            '''
        },
        'date-and-time': {
            'title': 'Date and Time',
            'category': 'Python Intermediate',
            'image': None,
            'content': '''
            <h2>Working with Date and Time</h2>
            <p>Python's datetime module provides classes for working with dates and times. It's essential for applications that need to handle temporal data.</p>
            
            <h3>datetime Module</h3>
            <p>The datetime module contains several classes: date, time, datetime, timedelta, and tzinfo.</p>
            
            <h3>Creating Dates and Times</h3>
            <p>You can create date and time objects using constructors or parse strings using strptime().</p>
            
            <h3>Formatting Dates</h3>
            <p>Use strftime() to format dates and times into strings with custom formats.</p>
            
            <h3>Time Calculations</h3>
            <p>Use timedelta objects to perform arithmetic operations on dates and times.</p>
            
            <h3>Timezone Handling</h3>
            <p>Python supports timezone-aware datetime objects. Use pytz library for comprehensive timezone support.</p>
            
            <h3>Common Operations</h3>
            <ul>
                <li>Get current date/time</li>
                <li>Parse date strings</li>
                <li>Format dates for display</li>
                <li>Calculate time differences</li>
                <li>Add/subtract time periods</li>
            </ul>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python">from datetime import datetime, timedelta

# Current date and time
now = datetime.now()
print(now)

# Creating specific date
date = datetime(2024, 1, 15, 10, 30, 0)
print(date)

# Formatting dates
formatted = now.strftime("%Y-%m-%d %H:%M:%S")
print(formatted)

# Parsing date string
date_str = "2024-01-15"
parsed = datetime.strptime(date_str, "%Y-%m-%d")
print(parsed)

# Time calculations
future = now + timedelta(days=7)
print(future)

# Time difference
diff = future - now
print(diff.days)  # 7</code></pre>
            '''
        },
        'working-with-apis': {
            'title': 'Working with APIs',
            'category': 'Python Advanced',
            'image': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&h=400&fit=crop&q=80',
            'content': '''
            <h2>API Integration</h2>
            <p>APIs (Application Programming Interfaces) allow different software applications to communicate with each other.</p>
            
            <h3>HTTP Requests</h3>
            <p>Python's requests library makes it easy to send HTTP requests and interact with REST APIs.</p>
            
            <h3>REST APIs</h3>
            <p>REST (Representational State Transfer) is an architectural style for designing networked applications.</p>
            
            <h3>Common HTTP Methods</h3>
            <ul>
                <li><strong>GET:</strong> Retrieve data</li>
                <li><strong>POST:</strong> Create new data</li>
                <li><strong>PUT:</strong> Update existing data</li>
                <li><strong>DELETE:</strong> Remove data</li>
            </ul>
            
            <h3>JSON Data</h3>
            <p>Most APIs return data in JSON format. Python's json module makes it easy to parse and work with JSON data.</p>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python">import requests
import json

# GET request
response = requests.get("https://api.github.com/users/octocat")
data = response.json()
print(data["name"])

# POST request
payload = {"name": "Alice", "job": "Developer"}
response = requests.post("https://reqres.in/api/users", json=payload)
print(response.status_code)  # 201

# With headers
headers = {"Authorization": "Bearer YOUR_TOKEN"}
response = requests.get("https://api.example.com/data", headers=headers)

# Error handling
try:
    response = requests.get("https://api.example.com/data", timeout=5)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")</code></pre>
            '''
        },
        'database-operations': {
            'title': 'Database Operations',
            'category': 'Python Advanced',
            'image': None,
            'content': '''
            <h2>Database Operations in Python</h2>
            <p>Python provides several libraries for working with databases. The most common are sqlite3 (built-in), MySQL, and PostgreSQL connectors.</p>
            
            <h3>SQLite Database</h3>
            <p>SQLite is a lightweight, file-based database that comes built-in with Python. It's perfect for small to medium applications.</p>
            
            <h3>Connecting to Databases</h3>
            <p>Use connection objects to connect to databases. Each database library has its own connection method.</p>
            
            <h3>Executing Queries</h3>
            <ul>
                <li><strong>CREATE:</strong> Create tables and databases</li>
                <li><strong>INSERT:</strong> Add new records</li>
                <li><strong>SELECT:</strong> Retrieve data</li>
                <li><strong>UPDATE:</strong> Modify existing records</li>
                <li><strong>DELETE:</strong> Remove records</li>
            </ul>
            
            <h3>Best Practices</h3>
            <ul>
                <li>Always use parameterized queries to prevent SQL injection</li>
                <li>Close connections properly</li>
                <li>Use context managers (with statement)</li>
                <li>Handle exceptions appropriately</li>
                <li>Use connection pooling for production</li>
            </ul>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python">import sqlite3

# Connect to database
conn = sqlite3.connect("example.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT
    )
""")

# Insert data
cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", 
               ("Alice", "alice@example.com"))
conn.commit()

# Query data
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close connection
conn.close()</code></pre>
            '''
        },
        'web-scraping': {
            'title': 'Web Scraping with BeautifulSoup',
            'category': 'Python Advanced',
            'image': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800&h=400&fit=crop&q=80',
            'content': '''
            <h2>Web Scraping in Python</h2>
            <p>Web scraping is the process of extracting data from websites. Python provides excellent libraries like BeautifulSoup and requests for this purpose.</p>
            
            <h3>BeautifulSoup Library</h3>
            <p>BeautifulSoup is a Python library for parsing HTML and XML documents. It creates a parse tree that makes it easy to extract data.</p>
            
            <h3>Basic Workflow</h3>
            <ol>
                <li>Send HTTP request to get webpage content</li>
                <li>Parse HTML content with BeautifulSoup</li>
                <li>Find and extract desired elements</li>
                <li>Process and store the extracted data</li>
            </ol>
            
            <h3>Finding Elements</h3>
            <ul>
                <li><strong>find():</strong> Find first matching element</li>
                <li><strong>find_all():</strong> Find all matching elements</li>
                <li><strong>select():</strong> Use CSS selectors</li>
                <li><strong>get_text():</strong> Extract text content</li>
            </ul>
            
            <h3>Best Practices</h3>
            <ul>
                <li>Respect robots.txt and website terms</li>
                <li>Add delays between requests</li>
                <li>Handle errors gracefully</li>
                <li>Use proper headers to identify yourself</li>
                <li>Consider using APIs when available</li>
            </ul>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python">from bs4 import BeautifulSoup
import requests

# Get webpage
url = "https://example.com"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# Find elements
title = soup.find("title")
print(title.text)

# Find all links
links = soup.find_all("a")
for link in links:
    print(link.get("href"))

# CSS selectors
headings = soup.select("h1, h2, h3")
for heading in headings:
    print(heading.text)

# Extract text
paragraphs = soup.find_all("p")
for p in paragraphs:
    print(p.get_text())</code></pre>
            '''
        },
        'testing-and-debugging': {
            'title': 'Testing and Debugging',
            'category': 'Python Advanced',
            'image': None,
            'content': '''
            <h2>Testing in Python</h2>
            <p>Testing is crucial for writing reliable code. Python provides the unittest framework and pytest library for testing.</p>
            
            <h3>Unit Testing</h3>
            <p>Unit tests verify that individual components of your code work correctly. Each test should focus on a single functionality.</p>
            
            <h3>pytest Framework</h3>
            <p>pytest is a popular testing framework that makes writing and running tests easier. It provides better output and more features than unittest.</p>
            
            <h3>Writing Tests</h3>
            <ul>
                <li>Create test files with test_ prefix</li>
                <li>Write test functions with test_ prefix</li>
                <li>Use assert statements to verify results</li>
                <li>Test edge cases and error conditions</li>
            </ul>
            
            <h2>Debugging in Python</h2>
            <p>Debugging is the process of finding and fixing errors in your code. Python provides several debugging tools.</p>
            
            <h3>Debugging Techniques</h3>
            <ul>
                <li><strong>Print statements:</strong> Simple but effective</li>
                <li><strong>pdb debugger:</strong> Python's built-in debugger</li>
                <li><strong>IDE debuggers:</strong> Use VS Code, PyCharm debuggers</li>
                <li><strong>Logging:</strong> Use logging module for better debugging</li>
            </ul>
            
            <h3>Common Debugging Strategies</h3>
            <ul>
                <li>Read error messages carefully</li>
                <li>Use breakpoints to pause execution</li>
                <li>Inspect variable values</li>
                <li>Trace execution flow</li>
                <li>Test with different inputs</li>
            </ul>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python"># Unit test example
def add(a, b):
    return a + b

# test_add.py
import pytest

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

# Run with: pytest test_add.py

# Debugging with pdb
import pdb

def divide(a, b):
    pdb.set_trace()  # Breakpoint
    return a / b

result = divide(10, 2)</code></pre>
            '''
        },
        'context-managers': {
            'title': 'Context Managers',
            'category': 'Python Advanced',
            'content': '''
            <h2>Context Managers</h2>
            <p>Context managers allow you to allocate and release resources precisely when you want to. The most common use is with the 'with' statement.</p>
            
            <h3>The 'with' Statement</h3>
            <p>The 'with' statement ensures that resources are properly managed. It automatically handles setup and teardown operations.</p>
            
            <h3>Creating Context Managers</h3>
            <p>You can create context managers using classes with __enter__ and __exit__ methods, or using the contextlib module.</p>
            
            <h3>Common Use Cases</h3>
            <ul>
                <li>File operations</li>
                <li>Database connections</li>
                <li>Thread locks</li>
                <li>Resource cleanup</li>
            </ul>
            
            <h3>Benefits</h3>
            <ul>
                <li>Automatic resource cleanup</li>
                <li>Exception-safe code</li>
                <li>Cleaner code structure</li>
                <li>Prevents resource leaks</li>
            </ul>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python"># Using 'with' statement
with open("file.txt", "r") as f:
    content = f.read()
    # File automatically closed

# Custom context manager
class MyContextManager:
    def __enter__(self):
        print("Entering context")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Exiting context")
        return False

with MyContextManager() as cm:
    print("Inside context")

# Using contextlib
from contextlib import contextmanager

@contextmanager
def my_context():
    print("Entering")
    yield
    print("Exiting")

with my_context():
    print("Inside")</code></pre>
            '''
        },
        'metaclasses': {
            'title': 'Metaclasses',
            'category': 'Python Advanced',
            'image': None,
            'content': '''
            <h2>Metaclasses in Python</h2>
            <p>Metaclasses are the "classes of classes". They define how classes are created. This is an advanced topic that allows you to customize class creation.</p>
            
            <h3>What are Metaclasses?</h3>
            <p>A metaclass is a class whose instances are classes. Just as a class defines how instances behave, a metaclass defines how classes behave.</p>
            
            <h3>When to Use Metaclasses</h3>
            <ul>
                <li>Creating APIs and frameworks</li>
                <li>Automatic class registration</li>
                <li>Adding methods to classes automatically</li>
                <li>Enforcing coding standards</li>
            </ul>
            
            <h3>Creating Metaclasses</h3>
            <p>Metaclasses are created by inheriting from type. You override __new__ or __init__ to customize class creation.</p>
            
            <h3>Best Practices</h3>
            <ul>
                <li>Use sparingly - they add complexity</li>
                <li>Document thoroughly</li>
                <li>Consider alternatives first (decorators, inheritance)</li>
                <li>Test extensively</li>
            </ul>
            
            <h3>Note</h3>
            <p>Metaclasses are powerful but complex. Most Python developers rarely need to create custom metaclasses. Understanding them helps you understand Python's object model better.</p>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python"># Metaclass example
class MyMeta(type):
    def __new__(cls, name, bases, attrs):
        # Add a class attribute
        attrs['created_by'] = 'metaclass'
        return super().__new__(cls, name, bases, attrs)

class MyClass(metaclass=MyMeta):
    pass

print(MyClass.created_by)  # 'metaclass'

# Note: Metaclasses are advanced and rarely needed
# Most Python developers don't need to create custom metaclasses</code></pre>
            '''
        },
        'async-programming': {
            'title': 'Async Programming',
            'category': 'Python Advanced',
            'image': 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800&h=400&fit=crop&q=80',
            'content': '''
            <h2>Asynchronous Programming</h2>
            <p>Asynchronous programming allows you to write concurrent code that can handle multiple tasks efficiently.</p>
            
            <h3>Async/Await</h3>
            <p>The async/await syntax makes asynchronous code look and behave like synchronous code, making it easier to read and write.</p>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python">import asyncio

# Async function
async def fetch_data(delay):
    print(f"Fetching data (delay: {delay}s)...")
    await asyncio.sleep(delay)
    return f"Data after {delay}s"

# Main async function
async def main():
    # Run concurrently
    task1 = asyncio.create_task(fetch_data(2))
    task2 = asyncio.create_task(fetch_data(1))
    
    result1 = await task1
    result2 = await task2
    
    print(result1, result2)

# Run
asyncio.run(main())</code></pre>
            
            <h3>asyncio Module</h3>
            <p>Python's asyncio module provides infrastructure for writing single-threaded concurrent code using coroutines.</p>
            
            <h3>Coroutines</h3>
            <p>Coroutines are functions that can be paused and resumed. They are defined using async def.</p>
            
            <h3>Code Examples</h3>
            <pre><code class="language-python">import asyncio

# Async function
async def fetch_data(delay):
    print(f"Fetching data (delay: {delay}s)...")
    await asyncio.sleep(delay)
    return f"Data after {delay}s"

# Main async function
async def main():
    # Run concurrently
    task1 = asyncio.create_task(fetch_data(2))
    task2 = asyncio.create_task(fetch_data(1))
    
    result1 = await task1
    result2 = await task2
    
    print(result1, result2)

# Run
asyncio.run(main())</code></pre>
            
            <h3>Benefits</h3>
            <ul>
                <li>Better performance for I/O-bound operations</li>
                <li>Efficient handling of concurrent tasks</li>
                <li>Non-blocking code execution</li>
            </ul>
            '''
        }
    }
    
    topic = topics_data.get(topic_slug)
    if not topic:
        flash('Topic not found', 'error')
        return redirect(url_for('blog_list'))
    
    return render_template('blog/topic_detail.html', 
                         topic=topic, 
                         topic_slug=topic_slug,
                         python_learning_post=python_learning_post)


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
    form.previous_post_id.choices = [(0, 'None')] + [(p.id, p.title) for p in Post.query.filter_by(status='published').order_by(Post.published_date.desc()).all()]
    
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
        
        if form.previous_post_id.data and form.previous_post_id.data != 0:
            post.previous_post_id = form.previous_post_id.data
        else:
            post.previous_post_id = None
        
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
        
        if form.previous_post_id.data and form.previous_post_id.data != 0:
            post.previous_post_id = form.previous_post_id.data
        else:
            post.previous_post_id = None
        
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
        filepath = os.path.join(directory, filename)
        
        # For production (Render), check static/images first for profile images
        # This handles the case where uploaded files don't persist on ephemeral filesystems
        if not os.path.exists(filepath):
            static_image_path = os.path.join(app.static_folder, 'images', filename)
            if os.path.exists(static_image_path):
                return send_from_directory(os.path.join(app.static_folder, 'images'), filename)
        
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
    # Only run in debug mode for local development
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug_mode)

