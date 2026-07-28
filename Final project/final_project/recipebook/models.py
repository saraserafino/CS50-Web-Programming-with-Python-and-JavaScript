from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Because it inherits from AbstractUser, it has already fields for a username, email, password, etc
    pass

# Define models for filtering the recipes

# Dish type will be protein, carbohydrate, vegetables, complete meal, dessert
class Dish(models.Model):
    dish_name = models.CharField(max_length=50)

    def __str__(self):
        return self.dish_name

# Labels will be vegan, vegetarian, gluten-free
class Label(models.Model):
    label_name = models.CharField(max_length=50)

    def __str__(self):
        return self.label_name
    
class Ingredient(models.Model):
    ingredient_name = models.CharField(max_length=50)

    def __str__(self):
        return self.ingredient_name

class Recipe(models.Model):
    title = models.CharField(max_length=50)
    procedure = models.CharField(max_length=10000)
    # Image can be uploaded from files or url
    image = models.ImageField(upload_to="images/", blank=True, null=True)
    url = models.URLField(max_length=500, blank=True, null=True)
    # Filters for recipe, multiple selection is possible
    dish = models.ManyToManyField(Dish, blank=True, related_name="dish")
    label = models.ManyToManyField(Label, blank=True, related_name="label")
    # Ingredients are managed by RecipeIngredient, an intermediary model of the many-to-many relationship
    ingredient = models.ManyToManyField(Ingredient, through="RecipeIngredient")
    # One recipe can be in the favourites of different people -> many-to-many relationship
    favourites = models.ManyToManyField(User, blank=True, related_name="favourites")
    # "New recipe" status for recipes that have not been tried yet
    is_new = models.BooleanField(default=False, help_text="Mark as new if you have not tried it yet.")

    # Use it with JavaScript to increase/decrease the portion of a recipe, automatically obtaining the new proportion of the ingredients
    base_portion = models.PositiveIntegerField(default=1, help_text="Base number of portions.")

    def ingredients_list(self):
        """
        Returns quantity and unit of measure for each ingredient of a recipe.
        """
        return [{
            "quantity": ingredient.quantity,
            "unit": ingredient.unit,
            "name": ingredient.ingredient.ingredient_name}
            for ingredient in self.recipe_ingredients.all()
            ]

    def get_similar_recipes(self, limit=4):
        """
        Returns a queryset of similar recipes based on shared ingredients and dishes.
        """
        # Get IDs of ingredients, dishes and labels for the current recipe
        main_ingredients = self.recipe_ingredients.all()[:3]
        ingredient_ids = [ingredient.ingredient.id for ingredient in main_ingredients]
        dish_ids = self.dish.values_list('id', flat=True)

        # Find recipes that share at least one ingredient, dish or label (excluding current recipe)
        similar_recipes = Recipe.objects.filter(ingredient__in=ingredient_ids, dish__in=dish_ids).exclude(id=self.id).distinct()

        # Order by newest and limit the results
        return similar_recipes.order_by("-id")[:limit]

    def __str__(self):
        return self.title

# Intermediary model between the many-to-many relationship between Ingredient and Recipe (https://docs.djangoproject.com/en/5.0/topics/db/models/#intermediary-manytomany)
class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="recipe_ingredients")
    quantity = models.DecimalField(max_digits=6, decimal_places=1, default=0, blank=True, null=True)
    unit = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.quantity} {self.unit} of {self.ingredient.ingredient_name} for {self.recipe.title}"

# Probably meal plan will be a model like this, but adjust later
class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meal_plans")
    created_at = models.DateTimeField(auto_now_add=True)
    recipes = models.ManyToManyField(Recipe, blank=True, related_name="meal_plans")

    def __str__(self):
        return f"{self.user.username}'s Meal Plan created at {self.created_at}"