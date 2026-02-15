document.addEventListener("DOMContentLoaded", () => {
    // 0. VISIBILITY FALLBACK & SAFETY
    // Ensure body becomes visible even if GSAP fails
    const revealBody = () => {
        document.body.classList.add('page-visible');
        document.body.style.opacity = "1";
    };

    // Check if GSAP is loaded
    if (typeof gsap === 'undefined') {
        console.warn("GSAP not found. Animations disabled.");
        revealBody();
        return;
    }

    // Register GSAP Plugins safely
    if (typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);
    } else {
        console.warn("ScrollTrigger not found.");
        revealBody();
        return;
    }

    // Always reveal body when animations start
    revealBody();

    console.log("Initializing Hero Animations");

    // 1. HERO ANIMATION
    const heroTl = gsap.timeline();

    // Fade in text column
    heroTl.from(".hero-text-col", {
        x: -50,
        opacity: 0,
        duration: 1,
        ease: "power3.out"
    });

    // Staggered Text Reveal
    heroTl.from(".hero-headline .line-text", {
        y: "110%",
        duration: 1.2,
        stagger: 0.2,
        ease: "power4.out"
    }, "-=0.5");

    // Image Card Unveil
    heroTl.from(".hero-image-card", {
        scale: 0.8,
        opacity: 0,
        duration: 1.5,
        ease: "expo.out"
    }, "-=1");

    // Enquire Button Pop
    heroTl.from(".enquire-btn", {
        y: 40,
        opacity: 0,
        duration: 1,
        ease: "back.out(1.7)"
    }, "-=0.8");

    // NEW: Hero Welcome Lines Stagger
    heroTl.to(".hero-welcome-wrap .line-wrapper", {
        onStart: function () {
            gsap.to(".hero-welcome-tag", { opacity: 1, x: 0, duration: 0.8, ease: "power2.out" });
            document.querySelectorAll(".hero-welcome-wrap .line-wrapper").forEach((el, i) => {
                setTimeout(() => el.classList.add('animate'), 200 + (i * 200));
            });
        }
    }, "-=0.5");


    // 2. WELCOME SECTION REVEAL
    gsap.from(".welcome-title", {
        scrollTrigger: {
            trigger: ".welcome-section",
            start: "top 80%",
        },
        y: 50,
        opacity: 0,
        duration: 1.2,
        ease: "power3.out"
    });

    gsap.from(".welcome-lines p", {
        scrollTrigger: {
            trigger: ".welcome-lines",
            start: "top 80%",
        },
        x: -50,
        opacity: 0,
        duration: 0.8,
        stagger: 0.15,
        ease: "power2.out"
    });


    // 2. WELCOME SECTION LINE ANIMATION
    const welcomeLines = document.querySelectorAll('.paragraph-lines .line-wrapper');
    if (welcomeLines.length > 0) {
        welcomeLines.forEach((line) => {
            const text = line.querySelector('.line-text');
            const underline = line.querySelector('.line-underline');

            // Set initial hidden states via GSAP (safer than CSS only)
            gsap.set(text, { opacity: 0, y: 20 });
            gsap.set(underline, { scaleX: 0, transformOrigin: "left" });

            ScrollTrigger.create({
                trigger: line,
                start: "top 95%",
                onEnter: () => {
                    gsap.to(text, { opacity: 1, y: 0, duration: 0.8, ease: "power2.out" });
                    gsap.to(underline, { scaleX: 1, duration: 1, ease: "expo.out", delay: 0.2 });
                },
                once: true
            });
        });
    }

    // 3. SMALA HORIZONTAL PINNING
    const smalaWrapper = document.querySelector('.smala-wrapper');
    const smalaPanes = document.querySelectorAll('.smala-pane');

    if (smalaWrapper && smalaPanes.length > 0) {
        let horizontalScroll = gsap.to(smalaWrapper, {
            x: () => -(smalaWrapper.scrollWidth - window.innerWidth),
            ease: "none",
            scrollTrigger: {
                trigger: ".smala-pinned-section",
                pin: true,
                scrub: 1,
                start: "top top",
                end: () => "+=" + (smalaWrapper.scrollWidth - window.innerWidth),
                invalidateOnRefresh: true,
                onUpdate: (self) => {
                    // Subtle skew effect on fast scroll
                    const velocity = self.getVelocity() / 500;
                    gsap.to(smalaWrapper, {
                        skewX: velocity,
                        overwrite: true,
                        duration: 0.5,
                        ease: "power3.out"
                    });
                }
            }
        });

        // Pane Content Animations
        smalaPanes.forEach((pane) => {
            const title = pane.querySelector('.smala-title');
            const desc = pane.querySelector('.smala-description');

            gsap.from(title, {
                x: 100,
                opacity: 0,
                duration: 1,
                scrollTrigger: {
                    trigger: pane,
                    containerAnimation: horizontalScroll,
                    start: "left 80%",
                    end: "left 20%",
                    scrub: true
                }
            });

            gsap.from(desc, {
                y: 50,
                opacity: 0,
                duration: 1,
                scrollTrigger: {
                    trigger: pane,
                    containerAnimation: horizontalScroll,
                    start: "left 70%",
                    end: "left 30%",
                    scrub: true
                }
            });
        });
    }


    // 4. INDUSTRY PLACES MARQUEE
    // Handled by CSS, but we can add a scroll entry for the title
    gsap.from(".places-title", {
        scrollTrigger: {
            trigger: ".industry-places-section",
            start: "top 85%",
        },
        y: 60,
        opacity: 0,
        duration: 1.2,
        ease: "power3.out"
    });


    // 5. ANTIGRAVITY SECTION WAVE & MOUSE EFFECTS
    const antigravitySection = document.querySelector('.about-antigravity');
    const bubbles = document.querySelectorAll('.icon-bubble');

    if (antigravitySection && bubbles.length > 0) {
        // Initial staggered entrance
        gsap.from(bubbles, {
            scrollTrigger: {
                trigger: ".about-antigravity",
                start: "top 70%",
            },
            scale: 0,
            opacity: 0,
            y: 50,
            duration: 1.2,
            stagger: {
                amount: 0.8,
                from: "random"
            },
            ease: "elastic.out(1, 0.5)"
        });

        // Perpetual floating motion with random offsets
        bubbles.forEach((b, i) => {
            gsap.to(b, {
                y: "random(-15, 15)",
                x: "random(-10, 10)",
                rotation: "random(-5, 5)",
                duration: "random(2, 4)",
                repeat: -1,
                yoyo: true,
                ease: "sine.inOut"
            });
        });

        // Mouse Parallax Effect
        antigravitySection.addEventListener('mousemove', (e) => {
            const { clientX, clientY } = e;
            const centerX = window.innerWidth / 2;
            const centerY = window.innerHeight / 2;

            bubbles.forEach((b, i) => {
                const speed = (i % 3 + 1) * 20; // Different speeds for depth
                const x = (clientX - centerX) / speed;
                const y = (clientY - centerY) / speed;

                gsap.to(b, {
                    x: x,
                    y: y,
                    duration: 1,
                    ease: "power2.out",
                    overwrite: "auto"
                });
            });
        });

        // Reset positions when mouse leaves
        antigravitySection.addEventListener('mouseleave', () => {
            bubbles.forEach((b) => {
                gsap.to(b, {
                    x: 0,
                    y: 0,
                    duration: 1.5,
                    ease: "power2.inOut"
                });
            });
        });
    }

    // 5. ANTIGRAVITY SECTION TYPING REVEAL
    const typingLines = document.querySelectorAll('.typing-text span');
    if (typingLines.length > 0) {
        // Set initial invisible state
        gsap.set(typingLines, { y: 30, opacity: 0 });

        gsap.to(typingLines, {
            scrollTrigger: {
                trigger: ".typing-text",
                start: "top 80%",
            },
            y: 0,
            opacity: 1,
            duration: 1.2,
            stagger: 0.3,
            ease: "power3.out"
        });
    }


    // 6. ENQUIRY FORM REVEAL
    gsap.from(".form-container", {
        scrollTrigger: {
            trigger: ".dynamic-form-section",
            start: "top 75%",
        },
        y: 100,
        opacity: 0,
        duration: 1.5,
        ease: "power4.out"
    });

    // 7. WELCOME TITLE SIGNAL & NOISE
    const ml5 = document.querySelector('.ml5');
    if (typeof anime !== 'undefined' && ml5) {
        // Reveal immediately if hidden
        gsap.set('.ml5 .letters', { opacity: 1 });

        anime.timeline({ loop: true })
            .add({
                targets: '.ml5 .line',
                opacity: [0.5, 1],
                scaleX: [0, 1],
                easing: "easeInOutExpo",
                duration: 700
            }).add({
                targets: '.ml5 .line',
                duration: 600,
                easing: "easeOutExpo",
                translateY: (el, i) => (-0.625 + 0.625 * 2 * i) + "em"
            }).add({
                targets: '.ml5 .letters',
                opacity: [0, 1],
                scaleY: [0.5, 1],
                easing: "easeOutExpo",
                duration: 600,
                offset: '-=600'
            }).add({
                targets: '.ml5',
                opacity: 0,
                duration: 800,
                easing: "easeOutExpo",
                delay: 2000
            });
    }
});
