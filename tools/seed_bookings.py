from support.models import Booking
from django.utils import timezone

def run():
    now = timezone.now()
    samples = [
        {'pnr':'ABC123','flight_id':1111,'source_airport_code':'JFK','destination_airport_code':'LAX','scheduled_departure':now,'scheduled_arrival':now,'assigned_seat':'10A'},
        {'pnr':'XYZ123','flight_id':2222,'source_airport_code':'SFO','destination_airport_code':'BOS','scheduled_departure':now,'scheduled_arrival':now,'assigned_seat':'7B'},
    ]
    for s in samples:
        Booking.objects.create(**s)
    print('Seeded bookings')

if __name__ == '__main__':
    run()
