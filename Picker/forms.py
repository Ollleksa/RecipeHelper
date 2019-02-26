from django import forms

from .models import Dish, Ingredient, Recipe

class NewIngredient(forms.Form):
    name = forms.CharField(max_length = 40)
    units = forms.CharField(max_length=10)
    description = forms.CharField(widget=forms.Textarea(attrs = {'rows': 10, 'cols': 80}))


class AddIngredient(forms.Form):
    choises = [tuple([x.id, x.name]) for x in Ingredient.objects.all()]
    ingredient = forms.CharField(widget=forms.Select(choices=choises))


class NewDish(forms.Form):
    name = forms.CharField(max_length = 100)
    #ingredients = forms.MultipleChoiceField(models.ingredient_for_choice())
    description = forms.CharField(widget=forms.Textarea(attrs = {'rows': 10, 'cols': 80}))


class DishForm(forms.Form):
    choises = [tuple([x.id, x.name]) for x in Ingredient.objects.all()]
    ingredient = forms.CharField(widget = forms.Select(choices = choises))
    amount = forms.DecimalField(max_digits = 10, decimal_places = 1)
