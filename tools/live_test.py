"""
Quick Test: Check if changes are working
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("TESTING LIVE SERVER")
print("=" * 70)

# Create a session to maintain cookies
session = requests.Session()

# Test 1: Verify PNR
print("\n1. Verifying PNR ABC123...")
response = session.post(f"{BASE_URL}/api/verify_pnr", 
    json={"pnr": "ABC123"},
    headers={"Content-Type": "application/json"}
)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print(f"   ✅ PNR Verified")
else:
    print(f"   ❌ Failed: {response.text}")

# Test 2: Get bookings list
print("\n2. Getting bookings list...")
response = session.get(f"{BASE_URL}/api/bookings?pnr=ABC123")
print(f"   Status: {response.status_code}")
bookings = response.json()
print(f"   Found {len(bookings)} bookings:")
for b in bookings:
    print(f"     - ID {b['id']}: Flight {b['flight_id']}, Status: {b.get('current_status', 'N/A')}")

# Test 3: Bot query for bookings
print("\n3. Bot Query: 'show my bookings'...")
response = session.post(f"{BASE_URL}/process",
    json={"message": "show my bookings"},
    headers={"Content-Type": "application/json"}
)
print(f"   Status: {response.status_code}")
bot_data = response.json()
print(f"   Reply: {bot_data.get('reply', '')[:100]}")
if 'bookings' in bot_data:
    print(f"   Bot returned {len(bot_data['bookings'])} bookings:")
    for b in bot_data['bookings']:
        print(f"     - Flight {b['flight_id']}: {b.get('current_status', 'N/A')}")

# Test 4: Invalid query
print("\n4. Testing invalid query: 'hello world'...")
response = session.post(f"{BASE_URL}/process",
    json={"message": "hello world"},
    headers={"Content-Type": "application/json"}
)
print(f"   Status: {response.status_code}")
bot_data = response.json()
reply = bot_data.get('reply', '')
print(f"   Reply: {reply}")
if "Please enter a valid query" in reply:
    print(f"   ✅ Fallback message is working!")
else:
    print(f"   ❌ Fallback message NOT working!")

# Test 5: Cancel a booking
if len(bookings) > 0:
    booking_to_cancel = bookings[0]['id']
    print(f"\n5. Cancelling booking ID {booking_to_cancel}...")
    response = session.post(f"{BASE_URL}/api/flight/cancel",
        json={"booking_id": booking_to_cancel, "cancellation_charges": 50.0, "refund_amount": 0.0},
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Response: {result.get('message', 'Success')}")
        
        # Test 6: Check if booking is deleted
        print(f"\n6. Checking if booking {booking_to_cancel} is deleted...")
        response = session.get(f"{BASE_URL}/api/bookings?pnr=ABC123")
        new_bookings = response.json()
        print(f"   Now found {len(new_bookings)} bookings:")
        for b in new_bookings:
            print(f"     - ID {b['id']}: Flight {b['flight_id']}")
        
        if len(new_bookings) < len(bookings):
            print(f"   ✅ Booking deleted! ({len(bookings)} → {len(new_bookings)})")
        else:
            print(f"   ❌ Booking still exists! Count unchanged.")
            # Check if the booking still exists
            still_there = any(b['id'] == booking_to_cancel for b in new_bookings)
            if still_there:
                print(f"   ❌ Booking ID {booking_to_cancel} STILL IN DATABASE!")
            else:
                print(f"   ✅ Booking ID {booking_to_cancel} is gone from results")
    else:
        print(f"   ❌ Cancellation failed: {response.text}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
