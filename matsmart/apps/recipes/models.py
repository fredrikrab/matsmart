from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.urls import reverse
from apps.profiles.models import UserProfile

class Recipe(models.Model):
    # Database model for a recipe.

    # Name of recipe
    name = models.CharField('Recipe name', max_length=100)

    # Text description of recipe
    description = models.TextField('Description', null=True, blank=True)

    # Image of recipe
    # Stores the URL to the image. Uses a default value if not provided.
    image = models.ImageField('Image', upload_to='recipe/', default='recipe/placeholder.jpg')
    
    # Cooking instructions
    method = models.TextField('Description', null=True, blank=True)

    # The user account who created the recipe
    # Deleting the user account will also delete the recipe.
    user = models.ForeignKey(User, verbose_name='Created by user', on_delete=models.CASCADE, default=2)

    # Date and time recipe was created
    created_on = models.DateTimeField('Time of creation', auto_now_add=True)

    # Date and time recipe was last updated
    updated_on = models.DateTimeField('Time of last update', auto_now=True)
    
    # True if recipe is a sponsored entry
    sponsored = models.BooleanField(default=False)

    # User who favorited this post
    favorites = models.ManyToManyField(User, 'favorite', default=None, blank=True)

    def get_absolute_url(self):
        return reverse("recipes:view", kwargs={"id": self.id})

    def get_edit_url(self):
        return reverse("recipes:edit", kwargs={"id": self.id})

    def get_ingredients(self):lagtlagtlagt
        queryset = RecipeIngredientMap.objects.filter(recipe_id=self.id).select_related('ingredient')
        return Ingredient.objects.filter(id__in=queryset)

    def get_ingredients_and_amounts(self):
        return RecipeIngredientMap.objects.filter(recipe_id=self.id).select_related('ingredient')
    
    def get_sponsor(self):
        sponsor = get_object_or_404(RecipeSponsor, recipe_id=self.id)
        return sponsor.name

    def delete_self(self):
        return reverse("recipes:delete", kwargs={"id": self.id})

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    # Database model for an ingredient (which subsequently can be used in one or more recipes).

    # Name of ingredient
    # Used as primary key to avoid duplicates.
    name = models.CharField('Ingredient', max_length=100, unique=True, blank=False, null=False)

    def get_amount(self, recipe):
        obj = get_object_or_404(RecipeIngredientMap, ingredient=self, recipe=recipe)
        return obj.amount

    def __str__(self):
        return self.name

class RecipeIngredientMap(models.Model):
    """
    Many-to-many table which maps recipes and ingredients.
    Used for finding all ingredients in a recipe or all recipes containing an ingredient.

    Contains an "amount" field which specifies how much of an ingredient is associated with a recipe.

    We can divide "amount" into two parts ("quantity" and "unit") for additional detail.
    For now, amount is simply a text field for simplicity.
    """

    # Linked recipe
    recipe = models.ForeignKey(Recipe, verbose_name="Recipe", on_delete=models.CASCADE)

    # Linked ingredient
    ingredient = models.ForeignKey(Ingredient, verbose_name="Ingredient", on_delete=models.CASCADE)

    # Amount of ingredient in recipe
    amount = models.CharField('Amount of ingredient', max_length=30, null=True)

    def get_absolute_url(self):
        return self.recipe.get_absolute_url()

    def __str__(self):
        if self.amount:
            return f"{self.recipe}: {self.amount} {self.ingredient}"
        else:
            return f"{self.recipe}: {self.ingredient}"

class Comment(models.Model):
    recipe = models.ForeignKey(Recipe,
                               on_delete=models.CASCADE,
                               related_name='comments')
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='comments')
    content = models.TextField()
    publish = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('publish',)

    def __str__(self):
        return f'Comment by {self.user}'
    
    def delete_self(self):
        return reverse("recipes:delete_comment", kwargs={"id": self.id})

    def __str__(self):
        return f'Comment by {self.user}'


class RecipeSponsor(models.Model):
    """
    Sponsored recipes and their sponsors
    """
    
    # Linked recipe
    recipe = models.OneToOneField(Recipe, verbose_name="Recipe", on_delete=models.CASCADE)
    
    # Name of recipe
    name = models.CharField('Sponsor name', max_length=100)
