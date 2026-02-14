// ======================================
// GLOBAL JAVASCRIPT - script.js
// Auth, Footer, Panda Bot
// ======================================

// ===== 1. AUTH HELPERS =====
function getAuthUser() {
    try {
        return JSON.parse(localStorage.getItem('authUser'));
    } catch {
        return null;
    }
}

function setAuthUser(user) {
    localStorage.setItem('authUser', JSON.stringify(user));
}

function clearAuth() {
    localStorage.removeItem('authUser');
}

// ===== 2. INIT AUTH (Navbar) =====
function initAuth() {
    const logoutLink = document.getElementById('logoutLink');
    const acc = document.querySelector('details.account-dropdown');

    if (logoutLink) {
        logoutLink.addEventListener('click', (e) => {
            // Let the link navigate to the logout URL naturally, 
            // but we might want to clear localStorage first.
            // However, usually we can just let the backend handle everything.
            clearAuth();
            // No need to preventDefault or manual redirect if the link is correct
        });
    }

    if (acc) {
        const summaryBtn = acc.querySelector('.account-summary');
        acc.addEventListener('toggle', () => {
            if (summaryBtn) summaryBtn.setAttribute('aria-expanded', acc.open ? 'true' : 'false');
        });
    }

    // Passkey Button Mock
    const passkeyBtn = document.getElementById('passkeyBtn');
    if (passkeyBtn) {
        passkeyBtn.addEventListener('click', () => {
            showToast('Initializing Passkey authentication...', 'info');
            setTimeout(() => {
                showToast('Passkey feature coming soon! Please use email login for now.', 'warning');
            }, 1000);
        });
    }
}

// ===== 3. FOOTER FUNCTIONALITY =====
function initFooter() {
    // Set current year
    const yearSpan = document.getElementById('footerYear');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }

    // Newsletter subscription
    const nlForm = document.getElementById('footerNewsletter');
    if (nlForm) {
        nlForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const emailInput = document.getElementById('nlEmail');
            const submitBtn = nlForm.querySelector('button');
            const email = (emailInput.value || '').trim();
            const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

            if (!isValid) {
                showToast('Please enter a valid email address.', 'error');
                return;
            }

            // Disable button
            const originalText = submitBtn.textContent;
            submitBtn.textContent = '...';
            submitBtn.disabled = true;

            try {
                // Get CSRF
                const getCookie = (name) => {
                    let cookieValue = null;
                    if (document.cookie && document.cookie !== '') {
                        const cookies = document.cookie.split(';');
                        for (let i = 0; i < cookies.length; i++) {
                            const cookie = cookies[i].trim();
                            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                break;
                            }
                        }
                    }
                    return cookieValue;
                };
                const csrftoken = getCookie('csrftoken');

                const response = await fetch('/api/newsletters/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify({ email: email })
                });

                if (response.ok) {
                    showToast('Thank you for subscribing! Check your email. 📧', 'success');
                    nlForm.reset();
                } else {
                    const data = await response.json();
                    if (data.email && Array.isArray(data.email) && data.email[0].includes('unique')) {
                        showToast('You are already subscribed! 🎉', 'info');
                    } else {
                        showToast('Subscription failed. Please try again.', 'error');
                    }
                }
            } catch (error) {
                console.error('Subscription error:', error);
                showToast('Network error. Please try again.', 'error');
            } finally {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        });
    }
}

// ===== 4. TOAST NOTIFICATION =====
function showToast(message, type = 'success') {
    // Remove existing toast if any
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    // Show
    setTimeout(() => toast.classList.add('show'), 100);

    // Hide after 3s
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}

