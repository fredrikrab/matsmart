from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.list_recipes, name='list'),
    path('ny/', views.create_edit_recipe, name='create'),
    path('<int:id>/', views.list_recipes, name='view'),
    path('<int:id>/rediger', views.create_edit_recipe, name='edit'),
    path('<int:id>/slett', views.delete_recipe, name='delete'),
    path('kommentar/<int:id>/slett', views.delete_comment, name='delete_comment'),
]
