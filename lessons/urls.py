from django.urls import path
from . import views

urlpatterns = [
    path('', views.lesson_list, name='lesson-list'),
    path('<int:pk>/', views.lesson_detail, name='lesson-detail'),
    path('new/', views.lesson_create, name='lesson-create'),
    path('<int:pk>/edit/', views.lesson_update, name='lesson-update'),
    path('<int:pk>/delete/', views.delete_lesson, name='lesson-delete'),
    path('attachment/<int:pk>/delete/', views.delete_attachment, name='attachment-delete'),
    path('category/create/', views.create_category, name='category-create'),
]