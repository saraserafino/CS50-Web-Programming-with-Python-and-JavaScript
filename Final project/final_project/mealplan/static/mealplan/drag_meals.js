// After generating the meal plan, the user can modify it
// Use Sortable to swap the cards
var cardSortable = document.getElementById('card-sortable');
new Sortable(cardSortable, {
    animation: 350,
    handle: ".drag-handle",
    swap: true, // enable swapping instead of sorting
    filter: '.locked', // ignore locked cards

    // Saving and restoring of the sort
	group: "card-sortable",
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
})

// User can lock/unlock a recipe
document.addEventListener('DOMContentLoaded', function () {
    var lockHandles = document.querySelectorAll('.lock-handle');
    lockHandles.forEach(function (lockHandle) {
        lockHandle.addEventListener('click', function (e) {
            e.stopPropagation();
            var cardBody = this.closest('.card-body');
            var cardWrap = cardBody.closest('.card-wrap');
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