from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse_lazy

from .models import Ingredient, Dish, Recipe, Fridge, recipe_finder
from .forms import NewIngredient, NewDish, DishForm, AddIngredient


def index(request):
    current_user = request.user
    fridge_ing = Fridge.objects.filter(user_id = current_user.id, is_available = True).select_related('ingredient')

    if request.method == 'POST':
        for temp in fridge_ing:
            if str(temp.ingredient_id) in request.POST:
                temp.is_available = False
                temp.save()

        form = AddIngredient(request.POST)
        if form.is_valid():
            ing_id = form.cleaned_data['ingredient']
            try:
                k = Fridge.objects.get(user_id = current_user.id, ingredient_id = ing_id)
                k.is_available = True
                k.save()
            except Fridge.DoesNotExist:
                k = Fridge(user_id = current_user.id, ingredient_id = ing_id)
                k.save()
    else:
        form = AddIngredient()

    available_dish_id = recipe_finder(current_user)
    dish_list = [Dish.objects.get(id=i['id']) for i in available_dish_id]
    context = {
        'user': current_user,
        'ing_list': fridge_ing,
        'dish_list': dish_list,
        'form': form,
    }
    template = loader.get_template('home.html')
    return HttpResponse(template.render(context, request))


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

    if request.method == 'POST':
        form = DishForm(request.POST)
        if form.is_valid():
            ing2rec = Recipe(dish_id = dish_id, ingredient_id = form.cleaned_data['ingredient'],
                             amount=form.cleaned_data['amount'])
            ing2rec.save()
    else:
        form = DishForm()

    ing_list = Recipe.objects.filter(dish_id = dish_id).select_related('ingredient')
    template = loader.get_template('dish.html')
    context = {
        'dish_name': rec.name,
        'ingredients_list': ing_list,
        'dish_description': rec.description,
        'form': form,
    }
    return HttpResponse(template.render(context, request))


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
    if request.method == 'POST':
        form = NewDish(request.POST)
        if form.is_valid():
            d = Dish(name = form.cleaned_data['name'], description = form.cleaned_data['description'])
            d.save()
            return HttpResponseRedirect('{}'.format(d.id))
    else:
        form = NewDish()

    dish_list = Dish.objects.all()
    template = loader.get_template('catalog.html')
    context = {
        'dish_list': dish_list,
        'form': form,
    }
    return HttpResponse(template.render(context, request))