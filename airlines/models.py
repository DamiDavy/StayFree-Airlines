from django.db import models
from django.urls import reverse
import datetime

class Country(models.Model):
    title = models.CharField(max_length=64)
    flag = models.URLField(max_length=200)

    def __str__(self):
        return self.title

class Airport(models.Model):
    city = models.CharField(max_length=64)
    code = models.CharField(max_length=3)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return '%s (%s)' % (self.city, self.code)
        
    def serialize(self):
        return {
            "city": self.city,
            "code": self.code,
            "country": self.country.title
        }

class Current(models.Model):
    day = models.DateField()

    def __str__(self):
        return str(self.day)
    class Meta:
        ordering = ["day"]

class Passenger(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    checked_in = models.BooleanField(default=False)
    date_of_birth = models.DateField()
    
    class Gender(models.TextChoices):
        Female = 'F'
        Male = 'M'
        Other = 'O'
    gender = models.CharField(max_length=1, choices=Gender.choices)

    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

class Flight(models.Model):
    departure = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departures")
    arrival = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrivals")
    daily = models.BooleanField() 
    days = models.ManyToManyField(Current, blank=True)
    departure_time = models.TimeField(default=datetime.time(9, 0, 0))
    arrival_time = models.TimeField()
    duration = models.TimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2, default=50)
    capacity = models.IntegerField(default=132)

    def __str__(self):
        return '%s %s- %s %s' % (self.departure, self.departure_time, self.arrival, self.arrival_time)

class Single(models.Model):
    days = models.ForeignKey(Current, on_delete=models.CASCADE, blank=True, default=1)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    capacity = models.IntegerField(default=132)
    passengers = models.ManyToManyField(Passenger, blank=True)

    def __str__(self):
        return '%s - %s %s' % (self.flight.departure, self.flight.arrival, self.days.day)

class Row(models.Model):
    flight = models.ForeignKey(Single, on_delete=models.CASCADE)
    number = models.IntegerField()
    def __str__(self):
        return str(self.number)

class Seat(models.Model):
    flight = models.ForeignKey(Single, on_delete=models.CASCADE, default=1, related_name="seat")
    row = models.ForeignKey(Row, on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, default=None, null=True, related_name="seat")
    number = models.IntegerField()
    taken = models.BooleanField(default=False)

    def lit(self):
        if self.number == 1:
            lit = "A"
        elif self.number == 2:
            lit = "B"
        elif self.number == 3:
            lit = "C"
        elif self.number == 4:
            lit = "D"  
        elif self.number == 5:
            lit = "E" 
        else:
            lit = "F"
        return lit
    
    def __str__(self):
        if self.number == 1:
            lit = "A"
        elif self.number == 2:
            lit = "B"
        elif self.number == 3:
            lit = "C"
        elif self.number == 4:
            lit = "D"  
        elif self.number == 5:
            lit = "E" 
        else:
            lit = "F"

        if self.passenger == None:
            return lit
        else:
            return '%s %s %s' % (lit, self.passenger.first_name, self.passenger.last_name)

class Booking(models.Model):
    user = models.CharField(max_length=64)
    passenger = models.ManyToManyField(Passenger)
    passengers_with_baggage = models.ManyToManyField(Passenger, related_name="baggage")
    flight1 = models.ForeignKey(Single, on_delete=models.CASCADE, related_name="bookings")
    flight2 = models.ForeignKey(Single, on_delete=models.CASCADE, null=True, blank=True, related_name="bookings_transit")
    transit = models.BooleanField(default=False)
    day = models.DateTimeField(auto_now_add=True)

    #dates

    def baggage_price(self):
        if self.transit == False:
            return str(5.00)
        else:
            return str(10.00)

    def ids(self):
        if self.transit == True:
            return str(self.flight1.flight.id) + "_" + str(self.flight2.flight.id)


    def __str__(self):
        if self.flight2 is None:
            return '%s - %s, %s passengers' % (self.flight1.flight.departure, self.flight1.flight.arrival, 
            self.passenger.count()) 
        else:
            return '%s - %s - %s, %s passengers' % (self.flight1.flight.departure, self.flight1.flight.arrival, 
            self.flight2.flight.arrival, self.passenger.count())

    def total_price(self):
        if self.transit == True:
            return self.flight1.flight.price + self.flight2.flight.price

    def past(self):
        today = datetime.datetime.now()
        combine = datetime.datetime.combine(self.flight1.days.day, self.flight1.flight.departure_time)
        if combine < today:
            return True
        else:
            return False

    def can_check_in(self):
        today = datetime.datetime.now()
        combine = datetime.datetime.combine(self.flight1.days.day, self.flight1.flight.departure_time)
        check_in_opens = combine - datetime.timedelta(days=1)
        if today < check_in_opens:
            return False
        else:
            return True

    def limit_count_of_passangers(self):
        if self.passenger.count() < 4:
            return False
        else:
            return True

    def when_arrival(self):
        if self.transit == True:
            day_of_ariival = self.flight1.days.day
            if self.flight1.flight.departure_time > self.flight1.flight.arrival_time:
                day_of_ariival = day_of_ariival + datetime.timedelta(days=1)

            if self.flight1.flight.arrival_time > self.flight2.flight.departure_time:
                day_of_ariival = day_of_ariival + datetime.timedelta(days=1)

            if self.flight2.flight.departure_time > self.flight2.flight.arrival_time:
                day_of_ariival = day_of_ariival + datetime.timedelta(days=1)

            return day_of_ariival
        else:
            day_of_ariival = self.flight1.days.day
            if self.flight1.flight.departure_time > self.flight1.flight.arrival_time:
                day_of_ariival = day_of_ariival + datetime.timedelta(days=1)
            return day_of_ariival

    class Meta:
        ordering = ["-day"]