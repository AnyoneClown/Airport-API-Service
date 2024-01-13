import time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport, Route, Flight, AirplaneType, Airplane, Order, Ticket

ORDER_URL = reverse("airport:order-list")
FLIGHTS_URL = reverse("airport:flight-list")


def detail_url(order_id):
    return reverse("airport:order-detail", args=[order_id])


def detail_flight_url(flight_id):
    return reverse("airport:flight-detail", args=[flight_id])


class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedOrderApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@user.com", "testpassword"
        )
        self.client.force_authenticate(self.user)
        self.airport1 = Airport.objects.create(
            name="airport1", closest_big_city="Paris"
        )
        self.airport2 = Airport.objects.create(
            name="airport2", closest_big_city="Berlin"
        )
        self.route = Route.objects.create(
            source=self.airport1, destination=self.airport2, distance=5000
        )
        self.airplane_type = AirplaneType.objects.create(name="type")
        self.airplane = Airplane.objects.create(
            name="test", rows=60, seats_in_row=8, airplane_type=self.airplane_type
        )
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now(),
        )

    def test_create_ticket_for_flight_in_past(self):
        past_departure_time = timezone.now() - timezone.timedelta(hours=3)
        flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=past_departure_time,
            arrival_time=past_departure_time + timezone.timedelta(hours=3),
        )

        payload = {"tickets": [{"flight": flight.id, "row": 2, "seat": 5}]}
        response = self.client.post(ORDER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_flight_detail_tickets(self):
        order = Order.objects.create(user=self.user)
        ticket = Ticket.objects.create(flight=self.flight, row=2, seat=8, order=order)
        response = self.client.get(detail_flight_url(self.flight.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["taken_places"][0]["row"], ticket.row)
        self.assertEqual(response.data["taken_places"][0]["seat"], ticket.seat)

    def test_flight_list_places_available(self):
        order = Order.objects.create(user=self.user)
        Ticket.objects.create(flight=self.flight, row=2, seat=8, order=order)
        response = self.client.get(FLIGHTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
