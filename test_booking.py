import os
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointment_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from appointments.models import AvailableSlot, Doctor, Appointment

# Ensure the slot exists
slot = AvailableSlot.objects.first()
if not slot:
    print("No slot found to book!")
else:
    print(f"Booking slot ID {slot.id}...")
    client = Client(SERVER_NAME='127.0.0.1')
    user = User.objects.first() # Get admin or any user
    client.force_login(user)
    try:
        response = client.post(f'/book/{slot.id}/')
        print("Status:", response.status_code)
        if response.status_code >= 400:
            print(response.content.decode())
        elif response.status_code in [301, 302]:
            print("Redirects to:", response.url)
            # Try to follow the redirect
            dash_response = client.get(response.url)
            print("Dashboard Status:", dash_response.status_code)
            if dash_response.status_code >= 400:
                print(dash_response.content.decode())
    except Exception as e:
        traceback.print_exc()
