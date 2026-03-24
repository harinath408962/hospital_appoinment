import datetime
from django.contrib import admin, messages
from django.utils import timezone
from .models import Doctor, AvailableSlot, Appointment, DoctorSchedule

class DoctorScheduleInline(admin.TabularInline):
    model = DoctorSchedule
    extra = 1

@admin.action(description='Generate slots for next 14 days')
def generate_slots(modeladmin, request, queryset):
    today = timezone.localdate()
    days_to_generate = 14
    slots_created = 0

    if queryset.model == Doctor:
        doctors = queryset
    else:
        doctors = list(set([sched.doctor for sched in queryset]))

    for doctor in doctors:
        schedules = doctor.schedules.all()
        if not schedules.exists():
            continue
        
        schedule_map = {s.day_of_week: s for s in schedules}
        
        for i in range(days_to_generate):
            current_date = today + datetime.timedelta(days=i)
            day_idx = current_date.weekday()
            
            if day_idx in schedule_map:
                sched = schedule_map[day_idx]
                
                current_time = datetime.datetime.combine(current_date, sched.start_time)
                end_time = datetime.datetime.combine(current_date, sched.end_time)
                delta = datetime.timedelta(minutes=sched.slot_duration_minutes)
                
                while current_time + delta <= end_time:
                    slot_start = current_time.time()
                    slot_end = (current_time + delta).time()
                    
                    _, created = AvailableSlot.objects.get_or_create(
                        doctor=doctor,
                        date=current_date,
                        start_time=slot_start,
                        defaults={'end_time': slot_end, 'is_booked': False}
                    )
                    if created:
                        slots_created += 1
                    
                    current_time += delta

    modeladmin.message_user(request, f"Successfully created {slots_created} new available slots.", messages.SUCCESS)

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization')
    search_fields = ('name', 'specialization')
    inlines = [DoctorScheduleInline]
    actions = [generate_slots]

@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'get_day_of_week_display', 'start_time', 'end_time', 'slot_duration_minutes')
    list_filter = ('doctor', 'day_of_week')
    actions = [generate_slots]

@admin.register(AvailableSlot)
class AvailableSlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'is_booked')
    list_filter = ('doctor', 'date', 'is_booked')
    search_fields = ('doctor__name',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'get_doctor', 'get_date', 'status')
    list_filter = ('status', 'slot__date')
    search_fields = ('patient__username', 'slot__doctor__name')

    def get_doctor(self, obj):
        return obj.slot.doctor.name
    get_doctor.short_description = 'Doctor'

    def get_date(self, obj):
        return obj.slot.date
    get_date.short_description = 'Date'
