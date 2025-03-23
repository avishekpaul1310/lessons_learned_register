from django.urls import path
from . import views

urlpatterns = [
    path('', views.lesson_list, name='lesson-list'),
    path('<int:pk>/', views.lesson_detail, name='lesson-detail'),
    path('new/', views.lesson_create, name='lesson-create'),
    path('<int:pk>/edit/', views.lesson_update, name='lesson-update'),
]