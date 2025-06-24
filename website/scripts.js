// Slideshow configuration
const SLIDE_COUNT = 10;
const SLIDE_INTERVAL = 6000;

let slideIndex = 0;
let slideInterval;

// Generate slideshow
function initializeSlideshow() {
    const wrapper = document.querySelector('.slideshow-wrapper');
    const indicators = document.querySelector('.slide-indicators');
    
    for (let i = 1; i <= SLIDE_COUNT; i++) {
        const slide = document.createElement('div');
        slide.className = `slide ${i === 1 ? 'active' : ''}`;
        slide.innerHTML = `<img src="images/travel-${i}.jpg" alt="Beautiful destination ${i}">`;
        wrapper.appendChild(slide);
    }
    
    for (let i = 1; i <= SLIDE_COUNT; i++) {
        const indicator = document.createElement('span');
        indicator.className = `indicator ${i === 1 ? 'active' : ''}`;
        indicator.onclick = () => currentSlide(i);
        indicators.appendChild(indicator);
    }
}

window.changeSlide = function(direction) {
    const slides = document.querySelectorAll('.slide');
    const indicators = document.querySelectorAll('.indicator');
    
    slideIndex = (slideIndex + direction + SLIDE_COUNT) % SLIDE_COUNT;
    showSlide(slideIndex, slides, indicators);
    resetTimer();
}

window.currentSlide = function(index) {
    const slides = document.querySelectorAll('.slide');
    const indicators = document.querySelectorAll('.indicator');
    
    slideIndex = index - 1;
    showSlide(slideIndex, slides, indicators);
    resetTimer();
}

function showSlide(index, slides, indicators) {
    slides.forEach(slide => slide.classList.remove('active'));
    indicators.forEach(indicator => indicator.classList.remove('active'));
    
    slides[index].classList.add('active');
    indicators[index].classList.add('active');
}

function nextSlide() {
    slideIndex = (slideIndex + 1) % SLIDE_COUNT;
    const slides = document.querySelectorAll('.slide');
    const indicators = document.querySelectorAll('.indicator');
    showSlide(slideIndex, slides, indicators);
}

function startSlideshow() {
    clearInterval(slideInterval);
    slideInterval = setInterval(nextSlide, SLIDE_INTERVAL);
}

function resetTimer() {
    clearInterval(slideInterval);
    startSlideshow();
}

// Initialize all page functionality on load
document.addEventListener('DOMContentLoaded', () => {
    initializeSlideshow();
    startSlideshow();
    
    const container = document.querySelector('.slideshow-container');
    container.addEventListener('mouseenter', () => clearInterval(slideInterval));
    container.addEventListener('mouseleave', startSlideshow);
    
    const animateElements = document.querySelectorAll('.feature-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
    
    animateElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
    
    document.querySelectorAll('img').forEach(img => {
        if (!img.complete) {
            img.style.opacity = '0';
            img.style.transition = 'opacity 0.3s ease';
        }
        img.addEventListener('load', () => img.style.opacity = '1');
    });
});