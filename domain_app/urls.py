from django.urls import path

from . import views


urlpatterns = [
    # Dashboard
    path(
        "",
        views.app_dashboard,
        name="app_dashboard",
    ),

    # Vehicles
    path(
        "vehicles/",
        views.vehicle_list,
        name="vehicle_list",
    ),

    path(
        "vehicles/add/",
        views.vehicle_create,
        name="vehicle_create",
    ),

    path(
        "vehicles/<int:vehicle_id>/",
        views.vehicle_detail,
        name="vehicle_detail",
    ),

    # Maintenance
    path(
        "vehicles/<int:vehicle_id>/maintenance/add/",
        views.maintenance_create,
        name="maintenance_create",
    ),

    path(
        "maintenance/",
        views.maintenance_list,
        name="maintenance_list",
    ),

    # Appointments
    path(
        "appointments/",
        views.appointment_list,
        name="appointment_list",
    ),

    path(
        "appointments/add/",
        views.appointment_create,
        name="appointment_create",
    ),

    # Services
    path(
        "services/",
        views.service_list,
        name="service_list",
    ),

    # Technicians
    path(
        "technicians/",
        views.technician_list,
        name="technician_list",
    ),
]