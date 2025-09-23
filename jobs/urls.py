from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>/', views.detail, name='detail'),
    path('post/', views.post_job, name='post_job'),
    path('<int:pk>/edit/', views.edit_job, name='edit_job'),
    path('<int:pk>/delete/', views.delete_job, name='delete_job'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
]
