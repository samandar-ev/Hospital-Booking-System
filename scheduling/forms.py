from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .models import Appointment, Doctor, Patient, Receptionist, Service


class StyledFormMixin:
    """Add the shared CSS classes to every form widget."""

    control_class = 'form-control'
    select_class = 'form-select'
    checkbox_class = 'form-check-input'

    def _apply_styling(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = f"{widget.attrs.get('class', '')} {self.checkbox_class}".strip()
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs['class'] = f"{widget.attrs.get('class', '')} {self.select_class}".strip()
            else:
                widget.attrs['class'] = f"{widget.attrs.get('class', '')} {self.control_class}".strip()
                widget.attrs.setdefault('placeholder', field.label)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_styling()


class UserRegistrationForm(StyledFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserUpdateForm(StyledFormMixin, ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class PatientForm(StyledFormMixin, ModelForm):
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'YYYY-MM-DD'}))

    class Meta:
        model = Patient
        fields = '__all__'

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        if not phone.startswith("998") or len(phone) != 12:
            raise ValidationError("Phone number must be in format: 998XXXXXXXXX")
        return phone


class DoctorForm(StyledFormMixin, ModelForm):
    class Meta:
        model = Doctor
        fields = ('name', 'specialization', 'phone_number')


class ReceptionistForm(StyledFormMixin, ModelForm):
    class Meta:
        model = Receptionist
        fields = ('name', 'phone_number')


class ServiceForm(StyledFormMixin, ModelForm):
    class Meta:
        model = Service
        fields = '__all__'


class AppointmentForm(StyledFormMixin, ModelForm):
    time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    class Meta:
        model = Appointment
        fields = ('patient', 'doctor', 'service', 'time')


class LoginForm(StyledFormMixin, AuthenticationForm):
    control_class = 'form-control form-control-lg'


class AppointmentConclusionForm(StyledFormMixin, ModelForm):
    class Meta:
        model = Appointment
        fields = ('diagnosis', 'condition_summary', 'medications', 'doctor_comments')
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
            'condition_summary': forms.Textarea(attrs={'rows': 3}),
            'medications': forms.Textarea(attrs={'rows': 3}),
            'doctor_comments': forms.Textarea(attrs={'rows': 3}),
        }
