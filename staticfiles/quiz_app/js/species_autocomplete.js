document.addEventListener('DOMContentLoaded', function() {
    console.log('Species autocomplete initialized');

    const speciesInput = document.getElementById('species_name');
    const suggestionsContainer = document.getElementById('suggestions');

    console.log('Elements found:', {
        speciesInput: !!speciesInput,
        suggestionsContainer: !!suggestionsContainer
    });

    if (!speciesInput || !suggestionsContainer) {
        console.error('Required elements not found');
        return;
    }

    let debounceTimer;
    let selectedIndex = -1;

    speciesInput.addEventListener('input', function(e) {
        console.log('Input event fired with value:', e.target.value);
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => fetchSuggestions(e.target.value), 300);
    });

    async function fetchSuggestions(query) {
        if (!query) {
            suggestionsContainer.innerHTML = '';
            return;
        }

        try {
            console.log('Fetching suggestions for:', query);
            const response = await fetch(`/quiz_app/api/species-suggestions/?query=${encodeURIComponent(query)}`);
            console.log('Response status:', response.status);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Received suggestions:', data);

            updateSuggestions(data.suggestions || []);
        } catch (error) {
            console.error('Error fetching suggestions:', error);
            suggestionsContainer.innerHTML = '';
        }
    }

    function updateSuggestions(suggestions) {
        suggestionsContainer.innerHTML = '';
        selectedIndex = -1;

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
        console.log('Selecting suggestion:', suggestion);
        speciesInput.value = suggestion;
        suggestionsContainer.innerHTML = '';
        speciesInput.focus();
    }

    function highlightSuggestion() {
        const items = suggestionsContainer.children;
        Array.from(items).forEach((item, index) => {
            item.classList.toggle('selected', index === selectedIndex);
        });
    }

    speciesInput.addEventListener('keydown', (e) => {
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

    document.addEventListener('click', (e) => {
        if (!speciesInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.innerHTML = '';
        }
    });
});