from datetime import date
from django.utils import timezone
from domain_app.models import (
    Vehicle,
    Appointment,
    Technician,
    Service,
)


def get_user_vehicles(user):
    vehicles = Vehicle.objects.filter(owner=user)

    return {
        "vehicles": [
            {
                "id": vehicle.id,
                "name": str(vehicle),
            }
            for vehicle in vehicles
        ]
    }


def get_user_appointments(user):
    appointments = Appointment.objects.filter(
        vehicle__owner=user
    ).select_related(
        "vehicle",
        "technician",
        "service",
    )

    result = []

    for appointment in appointments:
        result.append({
            "id": appointment.id,
            "vehicle": str(appointment.vehicle),
            "date": str(appointment.appointment_date),
            "time": str(appointment.appointment_time),
            "service": str(appointment.service),
            "technician": str(appointment.technician)
            if appointment.technician
            else "",
            "status": appointment.status,
            "notes": appointment.notes or "",
        })

    return {
        "appointments": result
    }


def get_available_services(user):
    services = Service.objects.all()

    return {
        "services": [
            {
                "id": service.id,
                "name": service.name,
                "description": service.description,
                "base_price": str(service.base_price),
                "estimated_duration": service.estimated_duration,
            }
            for service in services
        ]
    }


def get_available_technicians(user):
    technicians = Technician.objects.filter(
        is_available=True
    )

    return {
        "technicians": [
            {
                "id": technician.id,
                "name": technician.name,
                "specialization": technician.specialization,
            }
            for technician in technicians
        ]
    }



def create_appointment(
    user,
    vehicle_id,
    service_id,
    technician_id,
    appointment_date,
    appointment_time,
    notes="",
):
    try:
        vehicle = Vehicle.objects.filter(
            id=vehicle_id,
            owner=user,
        ).first()

        if not vehicle:
            return {
                "success": False,
                "error": "Vehicle not found or does not belong to the user.",
            }

        service = Service.objects.filter(
            id=service_id
        ).first()

        if not service:
            return {
                "success": False,
                "error": "Service not found.",
            }

        technician = Technician.objects.filter(
            id=technician_id,
            is_available=True,
        ).first()

        if not technician:
            return {
                "success": False,
                "error": "Technician not found or not available.",
            }

        if isinstance(appointment_date, str):
            appointment_date = appointment_date.strip()

            appointment_date = date.fromisoformat(
                appointment_date
            )

        if isinstance(appointment_time, str):
            appointment_time = appointment_time.strip()

            appointment_time = datetime.strptime(
                appointment_time,
                "%H:%M",
            ).time()

        today = timezone.localdate()

        if appointment_date < today:
            return {
                "success": False,
                "error": "You cannot book an appointment in the past.",
            }

        conflict = Appointment.objects.filter(
            technician=technician,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status__in=[
                "pending",
                "confirmed",
                "in_progress",
            ],
        ).exists()

        if conflict:
            return {
                "success": False,
                "error": (
                    "This technician already has an appointment "
                    "at this date and time."
                ),
            }

        appointment = Appointment.objects.create(
            vehicle=vehicle,
            technician=technician,
            service=service,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status="pending",
            notes=notes or "",
        )

        return {
            "success": True,
            "appointment": {
                "id": appointment.id,
                "vehicle": str(vehicle),
                "service": str(service),
                "technician": str(technician),
                "date": str(appointment.appointment_date),
                "time": str(appointment.appointment_time),
                "status": appointment.status,
                "notes": appointment.notes,
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Booking failed: {str(e)}",
        }