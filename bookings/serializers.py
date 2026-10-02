import re
from datetime import time

from django.utils import timezone
from rest_framework import serializers

from .models import Booking

# weekday(): Monday=0 ... Sunday=6 -> (opens, closes)
OPENING_HOURS = {
    **{d: (time(7, 0), time(18, 0)) for d in range(0, 5)},  # Mon-Fri
    5: (time(8, 0), time(17, 0)),                            # Saturday
    6: (time(9, 0), time(15, 0)),                            # Sunday
}

PHONE_RE = re.compile(r"^\+?[\d\s\-()]{7,20}$")


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            "id", "name", "email", "phone", "date", "time",
            "guests", "special_requests", "status", "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Please enter your name.")
        return value

    def validate_phone(self, value):
        value = value.strip()
        if not PHONE_RE.match(value):
            raise serializers.ValidationError("Enter a valid phone number.")
        return value

    def validate_guests(self, value):
        if value < 1 or value > 20:
            raise serializers.ValidationError("Guests must be between 1 and 20.")
        return value

    def validate(self, attrs):
        date, t = attrs["date"], attrs["time"]
        now = timezone.localtime()

        if date < now.date():
            raise serializers.ValidationError({"date": "Bookings can't be in the past."})
        if date == now.date() and t <= now.time():
            raise serializers.ValidationError({"time": "That time has already passed today."})

        opens, closes = OPENING_HOURS[date.weekday()]
        if not (opens <= t < closes):
            raise serializers.ValidationError(
                {"time": f"We're open {opens:%H:%M} - {closes:%H:%M} on that day."}
            )
        return attrs
