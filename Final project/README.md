# Final project: recipe book & meal plan
> [!NOTE]
> work in progress

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

## How to run
```bash
python manage.py runserver
```
Note to self: requirements.txt for possible Python packages to install