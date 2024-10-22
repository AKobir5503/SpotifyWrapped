from django.urls import path
from .views import index, login, callback, wrapper, logout  # Removed get_top_tracks

urlpatterns = [
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('callback/', callback, name='callback'),
    path('wrapper/', wrapper, name='wrapper'),  # Make sure this matches your view name
    path('logout/', logout, name='logout'),
]
