// ======================================
// PAGE TRANSITIONS - transitions.js
// ======================================

document.addEventListener('DOMContentLoaded', () => {
    // Add transition class to body
    document.body.classList.add('page-transition');

    // Fade in current page
    setTimeout(() => {
        document.body.classList.add('page-visible');
    }, 100);

    // Handle all internal links for smooth transition
    document.querySelectorAll('a[href]').forEach(link => {
        // Only handle same-origin links
        if (link.hostname === window.location.hostname && !link.hasAttribute('target')) {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');

                // Skip if it's a hash link or javascript:void
                if (!href || href.startsWith('#') || href.startsWith('javascript:')) {
                    return;
                }

                e.preventDefault();

                // Fade out
                document.body.classList.remove('page-visible');

                // Navigate after transition
                setTimeout(() => {
                    window.location.href = href;
                }, 400);
            });
        }
    });
});
