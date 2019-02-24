from Picker.models import Recipe, Dish, Ingredient, Fridge

START_INGREDIENT = ['Яйце', 'Олія',]
S_ID = []

def s():

    env_prep()

    for ing in START_INGREDIENT:
        new_ing = Ingredient(name = ing)
        new_ing.save()
        S_ID.append(new_ing.pk)

    start('./scripts/sample_ingredients.dat')

def start(file):
    with open(file) as f:
        ing = f.readlines()

    for i in ing:
        new_ing = Ingredient(name=i[:-1])
        new_ing.save()

    for i in ing:
        db_writing([i[:-1],])
        for j in ing:
            if i > j:
                db_writing([i[:-1], j[:-1]])

def db_writing(ingredients):
    if len(ingredients) == 1:
        name = 'Яєчня з {}'.format(ingredients[0])
    else:
        name = 'Яєчня з {} і {}'.format(ingredients[0], ingredients[1])

    pk = new_dish(name)
    connect_ing_dish(pk, ingredients)

def new_dish(name):
    new_dish = Dish(name = name)
    print(name)
    new_dish.save()
    return new_dish.pk


def connect_ing_dish(pk, ingredients):
    for i in S_ID:
        new = Recipe(dish_id=pk, ingredient_id=i, amount=200)
        new.save()

    for ing in ingredients:
        new = Recipe(dish_id = pk, ingredient_id = Ingredient.objects.get(name = ing).id, amount = 100)
        print('Adding ', ing)
        new.save()

def env_prep():
    Fridge.objects.all().delete()
    Recipe.objects.all().delete()
    Ingredient.objects.all().delete()
    Dish.objects.all().delete()
