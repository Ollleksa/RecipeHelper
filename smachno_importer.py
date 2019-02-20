import requests
import re

from Picker.models import Dish, Recipe, Ingredient

def get_site_content(url):
    r = requests.get(url)
    text_n = r.text[r.text.find('<title>')+len('<title>'):]
    name = text_n[:text_n.find('</title>')]
    ing_str = '<table border="0" class="content_post_ingridients">'
    ing_position = text_n.find(ing_str) + len(ing_str)
    recipe_str = '<div class="kd-io-article-body"'
    recipe_position = text_n.find(recipe_str) + len(recipe_str)
    end_str = '<p><a class="likeBlock"'
    end_position = text_n.find(end_str)
    ingredients = text_n[ing_position:recipe_position]
    recipe = text_n[recipe_position:end_position]

    final_recipe = recipe_post_prod(recipe)
    final_ingredients = ingredient_post_prod(ingredients)
    print(name)
    print('=' * 120)
    print(final_ingredients)
    print('='*120)
    print(final_recipe)
    return (name, final_recipe, final_ingredients)


def recipe_post_prod(str):
    reipe = ''
    temp = str
    while 1:
        pos = temp.find('<li>') + len('<li>')
        end = temp.find('</li>')
        if pos == -1 or end == -1:
            break
        reipe += temp[pos:end] + '\n'
        temp = temp[end+5:]

    reipe = re.sub("<.*?>", "", reipe)
    return reipe

def ingredient_post_prod(str):
    ingredients = []
    while 1:
        pos = str.find('<tr i-name="') + len('<tr i-name="')
        pos1 = str.find('" i-amount="')
        pos2 = str.find('" i-measurement="')
        end = str.find('"><td')
        if end == -1 or pos == -1:
            break
        name = str[pos:pos1]
        amount = str[pos1+len('" i-amount="'):pos2]
        units = str[pos2+len('" i-measurement="'):end]
        ingredients.append((name, amount, units))
        str = str[end+6:]
    return ingredients

def db_writing(urls):
    for url in urls:
        (name, recipe, ingredients) = get_site_content(url)
        print(name, recipe, ingredients)
        pk = new_dish(name, recipe)
        print('$'*80)
        print(pk)
        if pk == None:
            continue
        new_ingredients = add_ingredients(ingredients)
        connect_ing_dish(pk, new_ingredients)

def add_ingredients(ingredients):
    new_ingredients = []
    for ing in ingredients:
        try:
            get_ing = Ingredient.objects.get(name = ing[0])
            pk = get_ing.pk
        except Ingredient.DoesNotExist:
            new_ing = Ingredient(name = ing[0], units = ing[2])
            new_ing.save()
            pk = new_ing.pk
        new_ingredients.append((pk, ing[1]))

    return new_ingredients

def new_dish(name, recipe):
    try:
        get_dish = Dish.objects.get(name = name)
        print(get_dish.pk)
        return None
    except Dish.DoesNotExist:
        new_dish = Dish(name = name, description = recipe)
        new_dish.save()
        return new_dish.pk


def connect_ing_dish(pk, ingredients):
    for ing in ingredients:
        try:
            a = float(ing[1])
        except ValueError:
            if '/' in ing[1]:
                a = float(ing[1][0])/float(ing[1][-1])
            else:
                a = 0
        finally:
            new = Recipe(dish_id = pk, ingredient_id = ing[0], amount = a)
            new.save()

get_site_content('https://smachno.ua/ua/recepty/salaty/salat-ko-dnyu-svyatogo-valentina/')
get_site_content('https://smachno.ua/ua/recepty/osnovnye-blyuda/ragu-iz-zamorozhennyh-ovoshhej/')