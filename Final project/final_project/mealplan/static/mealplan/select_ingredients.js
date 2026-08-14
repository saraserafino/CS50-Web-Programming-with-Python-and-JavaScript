// Activate Chosen plugin for a more user-friendly selection of ingredients
$(document).ready(function() {
    $('.chosen-select').chosen({
        placeholder_text_multiple: "Select ingredients...",
        width: "100%",
    });
});

// When compiling the form for generating the meal plan, show/hide ingredient selection field based on generation_type
document.addEventListener('DOMContentLoaded', function() {
    const generationTypeRadios = document.querySelectorAll('input[name="generation_type"]');
    const ingredientSelectionDiv = document.getElementById('ingredient-selection');

    // Function to toggle ingredient selection fields
    function toggleIngredientSelection() {
        const selectedValue = document.querySelector('input[name="generation_type"]:checked').value;
        if (selectedValue === 'ingredients') {
            ingredientSelectionDiv.style.display = 'block';
            // Refresh Chosen dropdowns when shown
            if (typeof $('.chosen-select').trigger === 'function') {
                $('.chosen-select').trigger('chosen:updated');
            }
        } else {
            ingredientSelectionDiv.style.display = 'none';
        }
    }

    // Add event listeners to radio buttons
    generationTypeRadios.forEach(radio => {
        radio.addEventListener('change', toggleIngredientSelection);
    });

    // Call the function once to set the initial state
    toggleIngredientSelection();
});

// Disable include_leftovers if just_one_day is checked////NON FUNZIONA
document.addEventListener('DOMContentLoaded', function() {
    const justOneDayCheckbox = document.getElementById('{{ form.just_one_day.id_for_label }}');
    const includeLeftoversCheckbox = document.getElementById('{{ form.include_leftovers.id_for_label }}');

    // Disable include_leftovers if just_one_day is checked
    function toggleIncludeLeftovers() {
        includeLeftoversCheckbox.disabled = justOneDayCheckbox.checked;
        if (justOneDayCheckbox.checked) {
            includeLeftoversCheckbox.checked = false;
        }
    }
    justOneDayCheckbox.addEventListener('change', toggleIncludeLeftovers);
    toggleIncludeLeftovers();
});