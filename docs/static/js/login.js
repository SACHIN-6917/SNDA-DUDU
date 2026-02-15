// ======================================
// LOGIN PAGE - login.js
// ======================================

document.addEventListener('DOMContentLoaded', () => {
    initSocialLogin();
    initFormToggle();
    initPasswordToggle();
    initPandaCharacter();
});

// ===== 1. SOCIAL LOGIN SETUP =====
function initSocialLogin() {
    // Google Login (placeholder - requires actual Google Client ID)
    const googleBtn = document.getElementById('googleLogin');
    if (googleBtn) {
        googleBtn.addEventListener('click', () => {
            alert('Google login integration requires Google Client ID configuration.');
            // In production: use Google Identity Services
            // window.google.accounts.id.prompt();
        });
    }

    // Facebook Login (placeholder - requires actual Facebook App ID)
    const facebookBtn = document.getElementById('facebookLogin');
    if (facebookBtn) {
        facebookBtn.addEventListener('click', () => {
            alert('Facebook login integration requires Facebook App ID configuration.');
            // In production: use Facebook SDK
            // FB.login(response => { ... });
        });
    }
}

// ===== 2. FORM TOGGLE (Login / Signup / Forgot Password) =====
function initFormToggle() {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    const forgotForm = document.getElementById('forgotForm');

    const showSignupLink = document.getElementById('showSignup');
    const showLoginLink = document.getElementById('showLogin');
    const showForgotLink = document.getElementById('showForgot');
    const backToLoginLink = document.getElementById('backToLogin');

    function showForm(formToShow) {
        [loginForm, signupForm, forgotForm].forEach(form => {
            if (form) form.style.display = 'none';
        });
        if (formToShow) formToShow.style.display = 'block';
    }

    if (showSignupLink) {
        showSignupLink.addEventListener('click', (e) => {
            e.preventDefault();
            showForm(signupForm);
        });
    }

    if (showLoginLink) {
        showLoginLink.addEventListener('click', (e) => {
            e.preventDefault();
            showForm(loginForm);
        });
    }

    if (showForgotLink) {
        showForgotLink.addEventListener('click', (e) => {
            e.preventDefault();
            showForm(forgotForm);
        });
    }

    if (backToLoginLink) {
        backToLoginLink.addEventListener('click', (e) => {
            e.preventDefault();
            showForm(loginForm);
        });
    }
}

// ===== 3. PASSWORD VISIBILITY TOGGLE =====
function initPasswordToggle() {
    document.querySelectorAll('.password-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.closest('.password-wrapper').querySelector('input');
            const iconShow = btn.querySelector('.icon-show');
            const iconHide = btn.querySelector('.icon-hide');

            if (input.type === 'password') {
                input.type = 'text';
                if (iconShow) iconShow.style.display = 'none';
                if (iconHide) iconHide.style.display = 'block';
            } else {
                input.type = 'password';
                if (iconShow) iconShow.style.display = 'block';
                if (iconHide) iconHide.style.display = 'none';
            }
        });
    });
}

// ===== 4. PANDA CHARACTER ANIMATIONS =====
function initPandaCharacter() {
    const usernameInput = document.getElementById('loginEmail');
    const passwordInput = document.getElementById('loginPassword');
    const pandaContainer = document.querySelector('.panda-container');
    const leftArm = pandaContainer?.querySelector('.arm.left');
    const rightArm = pandaContainer?.querySelector('.arm.right');

    if (!pandaContainer) return;

    // Cover eyes when typing password
    if (passwordInput) {
        passwordInput.addEventListener('focus', () => {
            leftArm?.classList.add('cover');
            rightArm?.classList.add('cover');
        });

        passwordInput.addEventListener('blur', () => {
            leftArm?.classList.remove('cover');
            rightArm?.classList.remove('cover');
        });
    }

    // Eyes follow cursor (simple version)
    if (usernameInput) {
        usernameInput.addEventListener('focus', () => {
            const eyes = pandaContainer.querySelectorAll('.eye');
            eyes.forEach(eye => {
                eye.style.transform = 'translateX(2px)';
            });
        });

        usernameInput.addEventListener('blur', () => {
            const eyes = pandaContainer.querySelectorAll('.eye');
            eyes.forEach(eye => {
                eye.style.transform = 'translateX(0)';
            });
        });
    }
}

// ===== 5. FORM SUBMISSIONS =====
// Login Form
const loginFormEl = document.getElementById('loginForm');
// We let the form submit naturally to the backend view
// If you want AJAX, implement fetch() here.
// For now, we rely on the <form action="{% url 'login' %}">

// Signup Form
const signupFormEl = document.getElementById('signupForm');
// Similarly, let it submit naturally.

// Forgot Password Form
const forgotFormEl = document.getElementById('forgotForm');
if (forgotFormEl) {
    forgotFormEl.addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('forgotEmail')?.value.trim();

        if (!email) {
            alert('Please enter your email address.');
            return;
        }

        showSuccessToast('Password reset link sent to ' + email);

        setTimeout(() => {
            // Go back to login form
            document.getElementById('backToLogin')?.click();
        }, 2000);
    });
}

// ===== HELPER: SUCCESS TOAST =====
function showSuccessToast(message) {
    let toast = document.querySelector('.login-success-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.className = 'login-success-toast';
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}
