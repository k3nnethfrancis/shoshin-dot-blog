document.addEventListener('DOMContentLoaded', (event) => {
    const modeToggle = document.getElementById('mode-toggle');
    const htmlElement = document.documentElement;

    // Check for saved user preference
    const savedMode = localStorage.getItem('mode');
    if (savedMode === 'dark') {
        htmlElement.classList.add('dark-mode');
    }

    modeToggle.addEventListener('click', () => {
        htmlElement.classList.toggle('dark-mode');
        
        // Save user preference
        if (htmlElement.classList.contains('dark-mode')) {
            localStorage.setItem('mode', 'dark');
        } else {
            localStorage.setItem('mode', 'light');
        }
    });
});