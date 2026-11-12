from collections import defaultdict

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    AppointmentConclusionForm,
    AppointmentForm,
    DoctorForm,
    PatientForm,
    ReceptionistForm,
    ServiceForm,
    UserRegistrationForm,
    UserUpdateForm,
)
from .models import Appointment, Doctor, Patient, Receptionist, Service


def _ensure_group_membership(user, group_name: str) -> None:
    group, _ = Group.objects.get_or_create(name=group_name)
    user.groups.add(group)


def _has_group(user, name: str) -> bool:
    return user.groups.filter(name=name).exists()


def is_admin(user) -> bool:
    return user.is_superuser or _has_group(user, 'Admin')


def is_doctor(user) -> bool:
    return _has_group(user, 'Doctor')


def is_receptionist(user) -> bool:
    return _has_group(user, 'Receptionist')


def admin_or_receptionist(user) -> bool:
    return is_admin(user) or is_receptionist(user)


def admin_or_doctor(user) -> bool:
    return is_admin(user) or is_doctor(user)


@login_required
def home(request):
    if is_admin(request.user):
        stats = {
            'total_patients': Patient.objects.count(),
            'total_doctors': Doctor.objects.count(),
            'total_receptionists': Receptionist.objects.count(),
            'pending_appointments': Appointment.objects.filter(
                status=Appointment.STATUS_PENDING
            ).count(),
        }
        return render(request, 'admin_dashboard.html', stats)

    if is_doctor(request.user):
        doctor = getattr(request.user, 'doctor_profile', None)
        if not doctor:
            messages.error(request, "Doctor profile not found. Please contact an administrator.")
            return redirect('login')

        queue = Appointment.objects.select_related('patient', 'service').filter(
            doctor=doctor,
            status=Appointment.STATUS_PENDING,
        ).order_by('time')

        upcoming = Appointment.objects.select_related('patient', 'service').filter(
            doctor=doctor,
            status=Appointment.STATUS_CONFIRMED,
        ).order_by('time')

        history = Appointment.objects.select_related('patient', 'service').filter(
            doctor=doctor,
            status=Appointment.STATUS_COMPLETED,
        ).order_by('-completed_at', '-time')

        for appointment in upcoming:
            appointment.conclusion_form = AppointmentConclusionForm(instance=appointment)

        patients = Patient.objects.filter(appointment__doctor=doctor).distinct()

        stats = {
            'pending_total': queue.count(),
            'upcoming_total': upcoming.count(),
            'completed_total': history.count(),
            'panel_patients': patients.count(),
        }
        return render(
            request,
            'doctor_dashboard.html',
            {
                'queue': queue,
                'upcoming': upcoming,
                'history': history,
                'patients': patients,
                'stats': stats,
                'rejection_choices': Appointment.REJECTION_REASON_CHOICES,
            },
        )

    if is_receptionist(request.user):
        return render(
            request,
            'receptionist_dashboard.html',
            {
                'patients_count': Patient.objects.count(),
                'pending_appointments': Appointment.objects.filter(
                    status=Appointment.STATUS_PENDING
                ).count(),
            },
        )

    return render(request, 'home.html')


@login_required
@user_passes_test(admin_or_receptionist)
def patients(request):
    all_patients = Patient.objects.all().order_by('name')
    return render(request, 'patients.html', {'patients': all_patients})


@login_required
def patient_detail(request, id):
    patient = get_object_or_404(Patient, id=id)
    history = Appointment.objects.select_related('doctor__user', 'service').filter(
        patient=patient
    ).order_by('-time')

    if is_admin(request.user) or is_receptionist(request.user):
        access_granted = True
    elif is_doctor(request.user):
        doctor = getattr(request.user, 'doctor_profile', None)
        access_granted = bool(
            doctor and history.filter(doctor=doctor).exists()
        )
    else:
        access_granted = False

    if not access_granted:
        messages.error(
            request,
            "You do not have permission to view this patient's records."
        )
        return redirect('home')

    return render(
        request,
        'patient_detail.html',
        {
            'patient': patient,
            'appointments_history': history,
        },
    )


