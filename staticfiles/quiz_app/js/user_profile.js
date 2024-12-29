document.addEventListener('DOMContentLoaded', function() {
    const followersButton = document.getElementById('followersButton');
    const followingButton = document.getElementById('followingButton');
    const followButton = document.getElementById('followButton');
    const showMoreSpeciesButton = document.getElementById('showMoreSpecies');

    if (followersButton) {
        followersButton.addEventListener('click', function() {
            const username = this.dataset.username;
            fetch(`/quiz/followers/${username}/`)
                .then(response => response.json())
                .then(data => openModal(data.followers, 'Seguaci'))
                .catch(error => console.error('Error fetching followers:', error));
        });
    }

    if (followingButton) {
        followingButton.addEventListener('click', function() {
            const username = this.dataset.username;
            fetch(`/quiz/following/${username}/`)
                .then(response => response.json())
                .then(data => openModal(data.following, 'Seguiti'))
                .catch(error => console.error('Error fetching following:', error));
        });
    }

    if (followButton) {
        followButton.addEventListener('click', function() {
            const username = this.dataset.username;
            fetch(`/quiz/toggle_follow/${username}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                updateFollowButtonUI(this, data.is_following);
            })
            .catch(error => console.error('Error toggling follow:', error));
        });
    }

    if (showMoreSpeciesButton) {
        showMoreSpeciesButton.addEventListener('click', function() {
            const hiddenSpecies = document.querySelectorAll('.species-item.hidden');
            hiddenSpecies.forEach(item => item.classList.remove('hidden'));
            this.style.display = 'none';
        });
    }

    // Close modal when clicking outside
    window.onclick = function(event) {
        const modal = document.getElementById('followModal');
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }

    // Close modal when clicking the close button
    const closeButton = document.querySelector('.close');
    if (closeButton) {
        closeButton.onclick = function() {
            document.getElementById('followModal').style.display = 'none';
        }
    }

    // Avatar upload functionality
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

    // Initialize Tippy.js for achievements
    tippy('.achievement-item', {
        content(reference) {
            const name = reference.getAttribute('data-name');
            const description = reference.getAttribute('data-description');
            const isEarned = reference.getAttribute('data-is-earned') === 'True';
            const dateEarned = reference.getAttribute('data-date-earned');
            const progress = reference.getAttribute('data-progress');
            const encouragement = reference.getAttribute('data-encouragement');

            let content = `<strong>${name}</strong><br>${description}<br>`;
            if (isEarned) {
                content += `<span class='earned'>Ottenuto il ${dateEarned}</span>`;
            } else {
                content += `Progresso: ${progress}%<br><em>${encouragement}</em>`;
            }
            return content;
        },
        allowHTML: true,
    });
});

function openModal(users, title) {
    const modal = document.getElementById('followModal');
    const modalTitle = document.getElementById('modalTitle');
    const userList = document.getElementById('userList');
    
    modalTitle.textContent = title;
    userList.innerHTML = '';
    
    if (users.length === 0) {
        const emptyMessage = document.createElement('p');
        emptyMessage.textContent = title === 'Seguaci' ? 
            "Ancora non ti segue nessuno." : 
            "Non stai seguendo nessuno.";
        userList.appendChild(emptyMessage);

        const exploreButton = document.createElement('button');
        exploreButton.textContent = "Esplora";
        exploreButton.className = "btn btn-primary";
        exploreButton.onclick = fetchRandomUsers;
        userList.appendChild(exploreButton);
    } else {
        users.forEach(user => {
            const li = document.createElement('li');
            li.className = 'user-item';
            let buttonHtml = '';
            
            if (user.username !== currentUser) {
                buttonHtml = `
                    <button class="follow-button" data-username="${user.username}">
                        <i class="fas ${user.is_following ? 'fa-user-minus' : 'fa-user-plus'}"></i>
                        <span>${user.is_following ? 'Smetti di seguire' : 'Segui'}</span>
                    </button>
                `;
            }
            
            li.innerHTML = `
                <a href="/quiz/profile/${user.username}" class="user-link">
                    <img src="${user.avatar_url}" alt="${user.username}" class="user-avatar">
                    <span class="user-username">${user.username}</span>
                </a>
                ${buttonHtml}
            `;
            userList.appendChild(li);

            const followButton = li.querySelector('.follow-button');
            if (followButton) {
                followButton.addEventListener('click', function() {
                    toggleFollow(user.username, this);
                });
            }
        });
    }
    
    modal.style.display = 'block';
}

function toggleFollow(username, button) {
    if (username === currentUser) {
        alert("Non puoi seguire te stesso.");
        return;
    }

    fetch(`/quiz/toggle_follow/${username}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        updateFollowButtonUI(button, data.is_following);
        updateFollowStatus(username, data.is_following);
    })
    .catch(error => {
        console.error('Error toggling follow:', error);
        alert('Si è verificato un errore durante l\'aggiornamento dello stato del follow.');
    });
}

function updateFollowButtonUI(button, isFollowing) {
    if (!button) return;

    const icon = button.querySelector('i');
    const textSpan = button.querySelector('span');

    if (icon) {
        icon.className = isFollowing ? 'fas fa-user-minus' : 'fas fa-user-plus';
    }

    if (textSpan) {
        textSpan.textContent = isFollowing ? 'Smetti di seguire' : 'Segui';
    } else {
        button.textContent = isFollowing ? 'Smetti di seguire' : 'Segui';
        if (icon) button.prepend(icon);
    }
}

function updateFollowStatus(username, isFollowing) {
    const buttons = document.querySelectorAll(`.follow-button[data-username="${username}"]`);
    buttons.forEach(button => {
        updateFollowButtonUI(button, isFollowing);
    });
}

function fetchRandomUsers() {
    fetch('/quiz/random_users/')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => openModal(data.users, 'Utenti Suggeriti'))
        .catch(error => {
            console.error('Error fetching random users:', error);
            alert('Si è verificato un errore nel caricare gli utenti suggeriti.');
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