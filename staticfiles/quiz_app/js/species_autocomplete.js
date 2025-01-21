console.log('Test: species_autocomplete.js loaded');

document.addEventListener('DOMContentLoaded', function() {
    console.log('Test: DOMContentLoaded event fired');
    
    const speciesInput = document.getElementById('species_name');
    console.log('Test: species_name input element:', speciesInput);
    
    if (speciesInput) {
        speciesInput.addEventListener('input', function(e) {
            console.log('Test: Input event fired with value:', e.target.value);
            
            // Test API call
            fetch('/quiz_app/api/species-suggestions/?query=' + encodeURIComponent(e.target.value))
                .then(response => response.json())
                .then(data => {
                    console.log('Test: API response:', data);
                })
                .catch(error => {
                    console.error('Test: API error:', error);
                });
        });
    }
});