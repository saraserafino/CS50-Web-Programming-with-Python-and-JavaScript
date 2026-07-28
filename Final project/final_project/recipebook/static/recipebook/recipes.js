// Super user can edit a recipe
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', function() {
            // Find the parent container with data-recipe-id
            const recipeContainer = this.closest('[data-recipe-id]');
            const contentDiv = recipeContainer.nextElementSibling; // The <p class="procedure"> element
            const currentContent = contentDiv.textContent;
            const recipeId = recipeContainer.dataset.recipeId;

            // Replace procedure with a textarea
            const textarea = document.createElement('textarea');
            textarea.className = 'form-control';
            textarea.value = currentContent;
            textarea.rows = 10;
            contentDiv.innerHTML = '';
            contentDiv.appendChild(textarea);

            // Hide edit button and show save button
            this.style.display = 'none';
            recipeContainer.querySelector('.save-btn').style.display = 'inline-block';

            // Save
            recipeContainer.querySelector('.save-btn').addEventListener('click', function() {
                const newContent = textarea.value;

                // Send AJAX request to save
                fetch(`/edit_recipe/${recipeId}`, {
                    method: 'POST',
                    headers: {
// With this attribute, form data is encoded into a string of key-value pairs where key-value pairs are separated by & and keys and values are separated by = (ex. dish=1&label=2)
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrftoken
                    },
                    body: `procedure=${encodeURIComponent(newContent)}`
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        contentDiv.textContent = data.procedure;
                        textarea.remove();
                        recipeContainer.querySelector('.edit-btn').style.display = 'inline-block';
                        this.style.display = 'none';
                    } else {
                        alert('Error saving recipe: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(error => {
                    alert('Error: ' + error);
                });
            });
        });
    });
});

// Portion multiplier
document.addEventListener('DOMContentLoaded', function() {
    const decreaseBtn = document.getElementById('decrease-portion');
    const increaseBtn = document.getElementById('increase-portion');
    const portionValue = document.getElementById('portion-value');
    const ingredientsList = document.querySelector('.list-group');

    // Get the base portion from the data attribute
    const originalBasePortion = parseInt(portionValue.dataset.basePortion);
    let currentPortion = originalBasePortion;

    // Decrease and increase portion
    decreaseBtn.addEventListener('click', function() {
        if (currentPortion > 1) {
            currentPortion--;
            updatePortionDisplay();
        }
    });
    increaseBtn.addEventListener('click', function() {
        currentPortion++;
        updatePortionDisplay();
    });

    // Update the displayed quantities and multiplier
    function updatePortionDisplay() {
        portionValue.textContent = currentPortion;
        // Calculate the scaling factor
        const scalingFactor = currentPortion / originalBasePortion;
        // Update each ingredient's quantity
        const ingredientItems = ingredientsList.querySelectorAll('li');
        ingredientItems.forEach(item => {
            const quantitySpan = item.querySelector('.ingredient-quantity');
            if (quantitySpan) {
                const originalQuantity = parseFloat(quantitySpan.dataset.originalQuantity);
                const newQuantity = originalQuantity * scalingFactor;
                // Remove the .0 if integer
                if (Number.isInteger(newQuantity)) {
                    quantitySpan.textContent = newQuantity;
                } else {
                    quantitySpan.textContent = newQuantity.toFixed(1);
                }
            }
        });
    }
    updatePortionDisplay();
});