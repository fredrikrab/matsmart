"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

from apps.recipes.models import Recipe
from apps.recipes.views import get_favorite_count, get_comment_count
from django.db.models import OuterRef, Subquery

def homepage(request):
    favorite_count = get_favorite_count(Recipe.objects.all()).order_by('-count')
    # TODO: recipes will now include an additional column, which seems to be hard to remove without explicitly stating every field that should be kept
    recipes = Recipe.objects.all().annotate(count=Subquery(favorite_count.filter(id=OuterRef('id')).values('count'))).order_by('-count')

    return render(request, "index.html", {
        "user": request.user if request.user.is_authenticated else None,
        "recipes": recipes,
        "favorite_count": favorite_count,
        "comment_count": get_comment_count(recipes)
    })

# URL configuration
# path('',...) looks for module urls.py inside oppskrift-app and registeres any URLs defined there
# root path (localhost:8000) will take to oppskrifter page
urlpatterns = [
    path('', homepage),
    path('admin/', admin.site.urls),
    path('oppskrifter/', include('apps.recipes.urls')),
    path('profil/', include('apps.profiles.urls')),
    path('søk/', include('apps.search.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
