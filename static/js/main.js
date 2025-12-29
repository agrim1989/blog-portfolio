// Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    const body = document.body;
    const navbar = document.querySelector('.navbar');
    
    // Navbar scroll effect
    if (navbar) {
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
    
    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            navMenu.classList.toggle('active');
            menuToggle.classList.toggle('active');
            body.classList.toggle('menu-open');
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
    
    // Add copy buttons to code blocks
    const codeBlocks = document.querySelectorAll('.post-body pre');
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
});

