<<<<<<< HEAD
from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.index, name='index'),
]
=======
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='jobs.index'),
    path('about', views.about, name='jobs.about'),
] 
>>>>>>> c0c2653 (WIP)
