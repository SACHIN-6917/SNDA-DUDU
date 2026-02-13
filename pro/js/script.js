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
    const summaryBtn = document.querySelector('.account-summary');
    const logoutLink = document.getElementById('logoutLink');
    const loginMenuItem = document.getElementById('loginMenuItem');
    const acc = document.querySelector('details.account-dropdown');

    if (!summaryBtn) return;

    const authUser = getAuthUser();

    if (authUser && authUser.email) {
        summaryBtn.textContent = 'Account';
        if (loginMenuItem) loginMenuItem.style.display = 'none';
        if (logoutLink) logoutLink.style.display = 'block';
    } else {
        summaryBtn.textContent = 'Login';
        if (logoutLink) logoutLink.style.display = 'none';
        if (loginMenuItem) loginMenuItem.style.display = 'block';

        summaryBtn.addEventListener('click', (e) => {
            if (summaryBtn.textContent === 'Login') {
                e.preventDefault();
                if (!window.location.pathname.includes('login.html')) {
                    const returnTo = encodeURIComponent(window.location.href);
                    window.location.href = `login.html?returnTo=${returnTo}`;
                }
            }
        });
    }

    if (logoutLink) {
        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            clearAuth();
            showToast('Logged out successfully!', 'success');
            setTimeout(() => {
                if (window.location.pathname.includes('account.html')) {
                    window.location.href = 'index.html';
                } else {
                    window.location.reload();
                }
            }, 800);
        });
    }

    if (acc) {
        acc.addEventListener('toggle', () => {
            summaryBtn.setAttribute('aria-expanded', acc.open ? 'true' : 'false');
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
            if (pandaBody) pandaBody.scrollTop = pandaBody.scrollHeight;
        } else {
            pandaChat.style.display = 'none';
            pandaChat.setAttribute('aria-hidden', 'true');
        }
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

    function reply(q) {
        const t = (q || '').toLowerCase();
        if (t.includes('package') || t.includes('price')) return 'Visit our Packages page to see all available industrial visit packages!';
        if (t.includes('book') || t.includes('payment')) return 'Select a package and proceed to payment to book your visit.';
        if (t.includes('login') || t.includes('account')) return 'Click on the Login/Account button in the navbar to access your profile.';
        if (t.includes('feedback')) return 'We love feedback! Visit our Feedback page to share your experience.';
        if (t.includes('help') || t.includes('support')) return 'Need help? Use the Enquire form on our homepage or contact us directly!';
        return 'I\'m here to help! Ask me about packages, bookings, login, or feedback.';
    }

    function sendMessage() {
        const q = (pandaInput.value || '').trim();
        if (!q) return;
        addMsg(q, 'user');
        pandaInput.value = '';
        setTimeout(() => addMsg(reply(q), 'bot'), 500);
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

// ===== 6. INIT ON DOM READY =====
document.addEventListener('DOMContentLoaded', () => {
    initAuth();
    initFooter();
    initPandaBot();
});
