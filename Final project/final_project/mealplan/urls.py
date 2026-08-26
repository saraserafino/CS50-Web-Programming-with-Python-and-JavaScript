from django.urls import path
from . import views

urlpatterns = [
    path("", views.generate_mealplan, name='generate_mealplan'),
    path('result/<int:meal_plan_id>/', views.mealplan_result, name='mealplan_result'),
    path('update_positions/', views.update_positions, name='update_positions'),
    path('save/<int:meal_plan_id>/', views.save_mealplan, name='save_mealplan'),
    path('your_mealplans', views.user_mealplans, name='user_mealplans'),
    path("delete_mealplan/<int:meal_plan_id>", views.delete_mealplan, name='delete_mealplan')
]