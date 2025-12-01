document.addEventListener('DOMContentLoaded', (event) => {
    function typeText(element, text, index, callback) {
        if (index < text.length) {
            element.innerHTML += text.charAt(index);
            setTimeout(() => typeText(element, text, index + 1, callback), 50);
        } else {
            setTimeout(callback, 1000);
        }
    }

    function eraseText(element, callback) {
        const text = element.innerHTML;
        if (text.length > 0) {
            element.innerHTML = text.substring(0, text.length - 1);
            setTimeout(() => eraseText(element, callback), 50);
        } else {
            callback();
        }
    }

    // Modified to work with class instead of id
    const typingElements = document.querySelectorAll('.typing');
    typingElements.forEach(element => {
        const originalText = element.innerHTML;
        element.innerHTML = '';  // Start empty
        setTimeout(() => {
            typeText(element, '> ' + originalText, 0, () => {});
        }, 300);
    });

    // Add hover effect to show full title if truncated
    document.querySelectorAll('.post-title').forEach(title => {
        title.addEventListener('mouseover', (e) => {
            if (e.target.offsetWidth < e.target.scrollWidth) {
                e.target.title = e.target.textContent;
            }
        });
    });
});