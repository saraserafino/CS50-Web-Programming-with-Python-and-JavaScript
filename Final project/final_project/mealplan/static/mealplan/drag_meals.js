// Generate the days header
const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const daysHeaderContainer = document.getElementById("days-header");
days.forEach(day => {
    const dayColumn = document.createElement("div");
    dayColumn.className = "col";
    dayColumn.innerHTML = `<h4>${day}</h4>`;
    daysHeaderContainer.appendChild(dayColumn);
});

// Generate the meal cards
// Access the meal plan data
const mealPlanRecipes = mealPlanData.meal_plan_recipes;
// Sort the recipes by their position
mealPlanRecipes.sort((a, b) => a.position - b.position);
// Initialize recipesByDay with empty lunch and dinner slots for each day
const recipesByDay = {};
days.forEach(day => {
    recipesByDay[day] = { lunch: null, dinner: null };
});
// Populate recipesByDay based on the position
mealPlanRecipes.forEach((mealPlanRecipe, index) => {
    const dayIndex = Math.floor(index / 2); // 0-6 for lunch, 7-13 for dinner
    const day = days[dayIndex % 7]; // Wrap around for dinner (7-13 -> 0-6)
    const isLunch = index % 2 === 0; // Even indices are lunch, odd are dinner
    if (isLunch) {
        recipesByDay[day].lunch = mealPlanRecipe;
    } else {
        recipesByDay[day].dinner = mealPlanRecipe;
    }
});

// Generate the card layout
// Generate the meal plan layout
const mealPlanContainer = document.getElementById("meal-plan-container");
days.forEach(day => {
    const dayColumn = document.createElement("div");
    dayColumn.className = "col";
    // Create a container for lunch and dinner cards
    const lunchDinnerContainer = document.createElement("div");
    lunchDinnerContainer.className = "d-flex flex-column";

    if (recipesByDay[day].lunch) {
        const lunchRecipe = recipesByDay[day].lunch.recipe;
        const lunchCard = document.createElement("div");
        lunchCard.className = "mb-2 card-wrap";
        // Fixed day-lunch
        const lunchLabel = document.createElement("div");
        lunchLabel.className = "card-header text-center";
        lunchLabel.innerHTML = `<h5>${day} Lunch</h5>`;
        // Actual content of meal plan
        const lunchDraggableContent = document.createElement("div");
        lunchDraggableContent.className = "sortable-card card-meal h-100";
        lunchDraggableContent.innerHTML = `
                <div class="card-body text-center" data-id="${recipesByDay[day].lunch.id}">
                    <a href="/recipes/${lunchRecipe.id}" class="text-decoration-none text-dark">
                        <h6 class="card-title">${lunchRecipe.title}</h6>
                        <div class="recipe-image-container" style="width: 100px; height: 75px; margin: 0 auto;">
                        <img class="card-img-top recipe-image" alt="${lunchRecipe.title}" src="${lunchRecipe.imageUrl}">
                        </div>
                    </a>
                    <!-- Drag handle -->
                    <div class="card-handle">
                        <span class="iconify drag-handle ic--outline-drag-indicator"></span>
                        <span class="lock-handle circum--unlock"></span>
                    </div>
                </div>
        `;
        lunchCard.appendChild(lunchLabel);
        lunchCard.appendChild(lunchDraggableContent);
        lunchDinnerContainer.appendChild(lunchCard);
    }

    if (recipesByDay[day].dinner) {
        const dinnerRecipe = recipesByDay[day].dinner.recipe;
        const dinnerCard = document.createElement("div");
        dinnerCard.className = "mb-2 card-wrap";
        // Fixed day-dinner
        const dinnerLabel = document.createElement("div");
        dinnerLabel.className = "card-header text-center";
        dinnerLabel.innerHTML = `<h5>${day} Dinner</h5>`;
        // Actual content of meal plan
        const dinnerDraggableContent = document.createElement("div");
        dinnerDraggableContent.className = "sortable-card card-meal h-100";
        dinnerDraggableContent.innerHTML = `
                <div class="card-body text-center" data-id="${recipesByDay[day].dinner.id}">
                    <a href="/recipes/${dinnerRecipe.id}" class="text-decoration-none text-dark">
                        <h6 class="card-title">${dinnerRecipe.title}</h6>
                        <div class="recipe-image-container" style="width: 100px; height: 75px; margin: 0 auto;">
                        <img class="card-img-top recipe-image" alt="${dinnerRecipe.title}" src="${dinnerRecipe.imageUrl}">
                        </div>
                    </a>
                    <!-- Drag handle -->
                    <div class="card-handle">
                        <span class="iconify drag-handle ic--outline-drag-indicator"></span>
                        <span class="lock-handle circum--unlock"></span>
                    </div>
                </div>
        `;
        dinnerCard.appendChild(dinnerLabel);
        dinnerCard.appendChild(dinnerDraggableContent);
        lunchDinnerContainer.appendChild(dinnerCard);
    }
    dayColumn.appendChild(lunchDinnerContainer);
    mealPlanContainer.appendChild(dayColumn);
});

// After generating the meal plan, the user can modify it using Sortable to swap the cards
document.querySelectorAll('.sortable-card').forEach(sortableCard => {
    new Sortable(sortableCard, {
        animation: 350,
        handle: ".drag-handle",
        swap: true, // enable swapping instead of sorting
        filter: '.locked', // ignore locked cards
        group: "card-meal",////TO FIX BC IT DOES NOT SAVE

        // Saving and restoring of the sort
        store: {
            get: function (sortable) {
                var order = localStorage.getItem(sortable.options.group.name);
                return order ? order.split('|') : [];
            },

            set: function (sortable) {
                var order = sortable.toArray();
                localStorage.setItem(sortable.options.group.name, order.join('|'));
            }
        }
    });
});

// User can lock/unlock a recipe
document.addEventListener('DOMContentLoaded', function () {
    var lockHandles = document.querySelectorAll('.lock-handle');
    lockHandles.forEach(function (lockHandle) {
        lockHandle.addEventListener('click', function (e) {
            e.stopPropagation();
            var cardBody = this.closest('.card-body');
            var cardWrap = cardBody.closest('.sortable-card');
            var dragHandle = cardBody.querySelector('.drag-handle');

            // Toggle lock state
            if (this.classList.contains('circum--unlock')) {
                this.classList.remove('circum--unlock');
                this.classList.add('circum--lock');
                cardWrap.classList.add('locked');
                dragHandle.style.cursor = 'not-allowed';
                dragHandle.style.opacity = '0.5';
            } else {
                this.classList.remove('circum--lock');
                this.classList.add('circum--unlock');
                cardWrap.classList.remove('locked');
                dragHandle.style.cursor = 'move';
                dragHandle.style.opacity = '1';
            }
        });
    });
});

// User can export the grocery list
document.addEventListener('DOMContentLoaded', function() {
    const copyButton = document.getElementById('copy-grocery-list');
    const groceryText = document.getElementById('grocery-text').textContent;

    copyButton.addEventListener('click', function() {
        navigator.clipboard.writeText(groceryText)
            .then(() => { alert('Grocery list copied to clipboard!'); })
            .catch(err => {
                console.error('Failed to copy: ', err);
                alert('Failed to copy grocery list. Please try again.');
            });
    });
});