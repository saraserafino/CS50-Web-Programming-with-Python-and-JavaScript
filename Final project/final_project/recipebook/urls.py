from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_recipe", views.add_recipe, name="add_recipe"),
    path("favourites", views.favourites, name="favourites"),
    path("recipes/<int:id>", views.recipes, name="recipes"),
    path("display_filters", views.display_filters, name="display_filters"),
    path("search/", views.search, name="search"),
    path("random_recipe", views.random_recipe, name="random_recipe"),
    path("edit_recipe/<int:post_id>", views.edit_recipe, name="edit_recipe"),
]

# Ensures that media files are served during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)