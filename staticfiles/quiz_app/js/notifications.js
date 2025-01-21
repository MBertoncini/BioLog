document.addEventListener('DOMContentLoaded', function() {
    const notificationButton = document.getElementById('notificationButton');
    const notificationPopup = document.getElementById('notificationPopup');
    const notificationList = document.getElementById('notificationList');
    const notificationCount = document.getElementById('notificationCount');

    let lastFetchTime = 0;
    const FETCH_INTERVAL = 60000; // 1 minuto in millisecondi

    function toggleNotifications(e) {
        e.preventDefault();
        notificationPopup.classList.toggle('show');
        if (notificationPopup.classList.contains('show')) {
            fetchAndDisplayNotifications(true);
        }
    }

    function fetchAndDisplayNotifications(force = false) {
        const now = Date.now();
        if (force || now - lastFetchTime > FETCH_INTERVAL) {
            lastFetchTime = now;
            fetch('/quiz/api/notifications/')
                .then(response => response.json())
                .then(data => {
                    updateNotificationDisplay(data.notifications);
                    updateNotificationCount(data.notifications.filter(n => !n.is_read).length);
                })
                .catch(error => console.error('Error fetching notifications:', error));
        }
    }

    function updateNotificationDisplay(notifications) {
        notificationList.innerHTML = '';
        if (notifications.length === 0) {
            notificationList.innerHTML = '<div class="notification-item">Non hai nuove notifiche.</div>';
        } else {
            notifications.forEach(notification => {
                const notificationItem = createNotificationElement(notification);
                notificationList.appendChild(notificationItem);
            });
        }
    }

    function createNotificationElement(notification) {
        const notificationItem = document.createElement('div');
        notificationItem.className = `notification-item ${notification.is_read ? '' : 'unread'}`;
        notificationItem.dataset.id = notification.id;
        notificationItem.innerHTML = `
            ${notification.message}
            <span class="notification-date">${notification.created_at}</span>
            ${notification.is_read ? '' : '<button class="mark-as-read-btn">Segna come letta</button>'}
        `;
        return notificationItem;
    }

    function updateNotificationCount(count) {
        if (count > 0) {
            notificationCount.textContent = count;
            notificationCount.style.display = 'inline-block';
        } else {
            notificationCount.style.display = 'none';
        }
    }

    function markAsRead(notificationId, element) {
        fetch(`/quiz/notification/${notificationId}/mark-as-read/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                element.classList.remove('unread');
                const markAsReadBtn = element.querySelector('.mark-as-read-btn');
                if (markAsReadBtn) {
                    markAsReadBtn.remove();
                }
                const currentCount = parseInt(notificationCount.textContent) - 1;
                updateNotificationCount(currentCount);
                fetchAndDisplayNotifications(true);
            }
        })
        .catch(error => console.error('Error marking notification as read:', error));
    }

    function initializeNotifications() {
        if (document.body.classList.contains('just-logged-in')) {
            fetchAndDisplayNotifications(true);
            document.body.classList.remove('just-logged-in');
        } else {
            fetchAndDisplayNotifications();
        }

        if (notificationButton) {
            notificationButton.addEventListener('click', toggleNotifications);
        }

        if (notificationList) {
            notificationList.addEventListener('click', function(e) {
                if (e.target.classList.contains('mark-as-read-btn')) {
                    const notificationElement = e.target.closest('.notification-item');
                    const notificationId = notificationElement.dataset.id;
                    markAsRead(notificationId, notificationElement);
                }
            });
        }

        // Chiudi il popup se si clicca fuori
        document.addEventListener('click', function(e) {
            if (notificationPopup.classList.contains('show') && 
                !notificationPopup.contains(e.target) && 
                e.target !== notificationButton) {
                notificationPopup.classList.remove('show');
            }
        });

        // Aggiorna le notifiche ogni minuto
        setInterval(fetchAndDisplayNotifications, FETCH_INTERVAL);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Inizializza le notifiche
    initializeNotifications();
});