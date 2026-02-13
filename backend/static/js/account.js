// ======================================
// ACCOUNT PAGE - account.js
// ======================================

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadProfile();
    initEditMode();
    initAvatarUpload();
});

// ===== 1. CHECK AUTHENTICATION =====
function checkAuth() {
    // We'll trust the Django session for the backend.
    // However, the page uses these as toggles.
    // If we're on the account page, and the backend rendered it, we should be shown.
    const accountContainer = document.querySelector('.account-container');
    const loginRequired = document.querySelector('.login-required');

    if (accountContainer && accountContainer.style.display === 'block') return true;

    const authUser = JSON.parse(localStorage.getItem('authUser') || 'null');
    if (!authUser || !authUser.email) {
        // If localStorage is empty, check if Django session managed to show the container
        // If not, we still show login required
        if (accountContainer && accountContainer.style.display !== 'block') {
            if (accountContainer) accountContainer.style.display = 'none';
            if (loginRequired) loginRequired.style.display = 'block';
        }
        return false;
    }

    if (accountContainer) accountContainer.style.display = 'block';
    if (loginRequired) loginRequired.style.display = 'none';
    return true;
}

// ===== 2. LOAD PROFILE DATA =====
function loadProfile() {
    if (!checkAuth()) return;

    const authUser = JSON.parse(localStorage.getItem('authUser'));
    const userProfile = JSON.parse(localStorage.getItem('userProfile') || 'null');

    // Set header info
    const profileName = document.getElementById('profileName');
    const profileEmail = document.getElementById('profileEmail');
    if (profileName) profileName.textContent = userProfile?.name || authUser.name || 'User';
    if (profileEmail) profileEmail.textContent = authUser.email;

    // Set avatar
    const profileAvatar = document.getElementById('profileAvatar');
    if (profileAvatar && userProfile?.avatar) {
        profileAvatar.src = userProfile.avatar;
    }

    // Populate form fields
    if (userProfile) {
        const fields = {
            'userName': userProfile.name,
            'userEmail': authUser.email,
            'userPhone': userProfile.phone,
            'userDob': userProfile.dob,
            'userAddress': userProfile.address,
            'userCity': userProfile.city,
            'userState': userProfile.state,
            'userZip': userProfile.zip
        };

        Object.keys(fields).forEach(id => {
            const field = document.getElementById(id);
            if (field && fields[id]) field.value = fields[id];
        });
    } else {
        // Set email from auth
        const emailField = document.getElementById('userEmail');
        if (emailField) emailField.value = authUser.email;
    }
}

// ===== 3. EDIT MODE =====
function initEditMode() {
    const editBtn = document.getElementById('editBtn');
    const saveBtn = document.getElementById('saveBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const formInputs = document.querySelectorAll('.profile-body input, .profile-body textarea');

    // Disable email field always
    const emailField = document.getElementById('userEmail');
    if (emailField) emailField.disabled = true;

    let isEditMode = false;

    function setEditMode(enabled) {
        isEditMode = enabled;
        formInputs.forEach(input => {
            if (input.id !== 'userEmail') {
                input.disabled = !enabled;
            }
        });

        if (editBtn) editBtn.style.display = enabled ? 'none' : 'flex';
        if (saveBtn) saveBtn.style.display = enabled ? 'flex' : 'none';
        if (cancelBtn) cancelBtn.style.display = enabled ? 'flex' : 'none';
    }

    if (editBtn) {
        editBtn.addEventListener('click', () => setEditMode(true));
    }

    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            setEditMode(false);
            loadProfile(); // Reload original data
        });
    }

    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            saveProfile();
            setEditMode(false);
        });
    }

    // Initial state: view mode
    setEditMode(false);
}

// ===== 4. SAVE PROFILE =====
async function saveProfile() {
    const profileData = {
        name: document.getElementById('userName')?.value.trim() || '',
        phone: document.getElementById('userPhone')?.value.trim() || '',
        dob: document.getElementById('userDob')?.value || '',
        address: document.getElementById('userAddress')?.value.trim() || '',
        city: document.getElementById('userCity')?.value.trim() || '',
        state: document.getElementById('userState')?.value.trim() || '',
        zip: document.getElementById('userZip')?.value.trim() || '',
        // Avatar skipped for now to avoid payload size issues
    };

    // Validation
    if (!profileData.name) {
        alert('Name is required.');
        return;
    }

    try {
        const response = await fetch('/account/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Function needs to be defined or use value from DOM if available
            },
            body: JSON.stringify(profileData)
        });

        const result = await response.json();

        if (response.ok && result.status === 'success') {
            // Update authUser name in local storage just for sync
            const authUser = JSON.parse(localStorage.getItem('authUser') || '{}');
            authUser.name = profileData.name;
            localStorage.setItem('authUser', JSON.stringify(authUser));

            // Update profile header
            const profileName = document.getElementById('profileName');
            if (profileName) profileName.textContent = profileData.name;

            if (typeof showToast === 'function') {
                showToast('Profile updated successfully!', 'success');
            } else {
                alert('Profile updated successfully!');
            }
        } else {
            alert(result.message || 'Update failed.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
}

// Helper for CSRF
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

// ===== 5. AVATAR UPLOAD =====
function initAvatarUpload() {
    const avatarInput = document.getElementById('avatarInput');
    const profileAvatar = document.getElementById('profileAvatar');

    if (avatarInput) {
        avatarInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;

            // Validate file type
            if (!file.type.startsWith('image/')) {
                alert('Please select an image file.');
                return;
            }

            // Validate file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('File size must be less than 5MB.');
                return;
            }

            // Read and display image
            const reader = new FileReader();
            reader.onload = (event) => {
                if (profileAvatar) {
                    profileAvatar.src = event.target.result;
                }
            };
            reader.readAsDataURL(file);
        });
    }
}
