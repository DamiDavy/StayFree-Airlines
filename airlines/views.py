from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AbstractUser
from django.db import IntegrityError
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from datetime import timedelta, datetime, date
from django.core.paginator import Paginator

from .forms import FlightForm, PassengerForm
from .models import Country, Passenger, Airport, Flight, Current, Single, Booking, Row, Seat, User
from .utils import direct, transit

# Create your views here.

@csrf_exempt
def search(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    pattern = data.get("pattern")
    plow = pattern.lower()
    pcap = plow.capitalize()
    cities = Airport.objects.filter(city__startswith=pcap)
    results = []
    for city in cities:
        results.append(city)
    return JsonResponse([result.serialize() for result in results], safe=False)


def index(request):
    return render(request, "airlines/index.html", {
        "form": FlightForm(),
        })

def result(request):
    form = FlightForm(request.POST)
    if form.is_valid():
        #ahead
        departure = form.cleaned_data["departure"]
        arrival = form.cleaned_data["arrival"]
        date = form.cleaned_data["date"]
        back = form.cleaned_data["back"]
        person = int(request.POST["person"])
        way = request.POST.getlist('way', False)

        flights = Flight.objects.filter(departure__city=departure, arrival__city=arrival)
        suitable = direct(flights, date, person)

        #transfer
        transfer = request.POST.getlist('transfer', False)
        if transfer:
            first_flight = Flight.objects.filter(departure__city=departure)
            second_flight = Flight.objects.filter(arrival__city=arrival)
            transfer_list = transit(first_flight, second_flight, date, person)                                     
                        
        if way == False:
            if suitable == [] and transfer == False:
                return render(request, "airlines/index.html", {
                    "form": form,
                    "mes": "Flights not Found"
                })
            elif transfer == False:
                return render(request, "airlines/index.html", {
                    "form": form,
                    "suitable": suitable,
                    "pers": person,
                    "date": date
                    })
            elif suitable == []:
                return render(request, "airlines/index.html", {
                    "form": form,
                    "transfer_list": transfer_list,
                    "do_transit": transfer,
                    "pers": person,
                    "date": date
                    })
            else:
                return render(request, "airlines/index.html", {
                    "form": form,
                    "suitable": suitable,
                    "transfer_list": transfer_list,
                    "do_transit": transfer,
                    "pers": person,
                    "date": date
                    })

        #back
        else:
            back_flights = Flight.objects.filter(departure__city=arrival, arrival__city=departure)
            back_suitable = direct(back_flights, back, person)

            #transfer
            if transfer:
                back_first_flight = Flight.objects.filter(departure__city=arrival)
                back_second_flight = Flight.objects.filter(arrival__city=departure)
                back_transfer_list = transit(back_first_flight, back_second_flight, back, person)

            if back_suitable == [] and transfer == False:
                return render(request, "airlines/index.html", {
                    "form": form,
                    "mes": "Flights not Found"
                })
            
            elif back_suitable == [] and suitable == []:
                return render(request, "airlines/index.html", {
                    "form": form,
                    "transfer_list": transfer_list,
                    "back_transfer_list": back_transfer_list,
                    "do_transit": transfer,
                    "pers": person,
                    "date": date,
                    "back": back
                    })
            elif back_suitable == []:
                return render(request, "airlines/index.html", {
                    "form": form,
                    "suitable": suitable,
                    "transfer_list": transfer_list,
                    "back_transfer_list": back_transfer_list,
                    "do_transit": transfer,
                    "pers": person,
                    "date": date,
                    "back": back
                    })
                        
            elif transfer == False:
                return render(request, "airlines/index.html", {
                    "form": form,
                    "suitable": suitable,
                    "back_suitable": back_suitable,
                    "do_transit": transfer,
                    "pers": person,
                    "date": date,
                    "back": back
                })
            else:
                return render(request, "airlines/index.html", {
                    "form": form,
                    "suitable": suitable,
                    "transfer_list": transfer_list,
                    "back_suitable": back_suitable,
                    "back_transfer_list": back_transfer_list,
                    "do_transit": transfer,
                    "pers": person,
                    "date": date,
                    "back": back
                })
    else:
        return render(request, "airlines/index.html", {
            "form": form
        })

def detail(request, pk, date):
    flight = Flight.objects.get(pk=pk)
    days = Current.objects.get(day=date)
    date = days.day
    try:
        this_flight = Single.objects.get(flight=flight, days=days)
    except Single.DoesNotExist:
        this_flight = None
    try:
        booking = Booking.objects.get(user=request.user.username, flight1=this_flight, transit=False)
    except Booking.DoesNotExist:
        booking = None

    if this_flight is None:
        this_flight = Single.objects.create(flight=flight, days=days)
        this_flight.save()

    if this_flight.flight.departure_time > this_flight.flight.arrival_time:
        arrival_date = days.day + timedelta(days=1)
    else:
        arrival_date = days.day

    if request.method == "POST":
        form = PassengerForm(request.POST)
        if form.is_valid():

            if booking is None:  
                booking = Booking.objects.create(user=request.user.username, flight1=this_flight)
                booking.save()
            
            if this_flight.capacity > 0 and booking.passenger.count() < 4:
                first_name = form.cleaned_data["first_name"]
                last_name = form.cleaned_data["last_name"]
                date_of_birth = form.cleaned_data["date_of_birth"]
                gender = form.cleaned_data["gender"]
                passanger = Passenger.objects.create(first_name=first_name, last_name=last_name,
                date_of_birth=date_of_birth, gender=gender, checked_in=False)
                passanger.save()

                this_flight.passengers.add(passanger)
                this_flight.capacity -= 1
                this_flight.save()

                booking.passenger.add(passanger)

                return HttpResponseRedirect(reverse("flight-detail", args=(pk, date,)))
            else:
                return render(request, "airlines/flight_detail.html", {
                    "flight": flight,
                    "booking": booking,
                    "mes": "Not enough free seats in the flight. You can book a flight only for 4 persons.",
                })
        else:
            return render(request, "airlines/flight_detail.html", {
                "flight": flight,
                "booking": booking,
                "form_pas": form,
                "date": date,
                "arrival_date": arrival_date
            })

    return render(request, "airlines/flight_detail.html", {
        "flight": flight,
        "booking": booking,
        "form_pas": PassengerForm(),
        "date": date,
        "arrival_date": arrival_date
    })


def transit_detail(request, ids, date):
    x = ids.index("_")
    idf = int(ids[:x])
    idsec = int(ids[x+1:])

    first = Flight.objects.get(pk=idf)
    second = Flight.objects.get(pk=idsec)
    days = Current.objects.get(day=date)

    try:
        first_flight = Single.objects.get(flight=first, days=days)
    except Single.DoesNotExist:
        first_flight = None

    if first.arrival_time < first.departure_time or second.departure_time < first.arrival_time:
        transit_date = days.day + timedelta(days=1)
    else:
        transit_date = days.day
    
    transit_days = Current.objects.get(day=transit_date)

    try:
        second_flight = Single.objects.get(flight=second, days=transit_days)
    except Single.DoesNotExist:
        second_flight = None

    try:
        booking = Booking.objects.get(user=request.user.username, flight1=first_flight,
                flight2=second_flight, transit=True)
    except Booking.DoesNotExist:
        booking = None

    if first_flight is None:
        first_flight = Single.objects.create(flight=first, days=days)
        first_flight.save()
    #second transit flight
    if second_flight is None:
        second_flight = Single.objects.create(flight=second, days=transit_days)
        second_flight.save()

    #dates
    if first_flight.flight.departure_time > first_flight.flight.arrival_time:
        first_flight_arrival_date = days.day + timedelta(days=1)
    else:
        first_flight_arrival_date = days.day
    
    if first_flight.flight.arrival_time > second_flight.flight.departure_time:
        second_flight_departure_date = first_flight_arrival_date + timedelta(days=1)
    else:
        second_flight_departure_date = first_flight_arrival_date

    if second_flight.flight.departure_time > second_flight.flight.arrival_time:
        second_flight_arrival_date = second_flight_departure_date + timedelta(days=1)
    else:
        second_flight_arrival_date = second_flight_departure_date

    if request.method == "POST":
        #first transit flight

        form = PassengerForm(request.POST)
        if form.is_valid():
            if first_flight.capacity > 0 and second_flight.capacity > 0:
                first_name = form.cleaned_data["first_name"]
                last_name = form.cleaned_data["last_name"]
                date_of_birth = form.cleaned_data["date_of_birth"]
                gender = form.cleaned_data["gender"]
                passanger = Passenger.objects.create(first_name=first_name, last_name=last_name,
                date_of_birth=date_of_birth, gender=gender, checked_in=False)
                passanger.save()

                first_flight.passengers.add(passanger)
                first_flight.capacity -= 1
                first_flight.save()

                second_flight.passengers.add(passanger)
                second_flight.capacity -= 1
                second_flight.save()

                if booking is None:  
                    booking = Booking.objects.create(user=request.user.username, flight1=first_flight,
                    flight2=second_flight, transit=True)
                    booking.save()
                booking.passenger.add(passanger)

                return HttpResponseRedirect(reverse("transit-flight-detail", args=(ids, date,)))
                
            else:
                return render(request, "airlines/transit_flight_detail.html", {
                    "ids": ids,
                    "first": first,
                    "second": second,
                    "booking": booking,
                    "mes": "Not enough free seats in the flight",
                })
        else:
            return render(request, "airlines/transit_flight_detail.html", {
                "ids": ids,
                "first": first,
                "second": second,
                "booking": booking,
                "form_pas": form,
                "date": days.day,
                "first_flight_arrival_date": first_flight_arrival_date,
                "second_flight_departure_date": second_flight_departure_date,
                "second_flight_arrival_date": second_flight_arrival_date
            })
    return render(request, "airlines/transit_flight_detail.html", {
        "ids": ids,
        "first": first,
        "second": second,
        "booking": booking,
        "form_pas": PassengerForm(),
        "date": days.day,
        "first_flight_arrival_date": first_flight_arrival_date,
        "second_flight_departure_date": second_flight_departure_date,
        "second_flight_arrival_date": second_flight_arrival_date
    })

def bookings(request, name):
    bookings = Booking.objects.filter(user=name)
    
    paginator = Paginator(bookings, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "airlines/bookings.html", {
        "bookings": bookings,
        "page_obj": page_obj,
        "page_number": page_number
    })

def check_in(request, booking_id, pas_id):
    passenger = Passenger.objects.get(pk=pas_id)
    booking = Booking.objects.get(pk=booking_id)
    flight = booking.flight1
    date = flight.days.day
    flight_id = flight.flight.id

    for i in range(22):
        try:
            row = Row.objects.get(flight=flight, number=(i+1))
        except Row.DoesNotExist:
            row = None
        if row == None:
            row = Row.objects.create(flight=flight, number=(i+1))
            row.save()
            for j in range(6):
                seat = Seat.objects.create(flight=flight, row=row, number=j+1)
                seat.save()

    suited_seats = []
    for i in range(22):
        row = Row.objects.get(flight=flight, number=(i+1))
        for j in range(6):
            seat = Seat.objects.get(flight=flight, row=row, number=(j+1))
            if seat.taken == False:
                suited_seats.append(seat)

    first_suited_seat = suited_seats[0]
    first_suited_seat.passenger = passenger
    first_suited_seat.taken = True
    first_suited_seat.save()

    if not booking.transit:
        return HttpResponseRedirect(reverse("flight-detail", args=(flight_id, date,)))

    else:
        second_flight = booking.flight2
        second_flight_id = second_flight.flight.id
        flight_ids = str(flight_id) + "_" + str(second_flight_id)

        for i in range(22):
            try:
                row = Row.objects.get(flight=second_flight, number=(i+1))
            except Row.DoesNotExist:
                row = None
            if row == None:
                row = Row.objects.create(flight=second_flight, number=(i+1))
                row.save()
                for j in range(6):
                    seat = Seat.objects.create(flight=second_flight, row=row, number=j+1)
                    seat.save()

        suited_seats_on_second = []
        for i in range(22):
            row = Row.objects.get(flight=second_flight, number=(i+1))
            for j in range(6):
                seat = Seat.objects.get(flight=second_flight, row=row, number=(j+1))
                if seat.taken == False:
                    suited_seats_on_second.append(seat)

        first_suited_seat_on_second = suited_seats_on_second[0]
        first_suited_seat_on_second.passenger = passenger
        first_suited_seat_on_second.taken = True
        first_suited_seat_on_second.save()

        return HttpResponseRedirect(reverse("transit-flight-detail", args=(flight_ids, date,)))

def delete(request, pas_id, booking_id, date):
    passenger = Passenger.objects.get(pk=pas_id)
    booking = Booking.objects.get(pk=booking_id)
    flight_id = booking.flight1.flight.id
    try:
        seat = Seat.objects.get(passenger=passenger, flight=booking.flight1)
    except Seat.DoesNotExist:
        seat = None

    booking.passenger.remove(passenger)
    booking.passengers_with_baggage.remove(passenger)
    
    booking.flight1.passengers.remove(passenger)
    if seat:
        seat.taken = False
        seat.save()

    if booking.transit == False:
        if booking.passenger.count() != 0:
            return HttpResponseRedirect(reverse("flight-detail", args=(flight_id, date,)))
        else:
            booking.delete()
            return HttpResponseRedirect(reverse("bookings", args=(request.user.username,)))
    else:
        booking.flight2.passengers.remove(passenger)
        try:
            seat_on_sec = Seat.objects.get(passenger=passenger, flight=booking.flight2)
        except Seat.DoesNotExist:
            seat_on_sec = None
        if seat_on_sec:
            seat_on_sec.taken = False
            seat_on_sec.save()
        if booking.passenger.count() != 0:
            second_flight_id = booking.flight2.flight.id
            flight_ids = str(flight_id) + "_" + str(second_flight_id)
            return HttpResponseRedirect(reverse("transit-flight-detail", args=(flight_ids, date,)))
        else:
            booking.delete()
            return HttpResponseRedirect(reverse("bookings", args=(request.user.username,)))


def baggage(request, pas_id, booking_id, date):
    passenger = Passenger.objects.get(pk=pas_id)
    booking = Booking.objects.get(pk=booking_id)
    flight_id = booking.flight1.flight.id

    booking.passengers_with_baggage.add(passenger)
    booking.save()

    if booking.transit == False:
        return HttpResponseRedirect(reverse("flight-detail", args=(flight_id, date,)))

    else:
        second_flight_id = booking.flight2.flight.id
        flight_ids = str(flight_id) + "_" + str(second_flight_id)
        return HttpResponseRedirect(reverse("transit-flight-detail", args=(flight_ids, date,)))

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "airlines/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "airlines/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "airlines/register.html", {
                "message": "Passwords must match."
            })
        try:
            user = AbstractUser.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "airlines/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "airlines/register.html")