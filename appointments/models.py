from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    name = models.CharField(max_length=150)
    specialization = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='doctors/', blank=True, null=True)

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"

class AvailableSlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='available_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('doctor', 'date', 'start_time')
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.doctor.name} on {self.date} from {self.start_time} to {self.end_time}"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('Booked', 'Booked'),
        ('Cancelled', 'Cancelled'),
    )
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    slot = models.OneToOneField(AvailableSlot, on_delete=models.CASCADE, related_name='appointment')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Booked')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'Booked':
            self.slot.is_booked = True
            self.slot.save()
        elif self.status == 'Cancelled':
            self.slot.is_booked = False
            self.slot.save()

    def delete(self, *args, **kwargs):
        self.slot.is_booked = False
        self.slot.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Appointment for {self.patient.username} with {self.slot.doctor.name} on {self.slot.date}"

class DoctorSchedule(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration_minutes = models.IntegerField(default=30)

    class Meta:
        unique_together = ('doctor', 'day_of_week')

    def __str__(self):
        return f"{self.doctor.name} - {self.get_day_of_week_display()} ({self.start_time} to {self.end_time})"
