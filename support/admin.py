from django.contrib import admin
from .models import Booking, CancelledBooking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('pnr', 'flight_id', 'assigned_seat', 'current_status', 'booked_at')
    search_fields = ('pnr', 'flight_id')


@admin.register(CancelledBooking)
class CancelledBookingAdmin(admin.ModelAdmin):
    list_display = ('booking', 'cancelled_at', 'refund_amount')
