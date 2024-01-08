from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from airport.models import AirplaneType, Airplane, Airport, Route, Flight
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers import AirplaneTypeSerializer, AirplaneSerializer, AirplaneListSerializer, AirportSerializer, \
    RouteSerializer, RouteListSerializer, FlightSerializer, FlightListSerializer


class AirplaneTypeViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneViewSet(ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return AirplaneListSerializer
        return self.serializer_class


class AirportViewSet(ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RouteListSerializer
        return self.serializer_class


class FlightViewSet(ModelViewSet):
    queryset = Flight.objects.select_related("route__source", "route__destination", "airplane")
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return FlightListSerializer
        return self.serializer_class
