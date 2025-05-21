document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;

    const themeIcon = themeToggle.querySelector('.theme-icon i');

    // Инициализация темы
    function initTheme() {
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const isDark = savedTheme ? savedTheme === 'dark' : prefersDark;

        document.documentElement.classList.toggle('dark-theme', isDark);
        if (themeIcon) {
            themeIcon.classList.toggle('fa-moon', !isDark);
            themeIcon.classList.toggle('fa-sun', isDark);
        }
    }

    // Переключение темы
    function toggleTheme() {
        const isDark = !document.documentElement.classList.contains('dark-theme');
        document.documentElement.classList.toggle('dark-theme', isDark);

        if (themeIcon) {
            themeIcon.classList.toggle('fa-moon', !isDark);
            themeIcon.classList.toggle('fa-sun', isDark);
        }

        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }

    // Инициализация при загрузке
    initTheme();

    // Обработчик клика
    themeToggle.addEventListener('click', toggleTheme);

    // Следим за изменениями системной темы (если нет сохраненной)
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (!localStorage.getItem('theme')) {
            document.documentElement.classList.toggle('dark-theme', e.matches);
            if (themeIcon) {
                themeIcon.classList.toggle('fa-moon', !e.matches);
                themeIcon.classList.toggle('fa-sun', e.matches);
            }
        }
    });
});