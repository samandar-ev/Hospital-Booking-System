from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='registration/login.html',
            authentication_form=LoginForm,
        ),
        name='login',
    ),
    path('logout/', views.logout_user, name='logout'),
    path('', views.home, name='home'),
    path('patients/', views.patients, name='patients'),
    path('patients/create/', views.create_patient, name='create_patient'),
    path('patients/update/<int:id>/', views.update_patient, name='update_patient'),
    path('patients/delete/<int:id>/', views.delete_patient, name='delete_patient'),
    path('patients/<int:id>/detail/', views.patient_detail, name='patient_detail'),
    path('doctors/', views.doctors, name='doctors'),
    path('doctors/create/', views.create_doctor, name='create_doctor'),
    path('doctors/update/<int:id>/', views.update_doctor, name='update_doctor'),
    path('doctors/delete/<int:id>/', views.delete_doctor, name='delete_doctor'),
    path('receptionists/', views.receptionists, name='receptionists'),
    path('receptionists/create/', views.create_receptionist, name='create_receptionist'),
    path('receptionists/update/<int:id>/', views.update_receptionist, name='update_receptionist'),
    path('receptionists/delete/<int:id>/', views.delete_receptionist, name='delete_receptionist'),
    path('services/', views.services, name='services'),
    path('services/create/', views.create_service, name='create_service'),
    path('services/update/<int:id>/', views.update_service, name='update_service'),
    path('services/delete/<int:id>/', views.delete_service, name='delete_service'),
    path('appointments/', views.appointments, name='appointments'),
    path('appointments/create/', views.create_appointment, name='create_appointment'),
    path('appointments/update/<int:id>/', views.update_appointment, name='update_appointment'),
    path('appointments/delete/<int:id>/', views.delete_appointment, name='delete_appointment'),
    path('appointments/<int:id>/confirm/', views.confirm_appointment, name='confirm_appointment'),
    path('appointments/<int:id>/complete/', views.complete_appointment, name='complete_appointment'),
]
