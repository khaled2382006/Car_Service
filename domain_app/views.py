from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    AppointmentForm,
    MaintenanceRecordForm,
    VehicleForm,
)

from .models import (
    Appointment,
    MaintenanceRecord,
    Service,
    SparePart,
    Technician,
    Vehicle,
)


# =========================================================
# GLOBAL SEARCH
# =========================================================

@login_required
def global_search(request):
    query = request.GET.get("q", "").strip()

    vehicles = []
    appointments = []
    maintenance_records = []
    services = []
    technicians = []

    if query:
        vehicles = Vehicle.objects.filter(
            owner=request.user
        ).filter(
            Q(make__icontains=query) |
            Q(model__icontains=query) |
            Q(license_plate__icontains=query) |
            Q(vin__icontains=query) |
            Q(year__icontains=query)
        )

        appointments = Appointment.objects.filter(
            vehicle__owner=request.user
        ).filter(
            Q(vehicle__make__icontains=query) |
            Q(vehicle__model__icontains=query) |
            Q(service__name__icontains=query) |
            Q(technician__name__icontains=query) |
            Q(status__icontains=query) |
            Q(notes__icontains=query)
        ).select_related("vehicle", "service", "technician")

        maintenance_records = MaintenanceRecord.objects.filter(
            vehicle__owner=request.user
        ).filter(
            Q(service_name__icontains=query) |
            Q(description__icontains=query) |
            Q(vehicle__make__icontains=query) |
            Q(vehicle__model__icontains=query) |
            Q(notes__icontains=query)
        ).select_related("vehicle")

        services = Service.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

        technicians = Technician.objects.filter(
            Q(name__icontains=query) |
            Q(specialization__icontains=query)
        )

    total_results = (
        len(vehicles) +
        len(appointments) +
        len(maintenance_records) +
        len(services) +
        len(technicians)
    )

    return render(
        request,
        "domain_app/search_results.html",
        {
            "query": query,
            "vehicles": vehicles,
            "appointments": appointments,
            "maintenance_records": maintenance_records,
            "services": services,
            "technicians": technicians,
            "total_results": total_results,
        },
    )


# =========================================================
# DASHBOARD
# =========================================================

@login_required
def app_home(request):
    vehicles_count = Vehicle.objects.filter(
        owner=request.user
    ).count()

    appointments_count = Appointment.objects.filter(
        vehicle__owner=request.user
    ).count()

    maintenance_count = MaintenanceRecord.objects.filter(
        vehicle__owner=request.user
    ).count()

    technicians_count = Technician.objects.count()
    services_count = Service.objects.count()
    spare_parts_count = SparePart.objects.count()

    context = {
        "vehicles_count": vehicles_count,
        "appointments_count": appointments_count,
        "maintenance_count": maintenance_count,
        "technicians_count": technicians_count,
        "services_count": services_count,
        "spare_parts_count": spare_parts_count,
    }

    return render(
        request,
        "domain_app/app_home.html",
        context
    )


# =========================================================
# VEHICLES
# =========================================================

@login_required
def vehicle_list(request):
    query = request.GET.get("q", "").strip()
    vehicles = Vehicle.objects.filter(
        owner=request.user
    )

    if query:
        vehicles = vehicles.filter(
            Q(make__icontains=query) |
            Q(model__icontains=query) |
            Q(license_plate__icontains=query) |
            Q(vin__icontains=query) |
            Q(year__icontains=query)
        )

    return render(
        request,
        "domain_app/vehicle_list.html",
        {
            "vehicles": vehicles,
            "query": query,
        }
    )


@login_required
def vehicle_create(request):

    if request.method == "POST":

        form = VehicleForm(request.POST)

        if form.is_valid():

            vehicle = form.save(commit=False)

            vehicle.owner = request.user

            vehicle.save()

            return redirect("vehicle_list")

    else:

        form = VehicleForm()

    return render(
        request,
        "domain_app/vehicle_form.html",
        {
            "form": form
        }
    )


@login_required
def vehicle_detail(request, vehicle_id):

    vehicle = get_object_or_404(
        Vehicle,
        id=vehicle_id,
        owner=request.user
    )

    maintenance_records = vehicle.maintenance_records.all()

    appointments = vehicle.appointments.all()

    return render(
        request,
        "domain_app/vehicle_detail.html",
        {
            "vehicle": vehicle,
            "maintenance_records": maintenance_records,
            "appointments": appointments,
        }
    )


# =========================================================
# MAINTENANCE
# =========================================================

