// After generating the meal plan, the user can modify it using Sortable to swap the cards
document.querySelectorAll('.sortable-card').forEach(sortableCard => {
    new Sortable(sortableCard, {
        animation: 350,
        handle: ".drag-handle",
        swap: true, // enable swapping instead of sorting
        filter: '.locked', // locked cards cannot be dragged
        preventOnFilter: false, // still allow clicks/taps (e.g. on the lock icon) inside locked cards
        group: "card-meal",
        // Other cards cannot be swapped onto a locked card either
        onMove: evt => !evt.related.classList.contains('locked'),
        onEnd: function() {
            // Read every card in page order, with the day and meal of the slot it now sits in
            const orderData = [];
            document.querySelectorAll('.sortable-card').forEach(slot => {
                slot.querySelectorAll('.card-body').forEach(card => {
                    orderData.push({
                        meal_plan_recipe_id: card.dataset.id,
                        day: slot.dataset.day,
                        meal_type: slot.dataset.mealType,
                        new_position: orderData.length + 1
                    });
                });
            });
            // Send AJAX request to update positions
            fetch('/mealplan/update_positions/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    meal_plan_id: mealPlanId,
                    order_data: orderData
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('Positions updated successfully');
                } else {
                    console.error('Failed to update positions');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    });
});

// Lock/unlock a recipe
document.addEventListener('DOMContentLoaded', function () {
    var lockHandles = document.querySelectorAll('.lock-handle');
    lockHandles.forEach(function (lockHandle) {
        lockHandle.addEventListener('click', function (e) {
            e.stopPropagation();
            var cardBody = this.closest('.card-body');
            var isLocked = cardBody.classList.toggle('locked');
            this.classList.toggle('circum--lock', isLocked);
            this.classList.toggle('circum--unlock', !isLocked);

            // Save the lock state, so it is kept
            fetch('/mealplan/toggle_lock/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    meal_plan_recipe_id: cardBody.dataset.id,
                    is_blocked: isLocked
                })
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    console.error('Failed to save lock state');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    });
});

// Copy the grocery list
document.addEventListener('DOMContentLoaded', function() {
    const copyButton = document.getElementById('copy-grocery-list');
    const groceryList = document.getElementById('grocery-list');

    copyButton.addEventListener('click', function() {
        const listItems = groceryList.querySelectorAll('.list-group-item');
        // Build the list with check/uncheck symbols
        const groceryText = Array.from(listItems).map(item => {
            const checkbox = item.querySelector('input[type="checkbox"]');
            const isChecked = checkbox && checkbox.checked;
            const checkSymbol = isChecked ? '[✓]' : '[ ]';
            const text = item.textContent.trim().replace(/\s+/g, ' ');
            return `${checkSymbol} ${text}`;
        }).join('\n');
        // Copy the list to the clipboard
        navigator.clipboard.writeText(groceryText)
            .catch(err => {
                console.error('Failed to copy: ', err);
                alert('Failed to copy grocery list. Please try again.');
            });
    });
});
// "Copied!" message when grocery list is copied. Source https://stackoverflow.com/a/61092810
function copy(){
    var message = document.getElementById("box");
    message.value = window.location.href;
    message.focus();
    message.select();
    document.getElementById("custom-tooltip").style.display = "inline";
    document.execCommand("copy");
    setTimeout( function() {
        document.getElementById("custom-tooltip").style.display = "none";
    }, 1000);
};