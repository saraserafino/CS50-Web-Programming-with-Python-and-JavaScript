from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required


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
        image = request.FILES.get("image")
        time_required = int(request.POST["time_required"])
        is_new = request.POST.get("is_new", False) == "on"
        base_portion = int(request.POST["base_portion"])
        # Create a new object and insert it in the database
        new_recipe = Recipe(
            title = title,
            procedure = procedure,
            image = image,
            time_required = int(time_required),
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

        # Redirect to index page ## When you'll create it, redirect to the page of the created recipe
        return HttpResponseRedirect(reverse(index))

@login_required
def favourites(request):
    favourites = request.user.favourites.all()
    return render(request, "recipebook/favourites.html", {
        "favourites": favourites,
    })

# Display recipes
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