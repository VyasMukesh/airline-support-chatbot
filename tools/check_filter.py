"""
Check database state and API filtering
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asapp.settings')
django.setup()

from support.models import Booking
from django.test import Client

print('\n=== DATABASE STATE ===')
bookings = Booking.objects.filter(pnr='ABC123')
print(f'ABC123 Bookings in DB: {bookings.count()}')
for b in bookings:
    print(f'  ID {b.id}: Flight {b.flight_id}, Status: {b.current_status}')

print('\n=== API RESPONSE ===')
c = Client()
r = c.get('/api/bookings?pnr=ABC123')
api_bookings = r.json()
print(f'API returns: {len(api_bookings)} bookings')
for b in api_bookings:
    print(f'  - Flight {b["flight_id"]}: {b["current_status"]}')

print('\n=== ANALYSIS ===')
cancelled_count = Booking.objects.filter(pnr='ABC123', current_status='Cancelled').count()
active_count = Booking.objects.filter(pnr='ABC123').exclude(current_status='Cancelled').count()
print(f'Cancelled bookings: {cancelled_count}')
print(f'Active bookings: {active_count}')
print(f'API showing: {len(api_bookings)} bookings')

if len(api_bookings) == active_count:
    print('\n✅ Filter is working correctly!')
else:
    print('\n⚠️ Filter may have an issue')
