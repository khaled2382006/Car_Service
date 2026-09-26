from django.contrib import admin

from .models import (
    Appointment,
    MaintenanceRecord,
    Service,
    SparePart,
    Technician,
    Vehicle,
)


admin.site.register(Vehicle)
admin.site.register(MaintenanceRecord)
admin.site.register(Technician)
admin.site.register(Service)
admin.site.register(SparePart)
admin.site.register(Appointment)