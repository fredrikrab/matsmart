from django.db import models
from ..recipes.models import Recipe

class Category(models.Model):
    # Database model for a search category.

    name = models.CharField('Category name', max_length=100, unique=True)

    def __str__(self):
        return self.name

class CategoryRecipeMap(models.Model):
    # Database model for mapping between search category and recipe.

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
