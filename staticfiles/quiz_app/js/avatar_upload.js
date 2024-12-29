document.addEventListener('DOMContentLoaded', function() {
    const avatarContainer = document.querySelector('.profile-avatar-container');
    const avatarOverlay = document.querySelector('.avatar-overlay');
    const avatarUpload = document.getElementById('avatarUpload');
    const profileAvatar = document.getElementById('profileAvatar');

    if (avatarOverlay) {
        avatarOverlay.addEventListener('click', function() {
            avatarUpload.click();
        });

        avatarUpload.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const formData = new FormData();
                formData.append('avatar', file);

                fetch('/quiz/update_avatar/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        profileAvatar.src = data.avatar_url;
                        // Rimuovi la classe default-avatar se presente
                        profileAvatar.classList.remove('default-avatar');
                    } else {
                        alert('Errore durante il caricamento dell\'immagine');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Si è verificato un errore durante il caricamento dell\'immagine');
                });
            }
        });
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
});