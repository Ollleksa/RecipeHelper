from django import forms

from .models import Dish, Ingredient

class NewIngredient(forms.Form):
    name = forms.CharField(max_length = 40)
    units = forms.CharField(max_length=10)
    description = forms.CharField()

class AddIngredient(forms.Form):
    choises = [tuple([x.id, x.name]) for x in Ingredient.objects.all()]
    ingredient = forms.CharField(widget=forms.Select(choices=choises))


class NewDish(forms.Form):
    name = forms.CharField(max_length = 100)
    #ingredients = forms.MultipleChoiceField(models.ingredient_for_choice())
    description = forms.CharField()


class DishForm(forms.Form):
    choises = [tuple([x.id, x.name]) for x in Ingredient.objects.all()]
    ingredient = forms.CharField(widget = forms.Select(choices = choises))
    amount = forms.DecimalField(max_digits = 10, decimal_places = 1)
