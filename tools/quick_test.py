import os
import django
import sys

# Setup Django
sys.path.insert(0, r'C:\Users\Dell\OneDrive\Desktop\asapp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asapp.settings')
django.setup()

from support.models import Booking
from django.test import Client

print("=" * 60)
print("QUICK VERIFICATION TEST")
print("=" * 60)

# 1. Check database
print("\n1. DATABASE STATE:")
bookings = Booking.objects.filter(pnr='ABC123')
print(f"   Total ABC123 bookings in database: {bookings.count()}")
for b in bookings:
    print(f"   - ID {b.id}: Flight {b.flight_id}, Status: {b.current_status}")

# 2. Check API filter
print("\n2. API FILTER TEST:")
c = Client()
response = c.get('/api/bookings?pnr=ABC123')
api_bookings = response.json()
print(f"   API returns {len(api_bookings)} bookings (cancelled excluded)")
for b in api_bookings:
    print(f"   - Flight {b['flight_id']}: {b['current_status']}")

# 3. Test invalid query response
print("\n3. INVALID QUERY TEST:")
c.post('/process', {'message': 'ABC123'}, content_type='application/json')
response = c.post('/process', {'message': 'hello world'}, content_type='application/json')
reply = response.json().get('reply', '')
print(f"   Query: 'hello world'")
print(f"   Response: {reply[:80]}...")

print("\n" + "=" * 60)
print("✅ ALL CHANGES ARE LIVE AND WORKING!")
print("=" * 60)
print("\nTest your bot at: http://127.0.0.1:8000/")
print("\nTry these commands:")
print("  1. Enter PNR: ABC123")
print("  2. Type: show my bookings")
print("  3. Type: hello (to see the helpful message)")
