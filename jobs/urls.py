from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.index, name='index'),
    path('recommendations/', views.recommendations, name='recommendations'),
    path('map/', views.map_view, name='map'),
    path('applicant-clusters/', views.applicant_cluster_map, name='applicant_cluster_map'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/geocode/', views.geocode_job, name='geocode_job'),
    path('post/', views.post_job, name='post_job'),
    path('<int:pk>/edit/', views.edit_job, name='edit_job'),
    path('<int:pk>/delete/', views.delete_job, name='delete_job'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
]
