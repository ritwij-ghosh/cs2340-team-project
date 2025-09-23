from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('', views.index, name='index'),
    path('send/', views.send_email, name='send_email'),
    path('send/<int:user_id>/', views.send_quick_email, name='send_quick_email'),
    path('emails/', views.email_list, name='email_list'),
    path('emails/<int:email_id>/', views.email_detail, name='email_detail'),
]
