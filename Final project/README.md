# Final project: recipe book & meal plan
> [!NOTE]
> Recipe book is finished, meal plan is a work in progress.

This web application is an online recipe book designed to help users discover, save, and manage recipes. Users can filter by recipes by dish type (protein, carbohydrate, vegetables, dessert, sauce), dietary label (vegan, vegetarian, gluten-free) and approval status (whether the recipe has been approved by the super user or not). Additionally, users can search for recipes based on title, ingredients, or procedure.<br>
For every recipe, users can adjust the portion size, and the ingredient quantities will automatically scale accordingly, allowing for meal planning and cooking flexibility.

## Distinctiveness and Complexity
While the project interface of the recipe book has some front-end similarities with the [e-commerce project](https://cs50.harvard.edu/web/projects/2/commerce/) (e.g., filtering items by category and adding them to a watchlist), it introduces several unique features and complexities to differentiate itself:

1. Infinite scroll: recipes load dynamically as the user scrolls, improving the browsing experience and reducing page load times.
2. Similar Recipe Recommendations: at the end of each recipe page, the application suggests a maximum of 4 similar recipes based on shared dish labels and the first 3 ingredients. This feature enhances user engagement by helping them discover new recipes.
3. Portion scaling: users can increase or decrease the portion size of a recipe, and the ingredient quantities are automatically recalculated to maintain the correct proportions.
4. Ingredient checklist: users can temporarily check off ingredients as they add them, acting as a reminder for what has already been included.

Above all, the most distinctive and complex implemented feature is the creation of a balanced **meal plan**, either for a day or a week. The user can:
- Choose random generation or
- Select the ingredients they already have and decide whether to use only them or possibly buy others;
- Specify a label (vegan, vegetarian, gluten-free);
- Specify whether they would like to prepare more dinner to have lunch the day after;
- Specify how many new recipes they want to include.

When presented the plan:
- User can change the position of a meal;
- User can block meals they like and generate others until they are satisfied.

Then, an interactive grocery shopping list is presented, enabling the user to tick off food they already have; the rest of the list can be saved as a text to export.

### Back-End Complexity
Although the design may seem similar to previous projects (e.g., search functionality and random page generation), the back-end logic is significantly more complex:
- **[Many-to-Many Relationships](https://docs.djangoproject.com/en/5.0/ref/models/fields/#django.db.models.ManyToManyField)**: the application uses **Django's `ManyToManyField`** to relate recipes to dishes, labels, ingredients, and users (for favorites).
- **[Intermediary Model](https://docs.djangoproject.com/en/5.0/topics/db/models/#intermediary-manytomany)**: An **intermediary model (`RecipeIngredient`)** is used to store additional details (e.g., quantity and unit of measure) for the relationship between recipes and ingredients.
- **Django Admin Customization**: the **[`TabularInline`](https://docs.djangoproject.com/en/6.0/ref/contrib/admin/#django.contrib.admin.TabularInline)** class is used to edit `RecipeIngredient` directly on the `Recipe` admin page, streamlining data management.
- **Image Uploads**: users can upload images for recipes, which required configuring **Django's [`ModelForm`](https://www.geeksforgeeks.org/python/python-uploading-images-in-django/)** in `forms.py`, configuring `settings.py`, and `urls.py` to handle media files.
- **[Custom Template](https://docs.djangoproject.com/en/6.0/howto/custom-template-tags/)**: extended the template engine by defining a custom filter in `templatetags/custom_filters.py` able to [get an item from a dictionary using a dynamic key](https://github.com/2431540349-art/django-py1/blob/main/accounts/templatetags/custom_filters.py). This was required in order to iterate over the key `day` in the dictionary containing the meal plan.
- **Data Migration**: **[Django Data Migration](https://docs.djangoproject.com/en/6.0/topics/migrations/#data-migrations)** was used to add default values for dishes and labels, ensuring a clean, permanent and version-controlled way to populate the database. Whereas for the ingredients, [Fixtures](https://docs.djangoproject.com/en/6.0/topics/db/fixtures/) are generated loading a JSON file; this method requires manual loading that is automated in the app's setup *(not done yet)*.

## Technologies Used
- **Front-End**:
  - HTML, CSS, JavaScript
  - [Bootstrap](https://getbootstrap.com/) for responsive design
  - [Chosen](https://harvesthq.github.io/chosen/) for user-friendly multi-select dropdowns
- **Back-End**:
  - [Django](https://www.djangoproject.com/) (Python web framework)
  - [Django Admin](https://docs.djangoproject.com/en/5.0/ref/contrib/admin/) for backend management
  - [SQLite](https://www.sqlite.org/index.html) (default Django database)

## Code organisation
### Models
The application includes the following models:
- **`User`**: extends Django's `AbstractUser` to support user authentication and favorites.
- **`Dish`**: represents the type of dish (e.g., protein, carbohydrate, vegetables, sauce, dessert).
- **`Label`**: represents dietary labels (e.g., vegan, vegetarian, gluten-free).
- **`Ingredient`**: stores ingredient names (e.g., tofu, onion).
- **`Recipe`**: the core model, which includes:
  - Fields for title, procedure, image, favourite and approval status (`is_new`).
  - **Many-to-Many Relationships** with `Dish`, `Label`, `Ingredient`, and `User` (for favorites).
  - A **`base_portion`** field to define the default portion size.
  - Methods for **listing ingredients** and **getting similar recipes**.
- **`RecipeIngredient`**: an **intermediary model** for the many-to-many relationship between `Recipe` and `Ingredient`, storing **quantity** and **unit of measure**.
- **`MealPlan`**: allows users to save recipes to a meal plan.

### Views and Templates
- **`index`**: displays all recipes with a badge for each type of dish and dietary label which redirects to a filtered index page when clicked.
- **`infinite_scrolling`**: function to easily apply the infinite scroll to every page.
- **`display_filters`**: filters recipes based on user-selected dishes, labels or approval status, returning the index page with applied filters.
- **`recipes`**: shows a single recipe with the option to adjust portions and check off ingredients. At the end of the page, similar recipes are recommended.
- **`random_recipe`**: randomly shows a single recipe.
- **`favourites`**: displays the user's saved recipes.
- **`search`**: search for recipes where the query is contained in the title, procedure or ingredients.
- **`add_recipe`** and **`edit_recipe`**: only the super user can add new recipes and edit them.
- **`generate_mealplan`** and **`mealplan_result`**: allow users to create and modify meal plans.

### Static Files
- **CSS**: custom styles for the application, including responsive design, such as the "copied!" message when the grocery list is copied.
- **JavaScript**: handles dynamic features like chosen plugin, infinite scroll, portion scaling, ingredient checklists, recipe editing, adding and removing an ingredient when creating a recipe. Particularly in the mealplan application, it shows and hides the ingredient selection field when generating a plan and, most importantly, it allows the user to modify a meal plan by dragging each meal and blocking it for future generation; it also allows the user to copy the grocery list.
- **Images**: personally uploaded recipe images are stored in the `media` directory, while others are public urls.
- 
## How to run
```bash
python manage.py runserver
```
Note to self: requirements.txt for possible Python packages to install
