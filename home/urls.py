<<<<<<< HEAD
from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
]
=======
from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='home.index'),
]
>>>>>>> c0c2653 (WIP)
