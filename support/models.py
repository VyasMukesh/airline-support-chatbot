from django.db import models


class Booking(models.Model):
    pnr = models.CharField(max_length=20, db_index=True)
    flight_id = models.IntegerField()
    source_airport_code = models.CharField(max_length=10)
    destination_airport_code = models.CharField(max_length=10)
    scheduled_departure = models.DateTimeField()
    scheduled_arrival = models.DateTimeField()
    assigned_seat = models.CharField(max_length=10, blank=True, null=True)
    current_status = models.CharField(max_length=50, default='Scheduled')
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pnr} - {self.flight_id} ({self.assigned_seat})"


class CancelledBooking(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='cancellation')
    cancelled_at = models.DateTimeField(auto_now_add=True)
    cancellation_charges = models.DecimalField(max_digits=8, decimal_places=2)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_date = models.DateTimeField()

    def __str__(self):
        return f"Cancelled {self.booking.pnr} - {self.booking.flight_id}"


class Message(models.Model):
    # store all incoming/outgoing messages and metadata
    pnr = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    session_key = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    sender = models.CharField(max_length=10, choices=(('user','user'),('bot','bot')))
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_at} {self.sender}: {self.text[:40]}"


class ProcessLog(models.Model):
    ACTIONS = (
        ('cancel','cancel'),
        ('status','status'),
        ('pets','pets'),
        ('seats','seats'),
        ('verify_pnr','verify_pnr'),
    )
    action = models.CharField(max_length=30, choices=ACTIONS)
    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.SET_NULL)
    pnr = models.CharField(max_length=20, null=True, blank=True)
    payload = models.JSONField(null=True, blank=True)
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.created_at} {self.action} {self.pnr or ''}"
