import requests
import datetime

BASE = 'http://127.0.0.1:8000'

def pretty(r):
    print(r.status_code)
    try:
        print(r.json())
    except Exception:
        print(r.text)

def main():
    pnr = 'TEST123'
    print('Creating booking...')
    payload = {
        'pnr': pnr,
        'flight_id': 9999,
        'source_airport_code': 'JFK',
        'destination_airport_code': 'LAX',
        'scheduled_departure': '2025-12-01T10:00:00Z',
        'scheduled_arrival': '2025-12-01T16:00:00Z',
        'assigned_seat': '21C'
    }
    r = requests.post(f'{BASE}/api/book', json=payload)
    pretty(r)

    print('\nListing bookings for PNR...')
    r = requests.get(f'{BASE}/api/bookings?pnr={pnr}')
    pretty(r)
    bs = r.json()
    if not bs:
        print('No bookings found — smoke test stops')
        return
    bid = bs[0]['id'] if 'id' in bs[0] else bs[0].get('pk')
    print('\nCancelling booking id', bid)
    cancel_payload = {
        'booking_id': bid,
        'cancellation_charges': 50.0,
        'refund_amount': 200.0,
        'refund_date': (datetime.datetime.utcnow() + datetime.timedelta(days=5)).isoformat() + 'Z'
    }
    r = requests.post(f'{BASE}/api/flight/cancel', json=cancel_payload)
    pretty(r)

    print('\nListing bookings after cancellation (bookings table still shows booking; cancellation stored separately)')
    r = requests.get(f'{BASE}/api/bookings?pnr={pnr}')
    pretty(r)

if __name__ == '__main__':
    main()
