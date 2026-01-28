from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.utils.timezone import now
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView, DetailView
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from .models import Event, Category, UserProfile
from .forms import EventForm, CategoryForm, SignupForm, LoginForm, UserProfileForm, CustomPasswordChangeForm, CustomPasswordResetForm, CustomSetPasswordForm


def _in_group(user, group_name: str) -> bool:
    return user.is_authenticated and user.groups.filter(name=group_name).exists()


def admin_required(view_func):
    return user_passes_test(lambda u: u.is_superuser or _in_group(u, "Admin"))(view_func)


def organizer_required(view_func):
    def check(user):
        # Admins are allowed everywhere
        if user.is_superuser or _in_group(user, "Admin"):
            return True
        return _in_group(user, "Organizer")

    return user_passes_test(check)(view_func)


def participant_required(view_func):
    def check(user):
        # Admins and Organizers are allowed everywhere
        if user.is_superuser or _in_group(user, "Admin") or _in_group(user, "Organizer"):
            return True
        return _in_group(user, "Participant")

    return user_passes_test(check)(view_func)

class EventListView(ListView):
    """Class-based view for displaying list of events with filtering"""
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 20

    def get_queryset(self):
        events = Event.objects.select_related('category').prefetch_related('participants')
        
        start = self.request.GET.get('start')
        end = self.request.GET.get('end')
        category_id = self.request.GET.get('category')
        search = self.request.GET.get('search')
        
        # Search filter
        if search:
            events = events.filter(
                Q(name__icontains=search) | Q(location__icontains=search)
            )
        
        if start and end:
            events = events.filter(date__range=[start, end])
        
        if category_id:
            events = events.filter(category_id=category_id)
        
        return events
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['start_date'] = self.request.GET.get('start', '')
        context['end_date'] = self.request.GET.get('end', '')
        return context

@login_required
@participant_required
def dashboard(request):
    today = now().date()

    stats = {
        "total_events": Event.objects.count(),
        "upcoming_events": Event.objects.filter(date__gt=today).count(),
        "past_events": Event.objects.filter(date__lt=today).count(),
        "total_users": User.objects.count(),
    }

    filter_type = request.GET.get('filter', 'rsvp')
    events = Event.objects.select_related('category').prefetch_related('participants')
    
    if filter_type == 'upcoming':
        events = events.filter(date__gt=today).order_by('date', 'time')
    elif filter_type == 'past':
        events = events.filter(date__lt=today).order_by('-date', '-time')
    elif filter_type == 'all':
        events = events.order_by('date', 'time')
    elif filter_type == 'rsvp':
        events = events.filter(participants=request.user).order_by('date', 'time')
    else:  # 'today'
        events = events.filter(date=today).order_by('time')

    # Get user's RSVP'd events for the sidebar
    rsvp_events = Event.objects.filter(participants=request.user).select_related('category').order_by('date', 'time')

    return render(request, "events/dashboard.html", {
        **stats,
        'events': events,
        'rsvp_events': rsvp_events,
        'filter_type': filter_type,
        'today': today,
    })
   
@login_required
@admin_required
def user_list(request):
    users = User.objects.all().prefetch_related('groups')
    return render(request, 'events/user_list.html', {
        'users': users
    })
 
