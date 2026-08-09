from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import MealPlanForm
from .models import MealPlan, MealPlanRecipe
from recipebook.models import Recipe, Dish, Label, Ingredient
from collections import defaultdict
import random

# Create your views here.

def generate_mealplan(request):
    if request.method == 'POST':
        form = MealPlanForm(request.POST)
        if form.is_valid():
            # Create a meal plan allowing anonymous users
            meal_plan = MealPlan.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key if not request.user.is_authenticated else None,
            )
            # Generate the meal plan based on user preferences
            generation_type = form.cleaned_data['generation_type']
            label_ids = form.cleaned_data.get('label', [])
            include_leftovers = form.cleaned_data.get('include_leftovers', False)
            num_new_recipes = int(form.cleaned_data.get('num_new_recipes') or 0)

            # Base queryset for recipes
            recipes = Recipe.objects.all()

            # Get recipes based on the generation type
            if generation_type == 'ingredients':
                # Filter recipes based on selected ingredients
                available_ingredients = form.cleaned_data.get('available_ingredients', [])
                use_only_available = form.cleaned_data.get('use_only_available', False)

                if available_ingredients:
                    if use_only_available:
                        # Only include recipes that use the selected ingredients
                        recipes = Recipe.objects.filter(ingredient__in=available_ingredients).distinct()
                    else:
                        # Include recipes that use the selected ingredients, but allow others ## fix this
                        recipes = Recipe.objects.filter(ingredient__in=available_ingredients).distinct()

            # Apply label filter
            if label_ids:
                recipes = recipes.filter(label__in=label_ids).distinct()

            # Split the queryset into existing and new recipes
            existing_recipes = recipes.filter(is_new=False)
            new_recipes = recipes.filter(is_new=True)
            # Fetch their IDs
            existing_ids = list(existing_recipes.values_list('id', flat=True))
            new_ids = list(new_recipes.values_list('id', flat=True))
            # Randomly select their IDs
            ## Probably here you'll add something to balance a meal plan depending on dish filters
            random.shuffle(existing_ids)
            random.shuffle(new_ids)

            # if include_leftovers, every dinner is also next day's lunch, except for weekend
            num_meals_to_generate = 10 if include_leftovers else 14

            # Select up to (num_meals_to_generate-num_new_recipes) from existing recipes
            existing_ids = existing_ids[:num_meals_to_generate-num_new_recipes] if (num_meals_to_generate-num_new_recipes) > 0 else []
            # Select up to num_new_recipes from new recipes
            new_ids = new_ids[:num_new_recipes] if num_new_recipes > 0 else []
            # Combine their IDs
            meals_ids = existing_ids + new_ids # its length should be either 10 or 14

            # Fetch the selected recipes from the database
            recipes = Recipe.objects.filter(id__in=meals_ids)
            # Check if recipes is empty
            if not recipes.exists():
                messages.error(request, "No recipes match your criteria. Please try different filters.")
                return redirect('mealplan_home')
            # If there are not enough recipes, repeat some to fill the meals
            while len(meals_ids) < num_meals_to_generate:
                meals_ids.extend(random.sample(meals_ids, min(num_meals_to_generate-len(meals_ids), len(meals_ids))))

            # If include_leftovers, duplicate every dinner as the next day's lunch, except for weekend
            if include_leftovers:
                meals_leftovers = []
                meals_leftovers.append(meals_ids[0]) # Monday lunch
                for i in range(1, 5):
                    meals_leftovers.append(meals_ids[i]) # dinner
                    meals_leftovers.append(meals_ids[i]) # next day's lunch
                for i in range(5, num_meals_to_generate): # weekends
                    meals_leftovers.append(meals_ids[i])
                # Fetch the selected recipes from the database
                recipes = Recipe.objects.filter(id__in=meals_leftovers)
                meals_ids = meals_leftovers

            # Add recipes to the meal plan
            for position, recipe_id in enumerate(meals_ids, start=1):
                recipe = Recipe.objects.get(id=recipe_id)
                MealPlanRecipe.objects.create(
                    meal_plan=meal_plan,
                    recipe=recipe,
                    position=position,
                )

            return redirect('mealplan_result', meal_plan_id=meal_plan.id)
    else:
        form = MealPlanForm()

    return render(request, 'mealplan/home.html', {'form': form})

def mealplan_result(request, meal_plan_id):
    meal_plan = get_object_or_404(MealPlan, id=meal_plan_id)

    # Check if the meal plan belongs to the user or their session
    if request.user.is_authenticated:
        if meal_plan.user != request.user:
            messages.error(request, "You do not have permission to view this meal plan.")
            return redirect('mealplan_home')
    else:
        if meal_plan.session_key != request.session.session_key:
            messages.error(request, "You do not have permission to view this meal plan.")
            return redirect('mealplan_home')

    # Get the grocery list (all ingredients for the meal plan's recipes)
    ingredient_dict = defaultdict(lambda: {'quantity': 0, 'unit': ''})
    for meal_plan_recipe in meal_plan.meal_plan_recipes.all():
        for recipe_ingredient in meal_plan_recipe.recipe.recipe_ingredients.all():
            key = (recipe_ingredient.ingredient.ingredient_name, recipe_ingredient.unit)
            # If an ingredient is already present, sum the overall quantity depending on the unit
            if key in ingredient_dict: # unit matches
                if recipe_ingredient.unit == ingredient_dict[key]['unit']:
                    ingredient_dict[key]['quantity'] += recipe_ingredient.quantity
            else: # unit does not match
                ingredient_dict[key]['quantity'] = recipe_ingredient.quantity
                ingredient_dict[key]['unit'] = recipe_ingredient.unit
    # Alphabetically sort the dictionary of ingredients and convert it
    ingredient_dict = dict(sorted(ingredient_dict.items()))
    grocery_list = [
        {
            'name': name,
            'quantity': details['quantity'],
            'unit': details['unit']
        }
        for (name, unit), details in ingredient_dict.items()
    ]

    # Generate the plain-text grocery list to later export it
    grocery_text = []
    for ingredient in grocery_list:
        if ingredient["unit"] == "by heart":
            grocery_text.append(ingredient["name"])
        else:
            quantity = int(ingredient["quantity"]) if ingredient["quantity"] % 1 == 0 else ingredient["quantity"]
            grocery_text.append(f"{quantity} {ingredient["unit"]} of {ingredient["name"]}")
    grocery_text_str = "\n".join(grocery_text)

    return render(request, 'mealplan/result.html', {
        'meal_plan': meal_plan,
        'grocery_list': grocery_list,
        'grocery_text': grocery_text_str
    })

@login_required
def save_mealplan(request, meal_plan_id):
    meal_plan = get_object_or_404(MealPlan, id=meal_plan_id)

    # Check if the meal plan belongs to the anonymous user's session or user
    if meal_plan.user is None and meal_plan.session_key == request.session.session_key:
        # Associate the meal plan with the logged-in user
        meal_plan.user = request.user
        meal_plan.session_key = None # Clear session key after associating with user
        meal_plan.save()
        messages.success(request, "Meal plan saved successfully!")
    else:
        messages.error(request, "You must be logged in to save this meal plan.")

    return redirect('mealplan_result', meal_plan_id=meal_plan.id)