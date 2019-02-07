from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ingredient/<int:ingredient_id>/', views.ing, name='ing'),
    path('recipe/<int:dish_id>/', views.recipe, name='recipe'),
]
