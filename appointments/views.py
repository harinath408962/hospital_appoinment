from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.mail import send_mail
from .models import Doctor, AvailableSlot, Appointment

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

@login_required
def patient_dashboard(request):
    appointments = Appointment.objects.filter(patient=request.user).order_by('-created_at')
    return render(request, 'patient_dashboard.html', {'appointments': appointments})

def doctor_list(request):
    specialization = request.GET.get('specialization', '')
    search_query = request.GET.get('search', '')
    
    doctors = Doctor.objects.all().order_by('name')
    if specialization:
        doctors = doctors.filter(specialization__iexact=specialization)
    if search_query:
        doctors = doctors.filter(name__icontains=search_query)
    
    # Pagination: show 6 doctors per page
    paginator = Paginator(doctors, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    specializations = Doctor.objects.values_list('specialization', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'specializations': specializations,
        'current_specialization': specialization,
        'search_query': search_query
    }
    return render(request, 'doctor_list.html', context)

def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    
    now = timezone.localtime()
    current_date = now.date()
    current_time = now.time()
    
    # Filter out past dates, and for today, filter out past times
    slots = doctor.available_slots.filter(
        date__gte=current_date
    ).exclude(
        date=current_date, 
        start_time__lt=current_time
    ).order_by('date', 'start_time')
    
    return render(request, 'doctor_detail.html', {'doctor': doctor, 'slots': slots})

@login_required
def book_appointment(request, slot_id):
    if request.method == 'POST':
        with transaction.atomic():
            slot = get_object_or_404(AvailableSlot, id=slot_id)
            if slot.is_booked or hasattr(slot, 'appointment'):
                slot.is_booked = True
                slot.save()
                messages.error(request, 'Sorry, this slot is already booked. Please choose another one.')
                return redirect('doctor_detail', doctor_id=slot.doctor.id)
            
            try:
                appointment = Appointment.objects.create(
                    patient=request.user,
                    slot=slot,
                    status='Booked'
                )
                slot.is_booked = True
                slot.save()
                
                # Send email confirmation
                subject = 'Appointment Confirmation - HealthSync'
                message = f'Hello {request.user.username},\n\nYour appointment with Dr. {slot.doctor.name} on {slot.date} at {slot.start_time} has been confirmed.\n\nThank you for using HealthSync!'
                try:
                    if request.user.email:
                        send_mail(subject, message, 'noreply@healthsync.com', [request.user.email])
                    else:
                        send_mail(subject, message, 'noreply@healthsync.com', [f'{request.user.username}@example.com'])
                except Exception:
                    pass
                
                messages.success(request, f'Appointment booked successfully with {slot.doctor.name} on {slot.date} at {slot.start_time}. A confirmation email has been sent.')
                return redirect('patient_dashboard')
            except IntegrityError:
                slot.is_booked = True
                slot.save()
                messages.error(request, 'Sorry, this slot was just booked by someone else.')
                return redirect('doctor_detail', doctor_id=slot.doctor.id)
    
    return redirect('doctor_list')
