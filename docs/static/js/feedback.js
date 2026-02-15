// ======================================
// FEEDBACK PAGE - feedback.js
// ======================================

document.addEventListener('DOMContentLoaded', () => {
    initFeedback();
});

function initFeedback() {
    // Feedback stars UI logic
    const starBtns = [...document.querySelectorAll('#fb-stars .star-btn')];
    const ratingInput = document.getElementById('fb-rating');
    const label = document.getElementById('fb-stars-label');

    /**
     * Update stars visuals based on selection/hover
     */
    function paint(n) {
        starBtns.forEach((b, i) => {
            if (i < n) {
                b.classList.add('active');
                b.style.color = '#ffb800';
            } else {
                b.classList.remove('active');
                b.style.color = '#ccc';
            }
        });
        if (label) label.textContent = n ? `${n}/5 stars` : '';
    }

    starBtns.forEach(b => {
        b.addEventListener('click', () => {
            const val = parseInt(b.dataset.val, 10);
            if (ratingInput) ratingInput.value = val;
            paint(val);
        });

        b.addEventListener('mouseenter', () => {
            paint(parseInt(b.dataset.val, 10));
        });
    });

    const starsContainer = document.getElementById('fb-stars');
    if (starsContainer) {
        starsContainer.addEventListener('mouseleave', () => {
            const currentVal = ratingInput ? parseInt(ratingInput.value, 10) : 0;
            paint(currentVal);
        });
    }

    // Initialize average calculation (UI side)
    computeAverage();

    const form = document.getElementById('feedback-form');
    if (form) {
        form.addEventListener('submit', e => {
            const rating = ratingInput ? parseInt(ratingInput.value, 10) : 0;
            const err = document.getElementById('fb-error');

            if (rating < 1) {
                e.preventDefault(); // Stop submission if no rating
                if (err) err.textContent = 'Please select a rating before submitting.';
                return;
            }
            // Form will submit naturally to Django backend if rating matches
        });
    }
}

/**
 * Convers number to star signs
 */
function toStars(n) {
    return '★'.repeat(n) + '☆'.repeat(5 - n);
}

/**
 * Helper to parse stars from text
 */
function parseStars(s) {
    return (s.match(/★/g) || []).length;
}

/**
 * Calculate and display average rating based on visible cards
 */
function computeAverage() {
    const cardStars = [...document.querySelectorAll('#feedback-list .card-stars')];
    if (!cardStars.length) return;

    const ratings = cardStars.map(s => parseStars(s.textContent));
    const avg = ratings.reduce((a, b) => a + b, 0) / ratings.length;

    const starsEl = document.getElementById('stars');
    const countEl = document.getElementById('header-count');

    if (starsEl) starsEl.textContent = toStars(Math.round(avg));
    if (countEl) countEl.textContent = `${avg.toFixed(1)} / 5 from ${ratings.length} reviews`;
}
