from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('', views.index, name='index'),
]
