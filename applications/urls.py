<<<<<<< HEAD
from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('', views.index, name='index'),
]
=======
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='applications.index'),
    path('about', views.about, name='applications.about'),
] 
>>>>>>> c0c2653 (WIP)
