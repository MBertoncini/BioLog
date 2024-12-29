document.addEventListener('DOMContentLoaded', function() {
    const speciesInput = document.getElementById('species_name');
    const suggestionsContainer = document.getElementById('suggestions');
    const submitButton = document.querySelector('button[type="submit"]');
    const form = document.querySelector('form');
    let validSpecies = [];

    if (!speciesInput || !suggestionsContainer || !submitButton || !form) {
        console.error('Uno o più elementi necessari non sono stati trovati nel DOM');
        return;
    }

    function validateInput() {
        const inputValue = speciesInput.value.trim().toLowerCase();
        const isValidSpecies = validSpecies.some(species => species.toLowerCase() === inputValue);
        const isValidGenus = validSpecies.some(species => species.toLowerCase().startsWith(inputValue + ' '));
        submitButton.disabled = !(isValidSpecies || isValidGenus);
        return isValidSpecies || isValidGenus;
    }
    
    form.addEventListener('submit', function(e) {
        if (!validateInput()) {
            e.preventDefault();
            alert("Per favore, seleziona una specie o un genere valido.");
        }
    });

    speciesInput.addEventListener('input', function() {
        const inputValue = this.value;
        if (inputValue.length < 1) {
            suggestionsContainer.innerHTML = '';
            return;
        }

        fetch(`/quiz/api/species-suggestions/?query=${encodeURIComponent(inputValue)}`)
            .then(response => response.json())
            .then(data => {
                validSpecies = data.suggestions;
                suggestionsContainer.innerHTML = '';
                data.suggestions.forEach(suggestion => {
                    const div = document.createElement('div');
                    div.textContent = suggestion;
                    div.addEventListener('click', function() {
                        speciesInput.value = this.textContent;
                        suggestionsContainer.innerHTML = '';
                        validateInput();
                    });
                    suggestionsContainer.appendChild(div);
                });
                validateInput();
            })
            .catch(error => console.error("Error fetching suggestions:", error));
    });

    form.addEventListener('submit', function(e) {
        if (!validateInput()) {
            e.preventDefault();
            alert("Per favore, seleziona una specie o un genere valido.");
        }
    });

    // Chiudi i suggerimenti quando si clicca fuori
    document.addEventListener('click', function(e) {
        if (e.target !== speciesInput && e.target !== suggestionsContainer) {
            suggestionsContainer.innerHTML = '';
        }
    });

    // Gestisci la navigazione con tastiera
    speciesInput.addEventListener('keydown', function(e) {
        const suggestions = suggestionsContainer.children;
        let selectedIndex = -1;

        for (let i = 0; i < suggestions.length; i++) {
            if (suggestions[i].classList.contains('selected')) {
                selectedIndex = i;
                break;
            }
        }

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                if (selectedIndex < suggestions.length - 1) {
                    if (selectedIndex > -1) {
                        suggestions[selectedIndex].classList.remove('selected');
                    }
                    suggestions[selectedIndex + 1].classList.add('selected');
                }
                break;
            case 'ArrowUp':
                e.preventDefault();
                if (selectedIndex > 0) {
                    suggestions[selectedIndex].classList.remove('selected');
                    suggestions[selectedIndex - 1].classList.add('selected');
                }
                break;
            case 'Enter':
                e.preventDefault();
                if (selectedIndex > -1) {
                    speciesInput.value = suggestions[selectedIndex].textContent;
                    suggestionsContainer.innerHTML = '';
                    validateInput();
                }
                break;
        }
    });
});