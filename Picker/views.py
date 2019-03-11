from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse_lazy
from django.db import models
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied

from .models import Ingredient, Dish, Recipe, Fridge, recipe_finder, recipe_finder_session
from .forms import NewIngredient, NewDish, DishForm, AddIngredient, EditIngredient


def index(request):
    """
    Creation view for home page.
    :param request: Django request
    :return: Django HttpResponse.
    """

    edit = request.GET.get('edit_mode')

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
                    ing_id = form.cleaned_data['ingredient'].id
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
    if edit:
        print('Get')
        template = loader.get_template('base.html')

    return HttpResponse(template.render(context, request))


def ing(request, ingredient_id):
    """
    View for single ingredient.
    :param request: Django request
    :param ingredient_id: pk of ingredient
    :return: Django HttpResponse
    """
    try:
        ingredient = Ingredient.objects.get(pk=ingredient_id)
    except Ingredient.DoesNotExist:
        raise Http404("There is no such ingredient.")

    edit = request.GET.get('edit_mode')

    context = {
        'ing_name': ingredient.name,
        'ing_description': ingredient.description,
    }

    if edit:
        template = loader.get_template('ingredient_edit.html')
        data = {'name': ingredient.name, 'units': ingredient.units, 'description': ingredient.description}
        form = EditIngredient(data)
        if request.method == 'POST':
            form = EditIngredient(request.POST)
            if form.is_valid():
                ingredient.name = form.cleaned_data['name']
                ingredient.units = form.cleaned_data['units']
                ingredient.description = form.cleaned_data['description']
                ingredient.save()
                print('Updated.')
                return HttpResponseRedirect('../{}'.format(ingredient.id))
        context['form'] = form
    else:
        template = loader.get_template('ingredient.html')

    return HttpResponse(template.render(context, request))


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

    edit = request.GET.get('edit_mode')

    # ingredients list for dish, use Recipe model
    ing_list = Recipe.objects.filter(dish_id=dish_id).select_related('ingredient')

    # Formating description. \n -> list_item
    html_disctiption = '<ul><li>' + rec.description.replace('\n', '</li><li>') + '</li></ul>'
    context = {
        'dish_name': rec.name,
        'ingredients_list': ing_list,
        'dish_description': html_disctiption,
    }

    if edit:
        template = loader.get_template('dish_edit.html')
        data = {'name': rec.name, 'description': rec.description}
        form = NewDish(data)
        if request.method == 'POST':
            form = NewDish(request.POST)
            form_ing = DishForm(request.POST)

            for temp in ing_list:
                if 'Delete ' + str(temp.ingredient_id) in request.POST:
                    Recipe.objects.filter(pk=temp.pk).delete()
                    form = DishForm()
                    break

            if form.is_valid():
                rec.name = form.cleaned_data['name']
                rec.description = form.cleaned_data['description']
                rec.save()
                print('Updated.')
                return HttpResponseRedirect('../{}'.format(rec.id))

            if form_ing.is_valid():
                ing2rec = Recipe(dish_id=dish_id, ingredient_id=form_ing.cleaned_data['ingredient'].id,
                                 amount=form_ing.cleaned_data['amount'])
                ing2rec.save()
        else:
            form_ing = DishForm()

        context['form'] = form
        context['form_ing'] = form_ing
        ing_list = Recipe.objects.filter(dish_id=dish_id).select_related('ingredient')
        context['ingredients_list'] = ing_list
    else:
        template = loader.get_template('dish.html')

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

    #edit mode
    edit = request.GET.get('edit_mode')

    if edit and request.method == 'POST':
        for temp in product:
            if ('Delete ' + str(temp.id)) in request.POST:
                ingredient = Ingredient.objects.get(pk=temp.pk)
                try:
                    ingredient.delete()
                    break
                except models.ProtectedError:
                    # error page
                    return ingredient_error(request, ing)

            elif ('Edit ' + str(temp.id)) in request.POST:
                ingredient = Ingredient.objects.get(pk=temp.pk)
                return HttpResponseRedirect('{}?edit_mode=True'.format(ingredient.id))

        ing_list = Ingredient.objects.all().order_by('id')
        paginator = Paginator(ing_list, 20)
        page = request.GET.get('page')
        product = paginator.get_page(page)

    template = loader.get_template('ingredient_catalog.html')
    context = {
        'product': product,
        'edit': edit,
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

    # edit mode
    edit = request.GET.get('edit_mode')

    if edit and request.method == 'POST':
        for temp in dish_list:
            if ('Delete ' + str(temp.id)) in request.POST:
                Dish.objects.filter(pk=temp.pk).delete()
                break
            elif ('Edit ' + str(temp.id)) in request.POST:
                dish = Dish.objects.get(pk=temp.pk)
                return HttpResponseRedirect('{}?edit_mode=True'.format(dish.id))

        dish_list = Dish.objects.all().order_by('id')
        paginator = Paginator(dish_list, 20)
        page = request.GET.get('page')
        menu = paginator.get_page(page)

    template = loader.get_template('catalog.html')
    context = {
        'menu': menu,
        'edit': edit,
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

    i_list = request.session.setdefault('i_list', [])
    ingredients_list = [(Ingredient.objects.get(id=i[0]), i[1]) for i in request.session['i_list']]

    if request.method == 'POST':
        form = NewDish(request.POST)
        form_ing = DishForm(request.POST)

        not_deleted = True
        for temp in request.session['i_list']:
            if 'Delete ' + str(temp[0]) in request.POST:
                s = request.session['i_list']
                s.remove(temp)
                print("Lefted", s)
                request.session['i_list'] = s
                form_ing = DishForm()
                not_deleted = False
                break

        if not_deleted and form_ing.is_valid():
            ing_param = (form_ing.cleaned_data['ingredient'].id, float(form_ing.cleaned_data['amount']))
            i_list = request.session['i_list']
            request.session['i_list'] = i_list + [ing_param,]
        elif not_deleted and form.is_valid():
            d = Dish(name=form.cleaned_data['name'], description=form.cleaned_data['description'])
            d.save()
            for ing in ingredients_list:
                ing2rec = Recipe(dish_id=d.id, ingredient_id=ing[0].id, amount=ing[1])
                ing2rec.save()

            return HttpResponseRedirect('{}'.format(d.id))

        ingredients_list = [(Ingredient.objects.get(id=i[0]), i[1]) for i in request.session['i_list']]
    else:
        form = NewDish()
        form_ing = DishForm()

    template = loader.get_template('create_dish.html')
    context = {
        'form': form,
        'form_ing': form_ing,
        'ingredients_list': ingredients_list,
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

def help_page(request):
    """
    Help page with information
    :param request: Django request
    :return: HttpResponse
    """
    template = loader.get_template('help.html')
    context = {}
    return HttpResponse(template.render(context,request))