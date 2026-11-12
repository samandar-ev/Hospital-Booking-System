from django.contrib.auth.models import User
from django.db import models


class Doctor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name} ({self.specialization})"


class Receptionist(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='receptionist_profile'
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name


class Patient(models.Model):
    name = models.CharField(max_length=100)
    dob = models.DateField()
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    medical_history = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.dob})"

class Service(models.Model):
    name = models.CharField(max_length=100)
    duration = models.IntegerField()  # in minutes

    def __str__(self):
        return self.name

class Appointment(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_CONFIRMED = 'CONFIRMED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_COMPLETED = 'COMPLETED'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_COMPLETED, 'Completed'),
    )

    REJECTION_REASON_CHOICES = (
        ('CONFLICT', 'Conflicting commitment'),
        ('OUT_OF_HOURS', 'Outside working hours'),
        ('REALIGN', 'Requires reassignment'),
        ('CUSTOM', 'Custom reason'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    time = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    rejection_reason = models.CharField(
        max_length=20,
        choices=REJECTION_REASON_CHOICES,
        blank=True
    )
    rejection_note = models.TextField(blank=True)
    diagnosis = models.TextField(blank=True)
    condition_summary = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    doctor_comments = models.TextField(blank=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.patient.name} with {self.doctor.name} for {self.service.name} at {self.time}"
