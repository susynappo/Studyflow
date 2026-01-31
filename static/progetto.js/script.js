// script.js
document.addEventListener('DOMContentLoaded', () => {

    // 1. Mostra/nascondi sottomenu con animazione
    const submenuButtons = document.querySelectorAll('.submenu-toggle');
    submenuButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const submenu = btn.nextElementSibling;
            submenu.classList.toggle('open'); // apri/chiudi
        });
    });

    // 2. Notifiche personalizzate
    function showNotification(message, type = 'success') {
        const notif = document.createElement('div');
        notif.className = `notification ${type}`;
        notif.textContent = message;
        document.body.appendChild(notif);

        // Animazione in/out
        setTimeout(() => notif.classList.add('show'), 10);
        setTimeout(() => {
            notif.classList.remove('show');
            setTimeout(() => notif.remove(), 300);
        }, 3000);
    }

    // Esempio di test
    document.querySelector('#testNotif')?.addEventListener('click', () => {
        showNotification("Azione completata!");
    });

});