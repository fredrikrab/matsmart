from django.contrib.auth.decorators import login_required
from django.db.models import Count, F
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaulttags import register

from apps.search.models import Category, CategoryRecipeMap

from .forms import (CategoryFormSet, IngredientFormSet, NewCommentForm,
                    RecipeForm)
from .models import (Comment, Ingredient, Recipe, RecipeIngredientMap,
                     RecipeSponsor)


@register.filter
def get_count_from_id(count_table, id):
    return count_table.get(id=id)['count']

def get_favorite_count(recipes):
    return recipes.values().annotate(id=F('id'), count=Count('favorites'))

def get_comment_count(recipes):
    return recipes.values().annotate(id=F('id'), count=Count('comments'))

def list_recipes(request, id=None):
    # Send all Recipes entries to list_recipes.html
    # Alternatively send only the Recipe matching the given id

    single_view = False
    comments = None
    user_comment = None
    comment_form = None

    if id:
        recipes = Recipe.objects.filter(id=id)
        single_view = True
        comments = recipes[0].comments.all()
                
        if request.method == 'POST': # TODO: Check AUTH, Only in html at the moment
            comment_form = NewCommentForm(request.POST)
            if comment_form.is_valid():
                user_comment = comment_form.save(commit=False)
                user_comment.recipe = recipes[0]
                user_comment.user = request.user
                user_comment.save()
                return HttpResponseRedirect('/oppskrifter/' + str(recipes[0].id))
        else:
            comment_form = NewCommentForm()

        if recipes.count() == 0:
            raise Http404
    else:
        recipes = Recipe.objects.all().order_by('-id')

    return render(request, "list_recipes.html", {
        "recipes": recipes,
        "single_view": single_view,
        "favorite_count": get_favorite_count(recipes),
        "comment_count": get_comment_count(recipes),
        "comments": comments,
        "user_comment": user_comment,
        "comment_form": comment_form
    })

@login_required
def create_edit_recipe(request, id=None):
    """
    Send RecipeForm and IngredientFormSet to create_edit_recipe.html
    Handle submission of form:
    - Create Recipe entry
    - Create Ingredient entries
    - Create RecipeIngredientMap entries (link each Ingredient to Recipe with optional "amount" attribute)

    TODO: Populate amount fields when editing

    TODO: More robust IngredientFormSet validation

    TODO: Return error message to user if invalid form
    """

    if id:
        recipe = get_object_or_404(Recipe, id=id)
        ingredient_queryset = Ingredient.objects.filter(recipeingredientmap__recipe_id=id).annotate(amount=F('recipeingredientmap__amount'))
    else:
        recipe = None
        ingredient_queryset = Ingredient.objects.none()

    # Get recipe and associated ingredients from database if ID is provided (i.e. editing a recipe)
    # Otherwise use empty Recipe form and Ingredient formset (i.e. creating new recipe)

    if request.method == 'POST':
        # Handle form submission

        recipe_form = RecipeForm(request.POST, request.FILES, instance=recipe)
        ingredient_formset = IngredientFormSet(request.POST, prefix="ingredient")
        category_formset = CategoryFormSet(request.POST, prefix="category")
        sponsored = None

        try:
            sponsored = request.POST['sponsored']
            sponsor_name = request.POST['sponsor']
        except KeyError:
            pass
        """
        Get submitted data
        """

       #  Get submitted data
        if recipe_form.is_valid():
            created_recipe = recipe_form.save(commit=False)
            created_recipe.user = request.user
            created_recipe.save()
            if sponsored:
                created_recipe.sponsored = True
                sponsor = RecipeSponsor(recipe=created_recipe, name=sponsor_name)
                sponsor.save()

            # Iterate through submitted ingredient forms
            for ingredient_form in ingredient_formset:
                if (ingredient_form.has_changed()):
                    ingredient = ingredient_form['name'].value()    # Get form value
                    amount = ingredient_form['amount'].value()      # Get form value

                    # Continue if ingredient text field is empty
                    # This solves the error that occurs when user checks "delete" on an empty form
                    if ingredient == "":
                        continue
                    
                    # Get Ingredient object if it exists
                    if Ingredient.objects.filter(name=ingredient).exists():
                        ingredient = Ingredient.objects.get(name=ingredient)

                        # If delete is toggled, delete RecipeIngredientMap entry and continue
                        if (ingredient_form['DELETE'].value()):
                            RecipeIngredientMap.objects.get(recipe=created_recipe, ingredient=ingredient).delete()
                            continue

                    # Otherwise create new Ingredient object
                    else:
                        if (len(ingredient_form['name'].value()) > 0 and not ingredient_form['DELETE'].value()):
                            ingredient = ingredient_form.save()

                    # Get RecipeIngredientMap entry if it exists
                    if (RecipeIngredientMap.objects.filter(recipe=created_recipe, ingredient=ingredient).exists()):
                        map = RecipeIngredientMap.objects.get(recipe=created_recipe, ingredient=ingredient)

                    # Otherwise create new RecipeIngredientMap entry
                    else:
                        map = RecipeIngredientMap(recipe=created_recipe, ingredient=ingredient)

                    if amount:
                        map.amount = amount

                    map.save()


            # Create CategoryRecipeMap entry
            if category_formset.is_valid():
                for category in category_formset:
                    selection = category.cleaned_data.get('name')
                    if selection is not None:
                        CategoryRecipeMap.objects.create(
                            recipe = created_recipe,
                            category = Category.objects.get(name=selection)
                        )

            return HttpResponseRedirect(created_recipe.get_absolute_url())
            """
            1. Save/update Recipe (name, image, description)
            2. For each ingredient form:
                - Save or get ingredient from database
                - Delete existing RecipeIngredientMap entry if it exists
                - Add amount to RecipeIngredientMap entry if entered and save
            3. Redirect browser to URL of recipe
            """

        else:
            print(recipe_form.errors.values)    # for debugging
            return HttpResponseRedirect('.')
            # Invalid form

    else:

        recipe_form = RecipeForm(instance=recipe)
        # Create recipe form

        ingredient_formset = IngredientFormSet(queryset=ingredient_queryset, prefix="ingredient")
        # Create ingredient formset from queryset

        category_formset = CategoryFormSet(prefix="category")
        # Create category formset

        return render(request, "create_edit_recipe.html", {
            "recipe": recipe,
            "recipe_form": recipe_form,
            "ingredient_formset": ingredient_formset,
            "edit": not id,
            "category_formset": category_formset
            }
        )

def delete_recipe(request, id=None):
    recipe = get_object_or_404(Recipe, id=id)
    recipe.delete()
    return redirect('recipes:list')

def delete_comment(request, id=None):
    comment = get_object_or_404(Comment, id=id)
    comment.delete()
    return redirect(request.META["HTTP_REFERER"])  # Refresh page after delete
