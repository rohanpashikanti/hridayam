document.addEventListener('DOMContentLoaded', () => {
    // Back button functionality
    const backButton = document.querySelector('.back-button');
    backButton.addEventListener('click', () => {
        // Add slide-out animation
        document.querySelector('.container').style.animation = 'slideOut 0.5s ease-in forwards';
        
        setTimeout(() => {
            // In a real app, this would navigate back
            console.log('Navigate back');
        }, 500);
    });

    // Download button functionality
    const downloadButton = document.querySelector('.download-button');
    downloadButton.addEventListener('click', () => {
        downloadButton.style.transform = 'scale(0.95)';
        setTimeout(() => {
            downloadButton.style.transform = '';
            // In a real app, this would trigger the download
            console.log('Start download');
        }, 150);
    });

    // Web button functionality
    const webButton = document.querySelector('.web-button');
    webButton.addEventListener('click', () => {
        webButton.style.transform = 'scale(0.95)';
        setTimeout(() => {
            webButton.style.transform = '';
            // In a real app, this would open the web version
            console.log('Open web version');
        }, 150);
    });

    // Add hover effect to gallery items
    const galleryItems = document.querySelectorAll('.gallery-item');
    galleryItems.forEach(item => {
        item.addEventListener('mouseenter', () => {
            item.style.transform = 'scale(1.02)';
        });
        
        item.addEventListener('mouseleave', () => {
            item.style.transform = '';
        });
    });
});

// Add smooth scroll behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});