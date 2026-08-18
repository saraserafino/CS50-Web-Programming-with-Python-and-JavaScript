from django.db import models
from django.conf import settings
from recipebook.models import Recipe

# Create your models here.

class MealPlan(models.Model):
    # Use settings.AUTH_USER_MODEL instead of auth.User because MealPlan uses the user model from recipebook
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             null=True, # Allow null for anonymous users
                             blank=True, related_name="meal_plans")
    # Store session key for anonymous users
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    recipes = models.ManyToManyField(Recipe, blank=True, related_name="meal_plans")
    # Block meals the user likes
    is_locked = models.BooleanField(default=False)

    def __str__(self):
        return f"Meal Plan {self.id} (User: {self.user}, Session: {self.session_key}) created at {self.created_at}"

class MealPlanRecipe(models.Model):
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='meal_plan_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    # Block meals the user likes
    is_blocked = models.BooleanField(default=False)
    # Specify the position of the meal
    position = models.PositiveIntegerField()
    meal_type = models.CharField(max_length=10, choices=[('lunch', 'Lunch'), ('dinner', 'Dinner')], default='lunch')
    day = models.CharField(max_length=10, choices=[
        ('Monday', 'monday'),
        ('Tuesday', 'tuesday'),
        ('Wednesday', '2ednesday'),
        ('Thursday', 'thursday'),
        ('Friday', 'friday'),
        ('Saturday', 'saturday'),
        ('Sunday', 'sunday'),
        ('Today', 'today'),
    ], default='Monday')

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"{self.recipe.title} in {self.meal_plan}"