@login_required
def maintenance_create(request, vehicle_id):

    vehicle = get_object_or_404(
        Vehicle,
        id=vehicle_id,
        owner=request.user
    )

    if request.method == "POST":

        form = MaintenanceRecordForm(request.POST)

        if form.is_valid():

            record = form.save(commit=False)

            record.vehicle = vehicle

            record.save()

            return redirect(
                "vehicle_detail",
                vehicle_id=vehicle.id
            )

    else:

        form = MaintenanceRecordForm()

    return render(
        request,
        "domain_app/maintenance_form.html",
        {
            "form": form,
            "vehicle": vehicle,
        }
    )


# =========================================================
# APPOINTMENTS
# =========================================================

@login_required
def appointment_create(request):

    user_vehicles = Vehicle.objects.filter(
        owner=request.user
    )

    if request.method == "POST":

        form = AppointmentForm(request.POST)

        form.fields["vehicle"].queryset = user_vehicles

        if form.is_valid():

            appointment = form.save(commit=False)
            if appointment.vehicle.owner != request.user:

                return redirect("vehicle_list")

            appointment.save()

            return redirect(
                "vehicle_detail",
                vehicle_id=appointment.vehicle.id
            )

    else:

        form = AppointmentForm()

        form.fields["vehicle"].queryset = user_vehicles

    return render(
        request,
        "domain_app/appointment_form.html",
        {
            "form": form
        }
    )


# =========================================================
# TECHNICIANS
# =========================================================

@login_required
def technician_list(request):

    technicians = Technician.objects.all()

    return render(
        request,
        "domain_app/technician_list.html",
        {
            "technicians": technicians
        }
    )


# =========================================================
# SERVICES
# =========================================================

@login_required
def service_list(request):

    services = Service.objects.all()

    return render(
        request,
        "domain_app/service_list.html",
        {
            "services": services
        }
    )


# =========================================================
# SPARE PARTS
# =========================================================

@login_required
def spare_part_list(request):

    spare_parts = SparePart.objects.all()

    return render(
        request,
        "domain_app/spare_part_list.html",
        {
            "spare_parts": spare_parts
        }
    )
@login_required
def app_dashboard(request):
    vehicles = Vehicle.objects.filter(
        owner=request.user
    )

    appointments = Appointment.objects.filter(
        vehicle__owner=request.user
    ).select_related(
        "vehicle",
        "technician",
        "service",
    ).order_by(
        "appointment_date",
        "appointment_time",
    )

    return render(
        request,
        "domain_app/app_dashboard.html",
        {
            "vehicles": vehicles,
            "appointments": appointments,
        },
    )
@login_required
def maintenance_list(request):
    vehicles = Vehicle.objects.filter(
        owner=request.user
    ).prefetch_related("maintenance_records")

    return render(
        request,
        "domain_app/maintenance_list.html",
        {
            "vehicles": vehicles,
        },
    )
@login_required
def appointment_list(request):
    appointments = (
        Appointment.objects
        .filter(vehicle__owner=request.user)
        .select_related(
            "vehicle",
            "technician",
            "service",
        )
        .order_by("appointment_date", "appointment_time")
    )

    return render(
        request,
        "domain_app/appointment_list.html",
        {
            "appointments": appointments,
        },
    )


def service_list(request):
    services = Service.objects.all().order_by("name")

    return render(
        request,
        "domain_app/service_list.html",
        {
            "services": services,
        },
    )


def technician_list(request):
    technicians = Technician.objects.all().order_by("name")

    return render(
        request,
        "domain_app/technician_list.html",
        {
            "technicians": technicians,
        },
    )
@login_required
def appointment_list(request):
    appointments = (
        Appointment.objects
        .filter(vehicle__owner=request.user)
        .select_related("vehicle", "service", "technician")
        .order_by("-appointment_date", "-appointment_time")
    )

    return render(
        request,
        "domain_app/appointment_list.html",
        {
            "appointments": appointments,
        },
    )
@login_required
def maintenance_list(request):
    maintenance_records = (
        MaintenanceRecord.objects
        .filter(vehicle__owner=request.user)
        .select_related("vehicle")
        .order_by("-maintenance_date")
    )

    return render(
        request,
        "domain_app/maintenance_list.html",
        {
            "maintenance_records": maintenance_records,
        },
    )


@login_required
def service_list(request):
    services = Service.objects.all().order_by("name")

    return render(
        request,
        "domain_app/service_list.html",
        {
            "services": services,
        },
    )


@login_required
def technician_list(request):
    technicians = Technician.objects.all().order_by("name")

    return render(
        request,
        "domain_app/technician_list.html",
        {
            "technicians": technicians,
        },
    )