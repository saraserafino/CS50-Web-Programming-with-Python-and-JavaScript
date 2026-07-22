// Activate Chosen plugin for a more user-friendly selection of filters
$(".chosen-select").chosen({width: "20%"})

// When adding a recipe, user can add a new row of ingredients
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

// When adding a recipe, user can remove a row of ingredients
function removeIngredientRow(button) {
    const container = document.getElementById("ingredients-container");
    if (container.querySelectorAll('.ingredient-row').length > 1) {
        button.closest('.ingredient-row').remove();
    } else {
        alert("You must have at least one ingredient.");
    }
}

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

// Infinite scrolling
// Start with first recipes and load 20 per time when the DOM loads
let counter = document.querySelectorAll('#recipes-container > .card').length;
const quantity = 20;
document.addEventListener('DOMContentLoaded', load);
// If scrolled to bottom, load the next 20 recipes
window.onscroll = () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) { load(); }
};
// Add new recipes with given data to DOM
function add_recipe_js(recipe) {
    // Create new recipe card
    const recipeCard = document.createElement('div');
    recipeCard.className = 'card h-100';

    let dishesHtml = '';
    if (recipe.dishes && recipe.dishes.length > 0) {
        dishesHtml = recipe.dishes.map(dish =>
            `<a href="/display_filters?dish=${dish.id}"><span class="badge badge-pill badge-dish me-1">
            ${dish.dish_name}</span></a>`
        ).join('');
    }

    let labelsHtml = '';
    if (recipe.labels && recipe.labels.length > 0) {
        labelsHtml = recipe.labels.map(label =>
            `<a href="/display_filters?label=${label.id}"><span class="badge badge-pill badge-label me-1">
            ${label.label_name}</span></a>`
        ).join('');
    }

    recipeCard.innerHTML = `
        <a href="/recipes/${recipe.id}" class="text-decoration-none text-dark">

        <div class="recipe-image-container">
        <img class="card-img-top recipe-image" alt="${recipe.title}" src="${recipe.image_url}">
        </div>

        <div class="card-body">
        <h5 class="card-title">${recipe.title}</h5>
        </a>

            <div class="mb-2">
                ${dishesHtml}
                ${labelsHtml}
            </div>
        </div>
    `;
    // Append the recipe card to the container
    document.getElementById('recipes-container').appendChild(recipeCard);
};
// Load next set of recipes
function load() {
    // Set start and end recipe numbers, and update counter
    const start = counter;
    const end = start + quantity - 1;
    counter = end + 1;

    // Show loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.id = 'loading-indicator';
    loadingIndicator.style.textAlign = 'center';
    loadingIndicator.style.margin = '20px';
    loadingIndicator.innerHTML = `
        <div class="spinner-border text-warning" role="status">
            <span class="sr-only">Loading...</span>
        </div>
    `;
    document.getElementById('recipes-container').appendChild(loadingIndicator);

    // Get the current URL's query parameters (e.g., ?dish=1&label=2)
    const currentParams = new URLSearchParams(window.location.search);
    let fetchUrl = `?start=${start}&end=${end}`;
    // Append existing filter parameters to the fetch URL
    currentParams.forEach((value, key) => {
        if (key !== 'start' && key !== 'end') {
            fetchUrl += `&${key}=${value}`;
        }
    });

    // Fetch new recipes with the updated URL
    fetch(fetchUrl, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading indicator
        document.getElementById('loading-indicator').remove();
        if (data.recipes.length > 0) {
            // Add new recipes to the DOM
            data.recipes.forEach(add_recipe_js);
        } else {
            // No more recipes to load
            window.onscroll = null;
        }
    })
    .catch(error => {
        console.error('Error fetching data:', error);
        document.getElementById('loading-indicator').remove();
    });
}