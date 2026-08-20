from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import MealPlanForm
from .models import MealPlan, MealPlanRecipe
from recipebook.models import User, Recipe, Dish, Label, Ingredient
from collections import defaultdict
import random
from django.db.models import Q

# Create your views here.

# For a balanced meal plan
REQUIRED_CATEGORIES = {'carbohydrate', 'protein', 'vegetables'}
# Group recipes by their covered categories
CATEGORY_GROUPS = {
                'carbohydrate': [],
                'protein': [],
                'vegetables': [],
                'carbohydrate+protein': [],
                'carbohydrate+vegetables': [],
                'protein+vegetables': [],
                'carbohydrate+protein+vegetables': [],
            }
MEAL_DICTIONARY = {
        'Monday': {'lunch': [], 'dinner': []},
        'Tuesday': {'lunch': [], 'dinner': []},
        'Wednesday': {'lunch': [], 'dinner': []},
        'Thursday': {'lunch': [], 'dinner': []},
        'Friday': {'lunch': [], 'dinner': []},
        'Saturday': {'lunch': [], 'dinner': []},
        'Sunday': {'lunch': [], 'dinner': []},
    }

# Helper functions for generate_mealplan
def get_recipe_categories(recipe):
    """Return the set of required categories (carbohydrate, protein, vegetables) for a recipe."""
    return set(recipe.dish.values_list('dish_name', flat=True)) & REQUIRED_CATEGORIES

def covers_categories(meal_ids):
    """Check if a list of meal IDs covers all required categories."""
    covered_categories = set()
    for meal_id in meal_ids:
        if meal_id is None:
            continue
        recipe = Recipe.objects.get(id=meal_id)
        covered_categories.update(get_recipe_categories(recipe))
    return covered_categories >= REQUIRED_CATEGORIES

