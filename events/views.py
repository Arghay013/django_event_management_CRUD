from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.utils.timezone import now
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Event, Category
from .forms import EventForm, CategoryForm, SignupForm, LoginForm


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

def event_list(request):
    events = Event.objects.select_related('category').prefetch_related('participants')

    start = request.GET.get('start')
    end = request.GET.get('end')
    category_id = request.GET.get('category')
    search = request.GET.get('search')  

    # Search filter 
    if search:
        events = events.filter(
            Q(name__icontains=search) | Q(location__icontains=search)
        )

    if start and end:
        events = events.filter(date__range=[start, end])

    if category_id:
        events = events.filter(category_id=category_id)

    categories = Category.objects.all()

    return render(request, 'events/event_list.html', {
        'events': events,
        'categories': categories,
        'search': search,
        'selected_category': category_id,
        'start_date': start,
        'end_date': end,
    })

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
@organizer_required
def event_create(request):
    form = EventForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('event_list')
    return render(request, "events/form.html", {"form": form, "title": "Add Event"})

@login_required
@organizer_required
def event_update(request, id):
    event = get_object_or_404(Event, id=id)
    form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        return redirect('event_list')
    return render(request, "events/form.html", {"form": form, "title": "Edit Event"})

@login_required
@organizer_required
def event_delete(request, id):
    event = get_object_or_404(Event, id=id)
    event.delete()
    return redirect('event_list')

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
                messages.success(request, f"You have successfully RSVP'd to {event.name}!")
                
                # Send confirmation email
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
                    # Log the error but don't show to user
                    print(f"Email sending failed: {e}")
        
        elif action == 'cancel_rsvp':
            if request.user in event.participants.all():
                event.participants.remove(request.user)
                messages.success(request, f"You have cancelled your RSVP to {event.name}.")
            else:
                messages.warning(request, "You haven't RSVP'd to this event yet.")
    
    return redirect('event_detail', id=event_id)

@login_required
@organizer_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, "events/category_list.html", {
        "categories": categories
    })


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
    
@login_required
@organizer_required
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
            user = form.save()
            # Ensure default groups exist
            participant_group, _ = Group.objects.get_or_create(name="Participant")
            organizer_group, _ = Group.objects.get_or_create(name="Organizer")
            admin_group, _ = Group.objects.get_or_create(name="Admin")

            # New users become Participants by default
            user.groups.add(participant_group)

            login(request, user)
            return redirect("dashboard")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {"form": form})


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm


class UserLogoutView(LogoutView):
    next_page = "event_list"


# Admin views for managing users and groups
@login_required
@admin_required
def user_list(request):
    users = User.objects.all().prefetch_related('groups')
    return render(request, 'events/user_list.html', {
        'users': users
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
