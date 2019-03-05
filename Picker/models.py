from django.db import models
from django.contrib.auth.models import User


class Ingredient(models.Model):
    """
    Model for Ingredient
    """
    name = models.CharField(max_length = 40, unique = True)
    units = models.CharField(max_length = 10, default = 'g.')
    description = models.TextField(blank = True, default = '')

    def __str__(self):
        return self.name


class Dish(models.Model):
    """
    Model for Dish. Ingredients not included because of 3NF, they included in 'Recipe' model.
    """
    name = models.CharField(max_length = 100)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Model for connecting Dishes and Ingredients. Use two foreign keys to bind itself to instances.
    Ingredient include in Dish only once.
    """
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits = 10, decimal_places = 1, null = True)

    class Meta:
        unique_together = (('dish', 'ingredient'),)

    def __str__(self):
        des = 'Ingredient {0} from {1}'.format(self.ingredient.name, self.dish.name)
        return des


class Fridge(models.Model):
    """
    Model for user's fridge. Connect user with his ingredients.
    is_available is used to not generate high PrimaryKey and reuse DB instance.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    is_available = models.BooleanField(default = True)

    def __str__(self):
        if not self.is_available:
            insert = 'do not '
        else:
            insert = ''
        description = "Record {0}: User {1} {2}have {3}.".format(self.id, self.user.username, insert, self.ingredient.name)
        return description


def recipe_finder(user):
    """
    Find available recipes for user. Get his fridge from DB.
    :param user: Django user model.
    :return: id-s of available dishes

    Logic: found all dishes that have ingredients which are not in user's fridge. Then subtract it from all dishes.
    """
    recipes = Recipe.objects.exclude(
        ingredient__in = Ingredient.objects.filter(fridge__user__id = user.id, fridge__is_available = True)
    ).values('dish_id')
    dishes = Dish.objects.all().values('id')
    available_dish_id = dishes.difference(recipes)
    return available_dish_id

def recipe_finder_session(session):
    """
    Find available recipes with ingredients added in current session.
    :param session: Django session with ingredients id in attribute 'ing_re'
    :return:  id-s of available dishes

    Logic: found all dishes that have ingredients which are not in user's fridge. Then subtract it from all dishes.
    """
    recipes = Recipe.objects.exclude(ingredient__in=session['ing_re']).values('dish__id')
    dishes = Dish.objects.all().values('id')
    available_dish_id = dishes.difference(recipes)
    return available_dish_id