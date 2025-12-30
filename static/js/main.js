// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    const body = document.body;
    const navbar = document.querySelector('.navbar');
    
    // Navbar scroll effect and full-width handling for mobile devices
    if (navbar) {
        const checkMobile = () => window.innerWidth <= 768;
        
        // Function to set navbar to full width on mobile (100%)
        const setMobileNavbar = () => {
            navbar.style.position = 'fixed';
            navbar.style.top = '0';
            navbar.style.left = '0';
            navbar.style.right = '0';
            navbar.style.width = '100%';
            navbar.style.maxWidth = '100%';
            navbar.style.minWidth = '100%';
            navbar.style.margin = '0';
            navbar.style.marginLeft = '0';
            navbar.style.marginRight = '0';
            navbar.style.transform = 'none';
            navbar.style.overflow = 'visible';
            navbar.style.boxSizing = 'border-box';
            
            // Also fix the container inside navbar to be full width (100%)
            const navbarContainer = navbar.querySelector('.container');
            if (navbarContainer) {
                navbarContainer.style.width = '100%';
                navbarContainer.style.maxWidth = '100%';
                navbarContainer.style.minWidth = '100%';
                navbarContainer.style.margin = '0 auto';
                navbarContainer.style.marginLeft = '0';
                navbarContainer.style.marginRight = '0';
                navbarContainer.style.boxSizing = 'border-box';
            }
        };
        
        // Function to reset navbar for desktop
        const setDesktopNavbar = () => {
            navbar.style.position = '';
            navbar.style.top = '';
            navbar.style.left = '';
            navbar.style.right = '';
            navbar.style.width = '';
            navbar.style.maxWidth = '';
            navbar.style.minWidth = '';
            navbar.style.margin = '';
            navbar.style.marginLeft = '';
            navbar.style.marginRight = '';
            navbar.style.transform = '';
            navbar.style.overflow = '';
            navbar.style.boxSizing = '';
            
            const navbarContainer = navbar.querySelector('.container');
            if (navbarContainer) {
                navbarContainer.style.width = '';
                navbarContainer.style.maxWidth = '';
                navbarContainer.style.minWidth = '';
                navbarContainer.style.margin = '';
                navbarContainer.style.marginLeft = '';
                navbarContainer.style.marginRight = '';
                navbarContainer.style.boxSizing = '';
            }
        };
        
        let isMobile = checkMobile();
        
        // Set navbar to fixed and full width on mobile immediately
        if (isMobile) {
            setMobileNavbar();
        }
        
        // Only add scroll effect on desktop
        if (!isMobile) {
            let lastScroll = 0;
            window.addEventListener('scroll', function() {
                const currentScroll = window.pageYOffset;
                if (currentScroll > 50) {
                    navbar.classList.add('scrolled');
                } else {
                    navbar.classList.remove('scrolled');
                }
                lastScroll = currentScroll;
            });
        }
        
        // Handle window resize and orientation change
        let resizeTimer;
        const handleResize = () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                const isMobileNow = checkMobile();
                if (isMobileNow) {
                    // Switched to mobile - ensure navbar is fixed and full width
                    setMobileNavbar();
                } else if (!isMobile && isMobileNow !== isMobile) {
                    // Switched to desktop - reset navbar
                    setDesktopNavbar();
                }
                isMobile = isMobileNow;
            }, 100);
        };
        
        window.addEventListener('resize', handleResize);
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                if (checkMobile()) {
                    setMobileNavbar();
                }
            }, 100);
        });
        
        // Re-check on load to handle dynamic viewport changes
        window.addEventListener('load', () => {
            if (checkMobile()) {
                setMobileNavbar();
            }
        });
    }
    
    if (menuToggle && navMenu) {
        // Ensure menu is properly initialized
        console.log('Menu toggle found:', !!menuToggle);
        console.log('Nav menu found:', !!navMenu);
        const menuItems = navMenu.querySelectorAll('li');
        console.log('Nav menu items count:', menuItems.length);
        
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            e.preventDefault();
            const isActive = navMenu.classList.contains('active');
            
            if (isActive) {
                navMenu.classList.remove('active');
                menuToggle.classList.remove('active');
                body.classList.remove('menu-open');
            } else {
                navMenu.classList.add('active');
                menuToggle.classList.add('active');
                body.classList.add('menu-open');
            }
            
            // Force reflow to ensure styles are applied
            void navMenu.offsetWidth;
            
            // Debug log
            console.log('Menu toggle clicked. Active:', !isActive);
            console.log('Nav menu classes:', navMenu.className);
            console.log('Nav menu transform:', window.getComputedStyle(navMenu).transform);
            console.log('Nav menu visibility:', window.getComputedStyle(navMenu).visibility);
            console.log('Nav menu opacity:', window.getComputedStyle(navMenu).opacity);
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            const isClickInsideNav = navMenu.contains(event.target);
            const isClickOnToggle = menuToggle.contains(event.target);
            
            if (!isClickInsideNav && !isClickOnToggle && navMenu.classList.contains('active')) {
                navMenu.classList.remove('active');
                menuToggle.classList.remove('active');
                body.classList.remove('menu-open');
            }
        });
        
        // Close menu when clicking a link
        const navLinks = navMenu.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('active');
                menuToggle.classList.remove('active');
                body.classList.remove('menu-open');
            });
        });
        
        // Close menu on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && navMenu.classList.contains('active')) {
                navMenu.classList.remove('active');
                menuToggle.classList.remove('active');
                body.classList.remove('menu-open');
            }
        });
    }
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Animate skill bars on scroll
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progressBar = entry.target.querySelector('.skill-progress');
                if (progressBar) {
                    const width = progressBar.style.width;
                    progressBar.style.width = '0%';
                    setTimeout(() => {
                        progressBar.style.width = width;
                    }, 100);
                }
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.skill-item').forEach(item => {
        observer.observe(item);
    });
    
    // Add copy buttons to code blocks (both blog posts and topic pages)
    const codeBlocks = document.querySelectorAll('.post-body pre, .topic-body pre');
    codeBlocks.forEach(pre => {
        // Skip if already has copy button
        if (pre.querySelector('.code-copy-btn')) {
            return;
        }
        
        // Create copy button
        const copyBtn = document.createElement('button');
        copyBtn.className = 'code-copy-btn';
        copyBtn.setAttribute('aria-label', 'Copy code');
        copyBtn.innerHTML = `
            <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path d="M8 5.00005C7.01165 5.00005 6.49359 5.00005 6.09202 5.21799C5.71569 5.40973 5.40973 5.71569 5.21799 6.09202C5 6.49359 5 7.01165 5 8.00005M8 5.00005C8 4.06815 8 3.6022 8.15224 3.23463C8.35523 2.74458 8.74458 2.35523 9.23463 2.15224C9.6022 2.00005 10.0681 2.00005 11 2.00005H13C13.9319 2.00005 14.3978 2.00005 14.7654 2.15224C15.2554 2.35523 15.6448 2.74458 15.8478 3.23463C16 3.6022 16 4.06815 16 5.00005M8 5.00005H6C4.89543 5.00005 4 5.89548 4 7.00005V19C4 20.1046 4.89543 21 6 21H18C19.1046 21 20 20.1046 20 19V7.00005C20 5.89548 19.1046 5.00005 18 5.00005H16"/>
            </svg>
            <span>Copy</span>
        `;
        
        // Get code content
        const code = pre.querySelector('code') || pre;
        const codeText = code.textContent || code.innerText;
        
        // Add click handler
        copyBtn.addEventListener('click', async () => {
            try {
                await navigator.clipboard.writeText(codeText);
                copyBtn.classList.add('copied');
                copyBtn.innerHTML = `
                    <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path d="M20 6L9 17l-5-5"/>
                    </svg>
                    <span>Copied!</span>
                `;
                setTimeout(() => {
                    copyBtn.classList.remove('copied');
                    copyBtn.innerHTML = `
                        <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <path d="M8 5.00005C7.01165 5.00005 6.49359 5.00005 6.09202 5.21799C5.71569 5.40973 5.40973 5.71569 5.21799 6.09202C5 6.49359 5 7.01165 5 8.00005M8 5.00005C8 4.06815 8 3.6022 8.15224 3.23463C8.35523 2.74458 8.74458 2.35523 9.23463 2.15224C9.6022 2.00005 10.0681 2.00005 11 2.00005H13C13.9319 2.00005 14.3978 2.00005 14.7654 2.15224C15.2554 2.35523 15.6448 2.74458 15.8478 3.23463C16 3.6022 16 4.06815 16 5.00005M8 5.00005H6C4.89543 5.00005 4 5.89548 4 7.00005V19C4 20.1046 4.89543 21 6 21H18C19.1046 21 20 20.1046 20 19V7.00005C20 5.89548 19.1046 5.00005 18 5.00005H16"/>
                        </svg>
                        <span>Copy</span>
                    `;
                }, 2000);
            } catch (err) {
                console.error('Failed to copy code:', err);
                copyBtn.textContent = 'Error';
                setTimeout(() => {
                    copyBtn.innerHTML = `
                        <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                            <path d="M8 5.00005C7.01165 5.00005 6.49359 5.00005 6.09202 5.21799C5.71569 5.40973 5.40973 5.71569 5.21799 6.09202C5 6.49359 5 7.01165 5 8.00005M8 5.00005C8 4.06815 8 3.6022 8.15224 3.23463C8.35523 2.74458 8.74458 2.35523 9.23463 2.15224C9.6022 2.00005 10.0681 2.00005 11 2.00005H13C13.9319 2.00005 14.3978 2.00005 14.7654 2.15224C15.2554 2.35523 15.6448 2.74458 15.8478 3.23463C16 3.6022 16 4.06815 16 5.00005M8 5.00005H6C4.89543 5.00005 4 5.89548 4 7.00005V19C4 20.1046 4.89543 21 6 21H18C19.1046 21 20 20.1046 20 19V7.00005C20 5.89548 19.1046 5.00005 18 5.00005H16"/>
                        </svg>
                        <span>Copy</span>
                    `;
                }, 2000);
            }
        });
        
        // Insert copy button
        pre.style.position = 'relative';
        pre.appendChild(copyBtn);
    });
    
    // Make table rows clickable
    const clickableRows = document.querySelectorAll('.clickable-row');
    clickableRows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Don't navigate if clicking on action buttons
            if (e.target.closest('.action-buttons')) {
                return;
            }
            const href = this.getAttribute('data-href');
            if (href) {
                window.location.href = href;
            }
        });
    });
    
    // Modern Features: Fade-in animations on scroll
    const fadeElements = document.querySelectorAll('.resume-section, .project-card, .skill-category, .blog-card');
    const fadeObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    fadeElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        fadeObserver.observe(el);
    });
    
    // Smooth page transitions
    document.querySelectorAll('a[href^="/"], a[href^="#"]').forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('href').startsWith('#')) return;
            if (this.target === '_blank') return;
            
            const href = this.getAttribute('href');
            if (href && !href.startsWith('mailto:') && !href.startsWith('tel:')) {
                // Add loading state
                document.body.style.opacity = '0.7';
                document.body.style.transition = 'opacity 0.2s';
            }
        });
    });
    
    // Removed parallax effect to prevent overlap issues
    // Parallax can cause content overlap on scroll
    
    // Lazy loading images with fade-in
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    img.style.opacity = '0';
                    img.style.transition = 'opacity 0.5s';
                    img.onload = () => {
                        img.style.opacity = '1';
                    };
                }
                imageObserver.unobserve(img);
            }
        });
    }, {
        rootMargin: '50px'
    });
    
    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
    
    // Add ripple effect to buttons
    document.querySelectorAll('.btn-icon-only, .btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Progress indicator on scroll
    const progressBar = document.createElement('div');
    progressBar.className = 'scroll-progress';
    document.body.appendChild(progressBar);
    
    window.addEventListener('scroll', () => {
        const windowHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (window.pageYOffset / windowHeight) * 100;
        progressBar.style.width = scrolled + '%';
    });
    
    // Smooth reveal animations for text
    const textElements = document.querySelectorAll('h1, h2, h3, p, .bio');
    const textObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 50);
                textObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1
    });
    
    textElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(10px)';
        el.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
        textObserver.observe(el);
    });
});

