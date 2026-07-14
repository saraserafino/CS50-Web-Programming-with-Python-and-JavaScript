from django import forms
from .models import Recipe

# Django's ModelForm automatically generates form fields based on the model
class RecipeForm(forms.ModelForm):
    """Form for the recipe model"""
    class Meta:
        model = Recipe
        fields = ["title", "image"]