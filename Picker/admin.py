from django.contrib import admin
from .models import Dish, Ingredient, Recipe, Fridge

admin.site.register(Dish)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(Fridge)
