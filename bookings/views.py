from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.throttling import AnonRateThrottle

from .models import Booking
from .serializers import BookingSerializer


class BookingCreateThrottle(AnonRateThrottle):
    scope = "booking"
    rate = "20/hour"  # per IP; stops form spam without needing a settings change


class BookingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    POST /api/bookings/        public  - make a booking (guests don't need an account)
    GET  /api/bookings/        staff   - list bookings
    GET  /api/bookings/<id>/   staff   - view one booking
    """

    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAdminUser()]

    def get_throttles(self):
        if self.action == "create":
            return [BookingCreateThrottle()]
        return super().get_throttles()
