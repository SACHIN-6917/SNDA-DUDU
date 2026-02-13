// ======================================
// LANDING PAGE ANIMATIONS - landing.js
// ======================================

document.addEventListener('DOMContentLoaded', () => {
    initAnimations();
    initNavScroll();
});

// ===== 1. ANIMATIONS =====
function initAnimations() {
    // Anime.js - Signal & Noise Animation
    if (typeof anime !== 'undefined') {
        anime.timeline({ loop: true })
            .add({
                targets: '.ml5 .line',
                opacity: [0.5, 1],
                scaleX: [0, 1],
                easing: "easeInOut Quad",
                duration: 700
            })
            .add({
                targets: '.ml5 .line',
                duration: 600,
                easing: "easeOutExpo",
                translateY: (el, i) => (-0.625 + 0.625 * 2 * i) + "em"
            })
            .add({
                targets: '.ml5 .letters',
                opacity: [0, 1],
                easing: "easeOutExpo",
                duration: 600,
                offset: '-=775',
                delay: (el, i) => 34 * (i + 1)
            })
            .add({
                targets: '.ml5',
                opacity: 1,
                duration: 1000,
                easing: "easeOutExpo",
                delay: 1000
            });
    }

    // Intersection Observer for Paragraph Lines
    const observerOptions = {
        threshold: 0.2,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const paragraphLines = document.querySelectorAll('.paragraph-lines .line-wrapper');
    paragraphLines.forEach(line => observer.observe(line));

    // GSAP Animations
    if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);

        // Hero text reveal
        gsap.from('.line-text', {
            y: 100,
            opacity: 0,
            duration: 1.2,
            stagger: 0.2,
            ease: 'power3.out',
            scrollTrigger: {
                trigger: '.hero-headline',
                start: 'top 80%'
            }
        });

        // Hero image card
        gsap.from('.hero-image-card', {
            scale: 0.8,
            opacity: 0,
            duration: 1,
            ease: 'back.out(1.7)',
            scrollTrigger: {
                trigger: '.hero-image-card',
                start: 'top 80%'
            }
        });

        // Enquire button
        gsap.from('.enquire-btn', {
            y: 30,
            opacity: 0,
            duration: 0.8,
            ease: 'power2.out',
            scrollTrigger: {
                trigger: '.enquire-btn',
                start: 'top 90%'
            }
        });

        // Navbar fade in
        gsap.from('.hero-content', {
            y: -50,
            opacity: 0,
            duration: 0.8,
            ease: 'power2.out',
            delay: 0.3
        });
    }
}

// ===== 2. NAV SCROLL & SMOOTH SCROLLING =====
function initNavScroll() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href === '#' || href === '#!') return;

            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Highlight active section in navbar
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-links-floating a');

    function highlightNav() {
        const scrollY = window.pageYOffset;

        sections.forEach(section => {
            const sectionHeight = section.offsetHeight;
            const sectionTop = section.offsetTop - 100;
            const sectionId = section.getAttribute('id');

            if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }

    window.addEventListener('scroll', highlightNav);
}
