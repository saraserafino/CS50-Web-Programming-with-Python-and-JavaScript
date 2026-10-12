// Activate Chosen plugin for a more user-friendly selection of filters
$(".chosen-select").chosen({width: "20%"})

// Infinite scrolling
// Start with first recipes and load 20 per time when the DOM loads
const container = document.getElementById('recipes-container');
let counter = container.querySelectorAll(':scope > .card').length;
const quantity = 20;
let loading = false;
let done = false;

// Sentinel below the container so that when it comes into view, it loads more
const sentinel = document.createElement('div');
sentinel.style.textAlign = 'center';
sentinel.style.margin = '20px';
sentinel.innerHTML = `
    <div class="spinner-border text-warning" role="status" hidden>
        <span class="sr-only">Loading...</span>
    </div>`;
container.after(sentinel);
const spinner = sentinel.firstElementChild;

const observer = new IntersectionObserver(entries => {
    if (entries[0].isIntersecting) load();
}, { rootMargin: '400px' }); // loads a bit before the real bottom of the page

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
async function load() {
    if (loading || done) return;
    loading = true;
    spinner.hidden = false;

    // Get the current URL's query parameters (e.g., ?dish=1&label=2)
    const params = new URLSearchParams(window.location.search);
    // Set start and end recipe numbers
    params.set('start', counter);
    params.set('end', counter + quantity - 1);

    try {
        // Append existing filter parameters to the fetched URL
        const response = await fetch(`?${params}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();

        data.recipes.forEach(add_recipe_js);
        counter += data.recipes.length; // advance only on success

        if (!data.has_more || data.recipes.length === 0) {
            done = true;
            observer.disconnect();
            sentinel.remove();
        } else {
// Re-observe: fires immediately if the sentinel is still visible (page not tall enough yet), so loading continues without scrolling
            observer.unobserve(sentinel);
            observer.observe(sentinel);
        }
    } catch (error) {
        console.error('Error fetching recipes:', error);
    } finally {
        loading = false;
        spinner.hidden = true;
    }
}

observer.observe(sentinel); // replaces window.onscroll and the DOMContentLoaded load()