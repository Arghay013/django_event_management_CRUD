from django.urls import path
from django.views.generic import RedirectView
from . import views
urlpatterns = [
    path('', views.EventListView.as_view(), name='event_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('organizer-dashboard/', views.organizer_dashboard, name='organizer_dashboard'),

    path('events/add/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/rsvp/', views.rsvp_event, name='rsvp_event'),
    path('events/edit/<int:id>/', views.EventUpdateView.as_view(), name='event_update'),
    path('events/delete/<int:id>/', views.EventDeleteView.as_view(), name='event_delete'),

    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/edit/<int:id>/', views.category_update, name='category_update'),
    path('categories/delete/<int:id>/', views.category_delete, name='category_delete'),

    path('participants/', RedirectView.as_view(pattern_name='event_list', permanent=False)),
    
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/update-role/', views.user_update_role, name='user_update_role'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:group_id>/delete/', views.group_delete, name='group_delete'),
    
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('profile/change-password/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/done/', RedirectView.as_view(pattern_name='profile', permanent=False), name='password_reset_done'),
    path('password-reset/complete/', RedirectView.as_view(pattern_name='login', permanent=False), name='password_reset_complete'),
    
    path('signup/', views.signup_view, name='signup'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('login-redirect/', views.login_redirect, name='login_redirect'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
]