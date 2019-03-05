from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse_lazy
from django.db import models
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied

from .models import Ingredient, Dish, Recipe, Fridge, recipe_finder, recipe_finder_session
from .forms import NewIngredient, NewDish, DishForm, AddIngredient


def index(request):
    """
    Creation view for home page.
    :param request: Django request
    :return: Django HttpResponse.
    """
    current_user = request.user
    if current_user.is_authenticated:
        # get ingredients from users fridge for creating view
        fridge_ing = Fridge.objects.filter(user_id = current_user.id, is_available = True).select_related('ingredient')

        if request.method == 'POST':
            # check for POST called from deletion. Post send ingredient_id in name
            is_deleted = False
            for temp in fridge_ing:
                if str(temp.ingredient_id) in request.POST:
                    temp.is_available = False
                    temp.save()
                    form = AddIngredient()
                    is_deleted = True
                    break

            # else check for submitting new ingredient for fridge
            if not is_deleted:
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

            # calls one more time for updating ingredient list
            fridge_ing = Fridge.objects.filter(user_id=current_user.id, is_available=True).select_related('ingredient')
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
    else: #for anonymous user (Logic same as above)
        ing_re = request.session.setdefault('ing_re', [])
        ing_list = [Ingredient.objects.get(id=i) for i in request.session['ing_re']]
        if request.method == 'POST':
            is_deleted = False
            for temp in request.session['ing_re']:
                if str(temp) in request.POST:
                    s = request.session['ing_re']
                    s.remove(temp)
                    print("Lefted", s)
                    request.session['ing_re'] = s
                    form = AddIngredient()
                    is_deleted = True
                    break

            if not is_deleted:
                form = AddIngredient(request.POST)
                if form.is_valid():
                    ing_id = form.cleaned_data['ingredient'].id
                    request.session['ing_re'] = ing_re + [ing_id,]

            ing_list = [Ingredient.objects.get(id=i) for i in request.session['ing_re']]
        else:
            form = AddIngredient()

        dish_ids = recipe_finder_session(request.session)
        dish_list = [Dish.objects.get(id=i['id']) for i in dish_ids]
        context = {
            'user': request.session,
            'ing_list': ing_list,
            'dish_list': dish_list,
            'form': form,
        }

    template = loader.get_template('home.html')
    return HttpResponse(template.render(context, request))


def ing(request, ingredient_id):
    """
    View for single ingredient.
    :param request: Django request
    :param ingredient_id: pk of ingredient
    :return: Django HttpResponse
    """
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
    """
    View for single dish. Use forms for configuring ingredients.
    :param request: Django request
    :param dish_id: pk of dish
    :return: Django HttpResponse
    """
    try:
        rec = Dish.objects.get(pk=dish_id)
    except Dish.DoesNotExist:
        raise Http404("There is no such recipe.")

    # ingredients list for dish, use Recipe model
    ing_list = Recipe.objects.filter(dish_id=dish_id).select_related('ingredient')
    if request.method == 'POST':
        # check for POST called from deletion. Post send ingredient_id in name
        is_deleted = False
        for temp in ing_list:
            if str(temp.ingredient_id) in request.POST:
                Recipe.objects.filter(pk=temp.pk).delete()
                form = DishForm()
                is_deleted = True
                break

        # Add new ingredients to recipe
        if not is_deleted:
            form = DishForm(request.POST)
            if form.is_valid():
                ing2rec = Recipe(dish_id = dish_id, ingredient_id = form.cleaned_data['ingredient'].id,
                                 amount=form.cleaned_data['amount'])
                ing2rec.save()
        ing_list = Recipe.objects.filter(dish_id=dish_id).select_related('ingredient')
    else:
        form = DishForm()

    # Formating description. \n -> list_item
    html_disctiption ='<ul><li>' + rec.description.replace('\n','</li><li>') + '</li></ul>'
    template = loader.get_template('dish.html')
    context = {
        'dish_name': rec.name,
        'ingredients_list': ing_list,
        'dish_description': html_disctiption,
        'form': form,
    }
    return HttpResponse(template.render(context, request))


def catalog_ingredient(request):
    """
    View for ingredient catalog
    :param request: Django request
    :return: HttpResponse
    """
    ing_list = Ingredient.objects.all().order_by('id')

    # Django paginator (Maybe use direct request to DB?)
    paginator = Paginator(ing_list, 20)
    page = request.GET.get('page')
    product = paginator.get_page(page)

    if request.method == 'POST':
        for temp in product:
            if str(temp.id) in request.POST:
                ing = Ingredient.objects.get(pk=temp.pk)
                try:
                    ing.delete()
                    break
                except models.ProtectedError:
                    # error page
                    return ingredient_error(request, ing)

        ing_list = Ingredient.objects.all().order_by('id')
        paginator = Paginator(ing_list, 20)
        page = request.GET.get('page')
        product = paginator.get_page(page)

    template = loader.get_template('ingredient_catalog.html')
    context = {
        'product': product,
    }
    return HttpResponse(template.render(context, request))

def create_ingredient(request):
    """
    View for creation ingredients
    :param request: Django request
    :return: HttpResponse
    """
    if not request.user.is_staff:
        raise PermissionDenied
    if request.method == 'POST':
        form = NewIngredient(request.POST)
        if form.is_valid():
            ing = Ingredient(name=form.cleaned_data['name'], units=form.cleaned_data['units'],
                             description=form.cleaned_data['description'])
            ing.save()
    else:
        form=NewIngredient()

    template = loader.get_template('create_ingredient.html')
    context = {
        'form': form,
    }
    return HttpResponse(template.render(context, request))

def catalog_recipe(request):
    """
    View for dish catalog
    :param request: Django request
    :return: HttpResponse
    """
    dish_list = Dish.objects.all().order_by('id')

    paginator = Paginator(dish_list, 20)
    page = request.GET.get('page')
    menu = paginator.get_page(page)

    if request.method == 'POST':
        for temp in dish_list:
            if str(temp.id) in request.POST:
                Dish.objects.filter(pk=temp.pk).delete()
                break

        dish_list = Dish.objects.all().order_by('id')
        paginator = Paginator(dish_list, 20)
        page = request.GET.get('page')
        menu = paginator.get_page(page)

    template = loader.get_template('catalog.html')
    context = {
        'menu': menu,
    }
    return HttpResponse(template.render(context, request))

def create_dish(request):
    """
    View page for Dish creation. Ingredients adds after creation.
    :param request: Django request
    :return: HttpResponse
    """
    if not request.user.is_staff:
        raise PermissionDenied
    if request.method == 'POST':
        form = NewDish(request.POST)
        if form.is_valid():
            d = Dish(name=form.cleaned_data['name'], description=form.cleaned_data['description'])
            d.save()
            return HttpResponseRedirect('{}'.format(d.id))
    else:
        form=NewDish()

    template = loader.get_template('create_dish.html')
    context = {
        'form': form,
    }
    return HttpResponse(template.render(context, request))

def ingredient_error(request, ing):
    """
    Error page if somebody want to delete ingredient in use.
    :param request: Django request
    :param ing: ingredient what was deleted
    :return: HttpResponse
    """
    ingredient_name = ing.name
    recipes_list = Recipe.objects.filter(ingredient=ing.id)
    template = loader.get_template('delete_error.html')
    context = {
        "ingredient_name": ingredient_name,
        "recipes_list": recipes_list,

    }
    return HttpResponse(template.render(context,request))
