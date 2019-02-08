from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template import loader

from .models import Ingredient, Dish, Recipe, Fridge, recipe_finder
from .forms import NewIngredient


def index(request):
    current_user = request.user
    fridge_ing = Fridge.objects.filter(user_id = current_user.id, is_available = True).select_related('ingredient')
    available_dish_id = recipe_finder(current_user)
    dish_list = [Dish.objects.get(id=i['id']) for i in available_dish_id]
    context = {
        'user': current_user,
        'ing_list': fridge_ing,
        'dish_list': dish_list,
    }
    return render(request, 'home.html', context)


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


def catalog_ingredient(request):
    if request.method == 'POST':
        form = NewIngredient(request.POST)
        if form.is_valid():
            ing = Ingredient(name=form.cleaned_data['name'], units=form.cleaned_data['units'], description=form.cleaned_data['description'])
            ing.save()
    else:
        form=NewIngredient()

    ing_list = Ingredient.objects.all()
    template = loader.get_template('ingredient_catalog.html')
    context = {
        'ingredients_list': ing_list,
        'form': form,
    }
    return HttpResponse(template.render(context, request))


def catalog_recipe(request):
    dish_list = Dish.objects.all()
    context = {
        'dish_list': dish_list,
    }
    return render(request, 'catalog.html', context)