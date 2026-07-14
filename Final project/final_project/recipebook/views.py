from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required


from .models import User, Dish, Label, Ingredient, Recipe, RecipeIngredient, MealPlan

# Create your views here.
def index(request):
    return render(request, "recipebook/index.html")

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
def add_recipe(request): ## TO FIX ACCORDINGLY
    if request.method == "GET":
        all_dishes = Dish.objects.all()
        all_labels = Label.objects.all()
        all_ingredients = Ingredient.objects.all()
        return render(request, "recipebook/create.html", {
            "dishes": all_dishes,
            "labels": all_labels,
            "ingredients": all_ingredients
        })
    else: # == "POST"
        # Get data from the form in bookrecipe/create.html
        title = request.POST["title"]
        procedure = request.POST["procedure"]
        ##image = request.POST["image"]
        time_required = int(request.POST["time_required"])
        is_new = request.POST.get("is_new", False) == "on"
        base_portion = int(request.POST["base_portion"])
        # Create a new listing object and insert it in the database
        new_recipe = Recipe(
            title = title,
            procedure = procedure,
            ##image = image,
            time_required = int(time_required),
            favourites = False,
            is_new = is_new,
            base_portion = base_portion
        )
        new_recipe.save()

        # Handle many-to-many fields
        dishes = request.POST.getlist["dish"]
        labels = request.POST.getlist["label"]
        ingredients = request.POST.getlist["ingredient"]

        for dish_id in dishes:
            dish = Dish.objects.get(pk=dish_id)
            new_recipe.dish.add(dish)
        for label_id in labels:
            label = Label.objects.get(pk=label_id)
            new_recipe.label.add(label)
        for ingredient_id in ingredients:
            ingredient = Ingredient.objects.get(pk=ingredient_id)
            new_recipe.ingredient.add(ingredient)

        # Redirect to index page
        return HttpResponseRedirect(reverse(index))