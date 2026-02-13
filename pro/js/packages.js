/**
 * PACKAGES PAGE - packages.js
 * Handles dynamic rendering and hero slider
 */

const packagesData = [
    { id: 'bengaluru', title: 'Bengaluru', location: 'Karnataka', description: "India's Silicon Valley: tech parks & startups", price: 7500, image: 'images/Bengaluru.png', rating: 4.8 },
    { id: 'coimbatore', title: 'Coimbatore', location: 'Tamil Nadu', description: 'Top IT companies, hill views & temples', price: 6500, image: 'images/Coimbatore.webp', rating: 4.5 },
    { id: 'madurai', title: 'Madurai', location: 'Tamil Nadu', description: 'Heritage city & manufacturing units', price: 5800, image: 'images/Madurai.jpg', rating: 4.6 },
    { id: 'chennai', title: 'Chennai', location: 'Tamil Nadu', description: 'IT corridor & beach tourism', price: 7200, image: 'images/Chennai.jpg', rating: 4.7 }
];

document.addEventListener('DOMContentLoaded', () => {
    initHeroSlider();
    renderPackages();
});

function initHeroSlider() {
    const slides = document.querySelectorAll('.slide');
    if (!slides.length) return;

    let index = 0;
    setInterval(() => {
        slides[index].classList.remove('active');
        index = (index + 1) % slides.length;
        slides[index].classList.add('active');
    }, 4000);
}

function renderPackages() {
    const popularContainer = document.getElementById('popularContainer');
    const packagesContainer = document.getElementById('packagesContainer');

    if (popularContainer) {
        packagesData.slice(0, 3).forEach(pkg => {
            const card = document.createElement('a');
            card.href = `package-details.html?id=${pkg.id}`;
            card.className = 'popular-card';
            card.innerHTML = `
                <img src="${pkg.image}" alt="${pkg.title}" onerror="this.src='https://via.placeholder.com/100x100?text=IV+Hub';">
                <div class="popular-info">
                    <h3>${pkg.title}</h3>
                    <p>Trending in ${pkg.location}</p>
                </div>
            `;
            popularContainer.appendChild(card);
        });
    }

    if (packagesContainer) {
        packagesData.forEach((pkg, idx) => {
            const card = document.createElement('a');
            card.href = `package-details.html?id=${pkg.id}`;
            card.className = 'package-card';
            card.innerHTML = `
                <div class="card-image-wrap">
                    <img src="${pkg.image}" alt="${pkg.title}" onerror="this.src='https://via.placeholder.com/400x250?text=IV+Hub';">
                    ${idx < 2 ? '<span class="badge-top">Top Rated</span>' : ''}
                </div>
                <div class="card-content">
                    <h3>${pkg.title}</h3>
                    <p>${pkg.description}</p>
                    <div class="card-stats">
                        <div class="rating-stars">${'★'.repeat(Math.floor(pkg.rating))}</div>
                        <div class="price-tag">₹${pkg.price}</div>
                    </div>
                    <div class="view-btn">View Details</div>
                </div>
            `;
            packagesContainer.appendChild(card);
        });
    }
}
