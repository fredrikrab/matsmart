from django.test import TestCase
from django.test import Client
from html.parser import HTMLParser
from django.contrib.auth.models import User
from apps.recipes.models import Ingredient, Recipe, RecipeIngredientMap
from apps.search.models import Category, CategoryRecipeMap

class SearchResultParser(HTMLParser):
    recipes            = None
    encountered_errors = False
    in_recipe_a        = False
    recipe_name        = None

    def handle_starttag(self, tag, attribs):
        if tag == "a" and len(attribs) != 0 and attribs[0][0] == "class" and attribs[0][1] == "recipe-name-a":
            if self.in_recipe_a:
                print("nested recipe name")
                encountered_errors = True
            else:
                self.in_recipe_a = True

    def handle_data(self, data):
        self.recipe_name = data

    def handle_endtag(self, tag):
        if self.in_recipe_a:
            if self.recipe_name == None:
                print("missing recipe name")
                encountered_errors = True
            else:
                self.recipes.append(self.recipe_name)
                self.in_recipe_a = False

    def parse(self, content):
        self.recipes            = []
        self.encountered_errors = False
        self.in_recipe_a        = False
        self.recipe_name        = None

        self.feed(content)

        if self.in_recipe_a:
            print("unterminated recipe name")
            self.encountered_errors = True

        return self.recipes if not(self.encountered_errors) else None

class TestSearch(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(id=2)
        Ingredient.objects.create(name = 'nudler')
        Ingredient.objects.create(name = 'gulrot')
        Ingredient.objects.create(name = 'beinmarg')
        Ingredient.objects.create(name = 'laks')
        Ingredient.objects.create(name = 'vann')

        Recipe.objects.create(name = 'sushi')
        Recipe.objects.create(name = 'wok', description = "ape")
        Recipe.objects.create(name = 'suppe')

        RecipeIngredientMap.objects.create(
            recipe = Recipe.objects.get(name = 'sushi'),
            ingredient = Ingredient.objects.get(name = 'laks')
        )
        RecipeIngredientMap.objects.create(
            recipe = Recipe.objects.get(name = 'wok'),
            ingredient = Ingredient.objects.get(name = 'gulrot')
        )
        RecipeIngredientMap.objects.create(
            recipe = Recipe.objects.get(name = 'wok'),
            ingredient = Ingredient.objects.get(name = 'vann')
        )
        RecipeIngredientMap.objects.create(
            recipe = Recipe.objects.get(name = 'wok'),
            ingredient = Ingredient.objects.get(name = 'nudler')
        )
        RecipeIngredientMap.objects.create(
            recipe = Recipe.objects.get(name = 'suppe'),
            ingredient = Ingredient.objects.get(name = 'vann')
        )
        RecipeIngredientMap.objects.create(
            recipe = Recipe.objects.get(name = 'suppe'),
            ingredient = Ingredient.objects.get(name = 'beinmarg')
        )
        RecipeIngredientMap.objects.create(
            recipe = Recipe.objects.get(name = 'suppe'),
            ingredient = Ingredient.objects.get(name = 'laks')
        )

        cls.client = Client()

    def ExpectRecipes(self, url, recipes):
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)

        result_parser = SearchResultParser()
        resulting_recipe_names = result_parser.parse(str(response.content))

        resulting_recipe_names.sort()
        recipes.sort()

        self.assertEquals(resulting_recipe_names, recipes)

    def test_EmptyQueryGivesAllEntries(self):
        self.ExpectRecipes('/søk/', [recipe.name for recipe in Recipe.objects.all()])

    def test_SushiQueryGivesSushi(self):
        self.ExpectRecipes('/søk/?q=sushi', ['sushi'])

    def test_SQueryGivesSushiAndSuppe(self):
        self.ExpectRecipes('/søk/?q=s', ['sushi', 'suppe'])

    def test_WQueryGivesWok(self):
        self.ExpectRecipes('/søk/?q=w', ['wok'])

    def test_CapsSushiQueryGivesSushi(self):
        self.ExpectRecipes('/søk/?q=SUSHI', ['sushi'])

    def test_CapsSQueryGivesSushiAndSuppe(self):
        self.ExpectRecipes('/søk/?q=S', ['sushi', 'suppe'])

    def test_CapsWQueryGivesWok(self):
        self.ExpectRecipes('/søk/?q=W', ['wok'])
    
    def test_BogusQueryGivesNothing(self):
        self.ExpectRecipes('/søk/?q=bacdef', [])

    def test_ApeQueryGivesWokByDescription(self):
        self.ExpectRecipes("/søk/?q=ape", ["wok"])

    def test_LaksQueryGivesSuppeAndSushiByIngredients(self):
        self.ExpectRecipes("/søk/?q=laks", ["sushi", "suppe"])
