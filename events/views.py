from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.utils.timezone import now
from .models import Event, Category, Participant
from .forms import EventForm,CategoryForm, ParticipantForm

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

def dashboard(request):
    today = now().date()

    stats = {
        'total_events': Event.objects.count(),
        'upcoming_events': Event.objects.filter(date__gt=today).count(),
        'past_events': Event.objects.filter(date__lt=today).count(),
        'total_participants': Participant.objects.count(),
    }

    filter_type = request.GET.get('filter', 'today')
    events = Event.objects.select_related('category').prefetch_related('participants')
    
    if filter_type == 'upcoming':
        events = events.filter(date__gt=today).order_by('date', 'time')
    elif filter_type == 'past':
        events = events.filter(date__lt=today).order_by('-date', '-time')
    elif filter_type == 'all':
        events = events.order_by('date', 'time')
    else:  # 'today' or default
        events = events.filter(date=today).order_by('time')

    return render(request, 'events/dashboard.html', {
        **stats,
        'events': events,
        'filter_type': filter_type,
        'today': today,
    })
    
def event_create(request):
    form = EventForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('event_list')
    return render(request, 'events/form.html', {'form': form, 'title': 'Add Event'})

def event_update(request, id):
    event = get_object_or_404(Event, id=id)
    form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        return redirect('event_list')
    return render(request, 'events/form.html', {'form': form, 'title': 'Edit Event'})

def event_delete(request, id):
    event = get_object_or_404(Event, id=id)
    event.delete()
    return redirect('event_list')

def event_detail(request, id):
    event = get_object_or_404(Event, id=id)
    return render(request, 'events/event_detail.html', {'event': event})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'events/category_list.html', {
        'categories': categories
    })


def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('category_list')
    return render(request, 'events/form.html', {
        'form': form,
        'title': 'Add Category'
    })
    
def participant_list(request):
    participants = Participant.objects.all()
    return render(request, 'events/participant_list.html', {
        'participants': participants
    })

def category_update(request, id):
    category = get_object_or_404(Category, id=id)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        return redirect('category_list')
    return render(request, 'events/form.html', {'form': form, 'title': 'Edit Category'})

def category_delete(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    return redirect('category_list')

def participant_create(request):
    form = ParticipantForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('participant_list')
    return render(request, 'events/form.html', {
        'form': form,
        'title': 'Add Participant'
    })

def participant_update(request, id):
    participant = get_object_or_404(Participant, id=id)
    form = ParticipantForm(request.POST or None, instance=participant)
    if form.is_valid():
        form.save()
        return redirect('participant_list')
    return render(request, 'events/form.html', {'form': form, 'title': 'Edit Participant'})

def participant_delete(request, id):
    participant = get_object_or_404(Participant, id=id)
    participant.delete()
    return redirect('participant_list')
