<<<<<<< HEAD
from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('', views.index, name='index'),
]
=======
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='communications.index'),
    path('about', views.about, name='communications.about'),
] 
>>>>>>> c0c2653 (WIP)