@method_decorator(login_required, name='dispatch')
@method_decorator(organizer_required, name='dispatch')
class EventCreateView(CreateView):
    """Class-based view for creating new events (organizers only)"""
    model = Event
    form_class = EventForm
    template_name = "events/form.html"
    success_url = reverse_lazy('event_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Add Event"
        return context

@method_decorator(login_required, name='dispatch')
@method_decorator(organizer_required, name='dispatch')
class EventUpdateView(UpdateView):
    """Class-based view for updating events (organizers only)"""
    model = Event
    form_class = EventForm
    template_name = "events/form.html"
    success_url = reverse_lazy('event_list')
    pk_url_kwarg = 'id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Edit Event"
        return context

@method_decorator(login_required, name='dispatch')
@method_decorator(organizer_required, name='dispatch')
class EventDeleteView(DeleteView):
    """Class-based view for deleting events (organizers only)"""
    model = Event
    success_url = reverse_lazy('event_list')
    pk_url_kwarg = 'id'

def event_detail(request, id):
    event = get_object_or_404(Event, id=id)
    return render(request, "events/event_detail.html", {"event": event})

@login_required
@participant_required
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'rsvp':
            if request.user in event.participants.all():
                messages.warning(request, "You have already RSVP'd to this event.")
            else:
                event.participants.add(request.user)
                
                # Send RSVP confirmation email
                try:
                    send_mail(
                        subject=f'RSVP Confirmation: {event.name}',
                        message=f'Hi {request.user.get_full_name() or request.user.username},\n\n'
                               f'You have successfully RSVP\'d to the following event:\n\n'
                               f'Event: {event.name}\n'
                               f'Date: {event.date}\n'
                               f'Time: {event.time}\n'
                               f'Location: {event.location}\n\n'
                               f'Thank you for your interest!\n\n'
                               f'Best regards,\nEvent Management Team',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[request.user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"RSVP email sending failed: {e}") 
                
                messages.success(request, f"You have successfully RSVP'd to {event.name}!")
        
        elif action == 'cancel_rsvp':
            if request.user in event.participants.all():
                event.participants.remove(request.user)
                
                # Send cancellation confirmation email
                try:
                    send_mail(
                        subject=f'RSVP Cancellation: {event.name}',
                        message=f'Hi {request.user.get_full_name() or request.user.username},\n\n'
                               f'Your RSVP for the following event has been cancelled:\n\n'
                               f'Event: {event.name}\n'
                               f'Date: {event.date}\n'
                               f'Time: {event.time}\n'
                               f'Location: {event.location}\n\n'
                               f'If this was a mistake, you can RSVP again.\n\n'
                               f'Best regards,\nEvent Management Team',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[request.user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Cancellation email sending failed: {e}")  # Debug output
                
                messages.success(request, f"You have cancelled your RSVP for {event.name}.")
            else:
                messages.warning(request, "You are not RSVP'd to this event.")
        
        return redirect('event_detail', id=event_id)
class CategoryListView(ListView):
    """Class-based view for displaying list of categories"""
    model = Category
    template_name = "events/category_list.html"
    context_object_name = "categories"


# Profile Management Views
@method_decorator(login_required, name='dispatch')
class ProfileView(DetailView):
    """Class-based view for viewing user profile"""
    model = UserProfile
    template_name = "accounts/profile.html"
    context_object_name = "profile"
    
    def get_object(self, queryset=None):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


@method_decorator(login_required, name='dispatch')
class ProfileEditView(UpdateView):
    """Class-based view for editing user profile"""
    model = UserProfile
    form_class = UserProfileForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy('profile')
    
    def get_object(self, queryset=None):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
class CustomPasswordChangeView(PasswordChangeView):
    """Class-based view for changing password"""
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully!')
        return super().form_valid(form)


class CustomPasswordResetView(PasswordResetView):
    """Class-based view for password reset"""
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    
    def form_valid(self, form):
        messages.success(self.request, 'Check your email for password reset instructions!')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Class-based view for confirming password reset"""
    form_class = CustomSetPasswordForm
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')
    
    def form_valid(self, form):
        messages.success(self.request, 'Password reset successfully! You can now login with your new password.')
        return super().form_valid(form)


@login_required
@organizer_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('category_list')
    return render(request, 'events/form.html', {
        'form': form,
        'title': 'Add Category'
    })
def category_update(request, id):
    category = get_object_or_404(Category, id=id)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect('category_list')
    return render(request, "events/form.html", {"form": form, "title": "Edit Category"})

@login_required
@organizer_required
def category_delete(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    return redirect("category_list")


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until email confirmation
            user.save()
            
            # Ensure default groups exist and assign user to Participant group
            participant_group, _ = Group.objects.get_or_create(name="Participant")
            user.groups.add(participant_group)
            
            # Email is now handled by the signal in signals.py
            
            messages.success(request, 'Account created successfully! Please check your email to activate your account.')
            return redirect("login")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})


def activate_account(request, uidb64, token):
    """Activate user account from email link"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated successfully! You can now log in.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid or has expired.')
        return redirect('login')


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm


class UserLogoutView(LogoutView):
    next_page = "event_list"


# Admin views for managing users and groups
@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard - full system overview and management"""
    today = now().date()
    
    # Comprehensive stats for admins
    stats = {
        "total_events": Event.objects.count(),
        "upcoming_events": Event.objects.filter(date__gt=today).count(),
        "past_events": Event.objects.filter(date__lt=today).count(),
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "inactive_users": User.objects.filter(is_active=False).count(),
        "total_participants": User.objects.filter(groups__name="Participant").count(),
        "total_organizers": User.objects.filter(groups__name="Organizer").count(),
        "total_admins": User.objects.filter(groups__name="Admin").count(),
        "total_categories": Category.objects.count(),
    }

    # Recent events and users for admin overview
    recent_events = Event.objects.select_related('category').order_by('-date')[:5]
    recent_users = User.objects.order_by('-date_joined')[:5]

    return render(request, "events/admin_dashboard.html", {
        **stats,
        'recent_events': recent_events,
        'recent_users': recent_users,
        'today': today,
    })


@login_required
@organizer_required
def organizer_dashboard(request):
    """Organizer dashboard - manage events and categories"""
    today = now().date()
    
    # Events for organizer to manage
    my_events = Event.objects.select_related('category').prefetch_related('participants').order_by('date')
    
    # Calculate total RSVPs across all events
    total_rsvps = sum(event.participants.count() for event in my_events)
    
    # Stats relevant to organizers
    stats = {
        "my_events_count": my_events.count(),
        "upcoming_events": Event.objects.filter(date__gt=today).count(),
        "past_events": Event.objects.filter(date__lt=today).count(),
        "total_categories": Category.objects.count(),
        "total_participants": User.objects.filter(groups__name="Participant").count(),
        "total_rsvps": total_rsvps,
    }

    return render(request, "events/organizer_dashboard.html", {
        **stats,
        'my_events': my_events,
        'today': today,
    })


@login_required
@admin_required
def user_update_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        # Clear existing groups
        user.groups.clear()
        
        # Add selected groups
        group_names = request.POST.getlist('groups')
        for group_name in group_names:
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
        
        return redirect('user_list')
    
    # Get all available groups
    all_groups = Group.objects.all()
    user_groups = user.groups.all()
    
    return render(request, 'events/user_update_role.html', {
        'user': user,
        'all_groups': all_groups,
        'user_groups': user_groups
    })


@login_required
@admin_required
def group_create(request):
    if request.method == 'POST':
        group_name = request.POST.get('name')
        if group_name:
            Group.objects.get_or_create(name=group_name)
        return redirect('group_list')
    
    return render(request, 'events/group_create.html')


@login_required
@admin_required
def group_list(request):
    groups = Group.objects.all().prefetch_related('user_set')
    return render(request, 'events/group_list.html', {
        'groups': groups
    })


@login_required
@admin_required
def group_delete(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    # Prevent deletion of system groups
    if group.name in ['Admin', 'Organizer', 'Participant']:
        # You might want to add a message here
        pass
    else:
        group.delete()
    return redirect('group_list')

@login_required
def login_redirect(request):
    user = request.user

    if user.is_superuser or user.groups.filter(name="Admin").exists():
        return redirect('admin_dashboard')

    if user.groups.filter(name="Organizer").exists():
        return redirect('organizer_dashboard')

    return redirect('dashboard')  # Participant default

