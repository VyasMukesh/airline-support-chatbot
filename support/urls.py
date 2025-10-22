from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('chat', views.chat, name='chat'),
    path('process', views.process_message, name='process_message'),
    path('api/check_session', views.api_check_session, name='api_check_session'),
    path('api/verify_pnr', views.verify_pnr, name='verify_pnr'),
    path('api/log_message', views.log_message, name='log_message'),
    path('api/book', views.api_book_ticket, name='api_book_ticket'),
    path('api/bookings', views.api_list_bookings_by_pnr, name='api_list_bookings_by_pnr'),
    path('api/bookings/<int:booking_id>', views.api_get_booking_by_id, name='api_get_booking_by_id'),
    path('api/can_cancel', views.api_can_cancel, name='api_can_cancel'),
    path('api/pet_allowed', views.api_pet_allowed, name='api_pet_allowed'),
    path('api/cancelled_bookings', views.api_cancelled_bookings, name='api_cancelled_bookings'),
    path('api/flight/booking', views.api_get_booking, name='api_get_booking'),
    path('api/flight/cancel', views.api_cancel_booking, name='api_cancel_booking'),
    path('api/flight/available_seats', views.api_available_seats, name='api_available_seats'),
]
