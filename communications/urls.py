from django.urls import path
from . import views

app_name = 'communications'

urlpatterns = [
    path('', views.index, name='index'),
    path('send/', views.send_message, name='send_message'),
    path('view/<int:message_id>/', views.view_message, name='view_message'),
    path('reply/<int:message_id>/', views.reply_message, name='reply_message'),
]
