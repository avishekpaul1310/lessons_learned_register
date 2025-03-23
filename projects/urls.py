from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project-list'),
    path('<int:pk>/', views.project_detail, name='project-detail'),
    path('new/', views.project_create, name='project-create'),
    path('<int:pk>/add-member/', views.add_team_member, name='add-team-member'),
]