// ===== 5. PANDA BOT CHATBOT =====
function initPandaBot() {
    const pandaFab = document.getElementById('pandaFab');
    const pandaChat = document.getElementById('pandaChat');
    const pandaClose = document.getElementById('pandaClose');
    const pandaBody = document.getElementById('pandaBody');
    const pandaInput = document.getElementById('pandaInput');
    const pandaSend = document.getElementById('pandaSend');

    if (!pandaFab || !pandaChat) return;

    function toggleChat(show) {
        if (show) {
            pandaChat.style.display = 'flex';
            pandaChat.setAttribute('aria-hidden', 'false');
            if (pandaBody) {
                // If it's the first open, add greeting
                if (pandaBody.children.length <= 1) {
                    pandaBody.innerHTML = ''; // Clear default
                    addMsg("Hi! I'm Panda Bot 🐼😊", 'bot');
                    addMsg("I'm super excited to help you plan your industrial visit! 🎉", 'bot');
                    addMsg("Which city are you interested in today? 🏙✨", 'bot');
                }
                pandaBody.scrollTop = pandaBody.scrollHeight;
            }
        } else {
            pandaChat.style.display = 'none';
            pandaChat.setAttribute('aria-hidden', 'true');
        }
    }

    // Link Hero ENQUIRE button to open Panda Bot
    const heroEnquireBtn = document.querySelector('.hero-enquire-btn');
    if (heroEnquireBtn) {
        heroEnquireBtn.addEventListener('click', (e) => {
            e.preventDefault();
            toggleChat(true);
        });
    }

    pandaFab.addEventListener('click', () => toggleChat(true));
    if (pandaClose) pandaClose.addEventListener('click', () => toggleChat(false));

    function addMsg(text, who) {
        const msg = document.createElement('div');
        msg.className = 'chat-message ' + (who || 'bot');
        msg.textContent = text;
        pandaBody.appendChild(msg);
        pandaBody.scrollTop = pandaBody.scrollHeight;
    }

    async function sendMessage() {
        const q = (pandaInput.value || '').trim();
        if (!q) return;

        // Disable UI during request
        pandaInput.disabled = true;
        pandaSend.disabled = true;

        // Add User Message
        const userMsg = document.createElement('div');
        userMsg.className = 'chat-message user';
        userMsg.innerText = q;
        pandaBody.appendChild(userMsg);
        pandaBody.scrollTop = pandaBody.scrollHeight;

        pandaInput.value = '';

        // Add Loading Indicator
        const loadingMsg = document.createElement('div');
        loadingMsg.className = 'chat-message bot thinking';
        loadingMsg.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
        pandaBody.appendChild(loadingMsg);
        pandaBody.scrollTop = pandaBody.scrollHeight;

        // Helper to get CSRF token
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        try {
            const csrftoken = getCookie('csrftoken');
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 15000); // 15s timeout

            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ message: q }),
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();

            // Remove loading
            if (pandaBody.contains(loadingMsg)) {
                pandaBody.removeChild(loadingMsg);
            }

            // Add Bot Response
            const botMsg = document.createElement('div');
            botMsg.className = 'chat-message bot';
            botMsg.innerText = data.response || "I'm having a bit of trouble finding that answer right now. 🐼";
            pandaBody.appendChild(botMsg);
            pandaBody.scrollTop = pandaBody.scrollHeight;

        } catch (error) {
            console.error("Chatbot Error:", error);
            if (pandaBody.contains(loadingMsg)) {
                pandaBody.removeChild(loadingMsg);
            }
            const errorMsg = document.createElement('div');
            errorMsg.className = 'chat-message bot';
            errorMsg.innerText = error.name === 'AbortError'
                ? "Panda is taking too long to think. Please try again! 🐼⏳"
                : "⚠️ Something went wrong. Please check your connection and try again.";
            pandaBody.appendChild(errorMsg);
            pandaBody.scrollTop = pandaBody.scrollHeight;
        } finally {
            // Re-enable UI
            pandaInput.disabled = false;
            pandaSend.disabled = false;
            pandaInput.focus();
        }
    }

    if (pandaSend) {
        pandaSend.addEventListener('click', sendMessage);
    }

    if (pandaInput) {
        pandaInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });
    }
}

// ===== 6. COOKIE CONSENT =====
// Standalone function for emergency visibility
function forceShowCookies() {
    console.log('Cookie Consent: EMERGENCY SHOW TRIGGERED');
    const banner = document.getElementById('cookieConsent');
    if (banner) {
        banner.classList.add('visible');
        banner.style.display = 'block'; // Direct override if CSS fails
        console.log('Cookie Consent: Banner should now be visible');
    } else {
        console.error('Cookie Consent: Banner element NOT FOUND in DOM!');
    }
}

function initCookieConsent() {
    console.log('Cookie Consent: Initializing (Foolproof Mode)...');
    const banner = document.getElementById('cookieConsent');
    const acceptBtn = document.getElementById('acceptCookies');
    const rejectBtn = document.getElementById('rejectCookies');

    if (!banner) {
        console.error('Cookie Consent: Banner element not found!');
        return;
    }
    if (!acceptBtn || !rejectBtn) {
        console.error('Cookie Consent: Buttons not found!');
        return;
    }

    // Check if user has already made a choice (v1)
    const consent = localStorage.getItem('cookieConsent_v1');
    console.log('Cookie Consent: Current status:', consent);

    if (!consent) {
        // Show banner after a slight delay
        setTimeout(() => {
            console.log('Cookie Consent: Showing banner now');
            banner.classList.add('visible');
            // Additional safety: ensure it's not hidden by any parent
            banner.parentElement.style.overflow = 'visible';
        }, 1000);
    } else {
        console.log('Cookie Consent: Already dismissed');
    }

    acceptBtn.addEventListener('click', () => {
        console.log('Cookie Consent: Choice -> Accepted');
        localStorage.setItem('cookieConsent_v1', 'accepted');
        banner.classList.remove('visible');
        showToast('Cookies accepted. Enjoy your experience!', 'success');
    });

    rejectBtn.addEventListener('click', () => {
        console.log('Cookie Consent: Choice -> Rejected');
        localStorage.setItem('cookieConsent_v1', 'rejected');
        banner.classList.remove('visible');
        showToast('Cookies rejected. Some features may be limited.', 'info');
    });
}

