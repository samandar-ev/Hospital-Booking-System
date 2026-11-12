from django.contrib import admin

from .models import Appointment, Doctor, Patient, Receptionist, Service


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'email', 'phone_number')
    search_fields = ('name', 'specialization', 'email')


@admin.register(Receptionist)
class ReceptionistAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone_number')
    search_fields = ('name', 'email')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'dob', 'email', 'phone_number')
    search_fields = ('name', 'email', 'phone_number')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration')
    search_fields = ('name',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'service', 'time', 'status', 'completed_at')
    list_filter = ('status', 'service', 'doctor', 'completed_at')
    search_fields = ('patient__name', 'doctor__name', 'service__name')
