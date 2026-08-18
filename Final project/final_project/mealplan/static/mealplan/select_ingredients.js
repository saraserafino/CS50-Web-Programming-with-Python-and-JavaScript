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

// Disable include_leftovers if just_one_day is checked
document.addEventListener('DOMContentLoaded', function() {
    const justOneDayCheckbox = document.querySelector('input[name="just_one_day"]');
    const includeLeftoversCheckbox = document.querySelector('input[name="include_leftovers"]');
    // Disable include_leftovers if just_one_day is checked
    function toggleIncludeLeftovers() {
        if (justOneDayCheckbox && includeLeftoversCheckbox) {
            includeLeftoversCheckbox.disabled = justOneDayCheckbox.checked;
            if (justOneDayCheckbox.checked) {
                includeLeftoversCheckbox.checked = false;
            }
        }
    }
    // Add event listener if the checkbox exists
    if (justOneDayCheckbox) {
        justOneDayCheckbox.addEventListener('change', toggleIncludeLeftovers);
    }

    toggleIncludeLeftovers();
});