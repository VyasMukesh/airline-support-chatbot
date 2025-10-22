"""
Test complete flow: list bookings → select → query → cancel → list again
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asapp.settings')
django.setup()

from django.test import Client
from support.models import Booking, CancelledBooking

c = Client()
s = c.session
s['verified_pnr'] = 'ABC123'
s.save()

print('=== COMPLETE FLOW TEST ===\n')

print('1. List all bookings for ABC123:')
r1 = c.get('/api/bookings?pnr=ABC123')
bookings = r1.json()
print(f'   Found {len(bookings)} bookings')
for b in bookings:
    print(f'   - Flight {b["flight_id"]}: {b["source_airport_code"]} → {b["destination_airport_code"]} (Status: {b["current_status"]})')

if not bookings:
    print('   ⚠️  No bookings found! Run tools/add_more_bookings.py first.')
    sys.exit(0)

print('\n2. Select first booking:')
first_booking_id = bookings[0]['id']
r2 = c.post('/process', {'message': 'select', 'booking_id': first_booking_id}, content_type='application/json')
print(f'   {r2.json().get("reply")}')
print(f'   Selected booking ID: {first_booking_id}')

print('\n3. Query seat:')
r3 = c.post('/process', {'message': 'seat'}, content_type='application/json')
print(f'   {r3.json().get("reply")}')

print('\n4. Cancel booking:')
r4 = c.post('/api/flight/cancel', {'booking_id': first_booking_id}, content_type='application/json')
print(f'   Cancelled booking {first_booking_id}')

# Verify it's in CancelledBooking table
cancelled = CancelledBooking.objects.filter(booking_id=first_booking_id).first()
if cancelled:
    print(f'   ✓ Found in CancelledBooking table')
    print(f'     Cancellation charges: ${cancelled.cancellation_charges}')
    print(f'     Refund amount: ${cancelled.refund_amount}')

print('\n5. List bookings again:')
r5 = c.get('/api/bookings?pnr=ABC123')
new_bookings = r5.json()
print(f'   Found {len(new_bookings)} bookings (was {len(bookings)} before)')
for b in new_bookings:
    print(f'   - Flight {b["flight_id"]}: {b["source_airport_code"]} → {b["destination_airport_code"]} (Status: {b["current_status"]})')

if len(new_bookings) < len(bookings):
    print(f'\n✅ SUCCESS! Cancelled booking is hidden from list.')
else:
    print(f'\n⚠️  WARNING: Booking count didn\'t decrease.')

print('\n6. Check cancelled bookings endpoint:')
r6 = c.get('/api/cancelled_bookings?pnr=ABC123')
cancelled_list = r6.json()
print(f'   Found {len(cancelled_list)} cancelled bookings')
for cb in cancelled_list:
    print(f'   - Flight {cb["booking"]["flight_id"]}: Cancelled at {cb["cancelled_at"]}')

print('\n✅ All tests completed!')
