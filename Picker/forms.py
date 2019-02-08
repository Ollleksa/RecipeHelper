from django import forms

from . import models

class NewIngredient(forms.Form):
    name = forms.CharField(max_length = 40)
    units = forms.CharField(max_length=10)
    description = forms.CharField()

class NewDish(forms.Form):
    name = forms.CharField(max_length = 100)
    #ingredients = forms.MultipleChoiceField(models.ingredient_for_choice())
    description = forms.CharField()
