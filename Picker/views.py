from django.http import HttpResponse, Http404
from django.shortcuts import render

from .models import Ingredient, Dish, Recipe


def index(request):
    return HttpResponse("Hello, world.")


def ing(request, ingredient_id):
    try:
        ingerdient = Ingredient.objects.get(pk=ingredient_id)
    except Ingredient.DoesNotExist:
        raise Http404("There is no such ingredient.")
    context = {
        'ing_name': ingerdient.name,
        'ing_description': ingerdient.description,
    }
    return render(request, 'ingredient.html', context)


def recipe(request, dish_id):
    try:
        rec = Dish.objects.get(pk=dish_id)
    except Dish.DoesNotExist:
        raise Http404("There is no such recipe.")

    ing_list = Recipe.objects.filter(dish_id = dish_id).select_related('ingredient')
    context = {
        'dish_name': rec.name,
        'ingredients_list': ing_list,
        'dish_description': rec.description,
    }
    return render(request, 'dish.html', context)
