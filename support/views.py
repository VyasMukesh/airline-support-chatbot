from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime, timedelta
from django.views.decorators.http import require_http_methods
from .models import Booking, CancelledBooking, ProcessLog
from .serializers import BookingSerializer, CreateBookingSerializer, CancelBookingSerializer, CancelledBookingSerializer
from django.utils.dateparse import parse_datetime
from .serializers import MessageSerializer, VerifyPNRSerializer
from .models import Message
import random
from .intent_classifier import get_intent


def chat(request):
    return render(request, 'support/chat.html')


def home(request):
    # simple homepage with hero search and includes the chat widget
    return render(request, 'support/home.html')


@csrf_exempt
def api_check_session(request):
    """Check if the user's session already has a verified PNR"""
    verified_pnr = request.session.get('verified_pnr')
    if verified_pnr:
        return JsonResponse({'verified': True, 'pnr': verified_pnr})
    return JsonResponse({'verified': False})


def _mock_booking(pnr):
    if pnr.lower() == 'notfound':
        return None
    now = datetime.utcnow()
    return {
        'pnr': pnr,
        'flight_id': 1234,
        'source_airport_code': 'JFK',
        'destination_airport_code': 'LAX',
        'scheduled_departure': (now + timedelta(days=1)).isoformat() + 'Z',
        'scheduled_arrival': (now + timedelta(days=1, hours=6)).isoformat() + 'Z',
        'assigned_seat': '12A',
        'current_departure': (now + timedelta(days=1)).isoformat() + 'Z',
        'current_arrival': (now + timedelta(days=1, hours=6)).isoformat() + 'Z',
        'current_status': 'Scheduled',
    }


def api_get_booking(request):
    # Try returning from DB first
    pnr = request.GET.get('pnr')
    if not pnr:
        return JsonResponse({'message': 'PNR Not Found'}, status=404)
    qs = Booking.objects.filter(pnr__iexact=pnr)
    if qs.exists():
        serializer = BookingSerializer(qs, many=True)
        return JsonResponse(serializer.data, safe=False)
    # fallback to mock
    data = _mock_booking(pnr)
    if not data:
        return JsonResponse({'message': 'PNR Not Found'}, status=404)
    return JsonResponse(data)


@csrf_exempt
def api_cancel_booking(request):
    try:
        payload = json.loads(request.body)
    except Exception:
        return JsonResponse({'message': 'Invalid Request'}, status=400)
    # This endpoint will cancel by booking id if provided
    booking_id = payload.get('booking_id')
    if not booking_id:
        return JsonResponse({'message': 'Booking id required'}, status=400)
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return JsonResponse({'message': 'Booking Not Found'}, status=404)
    # create cancellation entry
    now = datetime.utcnow()
    cancellation_charges = payload.get('cancellation_charges', 50.0)
    refund_amount = payload.get('refund_amount', 0.0)
    refund_date = payload.get('refund_date')
    if isinstance(refund_date, str):
        refund_date = parse_datetime(refund_date)
    # If a cancellation already exists for this booking, return it instead of creating a duplicate
    existing = CancelledBooking.objects.filter(booking=booking).first()
    if existing:
        serializer = CancelledBookingSerializer(existing)
        # log the attempted cancel
        try:
            ProcessLog.objects.create(action='cancel', booking=booking, pnr=booking.pnr, payload=payload, result={'status':'exists'})
        except Exception:
            pass
        return JsonResponse(serializer.data)

    # Create cancellation record
    cancelled = CancelledBooking.objects.create(
        booking=booking,
        cancellation_charges=cancellation_charges,
        refund_amount=refund_amount,
        refund_date=refund_date or (now + timedelta(days=5)),
    )
    
    # Mark booking as Cancelled (keep it in database)
    booking.current_status = 'Cancelled'
    booking.save()
    
    serializer = CancelledBookingSerializer(cancelled)
    
    # Log cancellation
    try:
        ProcessLog.objects.create(action='cancel', booking=booking, pnr=booking.pnr, payload=payload, result=serializer.data)
    except Exception:
        pass
    
    # Clear the selected booking from session since it's cancelled
    if 'selected_booking_id' in request.session and request.session['selected_booking_id'] == booking_id:
        del request.session['selected_booking_id']
        request.session.modified = True
    
    return JsonResponse(serializer.data)