def generate_mealplan(request):
    if request.method == 'POST':
        form = MealPlanForm(request.POST)
        if form.is_valid():
            # Generate the meal plan based on user preferences
            generation_type = form.cleaned_data['generation_type']
            labels = form.cleaned_data.get('label', [])
            include_leftovers = form.cleaned_data.get('include_leftovers', False)
            just_one_day = form.cleaned_data.get('just_one_day', False)

            # Allow anonymous users
            meal_plan = MealPlan.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key if not request.user.is_authenticated else None,
            )

            # Base queryset for recipes
            recipes = Recipe.objects.all()

            # Get recipes based on the generation type
            if generation_type == 'ingredients':
                # Filter recipes based on selected ingredients
                available_ingredients = form.cleaned_data.get('available_ingredients', [])
                use_only_available = form.cleaned_data.get('use_only_available', False)

                if available_ingredients:
                    # Filter per recipes that use available ingredients
                    recipes = Recipe.objects.filter(ingredient__in=available_ingredients).distinct()
                    if use_only_available:
                        # Exclude recipes that have ingredients NOT in the selected list
                        recipes = recipes.exclude(ingredient__in=Ingredient.objects.exclude(id__in=available_ingredients)).distinct()

            # Apply label filter with AND logic (with "if labels" it would have been OR logic)
            label_ids = [label.id for label in labels] # labels = [<Label: vegan>, <Label: vegetarian>, <Label: gluten-free>]
            for label_id in label_ids:
                if label_id == 2: # if vegetarian (label=2), include also vegan (label=1) -> OR logic
                    recipes = recipes.filter(Q(label__id=1) | Q(label__id=2))
                else:
                    recipes = recipes.filter(label__id=label_id)
            recipes = recipes.distinct()

            # Fetch their IDs and shuffle them
            meals_ids = list(recipes.values_list('id', flat=True))
            random.shuffle(meals_ids)

            if just_one_day: # Just one lunch and dinner
                num_meals_to_generate = 2
            else: # if include_leftovers, every dinner is also next day's lunch, except for weekend
                num_meals_to_generate = 10 if include_leftovers else 14

            # Fetch the selected recipes from the database
            recipes = Recipe.objects.filter(id__in=meals_ids)
            # Check if recipes is empty
            if not recipes.exists():
                messages.error(request, "No recipes match your criteria. Please try different filters.")
                return render(request, 'mealplan/mealplan_generation.html', {'form': form})
            # If there are not enough recipes, repeat some to fill the meals
            while len(meals_ids) < num_meals_to_generate:
                meals_ids.extend(random.sample(meals_ids, min(num_meals_to_generate-len(meals_ids), len(meals_ids))))

            # Sort every filtered recipe per categories
            category_groups = CATEGORY_GROUPS.copy()
            for recipe in recipes:
                categories = get_recipe_categories(recipe)
                if not categories:
                    continue  # Skip recipes that don't cover any required category

                category_key = '+'.join(sorted(categories))
                if category_key in category_groups:
                    category_groups[category_key].append(recipe.id)

            meal_dict = MEAL_DICTIONARY.copy() if not just_one_day else {'Today': {'lunch': [], 'dinner': []}}
            if just_one_day:
                # Randomly decide whether to use a single but complete recipe or separate recipes for a meal
                # Lunch
                if category_groups['carbohydrate+vegetables'] and random.choice([True,False]):
                    meal_dict['Today']['lunch'].append(category_groups['carbohydrate+vegetables'].pop())
                else:
                    if category_groups['carbohydrate']:
                        meal_dict['Today']['lunch'].append(category_groups['carbohydrate'].pop())
                    if category_groups['vegetables']:
                        meal_dict['Today']['lunch'].append(category_groups['vegetables'].pop())
                # Dinner - again randomly decide whether single but complete or separate recipes
                if category_groups['protein+vegetables'] and random.choice([True,False]):
                    meal_dict['Today']['dinner'].append(category_groups['protein+vegetables'].pop())
                else: # Otherwise, pick separate protein and vegetables recipes
                    if category_groups['protein']:
                        meal_dict['Today']['dinner'].append(category_groups['protein'].pop())
                    if category_groups['vegetables']:
                        meal_dict['Today']['dinner'].append(category_groups['vegetables'].pop())

            # Weekly meal plan
            else:
                # Generate meals for each day
                for day_index, day_name in enumerate(meal_dict.keys()):
                    # if include_leftovers and it's not Monday or weekend, lunch is the previous day's dinner
                    if include_leftovers and day_index > 0 and day_index < 5:
                        prev_day = list(meal_dict.keys())[day_index - 1]
                        meal_dict[day_name]['lunch'] = meal_dict[prev_day]['dinner'].copy()

                    # If lunch is already set (because include_leftovers), balance dinner accordingly
                    if meal_dict[day_name]['lunch']:
                        lunch_categories = set()
                        for meal_id in meal_dict[day_name]['lunch']:
                            lunch_categories.update(get_recipe_categories(Recipe.objects.get(id=meal_id.id)))

                        remaining_categories = REQUIRED_CATEGORIES - lunch_categories
                        for category_key in sorted(category_groups.keys(), key=lambda x: -len(x.split('+'))):
                            if not category_groups[category_key]:
                                continue # Skip recipes that don't cover any required category
                            recipe_categories = set(category_key.split('+'))
                            if recipe_categories & remaining_categories:
                                meal_dict[day_name]['dinner'].append(category_groups[category_key].pop())
                                remaining_categories -= recipe_categories
                                if not remaining_categories:
                                    break
                        # It could happen that lunch already satisfies all REQUIRED_CATEGORIES, therefore dinner is skipped with the logic above
                        if not meal_dict[day_name]['dinner']:
                            # Then, randomly chose protein or carbohydrate and then a vegetable
                            if random.choice([True,False]):
                                meal_dict[day_name]['dinner'].append(category_groups['protein'].pop())
                            else:
                                meal_dict[day_name]['dinner'].append(category_groups['carbohydrate'].pop())
                            meal_dict[day_name]['dinner'].append(category_groups['vegetables'].pop())

                    else: # Generate both lunch (carbohydrate + vegetables) and dinner (protein + vegetables) - again randomly decide whether single but complete or separate recipes
                        if category_groups['carbohydrate+vegetables'] and random.choice([True,False]):
                            meal_dict[day_name]['lunch'].append(category_groups['carbohydrate+vegetables'].pop())
                        else:
                            if category_groups['carbohydrate']:
                                meal_dict[day_name]['lunch'].append(category_groups['carbohydrate'].pop())
                            if category_groups['vegetables']:
                                meal_dict[day_name]['lunch'].append(category_groups['vegetables'].pop())

                        if category_groups['protein+vegetables'] and random.choice([True,False]):
                            meal_dict[day_name]['dinner'].append(category_groups['protein+vegetables'].pop())
                        else:
                            if category_groups['protein']:
                                meal_dict[day_name]['dinner'].append(category_groups['protein'].pop())
                            if category_groups['vegetables']:
                                meal_dict[day_name]['dinner'].append(category_groups['vegetables'].pop())

            # Save the meal plan with lunch and dinner distinctions
            position = 1
            for day_name in meal_dict.keys():
                for meal_type in ['lunch', 'dinner']:
                    for recipe_id in meal_dict[day_name][meal_type]:
                        recipe = Recipe.objects.get(id=recipe_id)
                        MealPlanRecipe.objects.create(
                            meal_plan=meal_plan,
                            recipe=recipe,
                            position=position,
                            meal_type=meal_type,
                            day=day_name,
                        )
                        position += 1

            return redirect('mealplan_result', meal_plan_id=meal_plan.id)
    else:
        form = MealPlanForm()

    return render(request, 'mealplan/mealplan_generation.html', {'form': form})

def mealplan_result(request, meal_plan_id):
    meal_plan = get_object_or_404(MealPlan, id=meal_plan_id)
    # Determine if it is a single-day or weekly
    just_one_day = meal_plan.meal_plan_recipes.count() == 2
    # Reconstruct meal_dict ## poi controlla se non ti stampa meal_dict più volte perché ora quando refresho duplica la lista. però effettivamente perché dovrei refreshare la stessa pagina
    meal_dict = MEAL_DICTIONARY.copy() if not just_one_day else {'Today': {'lunch': [], 'dinner': []}}
    for meal_plan_recipe in meal_plan.meal_plan_recipes.all().order_by('position'):
        meal_type = meal_plan_recipe.meal_type
        meal_dict[meal_plan_recipe.day][meal_type].append(meal_plan_recipe.recipe) if not just_one_day else meal_dict['Today'][meal_type].append(meal_plan_recipe.recipe)

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

    return render(request, 'mealplan/result.html', {
        'meal_plan': meal_plan,
        'meal_dict': meal_dict,
        'grocery_list': grocery_list,
        'just_one_day': just_one_day
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

@login_required ## of course this is still to do
def user_mealplan(request):
    #meal_plan = get_object_or_404(MealPlan, id=meal_plan_id)
    #user = get_object_or_404(User, username=username)
    return render(request, 'mealplan/user_mealplan.html', {
        #'username': user
        #'meal_plan': meal_plan,
    })