// ===== 7. GLOBAL REVEAL ANIMATIONS (Intersection Observer) =====
function initRevealAnimations() {
    const reveals = document.querySelectorAll('.reveal, .reveal-left, .reveal-right');

    if (reveals.length === 0) return;

    const observerOptions = {
        threshold: 0.15,
        rootMargin: "0px 0px -50px 0px"
    };

    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                // Optional: unobserve after revealing
                // observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    reveals.forEach(el => revealObserver.observe(el));
}

// ===== 8. THEME TOGGLE (Light/Dark Mode) =====
function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;

    if (!themeToggle) return;

    // Load saved theme or use system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
    html.setAttribute('data-theme', initialTheme);
    updateToggleIcon(initialTheme);

    themeToggle.addEventListener('click', () => {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateToggleIcon(newTheme);
    });

    function updateToggleIcon(theme) {
        const icon = themeToggle.querySelector('i');
        if (icon) {
            icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        }
    }
}

// ===== 9. PROFILE DROPDOWN =====
function initProfileDropdown() {
    const trigger = document.getElementById('profileTrigger');
    const menu = document.getElementById('profileMenu');

    if (!trigger || !menu) return;

    trigger.addEventListener('click', (e) => {
        e.stopPropagation();
        menu.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
        if (!menu.contains(e.target) && !trigger.contains(e.target)) {
            menu.classList.remove('show');
        }
    });
}

// ===== 10. INIT ON DOM READY =====
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Ready: Initializing components...');

    // 1. Critical: Cookie Consent (Prioritize)
    try {
        initCookieConsent();
    } catch (e) {
        console.error('Error in initCookieConsent:', e);
    }

    // 2. Theme & UI
    try {
        initTheme();
        initProfileDropdown();
    } catch (e) {
        console.error('Error in UI inits:', e);
    }

    // 3. Auth
    try {
        initAuth();
    } catch (e) {
        console.error('Error in initAuth:', e);
    }

    // 4. Footer
    try {
        initFooter();
    } catch (e) {
        console.error('Error in initFooter:', e);
    }

    // 5. Chatbot
    try {
        initPandaBot();
    } catch (e) {
        console.error('Error in initPandaBot:', e);
    }

    // 6. Animations & Others
    try {
        initRevealAnimations();
        initCounters();
        initTypingAnimation();
    } catch (e) {
        console.error('Error in secondary inits:', e);
    }
});

// ===== 8. TYPING ANIMATION =====
function initTypingAnimation() {
    const target = document.getElementById('typing-target');
    if (!target) return;

    const lyrics = [
        "Dudu",
        "is bridge for",
        "connect your industrial visit",
        "smoothly ✅"
    ];

    let lyricIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    const typeSpeed = 100;
    const nextLyricDelay = 2000;

    function type() {
        const fullText = lyrics.join('\n');
        // We actually want them to appear line by line or all at once?
        // Let's do a simple continuous typing for the full block
        const currentFullText = lyrics.slice(0, lyricIndex + 1).join('\n');
        const currentVisibleText = lyrics.slice(0, lyricIndex).join('\n') + (lyricIndex > 0 ? '\n' : '') + lyrics[lyricIndex].substring(0, charIndex);

        target.innerText = currentVisibleText;

        if (charIndex < lyrics[lyricIndex].length) {
            charIndex++;
            setTimeout(type, typeSpeed);
        } else if (lyricIndex < lyrics.length - 1) {
            lyricIndex++;
            charIndex = 0;
            setTimeout(type, 500); // Pause between lines
        }
    }

    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
            type();
            observer.unobserve(target);
        }
    }, { threshold: 0.5 });

    observer.observe(target);
}

// ===== 9. COUNTER ANIMATION =====
function initCounters() {
    const counters = document.querySelectorAll('.stat-number');
    const speed = 800; // Increased from 200 to slow it down

    const animateCounter = (el) => {
        const target = +el.getAttribute('data-target');
        const count = +el.innerText;
        const inc = target / speed;

        if (count < target) {
            el.innerText = Math.ceil(count + inc);
            setTimeout(() => animateCounter(el), 1); // Maintain smooth 60fps feel but slower progress
        } else {
            el.innerText = target;
        }
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => observer.observe(counter));
}
