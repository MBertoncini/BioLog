document.addEventListener('DOMContentLoaded', function () {
    console.log('Species autocomplete script loaded');

    const speciesInput = document.getElementById('species_name');
    const suggestionsContainer = document.getElementById('suggestions');

    if (!speciesInput || !suggestionsContainer) {
        console.error('Required elements not found:', {
            speciesInput: !!speciesInput,
            suggestionsContainer: !!suggestionsContainer
        });
        return;
    }

    console.log('Found required elements');

    // Mostra che il JavaScript è caricato
    speciesInput.style.borderColor = '#007bff';

    let debounceTimer;
    let selectedIndex = -1;
    let systemActivated = false; // Variabile per verificare se il sistema è attivato

    speciesInput.addEventListener('input', function (e) {
        const query = e.target.value.trim();
        console.log('Input event:', query);

        if (!systemActivated && query.length > 0) {
            console.log('Activating autocomplete system');
            systemActivated = true; // Attiva il sistema solo dopo il primo input valido
        }

        if (!systemActivated) {
            return; // Non fare nulla finché il sistema non è attivato
        }

        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            if (query) {
                fetchSuggestions(query);
            } else {
                suggestionsContainer.innerHTML = '';
            }
        }, 300);
    });

    async function fetchSuggestions(query) {
        const currentUrl = window.location.href;
        const baseUrl = currentUrl.split('/quiz/')[0];
        const apiUrl = `${baseUrl}/quiz/api/species-suggestions/?query=${encodeURIComponent(query)}`;

        console.log('Fetching suggestions from:', apiUrl);

        try {
            const response = await fetch(apiUrl);
            console.log('Response:', response.status, response.statusText);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Received data:', data);

            if (data.suggestions) {
                updateSuggestions(data.suggestions);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    function updateSuggestions(suggestions) {
        suggestionsContainer.innerHTML = '';
        selectedIndex = -1;

        if (suggestions.length === 0) {
            console.log('No suggestions to display');
            return;
        }

        console.log('Updating suggestions UI:', suggestions);

        suggestions.forEach((suggestion, index) => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.textContent = suggestion;

            div.addEventListener('click', () => {
                selectSuggestion(suggestion);
            });

            div.addEventListener('mouseover', () => {
                selectedIndex = index;
                highlightSuggestion();
            });

            suggestionsContainer.appendChild(div);
        });
    }

    function selectSuggestion(suggestion) {
        console.log('Selected suggestion:', suggestion);
        speciesInput.value = suggestion;
        suggestionsContainer.innerHTML = '';
    }

    function highlightSuggestion() {
        const items = suggestionsContainer.children;
        Array.from(items).forEach((item, index) => {
            item.classList.toggle('selected', index === selectedIndex);
        });
    }

    speciesInput.addEventListener('keydown', (e) => {
        if (!systemActivated) {
            return; // Ignora l'input da tastiera finché il sistema non è attivato
        }

        const suggestions = suggestionsContainer.children;

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                selectedIndex = Math.min(selectedIndex + 1, suggestions.length - 1);
                highlightSuggestion();
                if (suggestions[selectedIndex]) {
                    speciesInput.value = suggestions[selectedIndex].textContent;
                }
                break;
            case 'ArrowUp':
                e.preventDefault();
                selectedIndex = Math.max(selectedIndex - 1, -1);
                highlightSuggestion();
                if (selectedIndex >= 0 && suggestions[selectedIndex]) {
                    speciesInput.value = suggestions[selectedIndex].textContent;
                }
                break;
            case 'Enter':
                if (selectedIndex >= 0 && suggestions[selectedIndex]) {
                    e.preventDefault();
                    selectSuggestion(suggestions[selectedIndex].textContent);
                }
                break;
            case 'Escape':
                suggestionsContainer.innerHTML = '';
                selectedIndex = -1;
                break;
        }
    });

    // Chiudi i suggerimenti al clic fuori
    document.addEventListener('click', (e) => {
        if (!speciesInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            console.log('Click outside detected, clearing suggestions');
            suggestionsContainer.innerHTML = '';
            selectedIndex = -1;
        }
    });
});
