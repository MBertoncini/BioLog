document.addEventListener('DOMContentLoaded', function() {
    const img = document.querySelector('.centered-image');
    const container = document.querySelector('.image-container');

    function resizeImage() {
        const containerWidth = container.clientWidth;
        const containerHeight = container.clientHeight;
        const imgAspectRatio = img.naturalWidth / img.naturalHeight;
        
        let newWidth = containerWidth;
        let newHeight = newWidth / imgAspectRatio;
    
        if (newHeight > containerHeight) {
            newHeight = containerHeight;
            newWidth = newHeight * imgAspectRatio;
        }
    
        img.style.width = `${newWidth}px`;
        img.style.height = `${newHeight}px`;
    }

    window.addEventListener('resize', resizeImage);
    img.addEventListener('load', resizeImage);
    const questionContainer = document.querySelector('.question-container');
    const loadingElement = document.getElementById('loading');
    const progressBar = document.querySelector('.progress');

    function attachFormListener() {
        const form = questionContainer.querySelector('form');
        if (form) {
            form.addEventListener('submit', handleSubmit);
        }
    }

    function handleSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        
        questionContainer.style.display = 'none';
        loadingElement.style.display = 'flex';
        
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Received data:', data);  // Per debugging
            if (data.quiz_complete) {
                window.location.href = data.results_url;
            } else {
                questionContainer.innerHTML = data.question_html;
                progressBar.style.width = data.progress + '%';
                questionContainer.style.display = 'flex';
                loadingElement.style.display = 'none';
                
                // Aggiorna l'URL della pagina senza ricaricarla
                const newUrl = window.location.origin + window.location.pathname.replace(/\/\d+\/$/, `/${data.question_number}/`);
                history.pushState(null, '', newUrl);
                
                // Aggiorna l'action del form
                const newForm = questionContainer.querySelector('form');
                if (newForm) {
                    newForm.action = newUrl;
                }
                
                attachFormListener();
    
                // Pre-carica la prossima domanda
                const nextQuestionNumber = data.question_number + 1;
                if (nextQuestionNumber <= 10) {
                    fetch(`/quiz/preload_next_question/${data.quiz_session_id}/${nextQuestionNumber}/`, {
                        method: 'GET',
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    }).then(response => response.json())
                      .then(preloadData => console.log('Next question pre-loaded:', preloadData))
                      .catch(error => console.error('Error pre-loading next question:', error));
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Si è verificato un errore. Ricarica la pagina e riprova.');
            loadingElement.style.display = 'none';
            questionContainer.style.display = 'flex';
        });
    }

    attachFormListener();
});

const speciesInput = document.getElementById('species_name');
const suggestionsList = document.getElementById('suggestions');

speciesInput.addEventListener('input', function() {
    const inputValue = this.value.toLowerCase();
    fetch(`/quiz/get_species_suggestions/?query=${inputValue}`)
        .then(response => response.json())
        .then(data => {
            suggestionsList.innerHTML = '';
            data.suggestions.forEach(suggestion => {
                const div = document.createElement('div');
                div.textContent = suggestion;
                div.addEventListener('click', function() {
                    speciesInput.value = this.textContent;
                    suggestionsList.innerHTML = '';
                });
                suggestionsList.appendChild(div);
            });
        });
});