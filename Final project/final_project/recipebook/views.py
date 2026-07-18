from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import random
from django.db.models import Q

from .models import User, Dish, Label, Ingredient, Recipe, RecipeIngredient, MealPlan

# Create your views here.
def index(request):
    dishes = Dish.objects.all()
    labels = Label.objects.all()
    recipes = Recipe.objects.all()
    return render(request, "recipebook/index.html", {
        "dishes": dishes,
        "labels": labels,
        "recipes": recipes,
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "recipebook/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "recipebook/login.html")

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "recipebook/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "recipebook/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "recipebook/register.html")

@login_required
def add_recipe(request):
    if request.method == "GET":
        all_dishes = Dish.objects.all()
        all_labels = Label.objects.all()
        all_ingredients = Ingredient.objects.all()
        return render(request, "recipebook/add_recipe.html", {
            "dishes": all_dishes,
            "labels": all_labels,
            "ingredients": all_ingredients
        })
    else: # == "POST"
        # Get data from the form in bookrecipe/add_recipe.html
        title = request.POST["title"]
        procedure = request.POST["procedure"]
        is_new = request.POST.get("is_new", False) == "on"
        base_portion = int(request.POST["base_portion"])
        url = request.POST["url"]
        if url:
            new_recipe = Recipe(
                title = title,
                procedure = procedure,
                url = url,
                is_new = is_new,
                base_portion = base_portion
            )
        else:
            image = request.FILES.get("image")
            new_recipe = Recipe(
                title = title,
                procedure = procedure,
                image = image,
                is_new = is_new,
                base_portion = base_portion
            )
        new_recipe.save()

        # Handle many-to-many fields of dishes and labels
        dishes = request.POST.getlist("dish")
        labels = request.POST.getlist("label")

        for dish_id in dishes:
            dish = Dish.objects.get(pk=dish_id)
            new_recipe.dish.add(dish)
        for label_id in labels:
            label = Label.objects.get(pk=label_id)
            new_recipe.label.add(label)

        # Handle ingredients
        ingredient_quantities = request.POST.getlist("ingredient_quantity[]")
        ingredient_units = request.POST.getlist("ingredient_unit[]")
        ingredient_names = request.POST.getlist("ingredient_name[]")

        for quantity, unit, name in zip(ingredient_quantities, ingredient_units, ingredient_names):
            ingredient, created = Ingredient.objects.get_or_create(ingredient_name=name)
            RecipeIngredient.objects.create(
                recipe=new_recipe,
                ingredient=ingredient,
                quantity=float(quantity),
                unit=unit
            )

        # Redirect to the page of the created recipe
        return render(request, "recipebook/recipes.html", {
        "recipes": new_recipe,
        })

@login_required
def favourites(request):
    favourites = request.user.favourites.all()
    return render(request, "recipebook/favourites.html", {
        "favourites": favourites,
    })

# Display a recipe
def recipes(request, id):
    recipes_data = Recipe.objects.get(pk=id)
    is_fav = request.user in recipes_data.favourites.all()
    if request.method == "POST":
        if is_fav: # Remove from favourites
            recipes_data.favourites.remove(request.user)
        else: # Add to favourites
            recipes_data.favourites.add(request.user)
    # Update the status
    is_fav = request.user in recipes_data.favourites.all()
    return render(request, "recipebook/recipes.html", {
        "recipes": recipes_data,
        "is_fav": is_fav
    })

# Display filtered recipes
def display_filters(request):
    all_dishes = Dish.objects.all()
    all_labels = Label.objects.all()
    # Default: all recipes, which is also base queryset for the filters
    recipes = Recipe.objects.all()
    # Filter recipes from list of possible multiple IDs
    if request.method == "POST" or request.method == "GET":
        dish_ids = request.POST.getlist("dish") if request.method == "POST" else request.GET.getlist("dish")
        label_ids = request.POST.getlist("label") if request.method == "POST" else request.GET.getlist("label")
        # Convert string IDs to integers
        dish_ids = [int(id) for id in dish_ids] if dish_ids else []
        label_ids = [int(id) for id in label_ids] if label_ids else []
        if dish_ids:
            recipes = recipes.filter(dish__id__in=dish_ids)
        if label_ids:
            recipes = recipes.filter(label__id__in=label_ids)
        # Avoid duplicates if multiple filters match the same recipe
        recipes = recipes.distinct()

    return render(request, "recipebook/index.html", {
        "recipes": recipes,
        "dishes": all_dishes,
        "labels": all_labels
    })

# Function for searching a recipe
def search(request):
    query = request.GET.get("q", "").strip()
    if not query: # If no query, return all recipes
        recipes = Recipe.objects.all()
    else:
        # Search for recipes where the title or procedure or ingredients contains the query (i stands for case-insensitive)
        recipes = Recipe.objects.filter(
            Q(title__icontains=query) |
            Q(procedure__icontains=query) |
            Q(recipe_ingredients__ingredient__ingredient_name__icontains=query)
        ).distinct() # distinct() avoids duplicate recipes

    return render(request, "recipebook/search_results.html", {
        "query": query,
        "recipes": recipes,
    })

def random_recipe(request):
    all_recipes = Recipe.objects.all()
    if all_recipes.exists():
        random_recipe = random.choice(all_recipes)
        return redirect('recipes', id=random_recipe.id)
    else: # If no recipes exist, redirect to the index page
        return redirect('index')

@login_required ## Working on this
def edit_recipe(request, recipe_id):
    if request.method == "POST":
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
        except Recipe.DoesNotExist:
            return JsonResponse({"success": False, "error": "Recipe not found."}, status=404)

        # Check if the logged-in user is the owner of the recipe (in realtà voglio fare che solo Prociona può modificare)
        #if request.user == recipe.user:
        new_procedure = request.POST.get("procedure", "").strip()
        if new_procedure:
            recipe.procedure = new_procedure
            recipe.save()
            return JsonResponse({"success": True, "procedure": recipe.procedure})
        else:
            return JsonResponse({"success": False, "error": "Procedure cannot be empty."}, status=400)
        #else:
        #    return JsonResponse({"success": False, "error": "You are not the author of this recipe."}, status=403)

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=400)