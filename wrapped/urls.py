from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', views.landing, name='landing'),  # Landing page
    path('about/', views.about, name='about'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.user_logout, name='logout'),  # Django's built-in logout view
    path('dashboard/', views.dashboard, name='dashboard'),
    path('spotify-login/', views.spotify_login, name='spotify-login'),
    path('callback/', views.spotify_callback, name='callback'),
    path('generate-wrap/', views.generate_wrap, name='generate-wrap'),
    path('wrapper/', views.wrapper, name='wrapper'),
    path('index/', views.index, name='index'),
    # Add more paths if needed for other views
]
