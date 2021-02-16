from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("result", views.result, name="result"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('flight/<int:pk>/<str:date>', views.detail, name='flight-detail'),
    path('flight/<str:ids>/<str:date>', views.transit_detail, name='transit-flight-detail'),
    path('bookings/<str:name>', views.bookings, name='bookings'),
    path('check-in/<int:booking_id>/<int:pas_id>', views.check_in, name='check_in'),
    path('delete/<int:pas_id>/<int:booking_id>/<str:date>', views.delete, name="delete"),
    path('baggage/<int:pas_id>/<int:booking_id>/<str:date>', views.baggage, name="baggage"),
]