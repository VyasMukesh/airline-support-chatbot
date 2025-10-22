"""
Script to add more test bookings to the database
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asapp.settings')
django.setup()

from support.models import Booking

# Clear any existing test bookings first (optional)
print("Adding new bookings...")

now = datetime.utcnow()

# Multiple bookings for PNR ABC123
bookings_data = [
    # ABC123 - Multiple flights
    {
        'pnr': 'ABC123',
        'flight_id': 1111,
        'source_airport_code': 'JFK',
        'destination_airport_code': 'LAX',
        'scheduled_departure': now + timedelta(days=1),
        'scheduled_arrival': now + timedelta(days=1, hours=6),
        'assigned_seat': '10A',
        'current_status': 'Scheduled'
    },
    {
        'pnr': 'ABC123',
        'flight_id': 2222,
        'source_airport_code': 'LAX',
        'destination_airport_code': 'SFO',
        'scheduled_departure': now + timedelta(days=3),
        'scheduled_arrival': now + timedelta(days=3, hours=2),
        'assigned_seat': '12B',
        'current_status': 'Scheduled'
    },
    {
        'pnr': 'ABC123',
        'flight_id': 3333,
        'source_airport_code': 'SFO',
        'destination_airport_code': 'ORD',
        'scheduled_departure': now + timedelta(days=5),
        'scheduled_arrival': now + timedelta(days=5, hours=4),
        'assigned_seat': '15C',
        'current_status': 'Scheduled'
    },
    
    # XYZ123 - Multiple flights
    {
        'pnr': 'XYZ123',
        'flight_id': 4444,
        'source_airport_code': 'MIA',
        'destination_airport_code': 'BOS',
        'scheduled_departure': now + timedelta(days=2),
        'scheduled_arrival': now + timedelta(days=2, hours=3),
        'assigned_seat': '8A',
        'current_status': 'Scheduled'
    },
    {
        'pnr': 'XYZ123',
        'flight_id': 5555,
        'source_airport_code': 'BOS',
        'destination_airport_code': 'SEA',
        'scheduled_departure': now + timedelta(days=4),
        'scheduled_arrival': now + timedelta(days=4, hours=5),
        'assigned_seat': '6D',
        'current_status': 'Scheduled'
    },
    {
        'pnr': 'XYZ123',
        'flight_id': 6666,
        'source_airport_code': 'SEA',
        'destination_airport_code': 'DEN',
        'scheduled_departure': now + timedelta(days=6),
        'scheduled_arrival': now + timedelta(days=6, hours=3),
        'assigned_seat': '14F',
        'current_status': 'Scheduled'
    },
    
    # TEST123 - Multiple flights
    {
        'pnr': 'TEST123',
        'flight_id': 7777,
        'source_airport_code': 'ATL',
        'destination_airport_code': 'DFW',
        'scheduled_departure': now + timedelta(days=1),
        'scheduled_arrival': now + timedelta(days=1, hours=2),
        'assigned_seat': '20A',
        'current_status': 'Scheduled'
    },
    {
        'pnr': 'TEST123',
        'flight_id': 8888,
        'source_airport_code': 'DFW',
        'destination_airport_code': 'PHX',
        'scheduled_departure': now + timedelta(days=3),
        'scheduled_arrival': now + timedelta(days=3, hours=2),
        'assigned_seat': '18B',
        'current_status': 'Scheduled'
    },
    {
        'pnr': 'TEST123',
        'flight_id': 9999,
        'source_airport_code': 'PHX',
        'destination_airport_code': 'LAS',
        'scheduled_departure': now + timedelta(days=7),
        'scheduled_arrival': now + timedelta(days=7, hours=1),
        'assigned_seat': '22C',
        'current_status': 'Scheduled'
    },
    
    # PQR456 - New PNR with multiple flights
    {
        'pnr': 'PQR456',
        'flight_id': 1234,
        'source_airport_code': 'EWR',
        'destination_airport_code': 'MCO',
        'scheduled_departure': now + timedelta(days=2),
        'scheduled_arrival': now + timedelta(days=2, hours=3),
        'assigned_seat': '5E',
        'current_status': 'Scheduled'
    },
    {
        'pnr': 'PQR456',
        'flight_id': 5678,
        'source_airport_code': 'MCO',
        'destination_airport_code': 'CLT',
        'scheduled_departure': now + timedelta(days=5),
        'scheduled_arrival': now + timedelta(days=5, hours=2),
        'assigned_seat': '9F',
        'current_status': 'Scheduled'
    },
]

created_count = 0
for booking_data in bookings_data:
    # Check if booking already exists
    existing = Booking.objects.filter(
        pnr=booking_data['pnr'],
        flight_id=booking_data['flight_id']
    ).first()
    
    if existing:
        print(f"⚠️  Booking already exists: PNR {booking_data['pnr']}, Flight {booking_data['flight_id']}")
    else:
        booking = Booking.objects.create(**booking_data)
        created_count += 1
        print(f"✓ Created booking: PNR {booking_data['pnr']}, Flight {booking_data['flight_id']}, {booking_data['source_airport_code']} → {booking_data['destination_airport_code']}, Seat {booking_data['assigned_seat']}")

print(f"\n✅ Created {created_count} new bookings")
print(f"📊 Total bookings in database: {Booking.objects.count()}")

# Show summary by PNR
print("\n📋 Bookings by PNR:")
for pnr in ['ABC123', 'XYZ123', 'TEST123', 'PQR456']:
    count = Booking.objects.filter(pnr=pnr, current_status='Scheduled').count()
    print(f"   {pnr}: {count} active bookings")
