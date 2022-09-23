from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProfileForm, UserProfileCreationForm
from .models import UserProfile

from apps.recipes.models import Recipe
from apps.recipes.views import get_favorite_count, get_comment_count

def login_request(request):
    """Login page
    
    Returns:
        AuthenticationForm: Django login form
    """
    login_error = None
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('recipes:list')
            else:
                login_error = "Ugyldig brukernavn eller passord."
        else:
            login_error = "Ugyldig brukernavn eller passord."

    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"login_form":form, "login_error": login_error})

def logout_request(request):
    logout(request)
    return redirect('recipes:list')

def registration(request):
    """Register a new user profile

    Returns:
        _type_: Error message (if any)
        UserProfileCreationForm: Submission form defined in models.py
    """
    errors = None
    if request.method == 'POST':
        submitted_form = UserProfileCreationForm(request.POST, request.FILES)
        if submitted_form.is_valid():
            # save submitted form
            submitted_form.save()
            # login after registration of userprofile
            username = submitted_form.cleaned_data.get('username')
            password = submitted_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('recipes:list')
        else:
            errors = submitted_form.errors.values

    profile_form = UserProfileCreationForm(instance=UserProfile())
    return render(request, "registration_form.html", {"form": profile_form, "errors":errors})

@login_required
def profile_page(request, username=None):
    """View profile page of a user
    
       Directs to logged-in user if username is not provided)
       Includes edit and delete functionality for logged-in user.

    Args:
        username (str): optional

    Returns:
        UserProfile object
    """
    if username:
        user = get_object_or_404(User, username=username)
        user_profile = UserProfile.objects.get(user_id = user.id)
    else:
        user_profile = UserProfile.objects.get(user=request.user)
    
    recipes = Recipe.objects.filter(user=user_profile.id)
    
    return render(request,
                  "profile_page.html",
                  {"user_profile": user_profile,
                   "recipes": recipes,
                    "favorite_count": get_favorite_count(recipes),
                    "comment_count": get_comment_count(recipes)
                   })

@login_required
def edit_profile(request):
    """Edit user profile

    Returns:
        ProfileForm: Django profile form
    """
    user_profile = get_object_or_404(UserProfile, user_id=request.user.id)
    profile_form = ProfileForm(instance=user_profile)

    if request.method == "POST":
        profile_form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        
        if profile_form.is_valid():
            profile_form.save()

        return redirect('profiles:profile_page_self')

    return render(request, 'edit_profile.html', {'profile_form': profile_form})

@login_required
def delete_profile(request):
    """Delete user profile
    """
    user = get_object_or_404(User, username=request.user.username)
    user.delete()
    return redirect('recipes:list')

@login_required
def list_all_user_profiles(request):
    """View list of all registered users (except own user)

    Returns:
        QuerySet: All UserProfile objects minus the logged-in user.
    """
    user_profiles = UserProfile.objects.exclude(user=request.user)
    return render(request, "list_all.html", {"user_profiles": user_profiles})

@login_required
def favorite_add(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    if recipe.favorites.filter(id=request.user.id).exists():
        recipe.favorites.remove(request.user)
    else:
        recipe.favorites.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def favorite_page(request):
    user_profile = UserProfile.objects.get(user=request.user)
    recipes = Recipe.objects.filter(favorites=user_profile.id)
    return render(request,
                  "favorites.html",
                  {"user_profile": user_profile,
                   "recipes": recipes,
                    "favorite_count": get_favorite_count(recipes),
                    "comment_count": get_comment_count(recipes)
                   })
