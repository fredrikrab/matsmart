from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

app_name = 'profiles'

# create a list of URL patterns corresponding to various view functions
urlpatterns = [
    path('', views.profile_page, name='profile_page_self'),
    path("logg-inn/", views.login_request, name="login"),
    path("logg-ut/", views.logout_request, name="logout"),
    path('registrer/', views.registration, name="registration"),
    path('vis/<str:username>/', views.profile_page, name='profile_page'),
    path('vis/alle/', views.list_all_user_profiles, name="list_all"),
    path('endre/', views.edit_profile, name="edit"),
    path('slett/', views.delete_profile, name='delete'),
    path('fav/<int:id>/', views.favorite_add, name="favorite_add"),
    path('favoritter/', views.favorite_page, name="favorite_page")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
