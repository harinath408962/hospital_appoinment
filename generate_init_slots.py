import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointment_system.settings')
django.setup()

from appointments.models import Doctor, AvailableSlot
from appointments.admin import generate_slots

class MockAdmin:
    def message_user(self, request, message, level):
        print("MESSAGE:", message)

class MockRequest:
    pass

doctors = Doctor.objects.all()
print("Initial slots:", AvailableSlot.objects.count())
try:
    generate_slots(MockAdmin(), MockRequest(), doctors)
except Exception as e:
    import traceback
    traceback.print_exc()
print("Final slots:", AvailableSlot.objects.count())

for doc in doctors:
    for s in doc.schedules.all():
        print(f"Doc {doc.name} Schedule {s.day_of_week}: {s.start_time} - {s.end_time}")
