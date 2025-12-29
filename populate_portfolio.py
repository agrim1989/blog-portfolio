"""
Script to populate portfolio database from resume information
"""
import os
from app import app, db
from config import config_dict
from models import (
    User, Profile, Education, Experience, Skill, Project, Achievement,
    Category, Tag, Post
)
from datetime import datetime, date
from werkzeug.security import generate_password_hash

def populate_database():
    # Set production config if needed
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        app.config.from_object(config_dict['production'])
    else:
        app.config.from_object(config_dict['default'])
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            try:
                admin_user.set_password('admin123')
            except:
                admin_user.password_hash = generate_password_hash('admin123', method='pbkdf2:sha256')
            db.session.add(admin_user)
            print("Admin user created")
        
        # Update admin username to display as "Agrim Sharma" for blog posts
        # We'll use the profile name for author display
        
        # Create or update profile
        profile = Profile.query.first()
        if not profile:
            profile = Profile()
        
        profile.name = "Agrim Sharma"
        profile.title = "Software Engineering Manager | Python Specialist | Generative AI Expert | Freelancer"
        profile.bio = """Accomplished Software Engineering Manager with 14+ years of progressive experience in 
designing, developing, and deploying scalable software solutions and leading high-performing engineering teams. 
Expertise in Python development (11+ years), microservices architecture, REST APIs, and emerging technologies 
including Generative AI, Retrieval-Augmented Generation (RAG), and Large Language Model (LLM) fine-tuning."""
        profile.email = "agrim89@gmail.com"
        profile.phone = "8800673006"
        profile.location = "North Delhi, Delhi, India"
        profile.linkedin_url = "https://linkedin.com/in/agrim-sharma"
        profile.github_url = "https://github.com/agrim1989"
        profile.website_url = "https://agrimsharma.github.io"
        # Set profile image to static file (works on Render)
        profile.profile_image = "profile.jpg"
        
        db.session.add(profile)
        db.session.flush()
        
        # Clear existing data
        Education.query.filter_by(profile_id=profile.id).delete()
        Experience.query.filter_by(profile_id=profile.id).delete()
        Skill.query.filter_by(profile_id=profile.id).delete()
        Project.query.filter_by(profile_id=profile.id).delete()
        Achievement.query.filter_by(profile_id=profile.id).delete()
        
        # Add Education
        education = Education(
            profile_id=profile.id,
            institution="PDM College of Engineering, India",
            degree="Bachelor of Engineering (BE) in Computer Science",
            start_date=date(2006, 8, 1),
            end_date=date(2010, 3, 1),
            order=1
        )
        db.session.add(education)
        
        # Add Experiences
        experiences = [
            {
                'company': 'Capgemini',
                'position': 'Software Engineering Manager',
                'start_date': date(2023, 9, 1),
                'end_date': None,
                'current': True,
                'description': """Led cross-functional team of 10+ developers through complete Software Development Life Cycle (SDLC), 
delivering mission-critical systems with high availability and enterprise-grade quality. Architected and deployed scalable 
microservices and RESTful APIs. Engineered Generative AI solutions using LangChain, OpenAI, and Google Gemini API, 
specializing in Retrieval-Augmented Generation (RAG) architectures.""",
                'order': 1
            },
            {
                'company': 'Capgemini',
                'position': 'Senior Consultant',
                'start_date': date(2019, 5, 1),
                'end_date': date(2023, 9, 1),
                'current': False,
                'description': """Modernized legacy codebases, achieving 20% reduction in operational costs while significantly 
improving system scalability and performance. Managed technical milestones and database architecture timelines. 
Implemented comprehensive regression testing suites, minimizing production defects by 30%.""",
                'order': 2
            },
            {
                'company': 'Publicis Groupe',
                'position': 'Senior Python Developer',
                'start_date': date(2018, 9, 1),
                'end_date': date(2019, 5, 1),
                'current': False,
                'description': """Adopted Scrum methodologies to streamline project delivery. Partnered with QA teams to integrate 
validated software updates. Identified and implemented system performance optimizations.""",
                'order': 3
            },
            {
                'company': 'Sirez Ltd.',
                'position': 'Senior Software Engineer',
                'start_date': date(2017, 12, 1),
                'end_date': date(2018, 9, 1),
                'current': False,
                'description': """Directed complex technical upgrade projects, ensuring seamless system integration. 
Facilitated continuous communication with key clients. Conducted in-depth architectural reviews.""",
                'order': 4
            },
            {
                'company': 'Innocata Inc.',
                'position': 'Senior Software Engineer',
                'start_date': date(2017, 4, 1),
                'end_date': date(2017, 11, 1),
                'current': False,
                'description': """Managed technical team of 20 members. Integrated Warehouse Management System (WMS) software. 
Developed Python-based PDF-to-XML conversion solution, reducing manual effort by 40%.""",
                'order': 5
            },
            {
                'company': 'Chetu, Inc.',
                'position': 'Senior Software Engineer',
                'start_date': date(2015, 11, 1),
                'end_date': date(2016, 11, 1),
                'current': False,
                'description': """Designed and delivered high-availability solutions for mission-critical applications. 
Established robust procedures for system monitoring, disaster recovery, and data backup.""",
                'order': 6
            },
            {
                'company': 'PyTechnologies (Snapdeal)',
                'position': 'Senior Software Engineer',
                'start_date': date(2015, 2, 1),
                'end_date': date(2015, 11, 1),
                'current': False,
                'description': """Engineered robust, high-availability solutions for critical backend systems. 
Standardized system monitoring and performance optimization protocols. Successfully introduced Agile methodologies.""",
                'order': 7
            },
            {
                'company': 'One97 Communications Limited',
                'position': 'Senior Associate',
                'start_date': date(2011, 3, 1),
                'end_date': date(2015, 2, 1),
                'current': False,
                'description': """Led and mentored team of 15 members. Optimized Outbound Dialer (OBD) configurations. 
Designed complex MySQL queries for high-performance data retrieval.""",
                'order': 8
            }
        ]
        
        for exp_data in experiences:
            exp = Experience(
                profile_id=profile.id,
                company=exp_data['company'],
                position=exp_data['position'],
                start_date=exp_data['start_date'],
                end_date=exp_data.get('end_date'),
                current=exp_data.get('current', False),
                description=exp_data['description'],
                order=exp_data['order']
            )
            db.session.add(exp)
        
        # Add Skills
        skills_data = [
            # Frameworks
            {'name': 'Python', 'category': 'framework', 'proficiency': 95, 'order': 1},
            {'name': 'Django', 'category': 'framework', 'proficiency': 95, 'order': 2},
            {'name': 'Flask', 'category': 'framework', 'proficiency': 90, 'order': 3},
            {'name': 'FastAPI', 'category': 'framework', 'proficiency': 85, 'order': 4},
            {'name': 'REST Framework', 'category': 'framework', 'proficiency': 90, 'order': 5},
            {'name': 'NumPy', 'category': 'framework', 'proficiency': 80, 'order': 6},
            
            # Databases
            {'name': 'MySQL', 'category': 'database', 'proficiency': 90, 'order': 1},
            {'name': 'SQL', 'category': 'database', 'proficiency': 90, 'order': 2},
            {'name': 'NoSQL', 'category': 'database', 'proficiency': 90, 'order': 3},
            {'name': 'Data Warehousing', 'category': 'database', 'proficiency': 85, 'order': 4},
            
            # Tools & Technologies
            {'name': 'AWS', 'category': 'tools', 'proficiency': 85, 'order': 1},
            {'name': 'Docker', 'category': 'tools', 'proficiency': 80, 'order': 2},
            {'name': 'Git', 'category': 'tools', 'proficiency': 90, 'order': 3},
            {'name': 'Linux', 'category': 'tools', 'proficiency': 85, 'order': 4},
            {'name': 'CI/CD', 'category': 'tools', 'proficiency': 85, 'order': 5},
            {'name': 'Microservices Architecture', 'category': 'tools', 'proficiency': 90, 'order': 6},
            
            # Others (AI/ML and Libraries)
            {'name': 'Generative AI', 'category': 'other', 'proficiency': 90, 'order': 1},
            {'name': 'RAG (Retrieval-Augmented Generation)', 'category': 'other', 'proficiency': 90, 'order': 2},
            {'name': 'LLM Fine-tuning', 'category': 'other', 'proficiency': 85, 'order': 3},
            {'name': 'OpenAI API', 'category': 'other', 'proficiency': 90, 'order': 4},
            {'name': 'Google Gemini API', 'category': 'other', 'proficiency': 85, 'order': 5},
            {'name': 'LangChain', 'category': 'other', 'proficiency': 85, 'order': 6},
            {'name': 'Pandas', 'category': 'other', 'proficiency': 85, 'order': 7},
        ]
        
        for skill_data in skills_data:
            skill = Skill(
                profile_id=profile.id,
                name=skill_data['name'],
                category=skill_data['category'],
                proficiency_level=skill_data['proficiency'],
                order=skill_data['order']
            )
            db.session.add(skill)
        
        # Add Professional Certifications
        certifications = [
            {
                'title': 'Machine Learning with Python (with Honors)',
                'date': date(2023, 1, 1),
                'issuer': 'Coursera',
                'description': 'Completed comprehensive machine learning course with honors'
            },
            {
                'title': 'Python Data Structures',
                'date': date(2022, 1, 1),
                'issuer': 'Coursera',
                'description': 'Advanced data structures and algorithms in Python'
            },
            {
                'title': 'Foundations: Data, Data, Everywhere',
                'date': date(2022, 1, 1),
                'issuer': 'Google',
                'description': 'Data analytics foundations and best practices'
            },
            {
                'title': 'Introduction to Information Technology and AWS Cloud',
                'date': date(2021, 1, 1),
                'issuer': 'AWS',
                'description': 'Cloud computing fundamentals and AWS services'
            },
            {
                'title': 'Advanced Learning Algorithms',
                'date': date(2023, 1, 1),
                'issuer': 'Coursera',
                'description': 'Deep learning and neural network algorithms'
            }
        ]
        
        for i, cert_data in enumerate(certifications, 1):
            cert = Achievement(
                profile_id=profile.id,
                title=cert_data['title'],
                description=cert_data.get('description', ''),
                date=cert_data['date'],
                issuer=cert_data.get('issuer', ''),
                order=i
            )
            db.session.add(cert)
        
        # Add Key Achievements
        achievements = [
            {
                'title': 'Led and scaled engineering teams from individual contributor to team of 20+ members',
                'date': date(2023, 1, 1),
                'description': 'Successfully transitioned from individual contributor to leading large engineering teams'
            },
            {
                'title': 'Architected RAG and LLM-based solutions delivering business value in Generative AI space',
                'date': date(2023, 6, 1),
                'description': 'Designed and implemented cutting-edge AI solutions using RAG and LLM technologies'
            },
            {
                'title': 'Achieved 20% reduction in operational costs through legacy codebase modernization',
                'date': date(2020, 1, 1),
                'description': 'Modernized legacy systems resulting in significant cost savings'
            },
            {
                'title': 'Implemented system optimizations reducing production defects by 30%',
                'date': date(2020, 6, 1),
                'description': 'Improved code quality and testing processes'
            },
            {
                'title': 'Automated large-scale data processing tasks, reducing manual effort by 40%',
                'date': date(2017, 8, 1),
                'description': 'Developed automation solutions for data processing'
            }
        ]
        
        for i, ach_data in enumerate(achievements, 1):
            achievement = Achievement(
                profile_id=profile.id,
                title=ach_data['title'],
                description=ach_data.get('description', ''),
                date=ach_data['date'],
                order=i + 10  # Separate from certifications
            )
            db.session.add(achievement)
        
        # Add Projects
        projects = [
            {
                'title': 'Generative AI Solutions with RAG Architecture',
                'description': 'Engineered enterprise-grade Generative AI solutions leveraging LangChain framework, OpenAI GPT models, and Google Gemini API. Specialized in designing and implementing Retrieval-Augmented Generation (RAG) architectures that combine vector databases with large language models to deliver contextually accurate responses. Built semantic search capabilities, implemented prompt engineering strategies, and optimized token usage to reduce costs by 35% while maintaining response quality. The solution enabled real-time access to proprietary knowledge bases, reducing information retrieval time by 60% and improving accuracy of AI-generated content.',
                'technologies': 'Python, LangChain, OpenAI API, Google Gemini API, RAG, LLM, Vector Databases, Semantic Search',
                'date': date(2023, 9, 1),
                'featured': True,
                'order': 1
            },
            {
                'title': 'Scalable Microservices Architecture',
                'description': 'Architected and deployed a highly scalable microservices ecosystem using Django REST Framework and Python. Designed service-oriented architecture with independent databases per service, implemented API gateway patterns for request routing, and established asynchronous communication using message queues. Built comprehensive monitoring, logging, and distributed tracing systems. The architecture supported horizontal scaling, enabling the platform to handle 10x traffic growth with minimal infrastructure changes. Implemented CI/CD pipelines reducing deployment time from 2 hours to 15 minutes and achieved 99.9% uptime.',
                'technologies': 'Python, Django, REST APIs, Microservices, AWS, Docker, Message Queues, API Gateway, CI/CD',
                'date': date(2023, 6, 1),
                'featured': True,
                'order': 2
            },
            {
                'title': 'Legacy Codebase Modernization',
                'description': 'Led comprehensive modernization initiative for legacy Python codebase spanning 15+ years. Conducted thorough technical assessment, identified critical technical debt, and executed incremental refactoring strategy using Strangler Fig pattern. Upgraded from Python 2.7 to Python 3.11, migrated from monolithic architecture to modular design, implemented comprehensive test coverage increasing from 20% to 85%, and established CI/CD pipelines. Achieved 20% reduction in operational costs, improved system response times by 40%, reduced production defects by 30%, and enhanced developer productivity by 50% through better code organization and documentation.',
                'technologies': 'Python, Django, System Design, Performance Optimization, Testing, CI/CD, Refactoring',
                'date': date(2020, 1, 1),
                'featured': True,
                'order': 3
            },
            {
                'title': 'Surgery View - AI-Powered Video Segmentation Portal',
                'description': 'Developed a comprehensive web portal enabling medical professionals to upload surgical procedure videos for AI-powered analysis and segmentation. Built secure video upload system with AWS S3 integration for scalable storage, implemented video processing pipelines using Python and computer vision libraries to automatically detect and segment key surgical phases (preparation, incision, procedure, closure). Created intelligent algorithms to identify critical moments, instrument usage, and procedural milestones. Designed intuitive dashboard for doctors to review segmented videos, add annotations, and share findings with medical teams. The platform reduced video review time by 70% and improved surgical training efficiency through automated content organization.',
                'technologies': 'Python, AWS, S3, Computer Vision, Video Processing, AI, Machine Learning, Web Portal',
                'date': date(2024, 3, 1),
                'featured': True,
                'order': 4
            },
            {
                'title': 'PDF-to-XML Conversion Automation',
                'description': 'Developed enterprise-grade Python application using PySide for GUI and advanced PDF parsing libraries to automate conversion of complex PDF documents to structured XML format. Implemented OCR capabilities for scanned documents, handled multi-column layouts, tables, and embedded images. Built batch processing system capable of handling thousands of documents simultaneously. Created validation and error handling mechanisms ensuring 99.5% conversion accuracy. The solution automated large-scale data processing tasks, reducing manual effort by 40% and processing time from weeks to hours for document archives containing 50,000+ files.',
                'technologies': 'Python, PySide, XML Processing, OCR, PDF Parsing, Automation, Batch Processing',
                'date': date(2017, 8, 1),
                'featured': False,
                'order': 5
            },
            # Freelance Work Projects
            {
                'title': 'Fitimage.io - Full Website Development',
                'description': 'Developed end-to-end fitness analytics platform using Django and Python. Built responsive web application with user authentication, profile management, and subscription system. Created RESTful API architecture including specialized endpoint for body fat percentage analysis that processes uploaded images using computer vision algorithms. Integrated Stripe payment gateway for subscription management, implemented secure file upload system, and built admin dashboard for content and user management. The platform processed over 10,000 image analyses with 95% accuracy rate and supported 500+ active subscribers.',
                'technologies': 'Django, Python, REST API, Stripe, Image Processing, Computer Vision, Body Fat Analysis API, PostgreSQL',
                'date': date(2019, 1, 1),
                'featured': False,
                'order': 6
            },
            {
                'title': 'AI-Powered Productivity Solutions',
                'description': 'Developed multiple freelance solutions leveraging AI and machine learning to automate complex workflows and improve precision beyond human capabilities. Built intelligent document processing systems using NLP for automated categorization and extraction, created predictive analytics dashboards for business intelligence, and developed chatbot solutions for customer service automation. Implemented custom machine learning models for pattern recognition and anomaly detection. These solutions improved operational efficiency by 45%, reduced error rates by 60%, and enabled 24/7 automated processing capabilities for clients across healthcare, finance, and e-commerce sectors.',
                'technologies': 'AI Tools, Machine Learning, Python, NLP, Automation, Predictive Analytics, Chatbots, Data Processing',
                'date': date(2020, 1, 1),
                'featured': False,
                'order': 7
            }
        ]
        
        for proj_data in projects:
            project = Project(
                profile_id=profile.id,
                title=proj_data['title'],
                description=proj_data['description'],
                technologies=proj_data['technologies'],
                date=proj_data['date'],
                featured=proj_data['featured'],
                order=proj_data['order']
            )
            db.session.add(project)
        
        # Create Categories and Tags for Blog
        tech_category = Category.query.filter_by(slug='technology').first()
        if not tech_category:
            tech_category = Category(name='Technology', slug='technology', description='Posts about technology and software development')
            db.session.add(tech_category)
        
        ai_category = Category.query.filter_by(slug='ai-ml').first()
        if not ai_category:
            ai_category = Category(name='AI & Machine Learning', slug='ai-ml', description='Posts about artificial intelligence and machine learning')
            db.session.add(ai_category)
        
        career_category = Category.query.filter_by(slug='career').first()
        if not career_category:
            career_category = Category(name='Career', slug='career', description='Career advice and professional development')
            db.session.add(career_category)
        
        db.session.flush()
        
        # Create Tags
        tags_data = ['Python', 'Django', 'Flask', 'FastAPI', 'AI', 'Machine Learning', 'RAG', 'LLM', 'Software Engineering', 'Leadership', 'Microservices', 'AWS', 'Generative AI', 'API Development', 'Web Development', 'System Design', 'Architecture', 'Design Patterns', 'Data Structures', 'Distributed Systems', 'Caching', 'Interview']
        tag_objects = {}
        for tag_name in tags_data:
            tag = Tag.query.filter_by(slug=tag_name.lower().replace(' ', '-')).first()
            if not tag:
                tag = Tag(name=tag_name, slug=tag_name.lower().replace(' ', '-'))
                db.session.add(tag)
            tag_objects[tag_name] = tag
        
        db.session.flush()
        
        # Create Dummy Blog Posts
        admin_user = User.query.filter_by(username='admin').first()
        
        blog_posts = [
            {
                'title': 'Getting Started with Retrieval-Augmented Generation (RAG)',
                'slug': 'getting-started-with-rag',
                'content': '''<h2>Introduction to RAG</h2>
                <p>Retrieval-Augmented Generation (RAG) is a powerful technique that combines the strengths of information retrieval and language generation. It allows AI systems to access external knowledge sources and generate more accurate and contextually relevant responses.</p>
                
                <h3>How RAG Works</h3>
                <p>RAG works in two main stages:</p>
                <ol>
                    <li><strong>Retrieval:</strong> The system searches through a knowledge base to find relevant information related to the query.</li>
                    <li><strong>Augmentation:</strong> The retrieved information is used to augment the context for the language model, enabling it to generate more accurate responses.</li>
                </ol>
                
                <h3>Benefits of RAG</h3>
                <ul>
                    <li>Improved accuracy by grounding responses in factual information</li>
                    <li>Ability to access up-to-date information without retraining models</li>
                    <li>Reduced hallucination in generated content</li>
                    <li>Better handling of domain-specific queries</li>
                </ul>
                
                <p>RAG has become essential for building enterprise AI applications that require access to proprietary knowledge bases and real-time information.</p>''',
                'excerpt': 'Learn how Retrieval-Augmented Generation (RAG) combines information retrieval with language generation to create more accurate AI systems.',
                'category': ai_category,
                'tags': ['AI', 'RAG', 'Machine Learning'],
                'status': 'published',
                'published_date': datetime(2024, 1, 15, 10, 0, 0),
                'featured_image': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=500&fit=crop&q=80'
            },
            {
                'title': 'Building Scalable Microservices with Django',
                'slug': 'scalable-microservices-django',
                'content': '''<h2>Microservices Architecture with Django</h2>
                <p>Django, while traditionally used for monolithic applications, can be effectively used to build microservices architectures. This post explores best practices for designing scalable microservices using Django.</p>
                
                <h3>Key Principles</h3>
                <ul>
                    <li><strong>Service Independence:</strong> Each microservice should be independently deployable and scalable</li>
                    <li><strong>API-First Design:</strong> Use Django REST Framework to create well-defined APIs</li>
                    <li><strong>Database per Service:</strong> Each service should have its own database</li>
                    <li><strong>Asynchronous Communication:</strong> Use message queues for inter-service communication</li>
                </ul>
                
                <h3>Implementation Strategies</h3>
                <p>When building microservices with Django, consider:</p>
                <ol>
                    <li>Using Docker for containerization</li>
                    <li>Implementing API gateways for routing</li>
                    <li>Setting up service discovery mechanisms</li>
                    <li>Implementing comprehensive monitoring and logging</li>
                </ol>
                
                <p>Microservices architecture allows teams to work independently, scale services based on demand, and adopt different technologies for different services.</p>''',
                'excerpt': 'Explore how to build scalable microservices architectures using Django and best practices for service design and deployment.',
                'category': tech_category,
                'tags': ['Django', 'Microservices', 'Software Engineering'],
                'status': 'published',
                'published_date': datetime(2024, 2, 10, 14, 30, 0),
                'featured_image': 'https://images.unsplash.com/photo-1558494949-ef010cbd0a6b?w=800&h=500&fit=crop&q=80&auto=format'
            },
            {
                'title': 'Leading Engineering Teams: Lessons from 14 Years',
                'slug': 'leading-engineering-teams',
                'content': '''<h2>My Journey in Engineering Leadership</h2>
                <p>After 14+ years in software engineering, including leading teams of 20+ developers, I've learned valuable lessons about engineering leadership. Here are some key insights.</p>
                
                <h3>Building Trust and Communication</h3>
                <p>Effective leadership starts with building trust. Regular one-on-ones, transparent communication, and being available for your team are crucial. Create an environment where team members feel comfortable sharing challenges and ideas.</p>
                
                <h3>Technical Excellence</h3>
                <p>As a technical leader, you need to:</p>
                <ul>
                    <li>Maintain your technical skills while developing leadership capabilities</li>
                    <li>Set high standards for code quality and architecture</li>
                    <li>Mentor junior engineers and help them grow</li>
                    <li>Make technical decisions that balance short-term needs with long-term goals</li>
                </ul>
                
                <h3>Agile and Process</h3>
                <p>Implementing Agile methodologies effectively requires:</p>
                <ol>
                    <li>Clear sprint planning and goal setting</li>
                    <li>Regular retrospectives to improve processes</li>
                    <li>Balancing feature development with technical debt</li>
                    <li>Ensuring team velocity while maintaining quality</li>
                </ol>
                
                <p>Leadership is about enabling your team to do their best work while aligning technical efforts with business objectives.</p>''',
                'excerpt': 'Key lessons learned from 14+ years of leading engineering teams, including building trust, maintaining technical excellence, and implementing effective processes.',
                'category': career_category,
                'tags': ['Leadership', 'Software Engineering'],
                'status': 'published',
                'published_date': datetime(2024, 3, 5, 9, 0, 0),
                'featured_image': 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&h=500&fit=crop&q=80'
            },
            {
                'title': 'Fine-tuning Large Language Models for Enterprise Use',
                'slug': 'fine-tuning-llms-enterprise',
                'content': '''<h2>LLM Fine-tuning for Business Applications</h2>
                <p>Fine-tuning Large Language Models (LLMs) for enterprise applications requires careful consideration of data, compute resources, and business requirements. This post covers practical approaches to LLM fine-tuning.</p>
                
                <h3>When to Fine-tune</h3>
                <p>Fine-tuning is appropriate when:</p>
                <ul>
                    <li>You need domain-specific knowledge that's not in the base model</li>
                    <li>You want to change the model's behavior or tone</li>
                    <li>You have sufficient high-quality training data</li>
                    <li>The cost of fine-tuning is justified by improved performance</li>
                </ul>
                
                <h3>Fine-tuning Approaches</h3>
                <ol>
                    <li><strong>Full Fine-tuning:</strong> Training all model parameters (requires significant compute)</li>
                    <li><strong>Parameter-Efficient Fine-tuning (PEFT):</strong> Using techniques like LoRA to train fewer parameters</li>
                    <li><strong>Prompt Engineering:</strong> Sometimes better than fine-tuning for specific tasks</li>
                </ol>
                
                <h3>Best Practices</h3>
                <p>Key considerations for successful fine-tuning:</p>
                <ul>
                    <li>Data quality is more important than quantity</li>
                    <li>Start with smaller models before scaling up</li>
                    <li>Implement proper evaluation metrics</li>
                    <li>Monitor for overfitting and model drift</li>
                </ul>
                
                <p>Fine-tuning LLMs can significantly improve performance for specific use cases, but it's important to evaluate whether the benefits justify the costs.</p>''',
                'excerpt': 'A practical guide to fine-tuning Large Language Models for enterprise applications, including when to fine-tune and best practices.',
                'category': ai_category,
                'tags': ['AI', 'LLM', 'Machine Learning'],
                'status': 'published',
                'published_date': datetime(2024, 3, 20, 11, 0, 0),
                'featured_image': 'https://images.unsplash.com/photo-1676299080923-6b5997670d1a?w=800&h=500&fit=crop&q=80'
            },
            {
                'title': 'Modernizing Legacy Python Codebases',
                'slug': 'modernizing-legacy-python-code',
                'content': '''<h2>Strategies for Legacy Code Modernization</h2>
                <p>Modernizing legacy Python codebases is a common challenge in software engineering. Here's how to approach it systematically while maintaining business continuity.</p>
                
                <h3>Assessment Phase</h3>
                <p>Before starting modernization:</p>
                <ul>
                    <li>Document current system architecture and dependencies</li>
                    <li>Identify technical debt and pain points</li>
                    <li>Assess risks and business impact</li>
                    <li>Create a modernization roadmap</li>
                </ul>
                
                <h3>Modernization Strategies</h3>
                <ol>
                    <li><strong>Incremental Refactoring:</strong> Modernize code in small, manageable chunks</li>
                    <li><strong>Strangler Fig Pattern:</strong> Gradually replace legacy components</li>
                    <li><strong>API Wrapper:</strong> Wrap legacy code with modern APIs</li>
                    <li><strong>Complete Rewrite:</strong> Only when incremental approaches aren't feasible</li>
                </ol>
                
                <h3>Key Improvements</h3>
                <p>Focus on:</p>
                <ul>
                    <li>Upgrading to modern Python versions and frameworks</li>
                    <li>Improving code structure and maintainability</li>
                    <li>Adding comprehensive tests</li>
                    <li>Implementing CI/CD pipelines</li>
                    <li>Improving documentation</li>
                </ul>
                
                <p>Successful modernization can reduce operational costs by 20% or more while improving system scalability and developer productivity.</p>''',
                'excerpt': 'Learn systematic approaches to modernizing legacy Python codebases, including assessment strategies and implementation techniques.',
                'category': tech_category,
                'tags': ['Python', 'Software Engineering'],
                'status': 'published',
                'published_date': datetime(2024, 4, 12, 15, 0, 0),
                'featured_image': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800&h=500&fit=crop&q=80'
            },
            {
                'title': 'Building High-Performance APIs with FastAPI',
                'slug': 'building-high-performance-apis-fastapi',
                'content': '''<h2>Why FastAPI is Revolutionizing API Development</h2>
                <p>FastAPI has emerged as one of the fastest-growing Python web frameworks, combining the best of modern Python features with automatic API documentation and high performance. Built on Starlette and Pydantic, FastAPI offers async support, type hints, and automatic validation.</p>
                
                <h3>Key Advantages of FastAPI</h3>
                <ul>
                    <li><strong>Performance:</strong> Comparable to Node.js and Go, thanks to async/await support</li>
                    <li><strong>Type Safety:</strong> Built-in type hints and Pydantic models for automatic validation</li>
                    <li><strong>Auto Documentation:</strong> Interactive API docs (Swagger UI and ReDoc) generated automatically</li>
                    <li><strong>Modern Python:</strong> Uses Python 3.6+ features like type hints and async/await</li>
                    <li><strong>Easy to Learn:</strong> Simple syntax that's intuitive for Python developers</li>
                </ul>
                
                <h3>Building Your First FastAPI Application</h3>
                <p>Here's a quick example of a FastAPI endpoint:</p>
                <pre><code>from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):
    return {"item": item, "message": "Item created successfully"}</code></pre>
                
                <h3>Best Practices</h3>
                <ol>
                    <li>Use Pydantic models for request/response validation</li>
                    <li>Leverage async/await for I/O-bound operations</li>
                    <li>Organize routes using APIRouter for larger applications</li>
                    <li>Implement proper error handling with HTTPException</li>
                    <li>Use dependency injection for shared logic</li>
                </ol>
                
                <p>FastAPI is ideal for building modern, scalable APIs that require high performance and developer productivity.</p>''',
                'excerpt': 'Discover how FastAPI combines high performance, automatic validation, and modern Python features to revolutionize API development.',
                'category': tech_category,
                'tags': ['FastAPI', 'Python', 'API Development'],
                'status': 'published',
                'published_date': datetime(2024, 5, 8, 10, 0, 0),
                'featured_image': 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&h=500&fit=crop&q=80'
            },
            {
                'title': 'Advanced RAG Implementation: Hybrid Search and Re-ranking',
                'slug': 'advanced-rag-hybrid-search-reranking',
                'content': '''<h2>Taking RAG to the Next Level</h2>
                <p>While basic RAG implementations use simple vector similarity search, production systems require more sophisticated approaches. Hybrid search combines multiple retrieval methods, and re-ranking improves result quality significantly.</p>
                
                <h3>Understanding Hybrid Search</h3>
                <p>Hybrid search combines:</p>
                <ul>
                    <li><strong>Dense Vector Search:</strong> Semantic similarity using embeddings</li>
                    <li><strong>Sparse Keyword Search:</strong> Traditional BM25 or TF-IDF matching</li>
                    <li><strong>Metadata Filtering:</strong> Structured data constraints (date ranges, categories, etc.)</li>
                </ul>
                
                <h3>Re-ranking Strategies</h3>
                <p>Re-ranking improves retrieval quality by:</p>
                <ol>
                    <li><strong>Cross-Encoder Models:</strong> More accurate but slower than bi-encoders</li>
                    <li><strong>Multi-stage Retrieval:</strong> Fast initial retrieval, then precise re-ranking</li>
                    <li><strong>Query Understanding:</strong> Analyzing query intent before retrieval</li>
                    <li><strong>Contextual Re-ranking:</strong> Considering document relationships</li>
                </ol>
                
                <h3>Implementation with LangChain</h3>
                <p>LangChain provides excellent tools for hybrid search:</p>
                <pre><code>from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.vectorstores import Chroma

# Combine vector and keyword search
vector_retriever = Chroma.as_retriever()
keyword_retriever = BM25Retriever.from_documents(documents)

ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, keyword_retriever],
    weights=[0.5, 0.5]
)</code></pre>
                
                <h3>Performance Optimization</h3>
                <ul>
                    <li>Use approximate nearest neighbor (ANN) indexes for large datasets</li>
                    <li>Implement caching for frequent queries</li>
                    <li>Optimize chunk sizes and overlap strategies</li>
                    <li>Monitor retrieval metrics (precision, recall, latency)</li>
                </ul>
                
                <p>Advanced RAG techniques can improve retrieval accuracy by 30-50% compared to basic vector search, making them essential for production AI applications.</p>''',
                'excerpt': 'Learn advanced RAG techniques including hybrid search and re-ranking to significantly improve retrieval accuracy in production systems.',
                'category': ai_category,
                'tags': ['RAG', 'AI', 'Machine Learning', 'LangChain'],
                'status': 'published',
                'published_date': datetime(2024, 5, 22, 14, 0, 0),
                'featured_image': 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=800&h=500&fit=crop&q=80'
            },
            {
                'title': 'Django ORM Optimization: Boosting Query Performance',
                'slug': 'django-orm-optimization-query-performance',
                'content': '''<h2>Mastering Django ORM for Better Performance</h2>
                <p>Django's ORM is powerful and convenient, but inefficient queries can cripple application performance. Understanding query optimization techniques is crucial for building scalable Django applications.</p>
                
                <h3>Common Performance Pitfalls</h3>
                <ul>
                    <li><strong>N+1 Queries:</strong> Fetching related objects in loops</li>
                    <li><strong>Over-fetching:</strong> Loading unnecessary data</li>
                    <li><strong>Missing Indexes:</strong> Slow lookups on unindexed fields</li>
                    <li><strong>Inefficient Aggregations:</strong> Processing data in Python instead of the database</li>
                </ul>
                
                <h3>Essential Optimization Techniques</h3>
                <h4>1. Use select_related() for Foreign Keys</h4>
                <pre><code># Bad: N+1 queries
authors = Author.objects.all()
for author in authors:
    print(author.publisher.name)  # Query for each author

# Good: Single query with join
authors = Author.objects.select_related('publisher').all()</code></pre>
                
                <h4>2. Use prefetch_related() for Many-to-Many</h4>
                <pre><code># Efficiently fetch related objects
books = Book.objects.prefetch_related('authors', 'categories').all()</code></pre>
                
                <h4>3. Use only() and defer() for Partial Loading</h4>
                <pre><code># Load only needed fields
users = User.objects.only('username', 'email')
# Defer heavy fields
articles = Article.objects.defer('content')</code></pre>
                
                <h4>4. Database-level Aggregations</h4>
                <pre><code># Use annotations instead of Python loops
from django.db.models import Count, Avg
publishers = Publisher.objects.annotate(
    book_count=Count('book'),
    avg_rating=Avg('book__rating')
)</code></pre>
                
                <h3>Monitoring and Debugging</h3>
                <p>Use Django Debug Toolbar or django-silk to identify slow queries. Enable query logging in development to catch N+1 problems early.</p>
                
                <p>Proper ORM optimization can reduce database queries by 80-90% and improve response times significantly, especially for complex data relationships.</p>''',
                'excerpt': 'Learn essential Django ORM optimization techniques to eliminate N+1 queries, reduce database load, and improve application performance.',
                'category': tech_category,
                'tags': ['Django', 'Python', 'Performance'],
                'status': 'published',
                'published_date': datetime(2024, 6, 5, 11, 0, 0),
                'featured_image': 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&h=500&fit=crop&q=80&auto=format'
            },
            {
                'title': 'Building RESTful APIs with Flask: Best Practices',
                'slug': 'building-restful-apis-flask-best-practices',
                'content': '''<h2>Creating Production-Ready Flask APIs</h2>
                <p>Flask's minimalism makes it perfect for building APIs, but following best practices is essential for creating maintainable, secure, and scalable applications. This guide covers everything from project structure to deployment.</p>
                
                <h3>Project Structure</h3>
                <p>Organize your Flask API project properly:</p>
                <pre><code>project/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── users.py
│   ├── services/
│   └── utils/
├── config.py
├── requirements.txt
└── run.py</code></pre>
                
                <h3>Essential Extensions</h3>
                <ul>
                    <li><strong>Flask-RESTful:</strong> For building REST APIs quickly</li>
                    <li><strong>Flask-SQLAlchemy:</strong> Database ORM</li>
                    <li><strong>Flask-JWT-Extended:</strong> Authentication and authorization</li>
                    <li><strong>Flask-Migrate:</strong> Database migrations</li>
                    <li><strong>Marshmallow:</strong> Serialization and validation</li>
                </ul>
                
                <h3>API Design Principles</h3>
                <ol>
                    <li><strong>RESTful URLs:</strong> Use nouns, not verbs (GET /users, not GET /getUsers)</li>
                    <li><strong>HTTP Methods:</strong> Use appropriate methods (GET, POST, PUT, DELETE)</li>
                    <li><strong>Status Codes:</strong> Return meaningful HTTP status codes</li>
                    <li><strong>Versioning:</strong> Version your API (/api/v1/users)</li>
                    <li><strong>Pagination:</strong> Implement pagination for list endpoints</li>
                    <li><strong>Error Handling:</strong> Consistent error response format</li>
                </ol>
                
                <h3>Security Best Practices</h3>
                <ul>
                    <li>Validate and sanitize all input</li>
                    <li>Use HTTPS in production</li>
                    <li>Implement rate limiting</li>
                    <li>Use environment variables for secrets</li>
                    <li>Enable CORS properly</li>
                    <li>Implement proper authentication</li>
                </ul>
                
                <h3>Example: Well-Structured Endpoint</h3>
                <pre><code>from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

api = Blueprint('users', __name__)

@api.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    users = User.query.paginate(
        page=page, 
        per_page=per_page, 
        error_out=False
    )
    
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'pagination': {
            'page': page,
            'pages': users.pages,
            'total': users.total
        }
    }), 200</code></pre>
                
                <p>Following these practices ensures your Flask API is maintainable, secure, and ready for production deployment.</p>''',
                'excerpt': 'Learn best practices for building production-ready RESTful APIs with Flask, including project structure, security, and design principles.',
                'category': tech_category,
                'tags': ['Flask', 'Python', 'API Development'],
                'status': 'published',
                'published_date': datetime(2024, 6, 18, 9, 0, 0),
                'featured_image': 'https://images.unsplash.com/photo-1551650975-87deedd944c3?w=800&h=500&fit=crop&q=80'
            },
            {
                'title': 'Generative AI in Production: Challenges and Solutions',
                'slug': 'generative-ai-production-challenges-solutions',
                'content': '''<h2>Deploying Generative AI at Scale</h2>
                <p>Moving generative AI from prototype to production presents unique challenges. From managing costs and latency to ensuring reliability and compliance, production AI systems require careful architecture and monitoring.</p>
                
                <h3>Key Production Challenges</h3>
                <h4>1. Cost Management</h4>
                <p>LLM API costs can spiral quickly. Strategies include:</p>
                <ul>
                    <li>Implementing caching for common queries</li>
                    <li>Using smaller models for simple tasks</li>
                    <li>Optimizing prompts to reduce token usage</li>
                    <li>Batching requests when possible</li>
                    <li>Setting up usage monitoring and alerts</li>
                </ul>
                
                <h4>2. Latency Optimization</h4>
                <p>Reduce response times through:</p>
                <ul>
                    <li>Streaming responses for better perceived performance</li>
                    <li>Using faster, smaller models for initial responses</li>
                    <li>Implementing async processing for long-running tasks</li>
                    <li>CDN caching for static AI-generated content</li>
                </ul>
                
                <h4>3. Reliability and Error Handling</h4>
                <p>Build resilient systems:</p>
                <ol>
                    <li>Implement retry logic with exponential backoff</li>
                    <li>Use fallback models when primary fails</li>
                    <li>Set up circuit breakers for API failures</li>
                    <li>Monitor model performance and drift</li>
                    <li>Implement graceful degradation</li>
                </ol>
                
                <h4>4. Quality and Safety</h4>
                <p>Ensure AI outputs meet standards:</p>
                <ul>
                    <li>Implement output validation and filtering</li>
                    <li>Use guardrails to prevent harmful content</li>
                    <li>Monitor for hallucinations and inaccuracies</li>
                    <li>Implement human-in-the-loop for critical decisions</li>
                    <li>Track and log all AI interactions</li>
                </ul>
                
                <h3>Architecture Patterns</h3>
                <p>Common patterns for production AI:</p>
                <pre><code># Example: Async processing with queue
from celery import Celery

app = Celery('ai_tasks')

@app.task
def generate_content(prompt):
    # Long-running AI task
    result = llm.generate(prompt)
    return result

# API endpoint
@app.route('/generate', methods=['POST'])
def generate():
    task = generate_content.delay(request.json['prompt'])
    return {'task_id': task.id}, 202</code></pre>
                
                <h3>Monitoring and Observability</h3>
                <p>Track key metrics:</p>
                <ul>
                    <li>Token usage and costs per request</li>
                    <li>Response latency (p50, p95, p99)</li>
                    <li>Error rates and types</li>
                    <li>User satisfaction scores</li>
                    <li>Model performance metrics</li>
                </ul>
                
                <p>Successfully deploying generative AI requires balancing performance, cost, and quality while maintaining system reliability and user trust.</p>''',
                'excerpt': 'Explore the challenges of deploying generative AI in production and learn practical solutions for cost management, latency, reliability, and quality.',
                'category': ai_category,
                'tags': ['Generative AI', 'AI', 'Machine Learning', 'Production'],
                'status': 'published',
                'published_date': datetime(2024, 7, 2, 13, 0, 0),
                'featured_image': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=500&fit=crop&q=80'
            },
            {
                'title': 'Python Async Programming: Beyond the Basics',
                'slug': 'python-async-programming-beyond-basics',
                'content': '''<h2>Mastering Asynchronous Python</h2>
                <p>Python's async/await syntax enables concurrent programming without threads, making it perfect for I/O-bound applications. Understanding advanced patterns is crucial for building high-performance applications.</p>
                
                <h3>Understanding the Event Loop</h3>
                <p>The event loop is the core of async Python:</p>
                <ul>
                    <li>Manages and distributes execution of different tasks</li>
                    <li>Handles I/O operations without blocking</li>
                    <li>Coordinates coroutines and callbacks</li>
                    <li>Runs in a single thread, avoiding GIL limitations</li>
                </ul>
                
                <h3>Advanced Async Patterns</h3>
                <h4>1. Concurrent Task Execution</h4>
                <pre><code>import asyncio

async def fetch_data(url):
    # Simulate API call
    await asyncio.sleep(1)
    return f"Data from {url}"

async def main():
    # Run multiple tasks concurrently
    results = await asyncio.gather(
        fetch_data("url1"),
        fetch_data("url2"),
        fetch_data("url3")
    )
    return results

# All three fetch_data calls run concurrently</code></pre>
                
                <h4>2. Task Groups (Python 3.11+)</h4>
                <pre><code>async def process_items(items):
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(process_item(item)) for item in items]
    # All tasks complete or one fails (raises exception)</code></pre>
                
                <h4>3. Async Context Managers</h4>
                <pre><code>class AsyncDatabaseConnection:
    async def __aenter__(self):
        self.conn = await connect_to_db()
        return self.conn
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.close()

async def use_db():
    async with AsyncDatabaseConnection() as conn:
        data = await conn.fetch("SELECT * FROM users")</code></pre>
                
                <h3>Common Pitfalls and Solutions</h3>
                <ul>
                    <li><strong>Blocking Calls:</strong> Never use blocking I/O in async code - use async libraries</li>
                    <li><strong>CPU-bound Tasks:</strong> Use ProcessPoolExecutor for CPU-intensive work</li>
                    <li><strong>Exception Handling:</strong> Properly handle exceptions in async contexts</li>
                    <li><strong>Resource Management:</strong> Use async context managers for cleanup</li>
                </ul>
                
                <h3>Performance Tips</h3>
                <ol>
                    <li>Use asyncio.gather() for independent operations</li>
                    <li>Implement connection pooling for databases</li>
                    <li>Set appropriate timeouts for all async operations</li>
                    <li>Monitor event loop performance</li>
                    <li>Use uvloop for better performance (Linux/macOS)</li>
                </ol>
                
                <p>Mastering async Python enables building highly concurrent applications that efficiently handle thousands of simultaneous connections, making it ideal for APIs, web scrapers, and real-time systems.</p>''',
                'excerpt': 'Dive deep into Python async programming with advanced patterns, best practices, and performance optimization techniques for building concurrent applications.',
                'category': tech_category,
                'tags': ['Python', 'Async Programming', 'Web Development'],
                'status': 'published',
                'published_date': datetime(2024, 7, 15, 10, 0, 0),
                'featured_image': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&h=500&fit=crop&q=80'
            },
            {
                'title': 'RAG Evaluation: Measuring Retrieval and Generation Quality',
                'slug': 'rag-evaluation-measuring-quality',
                'content': '''<h2>Evaluating RAG Systems Effectively</h2>
                <p>Building a RAG system is only half the battle - properly evaluating its performance is crucial for improvement and deployment. This guide covers comprehensive evaluation strategies for both retrieval and generation components.</p>
                
                <h3>Retrieval Evaluation Metrics</h3>
                <h4>1. Precision and Recall</h4>
                <p>Measure how well your retrieval finds relevant documents:</p>
                <ul>
                    <li><strong>Precision:</strong> Percentage of retrieved documents that are relevant</li>
                    <li><strong>Recall:</strong> Percentage of relevant documents that were retrieved</li>
                    <li><strong>F1 Score:</strong> Harmonic mean of precision and recall</li>
                </ul>
                
                <h4>2. Mean Reciprocal Rank (MRR)</h4>
                <p>Measures the rank of the first relevant document:</p>
                <pre><code>MRR = (1/n) * Σ(1/rank_i)
# Where rank_i is the position of first relevant doc for query i</code></pre>
                
                <h4>3. Normalized Discounted Cumulative Gain (NDCG)</h4>
                <p>Considers both relevance and position of retrieved documents, giving higher weight to top results.</p>
                
                <h3>Generation Evaluation Metrics</h3>
                <h4>1. Semantic Similarity</h4>
                <p>Use embedding models to measure semantic similarity between generated and reference answers:</p>
                <pre><code>from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
generated_embedding = model.encode(generated_answer)
reference_embedding = model.encode(reference_answer)
similarity = cosine_similarity(generated_embedding, reference_embedding)</code></pre>
                
                <h4>2. Faithfulness</h4>
                <p>Measures whether the generated answer is grounded in the retrieved context. Use NLI (Natural Language Inference) models to check if claims are supported by context.</p>
                
                <h4>3. Answer Relevance</h4>
                <p>Evaluates how well the answer addresses the original question, independent of context quality.</p>
                
                <h3>End-to-End Evaluation</h3>
                <p>Comprehensive evaluation framework:</p>
                <ol>
                    <li><strong>Create Test Dataset:</strong> Curated Q&A pairs with ground truth</li>
                    <li><strong>Retrieval Evaluation:</strong> Measure document retrieval quality</li>
                    <li><strong>Generation Evaluation:</strong> Assess answer quality and accuracy</li>
                    <li><strong>Latency Measurement:</strong> Track response times</li>
                    <li><strong>Cost Analysis:</strong> Monitor token usage and API costs</li>
                </ol>
                
                <h3>Automated Evaluation Tools</h3>
                <ul>
                    <li><strong>RAGAS:</strong> Framework for RAG evaluation</li>
                    <li><strong>LangSmith:</strong> LangChain's evaluation platform</li>
                    <li><strong>Custom Scripts:</strong> Build evaluation pipelines with your metrics</li>
                </ul>
                
                <h3>Best Practices</h3>
                <ul>
                    <li>Evaluate on domain-specific datasets</li>
                    <li>Test with edge cases and adversarial queries</li>
                    <li>Monitor performance over time (data drift)</li>
                    <li>Combine automated and human evaluation</li>
                    <li>Set up continuous evaluation pipelines</li>
                </ul>
                
                <p>Proper evaluation enables data-driven improvements to your RAG system, ensuring it meets quality standards before production deployment.</p>''',
                'excerpt': 'Learn comprehensive strategies for evaluating RAG systems, including retrieval metrics, generation quality assessment, and automated evaluation tools.',
                'category': ai_category,
                'tags': ['RAG', 'AI', 'Machine Learning', 'Evaluation'],
                'status': 'published',
                'published_date': datetime(2024, 8, 1, 14, 0, 0),
                'featured_image': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=500&fit=crop&q=80'
            },
            {
                'title': 'Django Channels: Building Real-Time Applications',
                'slug': 'django-channels-real-time-applications',
                'content': '''<h2>Real-Time Features with Django Channels</h2>
                <p>Django Channels extends Django to handle WebSockets, HTTP2, and other async protocols, enabling real-time features like chat, notifications, and live updates. This guide shows you how to build real-time applications with Django.</p>
                
                <h3>Understanding Django Channels</h3>
                <p>Channels adds async support to Django:</p>
                <ul>
                    <li>Handles WebSocket connections alongside HTTP</li>
                    <li>Uses ASGI (Asynchronous Server Gateway Interface)</li>
                    <li>Enables real-time bidirectional communication</li>
                    <li>Works with Django's existing ORM and authentication</li>
                </ul>
                
                <h3>Setting Up Channels</h3>
                <pre><code># settings.py
INSTALLED_APPS = [
    'django.contrib.auth',
    'channels',
    'myapp',
]

ASGI_APPLICATION = 'myproject.asgi.application'

# Install channels and channels-redis
# pip install channels channels-redis</code></pre>
                
                <h3>Building a WebSocket Consumer</h3>
                <pre><code>from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )
    
    async def chat_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))</code></pre>
                
                <h3>Use Cases</h3>
                <ul>
                    <li><strong>Real-Time Chat:</strong> Instant messaging applications</li>
                    <li><strong>Live Notifications:</strong> Push updates to users</li>
                    <li><strong>Collaborative Editing:</strong> Multiple users editing simultaneously</li>
                    <li><strong>Live Dashboards:</strong> Real-time data visualization</li>
                    <li><strong>Gaming:</strong> Multiplayer game state synchronization</li>
                </ul>
                
                <h3>Best Practices</h3>
                <ol>
                    <li>Use Redis or another channel layer for production</li>
                    <li>Implement proper authentication for WebSocket connections</li>
                    <li>Handle connection errors and reconnection logic</li>
                    <li>Monitor WebSocket connections and message rates</li>
                    <li>Implement rate limiting for WebSocket messages</li>
                </ol>
                
                <p>Django Channels enables building modern, real-time web applications while leveraging Django's powerful ecosystem and familiar patterns.</p>''',
                'excerpt': 'Learn how to build real-time applications with Django Channels, including WebSocket consumers, channel layers, and best practices for production.',
                'category': tech_category,
                'tags': ['Django', 'Python', 'Web Development', 'Real-Time'],
                'status': 'published',
                'published_date': datetime(2024, 8, 12, 11, 0, 0),
                'featured_image': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=500&fit=crop&q=80&auto=format'
            },
            {
                'title': 'High-Level System Design: Building Scalable Architectures',
                'slug': 'high-level-system-design-scalable-architectures',
                'content': '''<h2>Introduction to High-Level System Design</h2>
                <p>High-level system design (HLD) focuses on the overall architecture of a system, defining major components, their interactions, and how they work together to meet system requirements. It's the blueprint that guides the development of scalable, maintainable, and efficient systems.</p>
                
                <h3>Key Principles of High-Level Design</h3>
                <h4>1. Scalability</h4>
                <p>Design systems that can handle growth in users, data, and traffic:</p>
                <ul>
                    <li><strong>Horizontal Scaling:</strong> Add more servers to handle increased load</li>
                    <li><strong>Vertical Scaling:</strong> Increase resources of existing servers</li>
                    <li><strong>Load Balancing:</strong> Distribute traffic across multiple servers</li>
                    <li><strong>Database Sharding:</strong> Partition data across multiple databases</li>
                </ul>
                
                <h4>2. Reliability and Availability</h4>
                <p>Ensure system remains operational:</p>
                <ul>
                    <li>Redundancy at every level (servers, databases, networks)</li>
                    <li>Failover mechanisms for automatic recovery</li>
                    <li>Health checks and monitoring</li>
                    <li>Disaster recovery planning</li>
                </ul>
                
                <h4>3. Performance</h4>
                <p>Optimize for speed and efficiency:</p>
                <ul>
                    <li>Caching strategies (Redis, Memcached)</li>
                    <li>CDN for static content delivery</li>
                    <li>Database indexing and query optimization</li>
                    <li>Asynchronous processing for long-running tasks</li>
                </ul>
                
                <h3>Common High-Level Design Patterns</h3>
                <h4>1. Microservices Architecture</h4>
                <p>Break down application into independent, loosely coupled services:</p>
                <pre><code>┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   API       │    │   User      │    │   Payment   │
│   Gateway   │───▶│   Service   │    │   Service   │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
       └──────────────────┴──────────────────┘
                          │
                   ┌─────────────┐
                   │   Message   │
                   │   Queue     │
                   └─────────────┘</code></pre>
                
                <h4>2. Layered Architecture</h4>
                <p>Organize system into distinct layers:</p>
                <ul>
                    <li><strong>Presentation Layer:</strong> User interface and API endpoints</li>
                    <li><strong>Business Logic Layer:</strong> Core application logic</li>
                    <li><strong>Data Access Layer:</strong> Database interactions</li>
                    <li><strong>Infrastructure Layer:</strong> External services and utilities</li>
                </ul>
                
                <h4>3. Event-Driven Architecture</h4>
                <p>Components communicate through events:</p>
                <pre><code># Example: Event-driven system
class OrderService:
    def create_order(self, order_data):
        order = self.save_order(order_data)
        # Publish event
        event_bus.publish('order.created', {
            'order_id': order.id,
            'user_id': order.user_id,
            'amount': order.total
        })
        return order

class PaymentService:
    def handle_order_created(self, event):
        # Process payment when order is created
        self.process_payment(event['order_id'], event['amount'])</code></pre>
                
                <h3>Designing for Scale</h3>
                <h4>Capacity Estimation</h4>
                <p>Estimate system requirements:</p>
                <ul>
                    <li><strong>Traffic:</strong> Requests per second (RPS)</li>
                    <li><strong>Storage:</strong> Data volume and growth rate</li>
                    <li><strong>Bandwidth:</strong> Network throughput requirements</li>
                    <li><strong>Compute:</strong> CPU and memory needs</li>
                </ul>
                
                <h4>Database Design</h4>
                <p>Choose appropriate database types:</p>
                <ul>
                    <li><strong>SQL Databases:</strong> For structured data with ACID requirements</li>
                    <li><strong>NoSQL Databases:</strong> For flexible schemas and horizontal scaling</li>
                    <li><strong>Time-Series DB:</strong> For metrics and analytics</li>
                    <li><strong>Graph Databases:</strong> For relationship-heavy data</li>
                </ul>
                
                <h3>System Design Example: URL Shortener</h3>
                <p>Key components:</p>
                <ol>
                    <li><strong>API Service:</strong> Handle URL shortening requests</li>
                    <li><strong>Hash Service:</strong> Generate unique short codes</li>
                    <li><strong>Database:</strong> Store mappings (short URL → long URL)</li>
                    <li><strong>Cache:</strong> Redis for frequently accessed URLs</li>
                    <li><strong>Load Balancer:</strong> Distribute traffic</li>
                </ol>
                
                <h3>Best Practices</h3>
                <ul>
                    <li>Start simple, add complexity only when needed</li>
                    <li>Design for failure - assume components will fail</li>
                    <li>Use proven technologies and patterns</li>
                    <li>Consider trade-offs (consistency vs availability)</li>
                    <li>Document design decisions and rationale</li>
                    <li>Plan for monitoring and observability</li>
                </ul>
                
                <p>High-level system design is about making informed architectural decisions that balance requirements, constraints, and future scalability needs.</p>''',
                'excerpt': 'Learn the fundamentals of high-level system design, including scalability patterns, architecture styles, and best practices for building robust systems.',
                'category': tech_category,
                'tags': ['System Design', 'Architecture', 'Scalability', 'Software Engineering'],
                'status': 'published',
                'published_date': datetime(2024, 12, 20, 10, 0, 0),
                'featured_image': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&h=500&fit=crop&q=80'
            },
            {
                'title': 'Low-Level System Design: Implementing Efficient Components',
                'slug': 'low-level-system-design-efficient-components',
                'content': '''<h2>Introduction to Low-Level System Design</h2>
                <p>Low-level system design (LLD) focuses on the detailed design of individual components, classes, modules, and their interactions. It bridges the gap between high-level architecture and actual code implementation, ensuring components are well-designed, efficient, and maintainable.</p>
                
                <h3>Key Concepts in Low-Level Design</h3>
                <h4>1. Object-Oriented Design Principles</h4>
                <p>Apply SOLID principles:</p>
                <ul>
                    <li><strong>S - Single Responsibility:</strong> Each class has one reason to change</li>
                    <li><strong>O - Open/Closed:</strong> Open for extension, closed for modification</li>
                    <li><strong>L - Liskov Substitution:</strong> Subtypes must be substitutable for base types</li>
                    <li><strong>I - Interface Segregation:</strong> Clients shouldn't depend on unused interfaces</li>
                    <li><strong>D - Dependency Inversion:</strong> Depend on abstractions, not concretions</li>
                </ul>
                
                <h4>2. Design Patterns</h4>
                <p>Common patterns for component design:</p>
                
                <h5>Factory Pattern</h5>
                <pre><code>class PaymentProcessorFactory:
    @staticmethod
    def create_processor(payment_type):
        if payment_type == 'credit_card':
            return CreditCardProcessor()
        elif payment_type == 'paypal':
            return PayPalProcessor()
        elif payment_type == 'stripe':
            return StripeProcessor()
        else:
            raise ValueError(f"Unknown payment type: {payment_type}")

# Usage
processor = PaymentProcessorFactory.create_processor('stripe')
processor.process_payment(amount)</code></pre>
                
                <h5>Observer Pattern</h5>
                <pre><code>class EventPublisher:
    def __init__(self):
        self._observers = []
    
    def subscribe(self, observer):
        self._observers.append(observer)
    
    def notify(self, event):
        for observer in self._observers:
            observer.update(event)

class EmailService:
    def update(self, event):
        if event.type == 'order_placed':
            self.send_order_confirmation(event.data)

# Usage
publisher = EventPublisher()
publisher.subscribe(EmailService())
publisher.notify(OrderEvent('order_placed', order_data))</code></pre>
                
                <h5>Strategy Pattern</h5>
                <pre><code>class SortingStrategy:
    def sort(self, data):
        raise NotImplementedError

class QuickSort(SortingStrategy):
    def sort(self, data):
        # Quick sort implementation
        return sorted(data)

class MergeSort(SortingStrategy):
    def sort(self, data):
        # Merge sort implementation
        return self._merge_sort(data)

class DataProcessor:
    def __init__(self, strategy: SortingStrategy):
        self.strategy = strategy
    
    def process(self, data):
        return self.strategy.sort(data)</code></pre>
                
                <h3>Designing Data Structures</h3>
                <h4>1. Cache Implementation</h4>
                <pre><code>from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key):
        if key not in self.cache:
            return -1
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        
        if len(self.cache) > self.capacity:
            # Remove least recently used
            self.cache.popitem(last=False)</code></pre>
                
                <h4>2. Rate Limiter</h4>
                <pre><code>from collections import deque
import time

class RateLimiter:
    def __init__(self, max_requests, time_window):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
    
    def is_allowed(self, user_id):
        now = time.time()
        # Remove requests outside time window
        while self.requests and self.requests[0] < now - self.time_window:
            self.requests.popleft()
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False</code></pre>
                
                <h3>Component Design Example: Task Scheduler</h3>
                <pre><code>from heapq import heappush, heappop
import threading
import time

class Task:
    def __init__(self, task_id, execute_at, callback):
        self.task_id = task_id
        self.execute_at = execute_at
        self.callback = callback
    
    def __lt__(self, other):
        return self.execute_at < other.execute_at

class TaskScheduler:
    def __init__(self):
        self.tasks = []
        self.lock = threading.Lock()
        self.running = False
    
    def schedule(self, task_id, delay_seconds, callback):
        execute_at = time.time() + delay_seconds
        task = Task(task_id, execute_at, callback)
        
        with self.lock:
            heappush(self.tasks, task)
    
    def start(self):
        self.running = True
        while self.running:
            with self.lock:
                if not self.tasks:
                    time.sleep(0.1)
                    continue
                
                task = self.tasks[0]
                if task.execute_at <= time.time():
                    heappop(self.tasks)
                    task.callback()
                else:
                    sleep_time = task.execute_at - time.time()
                    time.sleep(min(sleep_time, 0.1))</code></pre>
                
                <h3>Designing for Performance</h3>
                <h4>1. Optimize Data Access</h4>
                <ul>
                    <li>Use appropriate data structures (hash maps for O(1) lookups)</li>
                    <li>Implement lazy loading for large datasets</li>
                    <li>Use connection pooling for database access</li>
                    <li>Batch operations when possible</li>
                </ul>
                
                <h4>2. Memory Management</h4>
                <ul>
                    <li>Avoid memory leaks (proper cleanup)</li>
                    <li>Use object pooling for frequently created objects</li>
                    <li>Implement pagination for large result sets</li>
                    <li>Monitor memory usage and optimize hot paths</li>
                </ul>
                
                <h4>3. Concurrency</h4>
                <pre><code>import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncDataProcessor:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process_batch(self, items):
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(self.executor, self.process_item, item)
            for item in items
        ]
        return await asyncio.gather(*tasks)
    
    def process_item(self, item):
        # Process individual item
        return processed_item</code></pre>
                
                <h3>Error Handling and Resilience</h3>
                <pre><code>class RetryableOperation:
    def __init__(self, max_retries=3, backoff_factor=2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    def execute(self, operation, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                wait_time = self.backoff_factor ** attempt
                time.sleep(wait_time)
        return None</code></pre>
                
                <h3>Best Practices</h3>
                <ul>
                    <li>Design for testability - make components easy to unit test</li>
                    <li>Keep components focused and cohesive</li>
                    <li>Minimize coupling between components</li>
                    <li>Use dependency injection for flexibility</li>
                    <li>Document interfaces and contracts clearly</li>
                    <li>Consider edge cases and error scenarios</li>
                    <li>Optimize for readability and maintainability</li>
                </ul>
                
                <p>Low-level design transforms architectural blueprints into concrete, implementable components that are efficient, maintainable, and aligned with system requirements.</p>''',
                'excerpt': 'Master low-level system design with design patterns, data structures, and component implementation strategies for building efficient software systems.',
                'category': tech_category,
                'tags': ['System Design', 'Design Patterns', 'Data Structures', 'Software Engineering'],
                'status': 'published',
                'published_date': datetime(2024, 12, 22, 14, 0, 0),
                'featured_image': 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=500&fit=crop&q=80'
            },
            {
                'title': 'System Design Interview: Designing a Distributed Cache',
                'slug': 'system-design-interview-distributed-cache',
                'content': '''<h2>Designing a Distributed Cache System</h2>
                <p>Distributed caching is a critical component of modern systems, enabling fast data access and reducing database load. This post walks through designing a production-ready distributed cache system, a common system design interview question.</p>
                
                <h3>Requirements</h3>
                <h4>Functional Requirements</h4>
                <ul>
                    <li>Store key-value pairs</li>
                    <li>Retrieve value by key</li>
                    <li>Set expiration time for keys</li>
                    <li>Handle cache eviction when full</li>
                </ul>
                
                <h4>Non-Functional Requirements</h4>
                <ul>
                    <li>High availability (99.9% uptime)</li>
                    <li>Low latency (&lt;10ms for cache hits)</li>
                    <li>Scalability (handle millions of requests per second)</li>
                    <li>Consistency (eventual consistency acceptable)</li>
                </ul>
                
                <h3>High-Level Design</h3>
                <h4>Architecture Overview</h4>
                <pre><code>┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Load      │
│   Balancer  │
└──────┬──────┘
       │
       ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Cache      │    │  Cache      │    │  Cache      │
│  Server 1   │    │  Server 2   │    │  Server 3   │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
       └──────────────────┴──────────────────┘
                          │
                   ┌─────────────┐
                   │  Consistent │
                   │  Hashing    │
                   └─────────────┘</code></pre>
                
                <h4>Key Design Decisions</h4>
                <ol>
                    <li><strong>Consistent Hashing:</strong> Distribute keys across cache servers</li>
                    <li><strong>Replication:</strong> Store copies on multiple servers for availability</li>
                    <li><strong>Eviction Policy:</strong> LRU (Least Recently Used) for cache eviction</li>
                    <li><strong>Write-Through vs Write-Back:</strong> Write-through for consistency</li>
                </ol>
                
                <h3>Low-Level Design</h3>
                <h4>Cache Node Implementation</h4>
                <pre><code>from collections import OrderedDict
import threading
import time

class CacheNode:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.expiry_times = {}
        self.lock = threading.RLock()
    
    def get(self, key):
        with self.lock:
            if key not in self.cache:
                return None
            
            # Check expiration
            if key in self.expiry_times:
                if time.time() > self.expiry_times[key]:
                    del self.cache[key]
                    del self.expiry_times[key]
                    return None
            
            # Move to end (LRU)
            self.cache.move_to_end(key)
            return self.cache[key]
    
    def set(self, key, value, ttl=None):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            elif len(self.cache) >= self.capacity:
                # Evict least recently used
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                if oldest_key in self.expiry_times:
                    del self.expiry_times[oldest_key]
            
            self.cache[key] = value
            if ttl:
                self.expiry_times[key] = time.time() + ttl
    
    def delete(self, key):
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                if key in self.expiry_times:
                    del self.expiry_times[key]</code></pre>
                
                <h4>Consistent Hashing</h4>
                <pre><code>import hashlib

class ConsistentHash:
    def __init__(self, nodes, replicas=3):
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []
        
        for node in nodes:
            for i in range(replicas):
                key = self._hash(f"{node}:{i}")
                self.ring[key] = node
                self.sorted_keys.append(key)
        
        self.sorted_keys.sort()
    
    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def get_node(self, key):
        if not self.ring:
            return None
        
        hash_key = self._hash(key)
        
        # Find first node with hash >= key's hash
        for ring_key in self.sorted_keys:
            if ring_key >= hash_key:
                return self.ring[ring_key]
        
        # Wrap around to first node
        return self.ring[self.sorted_keys[0]]</code></pre>
                
                <h4>Distributed Cache Client</h4>
                <pre><code>class DistributedCache:
    def __init__(self, nodes):
        self.hash_ring = ConsistentHash(nodes)
        self.nodes = {node: CacheNode(capacity=10000) for node in nodes}
    
    def get(self, key):
        node = self.hash_ring.get_node(key)
        return self.nodes[node].get(key)
    
    def set(self, key, value, ttl=None):
        node = self.hash_ring.get_node(key)
        self.nodes[node].set(key, value, ttl)
    
    def delete(self, key):
        node = self.hash_ring.get_node(key)
        self.nodes[node].delete(key)</code></pre>
                
                <h3>Scaling Considerations</h3>
                <h4>1. Horizontal Scaling</h4>
                <ul>
                    <li>Add/remove cache nodes dynamically</li>
                    <li>Rebalance keys when nodes are added/removed</li>
                    <li>Minimize data movement during rebalancing</li>
                </ul>
                
                <h4>2. Replication</h4>
                <ul>
                    <li>Replicate data across multiple nodes</li>
                    <li>Read from replica if primary fails</li>
                    <li>Handle replication lag</li>
                </ul>
                
                <h4>3. Monitoring</h4>
                <ul>
                    <li>Cache hit/miss ratio</li>
                    <li>Latency metrics</li>
                    <li>Memory usage per node</li>
                    <li>Network bandwidth</li>
                </ul>
                
                <h3>Trade-offs</h3>
                <ul>
                    <li><strong>Consistency vs Availability:</strong> Choose eventual consistency for better availability</li>
                    <li><strong>Memory vs Performance:</strong> More memory allows larger cache, better hit rates</li>
                    <li><strong>Complexity vs Features:</strong> Simple design vs advanced features like persistence</li>
                </ul>
                
                <p>This design demonstrates how to approach system design problems by breaking them down into high-level architecture and low-level implementation details.</p>''',
                'excerpt': 'Step-by-step guide to designing a distributed cache system, covering consistent hashing, replication, and implementation details for system design interviews.',
                'category': tech_category,
                'tags': ['System Design', 'Distributed Systems', 'Caching', 'Interview'],
                'status': 'published',
                'published_date': datetime(2024, 12, 24, 16, 0, 0),
                'featured_image': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&h=500&fit=crop&q=80'
            }
        ]
        
        for post_data in blog_posts:
            # Check if post already exists
            existing_post = Post.query.filter_by(slug=post_data['slug']).first()
            if existing_post:
                # Update existing post with latest data
                existing_post.title = post_data['title']
                existing_post.content = post_data['content']
                existing_post.excerpt = post_data['excerpt']
                existing_post.published_date = post_data['published_date']
                existing_post.status = post_data['status']
                if post_data.get('featured_image'):
                    existing_post.featured_image = post_data.get('featured_image', '')
                # Update tags
                existing_post.tags = []
                for tag_name in post_data['tags']:
                    if tag_name in tag_objects:
                        existing_post.tags.append(tag_objects[tag_name])
                print(f"Updated existing post: {existing_post.title}")
                continue
            
            post = Post(
                title=post_data['title'],
                slug=post_data['slug'],
                author_id=admin_user.id,
                content=post_data['content'],
                excerpt=post_data['excerpt'],
                category_id=post_data['category'].id,
                status=post_data['status'],
                published_date=post_data['published_date'],
                meta_description=post_data['excerpt'][:160],
                meta_keywords=', '.join(post_data['tags']),
                featured_image=post_data.get('featured_image', '')
            )
            
            # Add tags
            for tag_name in post_data['tags']:
                if tag_name in tag_objects:
                    post.tags.append(tag_objects[tag_name])
            
            db.session.add(post)
        
        # Commit all changes
        db.session.commit()
        print("Portfolio and blog data populated successfully!")
        print(f"Profile created for: {profile.name}")
        print(f"Added {len(experiences)} experiences")
        print(f"Added {len(skills_data)} skills")
        print(f"Added {len(certifications)} certifications")
        print(f"Added {len(achievements)} achievements")
        print(f"Added {len(projects)} projects")
        print(f"Added {len(blog_posts)} blog posts")

if __name__ == '__main__':
    populate_database()

