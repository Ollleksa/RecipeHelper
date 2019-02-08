from django.db import models
from django.contrib.auth.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length = 40, unique = True)
    units = models.CharField(max_length = 10)
    description = models.TextField(blank = True, default = '')

    def __str__(self):
        return self.name

def ingredient_for_choice():
    d = [(ing.id, ing.name) for ing in Ingredient.objects.all()]
    return d


class Dish(models.Model):
    name = models.CharField(max_length = 100)
    description = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits = 10, decimal_places = 1, null = True)

    class Meta:
        unique_together = (('dish', 'ingredient'),)

    def __str__(self):
        des = 'Ingredient {0} from {1}'.format(self.ingredient.name, self.dish.name)
        return des


class Fridge(models.Model):
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
