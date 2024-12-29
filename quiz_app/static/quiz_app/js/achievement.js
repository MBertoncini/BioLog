document.addEventListener('DOMContentLoaded', function() {
    const achievementItems = document.querySelectorAll('.achievement-item');
    achievementItems.forEach(item => {
        const tooltip = document.createElement('div');
        tooltip.classList.add('achievement-tooltip');
        tooltip.textContent = item.getAttribute('data-description');
        item.appendChild(tooltip);

        item.addEventListener('mouseenter', () => {
            tooltip.style.display = 'block';
        });

        item.addEventListener('mouseleave', () => {
            tooltip.style.display = 'none';
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
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