<<<<<<< HEAD
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
=======
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='accounts.index'),
    path('about', views.about, name='accounts.about'),
] 
>>>>>>> c0c2653 (WIP)
