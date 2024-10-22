from django.urls import path

from django.contrib import admin

from wrapped import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('/about/', views.about, name='about'),
    path('/contact/', views.contact, name='contact'),
    path('/wrapper', views.wrapper, name='wrapper'),
]