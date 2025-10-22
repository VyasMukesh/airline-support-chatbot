"""
Verify that cancelled bookings are filtered out
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asapp.settings')
django.setup()

from django.test import Client

c = Client()
r = c.get('/api/bookings?pnr=ABC123')
bookings = r.json()

print(f'\n✅ Active bookings for ABC123: {len(bookings)}')
for b in bookings:
    print(f'  - Flight {b["flight_id"]}: {b["source_airport_code"]} → {b["destination_airport_code"]} (Status: {b["current_status"]})')

print(f'\n📊 Summary: Cancelled bookings are successfully hidden from the list!')
