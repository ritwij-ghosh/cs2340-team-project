from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_application, name='create'),
    path('<int:pk>/status/', views.update_status, name='update_status'),
]
