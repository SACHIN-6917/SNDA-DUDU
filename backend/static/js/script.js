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
        nlForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const emailInput = document.getElementById('nlEmail');
            const email = (emailInput.value || '').trim();
            const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

            if (!isValid) {
                showToast('Please enter a valid email address.', 'error');
                return;
            }

            showToast('Thank you for subscribing!', 'success');
            nlForm.reset();
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
                    addMsg("Hi! I'm Panda Bot 🐼. Which area (city) are you interested in for an industrial visit?", 'bot');
                    addMsg("We have premium industrials for: Chennai, Coimbatore, Madurai, Bengaluru, Pondicherry, Ooty, Kodaikanal, and more!", 'bot');
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
        loadingMsg.innerText = 'Panda is thinking...';
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
            const response = await fetch('/api/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ message: q })
            });

            const data = await response.json();

            // Remove loading
            if (pandaBody.contains(loadingMsg)) {
                pandaBody.removeChild(loadingMsg);
            }

            // Add Bot Response
            const botMsg = document.createElement('div');
            botMsg.className = 'chat-message bot';
            botMsg.innerText = data.response || data.message || "I'm having trouble connecting right now.";
            if (!data.response && data.message) console.error("Chatbot Error:", data.message);
            pandaBody.appendChild(botMsg);
            pandaBody.scrollTop = pandaBody.scrollHeight;

        } catch (error) {
            if (pandaBody.contains(loadingMsg)) {
                pandaBody.removeChild(loadingMsg);
            }
            const errorMsg = document.createElement('div');
            errorMsg.className = 'chat-message bot';
            errorMsg.innerText = "Error encountered. Please try again.";
            pandaBody.appendChild(errorMsg);
            pandaBody.scrollTop = pandaBody.scrollHeight;
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
function initCookieConsent() {
    const banner = document.getElementById('cookieConsent');
    const acceptBtn = document.getElementById('acceptCookies');
    const rejectBtn = document.getElementById('rejectCookies');

    if (!banner || !acceptBtn || !rejectBtn) return;

    // Check if user has already made a choice
    const consent = localStorage.getItem('cookieConsent');
    if (!consent) {
        // Show banner after a slight delay
        setTimeout(() => {
            banner.style.display = 'block';
        }, 1000);
    }

    acceptBtn.addEventListener('click', () => {
        localStorage.setItem('cookieConsent', 'accepted');
        banner.style.display = 'none';
        showToast('Cookies accepted. Enjoy your experience!', 'success');
    });

    rejectBtn.addEventListener('click', () => {
        localStorage.setItem('cookieConsent', 'rejected');
        banner.style.display = 'none';
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

// ===== 8. INIT ON DOM READY =====
document.addEventListener('DOMContentLoaded', () => {
    initAuth();
    initFooter();
    initPandaBot();
    initCookieConsent();
    initRevealAnimations();
});
