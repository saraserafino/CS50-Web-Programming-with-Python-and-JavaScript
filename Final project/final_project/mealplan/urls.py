from django.urls import path
from . import views

urlpatterns = [
    path("", views.generate_mealplan, name='generate_mealplan'),
    path('result/<int:meal_plan_id>/', views.mealplan_result, name='mealplan_result'),
    path('save/<int:meal_plan_id>/', views.save_mealplan, name='save_mealplan'),
    path('yourmealplans', views.user_mealplan, name='user_mealplan')
]