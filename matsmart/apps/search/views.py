from django.shortcuts import render, redirect

from ..recipes.models import Ingredient, RecipeIngredientMap, Recipe
from .models import *

from ..recipes.views import get_favorite_count, get_comment_count

def list_all_recipes_matching_query(request):
    """
    Send all RecipeIngredientMap entries matching the query to search.html
    """

    encountered_errors = False

    filter_category_strings = None
    filter_categories       = None
    all_categories       = Category.objects.all()
    all_category_strings = [category.name for category in all_categories]

    query_args = request.GET.items()

    query_string = None
    for argument in query_args:
        if argument[0] == 'q' and query_string == None:
            query_string = argument[1]
        elif argument[0] == 'c' and filter_category_strings == None:
            filter_category_strings = argument[1].split(',')

            filter_categories = []

            for category_string in filter_category_strings:
                category = Category.objects.get(name__iexact=category_string)

                if category != None: filter_categories.append(category)
                else:
                    encountered_errors = True
                    break
        else:
            encountered_errors = True
        if encountered_errors: break

    if encountered_errors: return redirect('/søk')
    else:
        if query_string == None:
            queried_recipes = Recipe.objects.all()
            query_string = ''
        else:
            queried_recipes = Recipe.objects.filter(name__icontains = query_string)

        if filter_category_strings != None:
            category_map = CategoryRecipeMap.objects.all()

            for category in filter_categories:
                category_map = category_map.filter(category = category)

            queried_recipes = queried_recipes.filter(
                recipe__in = category_map.values('recipe')
            )

        return render(request, "search.html", {
            "filter_categories": filter_category_strings,
            "all_categories": all_category_strings,
            "recipes": queried_recipes,
            "favorite_count": get_favorite_count(queried_recipes),
            "comment_count": get_comment_count(queried_recipes)
        })
