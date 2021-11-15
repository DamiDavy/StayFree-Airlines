# StayFree Airlines
This is a transport company application.
It is hosted on [heroku](https://stayfreeairlines.herokuapp.com).

### Functionality
1.	searching for direct and return flights, for daily and not daily flights, including routes with one transfer
2.	during input of departure and arrival autocomplete starts
3.	clicking on a flight should take users to a page specific to that flight
4.	on flight detail page logged in users can book this flight for up to four passengers excluding flights with departure date in the past
5.	logged in users can view their bookings list sorted by booking date including flights with departure date in the past, if the booking does not contain passengers, it is deleted.
6.	flight detail page contains information about passengers for whom the flight was booked by logged in user
7.	the user who made the booking can add baggage, check-in or delete a specific passenger
8.	after check-in, the current passenger gets a seat on the flight, check-in opens 24 hours before the departure time, after removing the passenger, his seat is free again.

Several models was created in particular for the country, airport, flight, passenger and seat on the plane.
In air.js an asynchronous request to the server for the autocomplete form. In flight.js the final booking price is automatically calculated.
To avoid repetition, search functions was moved from views.py to utils.py.

Python 3.9.0, Django 3.1.4

### Demo 
![App Promo Gif](StayFree.gif)
