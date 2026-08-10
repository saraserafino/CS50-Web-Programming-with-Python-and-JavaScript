from django import forms
from django.db.models.functions import Lower
from recipebook.models import Label, Ingredient

class MealPlanForm(forms.Form):
    GENERATION_CHOICES = [
        ('random', 'Random Generation'),
        ('ingredients', 'Select Ingredients'),
    ]

    generation_type = forms.ChoiceField(choices=GENERATION_CHOICES, widget=forms.RadioSelect)

    # Preselect some ingredients by default
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        basic_ingredients = ["salt", "sugar", "garlic", "onion", "curry", "oil", "water", "cool water", "pasta", "flour", "rice", "basmati rice"]
        # Get the IDs of such ingredients (assuming they exist in the database)
        basic_ingredients = [Ingredient.objects.filter(ingredient_name__iexact=f'{i}').first() for i in basic_ingredients]
        if basic_ingredients:
            self.fields['available_ingredients'].initial = [i.id for i in basic_ingredients]

    # Use Chosen for typing ingredients to select
    available_ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all().order_by(Lower('ingredient_name')),
        widget=forms.SelectMultiple(attrs={'class': 'chosen-select'}),
        required=False,
    )

    use_only_available = forms.BooleanField(required=False, label="Use only available ingredients")

    # Select label for meals (vegan, vegetarian, gluten-free)
    label = forms.ModelMultipleChoiceField(
        queryset=Label.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    # Fields for meal plan preferences
    include_leftovers = forms.BooleanField(required=False, label="Include leftovers for lunch the next day")
    num_new_recipes = forms.IntegerField(min_value=0, max_value=10, required=False, label="Number of new recipes to include")