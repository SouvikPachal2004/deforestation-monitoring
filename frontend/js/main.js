document.addEventListener('DOMContentLoaded', function() {
    // Preloader
    const preloader = document.querySelector('.preloader');
    window.addEventListener('load', function() {
        setTimeout(function() {
            preloader.style.opacity = '0';
            setTimeout(function() {
                preloader.style.display = 'none';
            }, 500);
        }, 1000);
    });

    // Mobile Navigation Toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    menuToggle.addEventListener('click', function() {
        navLinks.classList.toggle('active');
    });

    // Close mobile menu when clicking on a link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function() {
            navLinks.classList.remove('active');
        });
    });

    // Active Navigation Link on Scroll
    const sections = document.querySelectorAll('section');
    const navItems = document.querySelectorAll('.nav-link');
    
    window.addEventListener('scroll', function() {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (pageYOffset >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });
        
        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href').slice(1) === current) {
                item.classList.add('active');
            }
        });
    });

    // Header Scroll Effect
    const header = document.querySelector('.header');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            header.style.boxShadow = '0 2px 15px rgba(0, 0, 0, 0.1)';
        } else {
            header.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        }
    });

    // Back to Top Button
    const backToTopBtn = document.querySelector('.back-to-top');
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            backToTopBtn.classList.add('visible');
        } else {
            backToTopBtn.classList.remove('visible');
        }
    });
    
    backToTopBtn.addEventListener('click', function(e) {
        e.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Smooth Scrolling for Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetSection = document.querySelector(targetId);
            if (targetSection) {
                window.scrollTo({
                    top: targetSection.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });

    // File Upload Area
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');
    
    browseBtn.addEventListener('click', function() {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', function() {
        handleFiles(this.files);
    });
    
    // Drag and Drop functionality
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', function() {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        if (e.dataTransfer.files.length) {
            handleFiles(e.dataTransfer.files);
        }
    });
    
    function handleFiles(files) {
        if (files.length > 0) {
            // Here you would normally upload the files to the server
            console.log('Files selected:', files);
            
            // Show a success message or update the UI
            const uploadContent = uploadArea.querySelector('.upload-content');
            uploadContent.innerHTML = `
                <i class="fas fa-check-circle" style="color: var(--success-color); font-size: 3rem; margin-bottom: 15px;"></i>
                <h4>${files.length} file(s) selected</h4>
                <p>Click "Analyze Images" to process</p>
            `;
        }
    }

    // Analyze Button
    const analyzeBtn = document.getElementById('analyzeBtn');
    analyzeBtn.addEventListener('click', function() {
        // Here you would normally send the files to the backend for analysis
        console.log('Analyzing images...');
        
        // Show loading state
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        this.disabled = true;
        
        // Simulate analysis process
        setTimeout(() => {
            this.innerHTML = 'Analyze Images';
            this.disabled = false;
            
            // Show results tab
            const resultsSection = document.querySelector('.results-section');
            resultsSection.scrollIntoView({ behavior: 'smooth' });
            
            // Switch to overview tab
            document.querySelector('.tab-btn[data-tab="overview"]').click();
        }, 2000);
    });

    // Tab Functionality
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Remove active class from all tabs and panes
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding pane
            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // Map View Toggle
    const mapBtns = document.querySelectorAll('.map-btn');
    mapBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            mapBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Here you would normally change the map view
            console.log('Map view changed to:', this.id);
        });
    });

    // Chart Period Selector
    const trendPeriod = document.getElementById('trendPeriod');
    trendPeriod.addEventListener('change', function() {
        // Here you would normally update the chart with new data
        console.log('Chart period changed to:', this.value);
    });

    // Report Generation
    const generateReportBtn = document.getElementById('generateReportBtn');
    generateReportBtn.addEventListener('click', function() {
        // Here you would normally generate a report based on the filters
        console.log('Generating report...');
        
        // Show loading state
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        this.disabled = true;
        
        // Simulate report generation
        setTimeout(() => {
            this.innerHTML = 'Generate Report';
            this.disabled = false;
            
            // Show success message
            showNotification('Report generated successfully!', 'success');
        }, 2000);
    });

    // View Toggle for Reports
    const gridView = document.getElementById('gridView');
    const listView = document.getElementById('listView');
    const reportsGrid = document.querySelector('.reports-grid');
    
    gridView.addEventListener('click', function() {
        gridView.classList.add('active');
        listView.classList.remove('active');
        reportsGrid.classList.remove('list-view');
    });
    
    listView.addEventListener('click', function() {
        listView.classList.add('active');
        gridView.classList.remove('active');
        reportsGrid.classList.add('list-view');
    });

    // Pagination
    const pageBtns = document.querySelectorAll('.page-btn:not(.dots)');
    pageBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.id === 'prevPage' || this.id === 'nextPage') return;
            
            document.querySelectorAll('.page-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Here you would normally load the corresponding page
            console.log('Page changed to:', this.textContent);
        });
    });

    // Contact Form
    const contactForm = document.getElementById('contactForm');
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Get form values
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const subject = document.getElementById('subject').value;
        const message = document.getElementById('message').value;
        
        // Here you would normally send the form data to the server
        console.log('Form submitted:', { name, email, subject, message });
        
        // Show loading state
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        submitBtn.disabled = true;
        
        // Simulate form submission
        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            
            // Reset form
            contactForm.reset();
            
            // Show success message
            showNotification('Message sent successfully!', 'success');
        }, 1500);
    });

    // Newsletter Form
    const newsletterForm = document.querySelector('.newsletter-form');
    newsletterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const email = this.querySelector('input').value;
        
        // Here you would normally subscribe the email
        console.log('Newsletter subscription:', email);
        
        // Show loading state
        const submitBtn = this.querySelector('button');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        submitBtn.disabled = true;
        
        // Simulate subscription
        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            
            // Reset form
            this.reset();
            
            // Show success message
            showNotification('Successfully subscribed to newsletter!', 'success');
        }, 1500);
    });

    // Export Button
    const exportBtn = document.getElementById('exportBtn');
    exportBtn.addEventListener('click', function() {
        // Here you would normally export the results
        console.log('Exporting results...');
        
        // Show loading state
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Exporting...';
        this.disabled = true;
        
        // Simulate export
        setTimeout(() => {
            this.innerHTML = '<i class="fas fa-download"></i> Export';
            this.disabled = false;
            
            // Show success message
            showNotification('Results exported successfully!', 'success');
        }, 1500);
    });

    // Share Button
    const shareBtn = document.getElementById('shareBtn');
    shareBtn.addEventListener('click', function() {
        // Here you would normally show share options
        console.log('Sharing results...');
        
        // Show success message
        showNotification('Share link copied to clipboard!', 'success');
    });

    // Notification Function
    function showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Add notification styles if they don't exist
        if (!document.querySelector('#notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                .notification {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    padding: 15px 20px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    min-width: 300px;
                    z-index: 1000;
                    transform: translateX(120%);
                    transition: transform 0.3s ease;
                }
                
                .notification.show {
                    transform: translateX(0);
                }
                
                .notification.success {
                    border-left: 4px solid var(--success-color);
                }
                
                .notification.error {
                    border-left: 4px solid var(--danger-color);
                }
                
                .notification.info {
                    border-left: 4px solid var(--info-color);
                }
                
                .notification-content {
                    display: flex;
                    align-items: center;
                }
                
                .notification-content i {
                    margin-right: 10px;
                    font-size: 1.2rem;
                }
                
                .notification.success i {
                    color: var(--success-color);
                }
                
                .notification.error i {
                    color: var(--danger-color);
                }
                
                .notification.info i {
                    color: var(--info-color);
                }
                
                .notification-close {
                    background: none;
                    border: none;
                    color: var(--text-light);
                    cursor: pointer;
                    margin-left: 15px;
                }
            `;
            document.head.appendChild(style);
        }
        
        // Add to DOM
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Close notification
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', function() {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        });
        
        // Auto close after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }

    // Intersection Observer for Animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationPlayState = 'running';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements with animation classes
    document.querySelectorAll('.animate-fade-in, .animate-fade-in-up, .animate-scale-in').forEach(el => {
        el.style.animationPlayState = 'paused';
        observer.observe(el);
    });

    // Counter Animation
    const counters = document.querySelectorAll('.stat-value');
    const speed = 200;
    
    const countUp = function() {
        counters.forEach(counter => {
            const target = +counter.innerText.replace(/,/g, '');
            const count = +counter.innerText.replace(/,/g, '');
            const inc = target / speed;
            
            if (count < target) {
                counter.innerText = Math.ceil(count + inc).toLocaleString();
                setTimeout(countUp, 10);
            } else {
                counter.innerText = target.toLocaleString();
            }
        });
    };
    
    // Start counter animation when in viewport
    const statsSection = document.querySelector('.stats-container');
    const statsObserver = new IntersectionObserver(function(entries) {
        if (entries[0].isIntersecting) {
            countUp();
            statsObserver.unobserve(statsSection);
        }
    }, { threshold: 0.5 });
    
    if (statsSection) {
        statsObserver.observe(statsSection);
    }
});