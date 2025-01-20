// Tippy.js is now available globally as 'tippy'
document.addEventListener('DOMContentLoaded', function() {
    const followersButton = document.getElementById('followersButton');
    const followingButton = document.getElementById('followingButton');
    const modal = document.getElementById('followModal');
    const closeButton = document.querySelector('.close');
    const currentUsername = document.body.dataset.username; // Aggiungi questo attributo al body nel tuo HTML
    const isLoggedIn = document.body.dataset.isLoggedIn === 'true'; // Aggiungi questo attributo al body nel tuo HTML
    
    if (followersButton) {
        followersButton.addEventListener('click', function() {
            openModal(this.dataset.username, 'followers');
        });
    }
    
    if (followingButton) {
        followingButton.addEventListener('click', function() {
            openModal(this.dataset.username, 'following');
        });
    }

    if (closeButton) {
        closeButton.addEventListener('click', closeModal);
    }

    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            closeModal();
        }
    });

    // Gestione del pulsante "segui/smetti di seguire" sulla pagina del profilo
    const profileFollowButton = document.querySelector('.profile-follow-button');
    if (profileFollowButton && isLoggedIn) {
        profileFollowButton.addEventListener('click', function() {
            const username = this.dataset.username;
            if (username !== currentUsername) {
                toggleFollow(username, this);
            }
        });
    }

    initializeAchievementTooltips();
});

function openModal(username, type) {
    fetch(`/quiz/${type}/${username}/`)
        .then(response => response.json())
        .then(data => {
            const modal = document.getElementById('followModal');
            const modalTitle = document.getElementById('modalTitle');
            const userList = document.getElementById('userList');
            
            modalTitle.textContent = type === 'followers' ? 'Seguaci' : 'Seguiti';
            userList.innerHTML = '';
            
            data[type].forEach(user => {
                const li = createUserListItem(user);
                userList.appendChild(li);
            });
            
            modal.style.display = 'block';
        })
        .catch(error => console.error(`Error fetching ${type}:`, error));
}

function closeModal() {
    const modal = document.getElementById('followModal');
    modal.style.display = 'none';
}

function createUserListItem(user) {
    const li = document.createElement('li');
    li.className = 'user-item';
    li.innerHTML = `
        <img src="${user.avatar_url}" alt="${user.username}" class="user-avatar">
        <div class="user-info">
            <a href="/quiz/profile/${user.username}" class="user-username">${user.username}</a>
            <div class="user-fullname">${user.full_name || ''}</div>
        </div>
    `;
    return li;
}

function toggleFollow(username, button) {
    const isLoggedIn = document.body.dataset.isLoggedIn === 'true';
    const currentUsername = document.body.dataset.username;

    if (!isLoggedIn) {
        alert("Devi effettuare il login per seguire altri utenti.");
        return;
    }

    if (username === currentUsername) {
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
    .then(response => response.json())
    .then(data => {
        button.textContent = data.is_following ? 'Smetti di seguire' : 'Segui';
        updateFollowersCount(data.followers_count);
    })
    .catch(error => console.error('Error toggling follow:', error));
}

function updateFollowersCount(count) {
    const followersCountElement = document.getElementById('followersCount');
    if (followersCountElement) {
        followersCountElement.textContent = count;
    }
}

function initializeAchievementTooltips() {
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