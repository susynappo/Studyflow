document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.stat-number').forEach(el => {
        const target = parseInt(el.textContent);
        let current = 0;

        const increment = Math.max(1, Math.floor(target / 40));

        const interval = setInterval(() => {
            current += increment;
            if (current >= target) {
                el.textContent = target;
                clearInterval(interval);
            } else {
                el.textContent = current;
            }
        }, 20);
    });
});
