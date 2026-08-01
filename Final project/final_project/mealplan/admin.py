from django.contrib import admin
from django import forms
from .models import MealPlan, MealPlanRecipe

# Register your models here.
admin.site.register(MealPlan)
admin.site.register(MealPlanRecipe)