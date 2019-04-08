from django import forms

from .models import Dish, Ingredient, Recipe, Unit

class NewIngredient(forms.Form):
    """
    Form for creating new ingredient:
    1) Description use big TextArea to nice view
    """
    name = forms.CharField(max_length = 40)
    description = forms.CharField(widget=forms.Textarea(attrs = {'rows': 10, 'cols': 80}), required = False)
    energy = forms.DecimalField(required = False)
    proteins = forms.DecimalField(required = False)
    fats = forms.DecimalField(required = False)
    carbohydrate = forms.DecimalField(required = False)

class EditIngredient(forms.Form):
    """
    Form for editing Ingredient after creation.
    """
    name = forms.CharField(max_length = 40)
    description = forms.CharField(widget=forms.Textarea(attrs = {'rows': 10, 'cols': 80}), required = False)
    energy = forms.DecimalField(required=False)
    proteins = forms.DecimalField(required=False)
    fats = forms.DecimalField(required=False)
    carbohydrate = forms.DecimalField(required=False)


class AddIngredient(forms.Form):
    """
    Form for adding ingredient to you fridge on main page
    """
    ingredient = forms.ModelChoiceField(queryset = Ingredient.objects.all())


class NewDish(forms.Form):
    """
    Form for creating new dish (and editing existing):
    1) Description use big TextArea to nice view
    """
    name = forms.CharField(max_length = 100)
    description = forms.CharField(widget=forms.Textarea(attrs = {'rows': 10, 'cols': 80}), required = False)


class DishForm(forms.Form):
    """
    Form for adding ingredient to recipe.
    """
    ingredient = forms.ModelChoiceField(queryset=Ingredient.objects.all())
    amount = forms.DecimalField(max_digits = 10, decimal_places = 1)
    units = forms.ModelChoiceField(queryset=Unit.objects.all())
