from django import forms
from .models import Vehicle, MaintenanceRecord, Appointment


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            "make",
            "model",
            "year",
            "license_plate",
            "vin",
        ]


class MaintenanceRecordForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRecord
        fields = [
            "service_name",
            "description",
            "maintenance_date",
            "cost",
            "notes",
        ]


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            "vehicle",
            "technician",
            "service",
            "appointment_date",
            "appointment_time",
            "notes",
        ]

        widgets = {
            "appointment_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "appointment_time": forms.TimeInput(
                attrs={"type": "time"}
            ),
        }