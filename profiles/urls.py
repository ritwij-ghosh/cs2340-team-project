from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.index, name='index'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('create/', views.create_profile, name='create'),
    path('edit/', views.edit_profile, name='edit'),
    path('edit-user-info/', views.edit_user_info, name='edit_user_info'),
    path('view/<int:user_id>/', views.view_profile, name='view'),
    path('save-search/', views.save_search, name='save_search'),
    path('saved-searches/', views.saved_searches, name='saved_searches'),
    path('saved-searches/<int:pk>/run/', views.run_saved_search, name='run_saved_search'),
    path('saved-searches/<int:pk>/delete/', views.delete_saved_search, name='delete_saved_search'),
]
