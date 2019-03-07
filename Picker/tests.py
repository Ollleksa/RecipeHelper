from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from .models import Ingredient, Dish, Fridge, Recipe
from .forms import AddIngredient

class IngredientModelTest(TestCase):

    def setUp(self):
        Ingredient.objects.create(name = 'Test_ing')

    def test_representation(self):
        new = Ingredient(name = 'Test')
        self.assertEqual(new.name, str(new))

    def test_default(self):
        new = Ingredient(name = 'Test')
        self.assertEqual(new.units, 'g.')
        self.assertEqual(new.description, '')

    def test_unique(self):
        self.assertRaises(IntegrityError, lambda: Ingredient.objects.create(name = Ingredient.objects.all().first().name))



class FreeAccessTest(TestCase):

    def setUp(self):
        self.ing = Ingredient.objects.create(name='Test_ing')
        self.d = Dish.objects.create(name = 'Test_dish')
        self.r = Recipe.objects.create(ingredient = self.ing, dish = self.d, amount = 100)
        self.c = Client()

    def test_homepage(self):
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)

    def test_welcome(self):
        response = self.c.get('/')
        self.assertContains(response, 'Welcome to RecipeHelper!')

    def test_ingredient(self):
        p = '/ingredient/' + str(self.ing.id) + '/'
        response = self.c.get(p)
        self.assertEqual(response.status_code, 200)

    def test_ingredient_catalog(self):
        p = '/ingredient/'
        response = self.c.get(p)
        self.assertContains(response, 'Test_ing')
        text = '<h3>Please click <a href="/ingredient/create">here</a> to create new ingredient.</h3>'
        self.assertNotContains(response, text, html = True)
        self.assertNotContains(response, '<div class ="delButton">', html=True)

    def test_dish_catalog(self):
        p = '/recipe/'
        response = self.c.get(p)
        self.assertContains(response, 'Test_dish')
        text = '<h3>Add new dish <a href="/recipe/create">here</a> </h3>'
        self.assertNotContains(response, text, html=True)
        self.assertNotContains(response, '<div class ="delButton">', html=True)

    def test_dish(self):
        p = '/recipe/' + str(self.d.id) + '/'
        response = self.c.get(p)
        self.assertContains(response, 'Test_dish')
        self.assertContains(response, 'Test_ing')
        text = '<input type="submit" value="Add">'
        self.assertNotContains(response, text, html=True)
        self.assertNotContains(response, '<div class ="delButton">', html=True)

    def test_create_page(self):
        p = '/recipe/create/'
        response = self.c.get(p)
        self.assertEqual(response.status_code, 404)
        p = '/ingredient/create/'
        response = self.c.get(p)
        self.assertEqual(response.status_code, 404) #?


class RegisterAccessTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_superuser('Test_Bender', email = 'test@t.t', password = 'password')
        self.ing = Ingredient.objects.create(name='Test_ing')
        self.d = Dish.objects.create(name = 'Test_dish')
        Recipe.objects.create(ingredient = self.ing, dish = self.d, amount = 100)
        self.c = Client()

    def test_login(self):
        response = self.c.post('/accounts/login/', {'username': 'Test_bender', 'password': 'password'})
        self.assertEqual(response.status_code, 200)

    def test_login_homepage(self):
        self.c.force_login(self.user, backend = 'django.contrib.auth.backends.ModelBackend')
        response = self.c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hi Test_Bender!')

    def test_ingredient_empty(self):
        self.c.force_login(self.user, backend='django.contrib.auth.backends.ModelBackend')
        response = self.c.get('/')
        self.assertContains(response, 'You fridge is empty :(')

    def test_ingredient_form(self):
        ing = Ingredient.objects.all().first()
        form_data = {'ingredient': str(ing.id)}
        form = AddIngredient(data=form_data)
        self.assertTrue(form.is_valid())

    def test_correct_working(self):
        self.c.force_login(self.user, backend='django.contrib.auth.backends.ModelBackend')
        response = self.c.get('/')
        self.assertContains(response, 'You fridge is empty :(')
        Fridge.objects.create(user = self.user, ingredient = self.ing)

        response = self.c.get('/')
        self.assertContains(response, 'Test_ing')
        self.assertContains(response, 'Test_dish')

    def test_ingredient_catalog(self):
        p = '/ingredient/'
        response = self.c.get(p)
        self.assertContains(response, 'Test_ing')
        text = '<h3>Please click <a href="/ingredient/create">here</a> to create new ingredient.</h3>'
        self.assertContains(response, text, html = True)
        self.assertContains(response, '<div class ="delButton">', html=True)

    def test_dish_catalog(self):
        p = '/recipe/'
        response = self.c.get(p)
        self.assertContains(response, 'Test_dish')
        text = '<h3>Add new dish <a href="/recipe/create">here</a> </h3>'
        self.assertContains(response, text, html=True)
        self.assertContains(response, '<div class ="delButton">', html=True)

    def test_dish(self):
        p = '/recipe/' + str(self.d.id) + '/'
        response = self.c.get(p)
        self.assertContains(response, 'Test_dish')
        self.assertContains(response, 'Test_ing')
        text = '<input type="submit" value="Add">'
        self.assertContains(response, text, html=True)
        self.assertContains(response, '<div class ="delButton">', html=True)

    def test_create_page(self):
        p = '/recipe/create/'
        response = self.c.get(p)
        self.assertEqual(response.status_code, 200)
        p = '/ingredient/create/'
        response = self.c.get(p)
        self.assertEqual(response.status_code, 200) #?
