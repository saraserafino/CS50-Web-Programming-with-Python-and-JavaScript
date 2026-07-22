# Final project: recipe book & meal plan
> [!NOTE]
> work in progress, for now the recipe book is almost finished.

This web application implements an online recipe book, where recipies can be filtered by dish (protein, carbohydrate, vegetables, complete meal, dessert), ingredients and time required, and have a label for vegan, vegetarian or gluten-free. For every recipe, it is possibile to increase the resulting portion, automatically obtaining the new proportion of the ingredients.<br>
Users can log in to save a recipe and generate a meal plan, whereas the super user can also add new recipes and modify them. Moreover, there is a label for "new recipes" that the super user has not tried yet; these recipies can also be found in a different page from the other recipies.

## Distinctiveness and Complexity
The project interface has some initial similarities with the [e-commerce project](https://cs50.harvard.edu/web/projects/2/commerce/) in the possibility to filter items per category and add them to a watchlist (here the favourite recipies). For this reason, some additions were made, namely at the end of the page of a single recipe, other similar are recommended.<br>
The most distinctive and complex implemented feature is the creation of a balanced **meal plan**, either for a day or a week. The user can:
- Choose random generation or
- Select the ingredients they already have and decide whether to use only them or possibly buy others;
- Specify whether they would like to prepare more dinner to have lunch the day after;
- Specify how many new recipies they want to include.

When presented the plan:
- User can change the position of a meal;
- User can block meals they like and generate others until they are satisfied.

Then, an interactive grocery shopping list is presented, enabling the user to tick off food they already have; the rest of the list can be saved as a text to export.

## Code organisation
### Models
Besides a model for User and Recipe, models for filtering by Dish, Label and Ingredients are defined and related to the recipe as a [many-to-many field](https://docs.djangoproject.com/en/5.0/ref/models/fields/#django.db.models.ManyToManyField), as multiple of them can be used in more recipies.<br>
Inside the Recipe model, saving a recipe as favourite is also a many-to-many field, as different users have this option. The label for "new recipes" that have not been tried yet is a boolean, set as False by default. The time required for preparing a recipe is a positive integer, as well as the portion for a recipe, that can be used to scale the ingredients accordingly.<br>
An interesting addition to the course material is the use of an [intermediary model of a many-to-many relationship](https://docs.djangoproject.com/en/5.0/topics/db/models/#intermediary-manytomany) called RecipeIngredient to relate an ingredient with a recipe, adding details of an ingredient such as its quantity and unit of measure. When registering the models to the Django admin interface, [Django Inline Admin TabularInline](https://docs.djangoproject.com/en/6.0/ref/contrib/admin/#django.contrib.admin.TabularInline) is used on RecipeIngredient to edit it on the same page as the parent model, that is Recipe.<br>
When adding a recipe, it is possible to upload an image, hence [Django's ModelForm](https://www.geeksforgeeks.org/python/python-uploading-images-in-django/) is employed in forms.py after configuring settings.py and urls.py for serving media.
### Other
The plugin [Chosen](https://harvesthq.github.io/chosen/) is employed to render selection of filters more user-friendly.<br>
[Django Data Migration](https://docs.djangoproject.com/en/6.0/topics/migrations/#data-migrations) has been performed for adding default values for dishes and labels in the cleanest way, as it ensures a permanent, version-controlled migration of data. Whereas for the ingredients, [Fixtures](https://docs.djangoproject.com/en/6.0/topics/db/fixtures/) are generated loading a JSON file; this method requires manual loading that is automated in the app's setup *(not done yet)*.

## How to run
```bash
python manage.py runserver
```
Note to self: requirements.txt for possible Python packages to install
