from django.urls import path
from . import views


urlpatterns = [
    path('', views.landing, name='landing'),
    path('about/', views.about, name='about'),
    path('settings/', views.user_settings, name='settings'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('spotify-login/', views.spotify_login, name='spotify-login'),
    path('callback/', views.callback, name='callback'),
    path('generate-wrap/', views.generate_wrap, name='generate-wrap'),
    path('save-wrap/', views.save_wrap, name='save-wrap'),
    path('wrap/<int:wrap_id>/', views.wrap_detail, name='wrap_detail'),  # Define the URL pattern for wrap details
    path('wrap/<int:wrap_id>/delete/', views.delete_wrap, name='delete-wrap'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('wrap/share/<str:share_token>/', views.share_wrap, name='share_wrap'),
    path('wrap/share-view/<str:share_token>/', views.share_view, name='share_view'),
]
