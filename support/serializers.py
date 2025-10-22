from rest_framework import serializers
from .models import Booking, CancelledBooking, ProcessLog


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'


class CreateBookingSerializer(serializers.Serializer):
    pnr = serializers.CharField()
    flight_id = serializers.IntegerField()
    source_airport_code = serializers.CharField()
    destination_airport_code = serializers.CharField()
    scheduled_departure = serializers.DateTimeField()
    scheduled_arrival = serializers.DateTimeField()
    assigned_seat = serializers.CharField(required=False, allow_null=True)


class CancelBookingSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()
    cancellation_charges = serializers.DecimalField(max_digits=8, decimal_places=2)
    refund_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    refund_date = serializers.DateTimeField()


class CancelledBookingSerializer(serializers.ModelSerializer):
    booking = BookingSerializer()

    class Meta:
        model = CancelledBooking
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = __import__('support.models', fromlist=['Message']).Message
        fields = '__all__'


class VerifyPNRSerializer(serializers.Serializer):
    pnr = serializers.CharField()


class ProcessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessLog
        fields = '__all__'
