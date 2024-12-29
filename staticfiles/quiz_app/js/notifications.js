document.addEventListener('DOMContentLoaded', function() {
    const notificationButton = document.getElementById('notificationButton');
    const notificationPopup = document.getElementById('notificationPopup');
    const notificationList = document.getElementById('notificationList');
    const notificationCount = document.getElementById('notificationCount');

    function toggleNotifications(e) {
        e.preventDefault();
        if (notificationPopup.style.display === 'block') {
            notificationPopup.style.display = 'none';
        } else {
            fetchNotifications();
            notificationPopup.style.display = 'block';
        }
    }

    function fetchNotifications() {
        fetch('/api/notifications/')
            .then(response => response.json())
            .then(data => {
                notificationList.innerHTML = '';
                data.notifications.forEach(notification => {
                    const notificationItem = document.createElement('div');
                    notificationItem.className = 'notification-item';
                    notificationItem.textContent = notification.message;
                    notificationList.appendChild(notificationItem);
                });
                updateNotificationCount(data.notifications.length);
            })
            .catch(error => console.error('Error fetching notifications:', error));
    }

    function updateNotificationCount(count) {
        notificationCount.textContent = count;
        notificationCount.style.display = count > 0 ? 'inline' : 'none';
    }

    // Inizializza il conteggio delle notifiche
    fetchNotifications();

    // Aggiungi l'event listener al pulsante delle notifiche
    if (notificationButton) {
        notificationButton.addEventListener('click', toggleNotifications);
    }

    // Chiudi il popup se si clicca fuori
    document.addEventListener('click', function(e) {
        if (notificationPopup.style.display === 'block' && !notificationPopup.contains(e.target) && e.target !== notificationButton) {
            notificationPopup.style.display = 'none';
        }
    });

    // Aggiorna il conteggio ogni minuto
    setInterval(fetchNotifications, 60000);
});