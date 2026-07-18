// Activate Chosen plugin for a more user-friendly selection of filters
$(".chosen-select").chosen({width: "20%"})

// Add a new row of ingredients
function addIngredientRow() {
    const container = document.getElementById("ingredients-container");
    const newRow = document.createElement("div");
    newRow.className = "ingredient-row row mb-2";
    newRow.innerHTML = `
        <div class="col-md-2">
        <input type="number" name="ingredient_quantity[]" class="form-control" placeholder="Quantity" step="0.1">
        </div>
        <div class="col-md-2">
            <select name="ingredient_unit[]" class="form-control" required>
                <option value="grams">grams</option>
                <option value="ml">ml</option>
                <option value="teaspoon">teaspoon</option>
                <option value="tablespoon">tablespoon</option>
                <option value="pieces">pieces</option>
                <option value="by heart">by heart</option>
            </select>
        </div>
        <div class="col-md-3">
            <input type="text" name="ingredient_name[]" class="form-control" placeholder="Ingredient name" required>
        </div>
        <div class="col-sm-1"> <!-- Button for removing an ingredient-->
            <button type="button" class="btn-remove-ingredient" onclick="removeIngredientRow(this)">&#10060</button>
        </div>
        `;
    container.appendChild(newRow);
}

// Remove a row of ingredients
function removeIngredientRow(button) {
    const container = document.getElementById("ingredients-container");
    if (container.querySelectorAll('.ingredient-row').length > 1) {
        button.closest('.ingredient-row').remove();
    } else {
        alert("You must have at least one ingredient.");
    }
}
// Working on this for edit
document.addEventListener('DOMContentLoaded', function() {
    // Edit recipe
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', function() {
            const recipeDiv = this.closest('.recipe');
            const contentDiv = recipeDiv.querySelector('.procedure');
            const currentContent = contentDiv.textContent;

            // Replace procedure with a textarea
            const textarea = document.createElement('textarea');
            textarea.className = 'form-control';
            textarea.value = currentContent;
            contentDiv.innerHTML = '';
            contentDiv.appendChild(textarea);

            // Hide edit button and show save button
            this.style.display = 'none';
            recipeDiv.querySelector('.save-btn').style.display = 'inline-block';

            // Save
            recipeDiv.querySelector('.save-btn').addEventListener('click', function() {
                const newContent = textarea.value;
                const postId = recipeDiv.dataset.postId;

                // Send AJAX request to save
                fetch(`/edit_recipe/${postId}`, {
                    method: 'POST',
                    headers: {
// With this attribute, form data is encoded into a string of key-value pairs where key-value pairs are separated by & and keys and values are separated by = (ex. name=Sara&age=27)
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
                        recipeDiv.querySelector('.edit-btn').style.display = 'inline-block';
                        this.style.display = 'none';
                    } else {
                        alert('Error saving post: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(error => {
                    alert('Error: ' + error);
                });
            });
        });
    });
});