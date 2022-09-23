from django.contrib import admin

# Register your models here.
from .models import *

class RecipeInline(admin.TabularInline):
    model = RecipeIngredientMap

class RecipeSponsorInline(admin.TabularInline):
    model = RecipeSponsor

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [RecipeInline, RecipeSponsorInline]

admin.site.register(Ingredient)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("recipe", "user", "publish")
    list_filter = ("recipe", "user", "publish")
    search_fields = ("recipe", "user", "content")
