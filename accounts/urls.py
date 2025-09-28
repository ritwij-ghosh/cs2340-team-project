from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('register/job-seeker/', views.register_job_seeker, name='register_job_seeker'),
    path('register/recruiter/', views.register_recruiter, name='register_recruiter'),
    path('logout/', views.logout_view, name='logout'),
]
