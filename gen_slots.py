import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointment_system.settings')
django.setup()

from appointments.models import Doctor, AvailableSlot
from appointments.admin import generate_slots

class MockAdmin:
    def message_user(self, *args, **kwargs):
        pass

def main():
    doctors = Doctor.objects.all()
    if not doctors.exists():
        print("❌ No doctors found in the database. Please add a doctor in the Admin panel first!")
        return

    print(f"Found {doctors.count()} doctors. Generating slots...")
    
    # We call the generation function directly
    generate_slots(MockAdmin(), None, doctors)
    
    count = AvailableSlot.objects.count()
    print(f"✅ SUCCESS! Total available slots in database: {count}")
    print("Now go to the Web tab and click 'RELOAD' on PythonAnywhere!")

if __name__ == "__main__":
    main()
