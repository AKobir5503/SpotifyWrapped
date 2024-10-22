from django.urls import path
from .views import index, login, get_top_tracks, callback, logout

urlpatterns = [
    path('', index, name='index'),
    #path('about/', about, name='about'),
    #path('contact/', contact, name='contact'),
    path('wrapper/', get_top_tracks, name='wrapper'),
    path('/login', login, name='login'),  # Ensure this is correct
    path('callback/', callback, name='callback'),  # Callback URL
    path('logout/', logout, name='logout'),

]
