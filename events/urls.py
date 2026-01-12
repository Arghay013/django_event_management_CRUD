from django.urls import path
from . import views
urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('events/add/', views.event_create, name='event_create'),
    path('events/<int:id>/', views.event_detail, name='event_detail'),
    path('events/edit/<int:id>/', views.event_update, name='event_update'),
    path('events/delete/<int:id>/', views.event_delete, name='event_delete'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/edit/<int:id>/', views.category_update, name='category_update'),
    path('categories/delete/<int:id>/', views.category_delete, name='category_delete'),

    path('participants/', views.participant_list, name='participant_list'),
    path('participants/add/', views.participant_create, name='participant_create'),
    path('participants/edit/<int:id>/', views.participant_update, name='participant_update'),
    path('participants/delete/<int:id>/', views.participant_delete, name='participant_delete'),
]