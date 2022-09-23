from django.urls import path

from . import views

app_name = 'search'

urlpatterns = [
    path('', views.list_all_recipes_matching_query, name="search"),
]
