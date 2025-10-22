"""
Test Script: Verify Cancelled Bookings Are Deleted from Database
"""
import os
import django
import sys

sys.path.insert(0, r'C:\Users\Dell\OneDrive\Desktop\asapp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asapp.settings')
django.setup()

from support.models import Booking, CancelledBooking
from django.test import Client

print("=" * 70)
print("TEST: Cancelled Bookings Are DELETED from Database")
print("=" * 70)

# Step 1: Check initial state
print("\n1. INITIAL STATE - ABC123 Bookings:")
initial_bookings = Booking.objects.filter(pnr='ABC123')
print(f"   Total bookings in database: {initial_bookings.count()}")
for b in initial_bookings:
    print(f"   - ID {b.id}: Flight {b.flight_id}, Status: {b.current_status}")

if initial_bookings.count() == 0:
    print("\n   ⚠ No bookings found! Please add bookings first.")
    sys.exit(1)

# Step 2: Test API returns all bookings
print("\n2. API TEST - List Bookings:")
c = Client()
response = c.get('/api/bookings?pnr=ABC123')
api_bookings = response.json()
print(f"   API returns {len(api_bookings)} bookings")
for b in api_bookings:
    print(f"   - Flight {b['flight_id']}: {b['current_status']}")

# Step 3: Cancel the first booking
print("\n3. CANCELLING FIRST BOOKING:")
first_booking = initial_bookings.first()
print(f"   Cancelling Booking ID {first_booking.id} (Flight {first_booking.flight_id})")

cancel_response = c.post(
    '/api/cancel',
    {'booking_id': first_booking.id, 'cancellation_charges': 50.0, 'refund_amount': 0.0},
    content_type='application/json'
)

if cancel_response.status_code == 200:
    print(f"   ✅ Cancellation successful!")
    print(f"   Response: {cancel_response.json().get('message', 'Success')}")
else:
    print(f"   ❌ Cancellation failed: {cancel_response.content}")

# Step 4: Verify booking is DELETED from database
print("\n4. DATABASE CHECK - After Cancellation:")
remaining_bookings = Booking.objects.filter(pnr='ABC123')
print(f"   Bookings remaining in database: {remaining_bookings.count()}")
for b in remaining_bookings:
    print(f"   - ID {b.id}: Flight {b.flight_id}, Status: {b.current_status}")

deleted_booking = Booking.objects.filter(id=first_booking.id).first()
if deleted_booking is None:
    print(f"   ✅ Booking ID {first_booking.id} has been DELETED from database!")
else:
    print(f"   ❌ Booking ID {first_booking.id} still exists in database!")

# Step 5: Verify CancelledBooking record exists
print("\n5. CANCELLED BOOKINGS TABLE:")
cancelled = CancelledBooking.objects.all()
print(f"   Total cancelled bookings: {cancelled.count()}")
for cb in cancelled:
    print(f"   - Booking ID: {cb.booking_id}, Charges: ${cb.cancellation_charges}, Cancelled at: {cb.cancelled_at}")

# Step 6: Test API again - should return fewer bookings
print("\n6. API TEST - After Cancellation:")
response2 = c.get('/api/bookings?pnr=ABC123')
api_bookings2 = response2.json()
print(f"   API now returns {len(api_bookings2)} bookings")
for b in api_bookings2:
    print(f"   - Flight {b['flight_id']}: {b['current_status']}")

if len(api_bookings2) < len(api_bookings):
    print(f"   ✅ Cancelled booking does NOT appear! ({len(api_bookings)} → {len(api_bookings2)})")
else:
    print(f"   ❌ Booking count unchanged!")

# Step 7: Test bot's "show my bookings" query
print("\n7. BOT TEST - 'show my bookings' Query:")
c.post('/process', {'message': 'ABC123'}, content_type='application/json')
bot_response = c.post('/process', {'message': 'show my bookings'}, content_type='application/json')
bot_data = bot_response.json()
if 'bookings' in bot_data:
    print(f"   Bot returns {len(bot_data['bookings'])} bookings")
    for b in bot_data['bookings']:
        print(f"   - Flight {b['flight_id']}: {b['current_status']}")
    if len(bot_data['bookings']) == len(api_bookings2):
        print(f"   ✅ Bot and API results match!")
    else:
        print(f"   ❌ Bot and API results differ!")
else:
    print(f"   Bot reply: {bot_data.get('reply', '')}")

# Step 8: Test invalid query
print("\n8. INVALID QUERY TEST:")
invalid_response = c.post('/process', {'message': 'hello world'}, content_type='application/json')
invalid_reply = invalid_response.json().get('reply', '')
print(f"   Query: 'hello world'")
print(f"   Response: {invalid_reply[:100]}")
if "Please enter a valid query" in invalid_reply:
    print(f"   ✅ Invalid query prompt is working!")
else:
    print(f"   ❌ Invalid query prompt not found!")

print("\n" + "=" * 70)
print("SUMMARY:")
print(f"  • Bookings before cancellation: {initial_bookings.count()}")
print(f"  • Bookings after cancellation: {remaining_bookings.count()}")
print(f"  • Booking was DELETED: {'✅ Yes' if deleted_booking is None else '❌ No'}")
print(f"  • CancelledBooking record created: {'✅ Yes' if cancelled.count() > 0 else '❌ No'}")
print(f"  • API excludes cancelled: {'✅ Yes' if len(api_bookings2) < len(api_bookings) else '❌ No'}")
print(f"  • Invalid query handling: {'✅ Working' if 'Please enter a valid query' in invalid_reply else '❌ Not working'}")
print("=" * 70)