@login_required
@user_passes_test(is_admin)
def doctors(request):
    all_doctors = Doctor.objects.select_related('user').all().order_by('name')
    return render(request, 'doctors.html', {'doctors': all_doctors})


@login_required
def services(request):
    all_services = Service.objects.all().order_by('name')
    return render(request, 'services.html', {'services': all_services})


@login_required
@user_passes_test(admin_or_receptionist)
def appointments(request):
    all_appointments = Appointment.objects.select_related(
        'patient', 'doctor__user', 'service'
    ).order_by('time')
    return render(request, 'appointments.html', {'appointments': all_appointments})


@login_required
@user_passes_test(admin_or_receptionist)
def create_patient(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient registered successfully.")
            return redirect('patients')
    else:
        form = PatientForm()
    return render(request, 'create_patient.html', {'form': form})


@login_required
@user_passes_test(admin_or_receptionist)
def update_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    form = PatientForm(request.POST or None, instance=patient)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Patient details updated.")
        return redirect('patients')
    return render(request, 'update_patient.html', {'form': form})


@login_required
@user_passes_test(admin_or_receptionist)
def delete_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    if request.method == "POST":
        patient.delete()
        messages.success(request, "Patient removed.")
        return redirect('patients')
    return render(request, 'delete_patient.html', {'patient': patient})


@login_required
@user_passes_test(is_admin)
def receptionists(request):
    all_receptionists = Receptionist.objects.select_related('user').all().order_by('name')
    return render(request, 'receptionists.html', {'receptionists': all_receptionists})


@login_required
@user_passes_test(is_admin)
def create_receptionist(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        receptionist_form = ReceptionistForm(request.POST)
        if user_form.is_valid() and receptionist_form.is_valid():
            user = user_form.save()
            _ensure_group_membership(user, 'Receptionist')
            receptionist = receptionist_form.save(commit=False)
            receptionist.user = user
            receptionist.email = user.email
            receptionist.save()
            messages.success(request, "Receptionist registered successfully.")
            return redirect('receptionists')
    else:
        user_form = UserRegistrationForm()
        receptionist_form = ReceptionistForm()
    return render(
        request,
        'create_receptionist.html',
        {'user_form': user_form, 'receptionist_form': receptionist_form},
    )


@login_required
@user_passes_test(is_admin)
def update_receptionist(request, id):
    receptionist = get_object_or_404(Receptionist, id=id)
    user = receptionist.user
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=user)
        receptionist_form = ReceptionistForm(request.POST, instance=receptionist)
        if user_form.is_valid() and receptionist_form.is_valid():
            user_form.save()
            updated_receptionist = receptionist_form.save(commit=False)
            updated_receptionist.email = user.email
            updated_receptionist.save()
            messages.success(request, "Receptionist details updated.")
            return redirect('receptionists')
    else:
        user_form = UserUpdateForm(instance=user)
        receptionist_form = ReceptionistForm(instance=receptionist)
    return render(
        request,
        'update_receptionist.html',
        {'user_form': user_form, 'receptionist_form': receptionist_form},
    )


@login_required
@user_passes_test(is_admin)
def delete_receptionist(request, id):
    receptionist = get_object_or_404(Receptionist, id=id)
    if request.method == "POST":
        user = receptionist.user
        receptionist.delete()
        user.delete()
        messages.success(request, "Receptionist removed.")
        return redirect('receptionists')
    return render(request, 'delete_receptionist.html', {'receptionist': receptionist})


@login_required
@user_passes_test(is_admin)
def create_doctor(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        doctor_form = DoctorForm(request.POST)
        if user_form.is_valid() and doctor_form.is_valid():
            user = user_form.save()
            _ensure_group_membership(user, 'Doctor')
            doctor = doctor_form.save(commit=False)
            doctor.user = user
            doctor.email = user.email
            doctor.save()
            messages.success(request, "Doctor registered successfully.")
            return redirect('doctors')
    else:
        user_form = UserRegistrationForm()
        doctor_form = DoctorForm()
    return render(
        request,
        'create_doctor.html',
        {'user_form': user_form, 'doctor_form': doctor_form},
    )


@login_required
@user_passes_test(is_admin)
def update_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    user = doctor.user
    if user is None:
        messages.error(
            request,
            "This doctor does not have an associated user account. Please delete and recreate the doctor to assign credentials.",
        )
        return redirect('doctors')
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=user)
        doctor_form = DoctorForm(request.POST, instance=doctor)
        if user_form.is_valid() and doctor_form.is_valid():
            user_form.save()
            updated_doctor = doctor_form.save(commit=False)
            updated_doctor.email = user.email
            updated_doctor.save()
            messages.success(request, "Doctor details updated.")
            return redirect('doctors')
    else:
        user_form = UserUpdateForm(instance=user)
        doctor_form = DoctorForm(instance=doctor)
    return render(
        request,
        'update_doctor.html',
        {'user_form': user_form, 'doctor_form': doctor_form},
    )


@login_required
@user_passes_test(is_admin)
def delete_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)
    if request.method == "POST":
        user = doctor.user
        doctor.delete()
        if user:
            user.delete()
        messages.success(request, "Doctor removed.")
        return redirect('doctors')
    return render(request, 'delete_doctor.html', {'doctor': doctor})


