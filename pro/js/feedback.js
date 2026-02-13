// ======================================
// FEEDBACK PAGE - feedback.js
// ======================================

document.addEventListener('DOMContentLoaded', () => {
    initStarRating();
    initFeedbackForm();
    loadFeedback();
});

// ===== 1. STAR RATING =====
let selectedRating = 0;

function initStarRating() {
    const stars = document.querySelectorAll('#fb-stars button');
    const starsLabel = document.getElementById('fb-stars-label');

    stars.forEach((star, index) => {
        star.addEventListener('click', () => {
            selectedRating = index + 1;
            updateStars();
            if (starsLabel) {
                starsLabel.textContent = `${selectedRating} star${selectedRating > 1 ? 's' : ''}`;
            }
        });

        star.addEventListener('mouseenter', () => {
            highlightStars(index + 1);
        });
    });

    const starsContainer = document.getElementById('fb-stars');
    if (starsContainer) {
        starsContainer.addEventListener('mouseleave', () => {
            updateStars();
        });
    }

    function highlightStars(count) {
        stars.forEach((star, i) => {
            star.textContent = i < count ? '★' : '☆';
        });
    }

    function updateStars() {
        highlightStars(selectedRating);
    }
}

// ===== 2. FEEDBACK FORM SUBMISSION =====
function initFeedbackForm() {
    const form = document.getElementById('feedback-form');
    const fbName = document.getElementById('fb-name');
    const fbComment = document.getElementById('fb-comment');
    const fbError = document.getElementById('fb-error');

    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();

            const name = fbName?.value.trim() || '';
            const comment = fbComment?.value.trim() || '';

            // Validation
            if (!name || !comment || selectedRating === 0) {
                if (fbError) fbError.textContent = 'Please fill in all fields and select a rating.';
                return;
            }

            if (fbError) fbError.textContent = '';

            // Create feedback object
            const feedback = {
                id: Date.now(),
                name,
                comment,
                rating: selectedRating,
                date: new Date().toLocaleDateString()
            };

            // Save to localStorage
            const allFeedback = JSON.parse(localStorage.getItem('feedbackList') || '[]');
            allFeedback.unshift(feedback);
            localStorage.setItem('feedbackList', JSON.stringify(allFeedback));

            // Show success message
            if (typeof showToast === 'function') {
                showToast('Thank you for your feedback!', 'success');
            } else {
                alert('Thank you for your feedback!');
            }

            // Reset form
            form.reset();
            selectedRating = 0;
            updateStarDisplay();

            // Reload feedback display
            loadFeedback();
        });
    }
}

function updateStarDisplay() {
    const stars = document.querySelectorAll('#fb-stars button');
    const starsLabel = document.getElementById('fb-stars-label');

    stars.forEach(star => {
        star.textContent = '☆';
    });

    if (starsLabel) {
        starsLabel.textContent = 'Select rating';
    }
}

// ===== 3. LOAD AND DISPLAY FEEDBACK =====
function loadFeedback() {
    const container = document.getElementById('feedback-cards');
    if (!container) return;

    const allFeedback = JSON.parse(localStorage.getItem('feedbackList') || '[]');

    if (allFeedback.length === 0) {
        container.innerHTML = '<p style="text-align:center; color:#666;">No feedback yet. Be the first to share your experience!</p>';
        return;
    }

    container.innerHTML = allFeedback.map(fb => `
        <div class="feedback-card">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <strong style="color:#e96718;">${escapeHtml(fb.name)}</strong>
                <div style="color:#FFB800;">${'★'.repeat(fb.rating)}${'☆'.repeat(5 - fb.rating)}</div>
            </div>
            <p style="color:#555;line-height:1.6;">${escapeHtml(fb.comment)}</p>
            <small style="color:#999;">${fb.date}</small>
        </div>
    `).join('');

    // Update average rating if element exists
    updateAverageRating(allFeedback);
}

function updateAverageRating(feedbackList) {
    const avgRatingEl = document.getElementById('averageRating');
    if (!avgRatingEl || feedbackList.length === 0) return;

    const totalRating = feedbackList.reduce((sum, fb) => sum + fb.rating, 0);
    const average = (totalRating / feedbackList.length).toFixed(1);

    avgRatingEl.textContent = `${average} ★ (${feedbackList.length} reviews)`;
}

// ===== HELPER: ESCAPE HTML =====
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
