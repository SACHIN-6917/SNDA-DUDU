// ======================================
// INDUSTRIALS PAGE - industrials.js
// ======================================

document.addEventListener('DOMContentLoaded', () => {
    initHeroSlider();
    initFooterYear();
});

/**
 * Hero Slider functionality for industrial.html with pause-on-hover
 */
function initHeroSlider() {
    const slides = document.querySelectorAll('.slide');
    const heroSection = document.querySelector('.hero');

    if (!slides.length) return;

    let index = 0;
    let intervalId;
    let isPaused = false;

    // Function to change slides
    function changeSlide() {
        if (isPaused) return;

        slides[index].classList.remove('active');
        index = (index + 1) % slides.length;
        slides[index].classList.add('active');
    }

    // Start autoplay
    function startAutoPlay() {
        intervalId = setInterval(changeSlide, 4000);
    }

    // Pause on hover
    if (heroSection) {
        heroSection.addEventListener('mouseenter', () => {
            isPaused = true;
            clearInterval(intervalId);
        });

        heroSection.addEventListener('mouseleave', () => {
            isPaused = false;
            startAutoPlay();
        });
    }

    // Initialize autoplay
    startAutoPlay();
}

/**
 * Set current year in footer
 */
function initFooterYear() {
    const yearEl = document.getElementById('footerYear');
    if (yearEl) {
        yearEl.textContent = new Date().getFullYear();
    }
}
