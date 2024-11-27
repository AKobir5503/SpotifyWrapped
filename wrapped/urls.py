from django.urls import path
from . import views


urlpatterns = [
    path('', views.landing, name='landing'),
    path('about/', views.about, name='about'),

    path('settings/', views.settings, name='settings'),

    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('spotify-login/', views.spotify_login, name='spotify-login'),
    path('callback/', views.callback, name='callback'),
    path('generate-wrap/', views.generate_wrap, name='generate-wrap'),
    path('save-wrap/', views.save_wrap, name='save-wrap'),
    path('wrap/<int:wrap_id>/', views.wrap_detail, name='wrap_detail'),  # Define the URL pattern for wrap details

]
