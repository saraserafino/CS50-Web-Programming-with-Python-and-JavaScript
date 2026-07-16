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