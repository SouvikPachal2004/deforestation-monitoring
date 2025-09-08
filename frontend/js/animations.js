document.addEventListener('DOMContentLoaded', function() {
    // Add animation classes to elements when they come into view
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.animate-on-scroll');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.2;
            
            if (elementPosition < screenPosition) {
                element.classList.add('animated');
            }
        });
    };
    
    // Add animate-on-scroll class to elements that should animate when scrolled into view
    const addAnimationClasses = function() {
        // Sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.add('animate-on-scroll');
        });
        
        // Cards
        document.querySelectorAll('.card').forEach(card => {
            card.classList.add('animate-on-scroll');
        });
        
        // Stat cards
        document.querySelectorAll('.stat-card').forEach(card => {
            card.classList.add('animate-on-scroll');
        });
        
        // Feature items
        document.querySelectorAll('.feature-item').forEach(item => {
            item.classList.add('animate-on-scroll');
        });
        
        // Team members
        document.querySelectorAll('.team-member').forEach(member => {
            member.classList.add('animate-on-scroll');
        });
    };
    
    // Initialize animation classes
    addAnimationClasses();
    
    // Run animation check on scroll
    window.addEventListener('scroll', animateOnScroll);
    
    // Initial check
    animateOnScroll();
    
    // Parallax effect for hero section
    const parallaxElements = document.querySelectorAll('.parallax');
    
    window.addEventListener('scroll', function() {
        const scrollPosition = window.pageYOffset;
        
        parallaxElements.forEach(element => {
            const speed = element.dataset.speed || 0.5;
            element.style.transform = `translateY(${scrollPosition * speed}px)`;
        });
    });
    
    // Add parallax class to hero image
    const heroImage = document.querySelector('.hero-image');
    if (heroImage) {
        heroImage.classList.add('parallax');
        heroImage.dataset.speed = '0.3';
    }
    
    // Counter animation for statistics
    const animateCounters = function() {
        const counters = document.querySelectorAll('.counter');
        
        counters.forEach(counter => {
            const target = +counter.getAttribute('data-target');
            const count = +counter.innerText.replace(/,/g, '');
            const increment = target / 200;
            
            if (count < target) {
                counter.innerText = Math.ceil(count + increment).toLocaleString();
                setTimeout(() => animateCounters(), 10);
            } else {
                counter.innerText = target.toLocaleString();
            }
        });
    };
    
    // Add counter class to stat values
    document.querySelectorAll('.stat-value').forEach(value => {
        value.classList.add('counter');
        const currentValue = value.innerText;
        value.setAttribute('data-target', currentValue.replace(/,/g, ''));
    });
    
    // Trigger counter animation when stats section is in view
    const statsSection = document.querySelector('.stats-container');
    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounters();
                statsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    if (statsSection) {
        statsObserver.observe(statsSection);
    }
    
    // Typing animation for hero title
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        const text = heroTitle.innerText;
        heroTitle.innerText = '';
        
        let i = 0;
        const typeWriter = function() {
            if (i < text.length) {
                heroTitle.innerText += text.charAt(i);
                i++;
                setTimeout(typeWriter, 50);
            }
        };
        
        // Start typing animation after page load
        setTimeout(typeWriter, 1000);
    }
    
    // Progress bar animation
    const animateProgressBars = function() {
        const progressBars = document.querySelectorAll('.progress-fill');
        
        progressBars.forEach(bar => {
            const width = bar.getAttribute('data-width');
            bar.style.width = width;
        });
    };
    
    // Add progress bar animation when skills section is in view
    const skillsSection = document.querySelector('.skills-section');
    const skillsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateProgressBars();
                skillsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    if (skillsSection) {
        skillsObserver.observe(skillsSection);
    }
    
    // Add hover animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        });
    });
    
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
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
    
    // Add ripple styles
    const style = document.createElement('style');
    style.textContent = `
        .btn {
            position: relative;
            overflow: hidden;
        }
        
        .ripple {
            position: absolute;
            border-radius: 50%;
            background-color: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: ripple-animation 0.6s ease-out;
        }
        
        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        
        .animate-on-scroll {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .animate-on-scroll.animated {
            opacity: 1;
            transform: translateY(0);
        }
        
        .parallax {
            will-change: transform;
            transition: transform 0.1s ease-out;
        }
    `;
    
    if (!document.querySelector('#animation-styles')) {
        style.id = 'animation-styles';
        document.head.appendChild(style);
    }
    
    // Add stagger animation to elements
    const addStaggerAnimation = function(parentSelector, childSelector, stagger = 100) {
        const parents = document.querySelectorAll(parentSelector);
        
        parents.forEach(parent => {
            const children = parent.querySelectorAll(childSelector);
            
            children.forEach((child, index) => {
                child.style.animationDelay = `${index * stagger}ms`;
            });
        });
    };
    
    // Apply stagger animations
    addStaggerAnimation('.stats-container', '.stat-card', 100);
    addStaggerAnimation('.features-list', '.feature-item', 100);
    addStaggerAnimation('.team-grid', '.team-member', 100);
    
    // Add floating animation to elements
    const floatingElements = document.querySelectorAll('.floating');
    floatingElements.forEach(element => {
        element.style.animation = `floating ${element.dataset.duration || '3s'} ease-in-out infinite`;
        element.style.animationDelay = element.dataset.delay || '0s';
    });
    
    // Add pulse animation to elements
    const pulseElements = document.querySelectorAll('.pulse');
    pulseElements.forEach(element => {
        element.style.animation = `pulse ${element.dataset.duration || '2s'} ease-in-out infinite`;
        element.style.animationDelay = element.dataset.delay || '0s';
    });
    
    // Add rotate animation to elements
    const rotateElements = document.querySelectorAll('.rotate');
    rotateElements.forEach(element => {
        element.style.animation = `rotate ${element.dataset.duration || '20s'} linear infinite`;
    });
});