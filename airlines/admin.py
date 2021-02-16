from django.contrib import admin

from .models import Country, Passenger, Airport, Flight, Current, Single, Booking, Row, Seat

admin.site.register(Country)
admin.site.register(Passenger)
admin.site.register(Airport)
admin.site.register(Flight)
admin.site.register(Current)
admin.site.register(Single)
admin.site.register(Booking)
admin.site.register(Row)
admin.site.register(Seat)

