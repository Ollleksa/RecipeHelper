from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ingredient/<int:ingredient_id>/', views.ing, name='ing'),
    path('ingredient/', views.catalog_ingredient, name='ing_cat'),
    path('recipe/<int:dish_id>/', views.recipe, name='recipe'),
    path('recipe/', views.catalog_recipe, name='catalog'),
]
