from django.contrib import admin
from .models import User, Dish, Label, Ingredient, Recipe, RecipeIngredient, MealPlan

# Register your models here.
admin.site.register(User)
admin.site.register(Dish)
admin.site.register(Label)
admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)
admin.site.register(MealPlan)

# Since ingredient is a many-to-many field with RecipeIngredient as intermediary model, TabularInline is used to create an inline class and associate it with the parent model
class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1  # Number of empty forms to display for adding new ingredients
    fields = ('ingredient', 'quantity', 'unit')

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'procedure', 'base_portion', 'ingredients_list')
    list_filter = ('dish', 'label', 'is_new')
    filter_horizontal = ('dish', 'label')
    search_fields = ('title', 'procedure')
    inlines = [RecipeIngredientInline]

    def ingredients_list(self, obj):
        return obj.ingredients_list()
    ingredients_list.short_description = "Ingredients"
