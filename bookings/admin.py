from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "time", "guests", "phone", "status", "created_at")
    list_filter = ("status", "date")
    search_fields = ("name", "email", "phone")
    list_editable = ("status",)
    ordering = ("date", "time")