@login_required
@user_passes_test(is_admin)
def create_service(request):
    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Service created successfully.")
            return redirect('services')
    else:
        form = ServiceForm()
    return render(request, 'create_service.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def update_service(request, id):
    service = get_object_or_404(Service, id=id)
    form = ServiceForm(request.POST or None, instance=service)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Service updated.")
        return redirect('services')
    return render(request, 'update_service.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def delete_service(request, id):
    service = get_object_or_404(Service, id=id)
    if request.method == "POST":
        service.delete()
        messages.success(request, "Service removed.")
        return redirect('services')
    return render(request, 'delete_service.html', {'service': service})


@login_required
@user_passes_test(admin_or_receptionist)
def create_appointment(request):
    doctor_schedules = []
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.status = Appointment.STATUS_PENDING
            appointment.rejection_reason = ''
            appointment.rejection_note = ''
            appointment.save()
            messages.success(request, "Appointment booked. Waiting for doctor's confirmation.")
            return redirect('appointments')
    else:
        form = AppointmentForm()

    upcoming = Appointment.objects.select_related('doctor', 'patient').filter(
        status__in=[Appointment.STATUS_PENDING, Appointment.STATUS_CONFIRMED]
    ).order_by('time')
    grouped = defaultdict(list)
    for appointment in upcoming:
        grouped[appointment.doctor_id].append(appointment)

    for doctor in Doctor.objects.order_by('name'):
        doctor_schedules.append((doctor, grouped.get(doctor.id, [])))

    return render(
        request,
        'create_appointment.html',
        {
            'form': form,
            'doctor_schedules': doctor_schedules,
        },
    )


@login_required
@user_passes_test(admin_or_receptionist)
def update_appointment(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    form = AppointmentForm(request.POST or None, instance=appointment)
    if request.method == "POST" and form.is_valid():
        updated_appointment = form.save(commit=False)
        if appointment.status == Appointment.STATUS_CONFIRMED:
            messages.warning(request, "Confirmed appointments will remain confirmed unless doctor changes status.")
            updated_appointment.status = appointment.status
            updated_appointment.rejection_reason = appointment.rejection_reason
            updated_appointment.rejection_note = appointment.rejection_note
            updated_appointment.diagnosis = appointment.diagnosis
            updated_appointment.condition_summary = appointment.condition_summary
            updated_appointment.medications = appointment.medications
            updated_appointment.doctor_comments = appointment.doctor_comments
            updated_appointment.completed_at = appointment.completed_at
        elif appointment.status == Appointment.STATUS_COMPLETED:
            messages.warning(request, "Completed appointments cannot be reverted.")
            updated_appointment.status = appointment.status
            updated_appointment.rejection_reason = appointment.rejection_reason
            updated_appointment.rejection_note = appointment.rejection_note
            updated_appointment.diagnosis = appointment.diagnosis
            updated_appointment.condition_summary = appointment.condition_summary
            updated_appointment.medications = appointment.medications
            updated_appointment.doctor_comments = appointment.doctor_comments
            updated_appointment.completed_at = appointment.completed_at
        else:
            updated_appointment.status = Appointment.STATUS_PENDING
            updated_appointment.rejection_reason = ''
            updated_appointment.rejection_note = ''
            updated_appointment.diagnosis = ''
            updated_appointment.condition_summary = ''
            updated_appointment.medications = ''
            updated_appointment.doctor_comments = ''
            updated_appointment.completed_at = None
        updated_appointment.save()
        messages.success(request, "Appointment updated.")
        return redirect('appointments')
    return render(request, 'update_appointment.html', {'form': form})


@login_required
@user_passes_test(admin_or_receptionist)
def delete_appointment(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    if request.method == "POST":
        appointment.delete()
        messages.success(request, "Appointment deleted.")
        return redirect('appointments')
    return render(request, 'delete_appointment.html', {'appointment': appointment})


@login_required
@user_passes_test(admin_or_doctor)
def confirm_appointment(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    if request.method != "POST":
        return redirect('home')
    doctor = getattr(request.user, 'doctor_profile', None)
    if is_doctor(request.user) and appointment.doctor != doctor:
        messages.error(request, "You can only confirm appointments assigned to you.")
        return redirect('home')
    action = request.POST.get('action', 'confirm').lower()
    if action == 'confirm':
        appointment.status = Appointment.STATUS_CONFIRMED
        appointment.rejection_reason = ''
        appointment.rejection_note = ''
        appointment.save(update_fields=['status', 'rejection_reason', 'rejection_note'])
        messages.success(request, "Appointment confirmed.")
    elif action == 'reject':
        reason = request.POST.get('rejection_reason')
        valid_codes = {code for code, _ in Appointment.REJECTION_REASON_CHOICES}
        if reason not in valid_codes:
            messages.error(request, "Select a valid decline reason.")
            return redirect('home')
        rejection_note = request.POST.get('rejection_note', '').strip()
        if reason == 'CUSTOM' and not rejection_note:
            messages.error(request, "Please include context when selecting a custom reason.")
            return redirect('home')
        appointment.status = Appointment.STATUS_REJECTED
        appointment.rejection_reason = reason
        appointment.rejection_note = rejection_note if reason == 'CUSTOM' else ''
        appointment.save(update_fields=['status', 'rejection_reason', 'rejection_note'])
        messages.info(request, "Appointment declined. Reception can see your reason.")
    else:
        messages.error(request, "Unknown action.")
    return redirect('home')


@login_required
@user_passes_test(admin_or_doctor)
def complete_appointment(request, id):
    appointment = get_object_or_404(Appointment, id=id)
    if request.method != "POST":
        return redirect('home')
    doctor = getattr(request.user, 'doctor_profile', None)
    if is_doctor(request.user) and appointment.doctor != doctor:
        messages.error(request, "You can only complete appointments assigned to you.")
        return redirect('home')
    if appointment.status not in (Appointment.STATUS_CONFIRMED, Appointment.STATUS_COMPLETED):
        messages.error(request, "Only confirmed appointments can be completed.")
        return redirect('home')
    form = AppointmentConclusionForm(request.POST, instance=appointment)
    if form.is_valid():
        completed_appointment = form.save(commit=False)
        completed_appointment.status = Appointment.STATUS_COMPLETED
        completed_appointment.completed_at = timezone.now()
        completed_appointment.rejection_reason = appointment.rejection_reason
        completed_appointment.rejection_note = appointment.rejection_note
        completed_appointment.save()
        messages.success(request, "Appointment marked as completed.")
    else:
        error_text = "; ".join(
            [error for errors in form.errors.values() for error in errors]
        )
        messages.error(request, f"Please correct the conclusion details: {error_text}")
    return redirect('home')


@require_POST
@login_required
def logout_user(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')
