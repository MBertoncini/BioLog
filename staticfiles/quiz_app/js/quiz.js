document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const questionContainer = document.querySelector('.question-container');
    const loadingElement = document.getElementById('loading');
    const progressBar = document.querySelector('.progress');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        // Mostra l'elemento di caricamento
        questionContainer.style.display = 'none';
        loadingElement.style.display = 'flex';

        // Invia la risposta e carica la prossima domanda
        const formData = new FormData(form);
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Aggiorna il contenuto della domanda
            questionContainer.innerHTML = data.question_html;
            
            // Aggiorna la barra di avanzamento
            progressBar.style.width = data.progress + '%';

            // Nascondi l'elemento di caricamento e mostra la nuova domanda
            loadingElement.style.display = 'none';
            questionContainer.style.display = 'flex';

            // Se il quiz è finito, reindirizza alla pagina dei risultati
            if (data.quiz_complete) {
                window.location.href = data.results_url;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            loadingElement.style.display = 'none';
            questionContainer.style.display = 'flex';
        });
    });
});