@csrf_exempt
@require_http_methods(['POST'])
def api_book_ticket(request):
    try:
        payload = json.loads(request.body)
    except Exception:
        return JsonResponse({'message': 'Invalid Request'}, status=400)
    ser = CreateBookingSerializer(data=payload)
    if not ser.is_valid():
        return JsonResponse({'message': 'Invalid input', 'errors': ser.errors}, status=400)
    data = ser.validated_data
    booking = Booking.objects.create(
        pnr=data['pnr'],
        flight_id=data['flight_id'],
        source_airport_code=data['source_airport_code'],
        destination_airport_code=data['destination_airport_code'],
        scheduled_departure=data['scheduled_departure'],
        scheduled_arrival=data['scheduled_arrival'],
        assigned_seat=data.get('assigned_seat')
    )
    return JsonResponse(BookingSerializer(booking).data, status=201)


@csrf_exempt
def api_list_bookings_by_pnr(request):
    pnr = request.GET.get('pnr')
    if not pnr:
        return JsonResponse({'message': 'PNR required'}, status=400)
    # Exclude cancelled bookings from the list
    qs = Booking.objects.filter(pnr__iexact=pnr).exclude(current_status='Cancelled')
    serializer = BookingSerializer(qs, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def api_get_booking_by_id(request, booking_id):
    """Get a single booking by ID (includes cancelled bookings for displaying after cancellation)"""
    try:
        booking = Booking.objects.get(id=booking_id)
        serializer = BookingSerializer(booking)
        return JsonResponse(serializer.data)
    except Booking.DoesNotExist:
        return JsonResponse({'message': 'Booking not found'}, status=404)


@csrf_exempt
def api_can_cancel(request):
    try:
        payload = json.loads(request.body)
    except Exception:
        return JsonResponse({'message': 'Invalid Request'}, status=400)
    booking_id = payload.get('booking_id')
    if not booking_id:
        return JsonResponse({'message': 'booking_id required'}, status=400)
    # randomly decide cancellation availability
    allowed = random.choice([True, False])
    reason = 'Within refund window' if allowed else 'Non-refundable fare'
    return JsonResponse({'booking_id': booking_id, 'can_cancel': allowed, 'reason': reason})


@csrf_exempt
def api_pet_allowed(request):
    try:
        payload = json.loads(request.body)
    except Exception:
        return JsonResponse({'message': 'Invalid Request'}, status=400)
    booking_id = payload.get('booking_id')
    if not booking_id:
        return JsonResponse({'message': 'booking_id required'}, status=400)
    allowed = random.choice([True, False])
    note = 'Pet allowed in cabin' if allowed else 'Pet not allowed for this fare/class'
    # log pet check
    try:
        booking = None
        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
            except Exception:
                booking = None
        ProcessLog.objects.create(action='pets', booking=booking, pnr=(booking.pnr if booking else None), payload={'booking_id': booking_id}, result={'pet_allowed': allowed, 'note': note})
    except Exception:
        pass
    return JsonResponse({'booking_id': booking_id, 'pet_allowed': allowed, 'note': note})


def api_cancelled_bookings(request):
    pnr = request.GET.get('pnr')
    if not pnr:
        return JsonResponse({'message': 'PNR required'}, status=400)
    qs = CancelledBooking.objects.filter(booking__pnr__iexact=pnr)
    serializer = CancelledBookingSerializer(qs, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def api_available_seats(request):
    try:
        payload = json.loads(request.body)
    except Exception:
        return JsonResponse({'message': 'Invalid Request'}, status=400)
    if payload.get('pnr') == 'notfound':
        return JsonResponse({'message': 'Flight Not Found'}, status=404)
    seats = []
    for r in range(20, 26):
        seats.append({
            'row_number': r,
            'column_letter': 'A',
            'price': 99.0 + r,
            'class': 'Economy',
        })
    return JsonResponse({'flight_id': payload.get('flight_id', 1234), 'pnr': payload.get('pnr'), 'available_seats': seats})


@csrf_exempt
def process_message(request):
    try:
        payload = json.loads(request.body)
    except Exception:
        return JsonResponse({'reply': 'Invalid request'}, status=400)
    msg = payload.get('message','').lower()

    # Simple stateful dialog using session; require PNR verification first
    sess = request.session
    state = sess.get('state')
    verified_pnr = sess.get('verified_pnr')
    selected_booking_id = sess.get('selected_booking_id')  # Remember selected booking in session

    # Persist user message
    try:
        Message.objects.create(session_key=request.session.session_key, sender='user', text=msg, pnr=verified_pnr)
    except Exception:
        pass

    # Start flows
    if not verified_pnr:
        return JsonResponse({'reply': 'Please verify your PNR first by clicking the bot and entering your PNR.', 'need_pnr': True})

    # Get booking_id from request payload (if user just selected a booking)
    booking_id = None
    try:
        body = payload if isinstance(payload, dict) else {}
        booking_id = body.get('booking_id')
        # If user sends a booking_id, store it in session for future use
        if booking_id:
            sess['selected_booking_id'] = booking_id
            selected_booking_id = booking_id
            request.session.modified = True
            # If message is just 'select', return success immediately (user clicked a booking)
            if msg.strip() == 'select':
                return JsonResponse({'reply': 'Booking selected'})
    except Exception:
        booking_id = None

    # If no booking_id in request, use the one from session
    if not booking_id and selected_booking_id:
        booking_id = selected_booking_id

    # Use BERT-based intent classification instead of keyword matching
    # States that allow free-form input (like entering PNR)
    conversation_states = ['awaiting_pnr_for_cancel', 'awaiting_pnr_for_status', 'awaiting_pnr_for_seats', 'confirm_cancel']
    
    detected_intent = None
    if state not in conversation_states and msg.strip() != 'select':
        # Use AI to detect intent from natural language
        try:
            intent, confidence = get_intent(msg)
            
            # If no intent detected or low confidence, reject
            if intent is None:
                return JsonResponse({'reply': 'Invalid query'})
            
            detected_intent = intent
        except Exception as e:
            # If BERT fails, fall back to basic validation
            print(f"Intent classification error: {e}")
            return JsonResponse({'reply': 'Invalid query'})

    short_intents = ['cancel', 'status', 'seat', 'pets']
    # Only ask for booking selection if no booking is selected in session
    if verified_pnr and not booking_id and detected_intent in short_intents:
        qs = Booking.objects.filter(pnr__iexact=verified_pnr).exclude(current_status='Cancelled')
        serializer = BookingSerializer(qs, many=True)
        return JsonResponse({'reply': 'Please choose a booking for that action.', 'action': 'list_bookings', 'bookings': serializer.data})

    # If user asks to see booked flights, return them (do not auto-list earlier)
    if detected_intent == 'booked_flights':
        qs = Booking.objects.filter(pnr__iexact=verified_pnr).exclude(current_status='Cancelled')
        serializer = BookingSerializer(qs, many=True)
        return JsonResponse({'reply': 'Here are your bookings', 'action': 'list_bookings', 'bookings': serializer.data})

    if detected_intent == 'cancel':
        # If a booking is already selected in session, proceed with cancellation
        if booking_id:
            # Let the frontend handle the cancellation flow
            return JsonResponse({'reply': 'Are you sure you want to cancel this booking?', 'action': 'confirm_cancel', 'booking_id': booking_id})
        # If PNR verified but no booking selected, return bookings so user can select which to cancel
        if verified_pnr:
            qs = Booking.objects.filter(pnr__iexact=verified_pnr).exclude(current_status='Cancelled')
            serializer = BookingSerializer(qs, many=True)
            return JsonResponse({'reply': 'Sure — select which booking you want to cancel.', 'action': 'list_bookings', 'bookings': serializer.data})
        sess['state'] = 'awaiting_pnr_for_cancel'
        request.session.modified = True
        return JsonResponse({'reply': 'Sure — please provide your PNR so I can list your bookings.'})

    if any(k in msg for k in ['cancellation policy', 'cancel policy', 'refund policy']):
        return JsonResponse({'reply': 'Cancellation policies vary. See: https://www.jetblue.com/flying-with-us/our-fares'})

    if detected_intent == 'status':
        # If a booking is already selected, return its status
        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                # Generate realistic flight status
                flight_status = random.choice(['On Time', 'Departed', 'Arrived', 'Delayed'])
                return JsonResponse({'reply': f'Flight {booking.flight_id} status: {flight_status}', 'booking': BookingSerializer(booking).data})
            except Booking.DoesNotExist:
                pass
        # If PNR verified but no booking selected, return bookings for selection
        if verified_pnr:
            qs = Booking.objects.filter(pnr__iexact=verified_pnr).exclude(current_status='Cancelled')
            serializer = BookingSerializer(qs, many=True)
            return JsonResponse({'reply': 'Which booking would you like to check?', 'action': 'list_bookings', 'bookings': serializer.data})
        sess['state'] = 'awaiting_pnr_for_status'
        request.session.modified = True
        return JsonResponse({'reply': 'Please provide your PNR so I can look up the flight status.'})

    if detected_intent == 'seat':
        # If a booking is already selected, show its seat info
        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                return JsonResponse({'reply': f'Your assigned seat is: {booking.assigned_seat}', 'booking': BookingSerializer(booking).data})
            except Booking.DoesNotExist:
                pass
        if verified_pnr:
            qs = Booking.objects.filter(pnr__iexact=verified_pnr).exclude(current_status='Cancelled')
            serializer = BookingSerializer(qs, many=True)
            return JsonResponse({'reply': 'Select booking to check seats for.', 'action': 'list_bookings', 'bookings': serializer.data})
        sess['state'] = 'awaiting_pnr_for_seats'
        request.session.modified = True
        return JsonResponse({'reply': 'Please provide your PNR to check seat availability.'})

    if detected_intent == 'pets':
        # If a booking is already selected, check pet policy for it
        if booking_id:
            allowed = random.choice([True, False])
            note = 'Pet allowed in cabin' if allowed else 'Pet not allowed for this fare/class'
            try:
                booking = Booking.objects.get(id=booking_id)
                ProcessLog.objects.create(action='pets', booking=booking, pnr=booking.pnr, payload={'booking_id': booking_id}, result={'pet_allowed': allowed, 'note': note})
            except Exception:
                pass
            return JsonResponse({'reply': note, 'pet_allowed': allowed})
        # If PNR verified but no booking selected, show bookings for selection
        if verified_pnr:
            qs = Booking.objects.filter(pnr__iexact=verified_pnr).exclude(current_status='Cancelled')
            serializer = BookingSerializer(qs, many=True)
            return JsonResponse({'reply': 'Select a booking to check pet travel rules.', 'action': 'list_bookings', 'bookings': serializer.data})
        return JsonResponse({'reply': 'Pets: JetBlue allows small pets in-cabin and has specific rules. See: https://www.jetblue.com/traveling-together/traveling-with-pets'})

    # If waiting for PNR in various flows
    if state in ('awaiting_pnr_for_cancel', 'awaiting_pnr_for_status', 'awaiting_pnr_for_seats'):
        # extract plausible pnr
        tokens = msg.upper().split()
        pnr = None
        for t in tokens[::-1]:
            if 3 <= len(t) <= 7 and t.isalnum():
                pnr = t
                break
        if not pnr:
            return JsonResponse({'reply': 'I could not find a PNR in your message. Please send the PNR (alphanumeric, 3-7 chars).'})

        # prefer DB booking
        booking_qs = Booking.objects.filter(pnr__iexact=pnr)
        booking = None
        if booking_qs.exists():
            booking = BookingSerializer(booking_qs.first()).data
        else:
            booking = _mock_booking(pnr)
        if not booking:
            return JsonResponse({'reply': 'PNR not found. Please check and resend.'})

        # handle each state
        if state == 'awaiting_pnr_for_cancel':
            sess['state'] = 'confirm_cancel'
            sess['pnr'] = pnr
            request.session.modified = True
            return JsonResponse({'reply': f"Found booking for PNR {pnr}: flight {booking['flight_id']} from {booking['source_airport_code']} to {booking['destination_airport_code']} on {booking['scheduled_departure']}. Reply 'confirm' to cancel or 'abort' to keep."})

        if state == 'awaiting_pnr_for_status':
            sess['state'] = None
            request.session.modified = True
            flight_status = random.choice(['On Time', 'Departed', 'Arrived', 'Delayed'])
            return JsonResponse({'reply': f"Flight status for PNR {pnr}: {flight_status}. Scheduled departure: {booking['scheduled_departure']}"})

        if state == 'awaiting_pnr_for_seats':
            # call available seats
            payload = {
                'pnr': pnr,
                'flight_id': booking['flight_id'],
                'source_airport_code': booking['source_airport_code'],
                'destination_airport_code': booking['destination_airport_code'],
                'scheduled_departure': booking['scheduled_departure'],
                'scheduled_arrival': booking['scheduled_arrival'],
            }
            class DummyReq:
                body = json.dumps(payload).encode()
            seats_resp = api_available_seats(DummyReq())
            seats_data = json.loads(seats_resp.content)
            seats = seats_data.get('available_seats', [])
            top3 = seats[:3]
            text = 'Available seats: ' + ', '.join([f"{s['row_number']}{s['column_letter']} (${s['price']})" for s in top3])
            sess['state'] = None
            request.session.modified = True
            return JsonResponse({'reply': text})

    # Confirmation step
    if state == 'confirm_cancel' and 'confirm' in msg:
        pnr = sess.get('pnr') or verified_pnr or 'ABC123'
        payload = {
            'pnr': pnr,
            'flight_id': 1234,
            'source_airport_code': 'JFK',
            'destination_airport_code': 'LAX',
            'scheduled_departure': datetime.utcnow().isoformat()+'Z',
            'scheduled_arrival': (datetime.utcnow()+timedelta(hours=6)).isoformat()+'Z'
        }
        class DummyReq:
            body = json.dumps(payload).encode()
        cancel_resp = api_cancel_booking(DummyReq())
        data = json.loads(cancel_resp.content)
        # persist bot message
        try:
            Message.objects.create(session_key=request.session.session_key, sender='bot', text=data.get('message'), pnr=pnr)
        except Exception:
            pass
        sess['state'] = None
        sess.pop('pnr', None)
        request.session.modified = True
        return JsonResponse({'reply': f"{data.get('message')}. Cancellation charges: {data.get('cancellation_charges')}. Refund: {data.get('refund_amount')} (expected {data.get('refund_date')})."})

    if state == 'confirm_cancel' and 'abort' in msg:
        sess['state'] = None
        sess.pop('pnr', None)
        request.session.modified = True
        return JsonResponse({'reply': 'Cancellation aborted. Let me know if you need anything else.'})

    # Check status action: allow front-end to call process with message 'status' and booking_id
    try:
        body = json.loads(request.body)
    except Exception:
        body = {}
    if body.get('booking_id') and 'status' in msg:
        try:
            bk = Booking.objects.get(id=body.get('booking_id'))
            # Generate realistic flight status
            flight_status = random.choice(['On Time', 'Departed', 'Arrived', 'Delayed'])
            # log status check
            try:
                ProcessLog.objects.create(action='status', booking=bk, pnr=bk.pnr, payload={'booking_id': bk.id}, result={'status': flight_status})
            except Exception:
                pass
            return JsonResponse({'reply': f"Booking {bk.id} status: {flight_status}"})
        except Booking.DoesNotExist:
            return JsonResponse({'reply': 'Booking not found'}, status=404)

    # Final fallback for any unhandled queries
    return JsonResponse({'reply': 'Invalid query'})


@csrf_exempt
def verify_pnr(request):
    try:
        payload = json.loads(request.body)
    except Exception:
        return JsonResponse({'message': 'Invalid Request'}, status=400)
    ser = VerifyPNRSerializer(data=payload)
    if not ser.is_valid():
        return JsonResponse({'message': 'Invalid input', 'errors': ser.errors}, status=400)
    pnr = ser.validated_data['pnr']
    exists = Booking.objects.filter(pnr__iexact=pnr).exists()
    if exists:
        request.session['verified_pnr'] = pnr
        request.session.modified = True
        try:
            # record verification
            ProcessLog.objects.create(action='verify_pnr', pnr=pnr, payload={'exists': True}, result={'exists': True})
        except Exception:
            pass
    return JsonResponse({'pnr': pnr, 'exists': exists})


@csrf_exempt
def log_message(request):
    try:
        payload = json.loads(request.body)
    except Exception:
        return JsonResponse({'message': 'Invalid Request'}, status=400)
    text = payload.get('text')
    sender = payload.get('sender','user')
    pnr = request.session.get('verified_pnr')
    msg = Message.objects.create(session_key=request.session.session_key, sender=sender, text=text, pnr=pnr)
    return JsonResponse({'id': msg.id, 'created_at': msg.created_at.isoformat()})


def api_get_booking_fake(pnr):
    # reuse mock
    return _mock_booking(pnr)
