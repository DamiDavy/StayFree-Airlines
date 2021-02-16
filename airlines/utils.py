from datetime import datetime, timedelta
from .models import Country, Passenger, Airport, Flight, Current, Single, Booking, Row, Seat

now = datetime.now()

#function for searching direct routes        
def direct(flights, date, person):
    days = Current.objects.get(day=date)
    suitable = []   
    for flight in flights:
        combine = datetime.combine(date, flight.departure_time)
        comparison = combine > now
        try:
            this_flight = Single.objects.get(flight=flight, days=days)
        except Single.DoesNotExist:
            this_flight = None
        if (this_flight is None or (this_flight.capacity - person) >= 0) and comparison:
            if flight.daily == True:
                suitable.append(flight)
            elif flight.days.count() > 0:
                for day in flight.days.all():
                    if date == day.day:
                        suitable.append(flight)
    return suitable

#function for searching transit routes
def transit(first_flight, second_flight, date, person):
    transfer_list = []
    days = Current.objects.get(day=date)
    for first in first_flight:
        for second in second_flight:
            f = datetime.combine(datetime(2020,8,8), first.arrival_time)
            r = f + timedelta(hours=1)
            if first.arrival_time < second.departure_time:
                c = datetime.combine(datetime(2020,8,8), second.departure_time)
                second_days = days
            else:
                c = datetime.combine(datetime(2020,8,9), second.departure_time)
                second_date = date + timedelta(days=1)
                second_days = Current.objects.get(day=second_date)
            if first.arrival == second.departure and c >= r:
                combine = datetime.combine(date, first.departure_time)
                comparison = combine > now
                try:
                    f_flight = Single.objects.get(flight=first, days=days)
                except Single.DoesNotExist:
                    f_flight = None

                try:
                    s_flight = Single.objects.get(flight=second, days=second_days)
                except Single.DoesNotExist:
                    s_flight = None

                if (f_flight is None or (f_flight.capacity - person) >= 0) and comparison: 
                    if s_flight is None or (s_flight.capacity - person) >= 0:
                        if first.daily == True and second.daily == True:
                            item = {}
                            item["first"] = first
                            item["second"] = second
                        
                            total = first.price + second.price
                            item["price"] = total
                            item["ids"] = str(first.id) + "_" + str(second.id)

                            transfer_list.append(item)

                        elif first.daily == True and second.days.count() > 0:
                            for dayc in second.days.all():
                                if second_days == dayc:
                                    item = {}
                                    item["first"] = first
                                    item["second"] = second
                                
                                    total = first.price + second.price
                                    item["price"] = total
                                    item["ids"] = str(first.id) + "_" + str(second.id)

                                    transfer_list.append(item)
                        elif first.days.count() > 0 and second.daily == True:
                            for dayf in first.days.all():
                                if days == dayf:
                                    item = {}
                                    item["first"] = first
                                    item["second"] = second
                                
                                    total = first.price + second.price
                                    item["price"] = total
                                    item["ids"] = str(first.id) + "_" + str(second.id)

                                    transfer_list.append(item)
                        elif first.days.count() > 0 and second.days.count() > 0:
                            for dayf in first.days.all():
                                for dayc in second.days.all():
                                    if days == dayf and second_days == dayc:
                                        item = {}
                                        item["first"] = first
                                        item["second"] = second
                                    
                                        total = first.price + second.price
                                        item["price"] = total
                                        item["ids"] = str(first.id) + "_" + str(second.id)

                                        transfer_list.append(item)
    return transfer_list