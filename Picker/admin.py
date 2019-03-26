from django.contrib import admin
from .models import Dish, Ingredient, Recipe, Fridge, DishCategory, IngredientCategory, Unit

admin.site.register(Dish)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(Fridge)

admin.site.register(DishCategory)
admin.site.register(IngredientCategory)
admin.site.register(Unit)