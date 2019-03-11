from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'), #home page
    path('ingredient/<int:ingredient_id>/', views.ing, name='ing'), #single ingredient page
    path('ingredient/', views.catalog_ingredient, name='ing_cat'), #catalog of ingredients
    path('ingredient/create', views.create_ingredient, name='ing_create'), #ingredient creation page
    path('recipe/<int:dish_id>/', views.recipe, name='recipe'), #single dish page
    path('recipe/', views.catalog_recipe, name='catalog'), #catalog of recipes
    path('recipe/create', views.create_dish, name='dish_create'), #recipe creation page
    path('help/', views.help_page, name='help'), #help page
]
