from django.urls import path
from django.views.generic import RedirectView
from . import views
urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('events/add/', views.event_create, name='event_create'),
    path('events/<int:id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/rsvp/', views.rsvp_event, name='rsvp_event'),
    path('events/edit/<int:id>/', views.event_update, name='event_update'),
    path('events/delete/<int:id>/', views.event_delete, name='event_delete'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/edit/<int:id>/', views.category_update, name='category_update'),
    path('categories/delete/<int:id>/', views.category_delete, name='category_delete'),

    # Participants are now regular users; keep old URL but redirect to events list
    path('participants/', RedirectView.as_view(pattern_name='event_list', permanent=False)),
    
    # User management views (for admins only)
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/update-role/', views.user_update_role, name='user_update_role'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:group_id>/delete/', views.group_delete, name='group_delete'),
    
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
]