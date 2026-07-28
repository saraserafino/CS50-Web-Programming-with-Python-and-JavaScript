// Activate Chosen plugin for a more user-friendly selection of filters
$(".chosen-select").chosen({width: "20%"})

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
            // Stop fetching if no more recipes are available
            if (!data.has_more) {
                window.onscroll = null;
            }
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