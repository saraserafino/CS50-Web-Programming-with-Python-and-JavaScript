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

// After generating the meal plan, the user can modify it
document.addEventListener('DOMContentLoaded', function() {
    // Handle move up/down buttons
    document.querySelectorAll('.move-up').forEach(button => {
        button.addEventListener('click', function() {
            const card = this.closest('.col-md-4');
            const prevCard = card.previousElementSibling;
            if (prevCard) {
                card.parentNode.insertBefore(card, prevCard);
            }
        });
    });

    document.querySelectorAll('.move-down').forEach(button => {
        button.addEventListener('click', function() {
            const card = this.closest('.col-md-4');
            const nextCard = card.nextElementSibling;
            if (nextCard) {
                card.parentNode.insertBefore(nextCard, card);
            }
        });
    });

    // Handle block button
    document.querySelectorAll('.block').forEach(button => {
        button.addEventListener('click', function() {
            this.closest('.card').classList.add('blocked');
            this.textContent = 'Blocked';
            this.classList.remove('btn-outline-success');
            this.classList.add('btn-success');
        });
    });
});