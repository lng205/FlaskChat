function toggleDarkMode() {
    let darkMode = localStorage.getItem('darkMode') === 'true';
    darkMode = !darkMode; // Toggle the state
    localStorage.setItem('darkMode', darkMode);
    updateDarkMode(); // Apply changes
}

function updateDarkMode() {
    const icon = document.getElementById('darkModeIcon');
    if (localStorage.getItem('darkMode') === 'true') {
        document.documentElement.classList.add('dark-mode');
        icon.className = 'bi bi-sun'; // Change icon to sun
    } else {
        document.documentElement.classList.remove('dark-mode');
        icon.className = 'bi bi-moon'; // Change icon to moon
    }
}

document.addEventListener('DOMContentLoaded', function() {
    updateDarkMode(); // Ensure correct mode on page load
});
