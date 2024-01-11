from django.db.models import F, Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from airport.models import AirplaneType, Airplane, Airport, Route, Flight, Order, Crew
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers import (
    AirplaneTypeSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirportSerializer,
    RouteSerializer,
    RouteListSerializer,
    FlightSerializer,
    FlightListSerializer,
    OrderSerializer,
    OrderListSerializer,
    FlightDetailSerializer,
    CrewSerializer,
)


class AirplaneTypeViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet
):
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

    def get_queryset(self):
        queryset = self.queryset
        city = self.request.query_params.get("city")

        if city:
            queryset = queryset.filter(closest_big_city__icontains=city)
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "city",
                description="Filter by closest_big_city (ex. ?city=Paris)",
                required=False,
                type=str,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CrewViewSet(ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")

        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)

        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "first_name",
                description="Filter by first name (ex. ?first_name=David)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                "last_name",
                description="Filter by last name (ex. ?last_name=Johnson)",
                required=False,
                type=str,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class RouteViewSet(ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        if source:
            queryset = queryset.filter(source__closest_big_city__icontains=source)

        if destination:
            queryset = queryset.filter(
                destination__closest_big_city__icontains=destination
            )

        return queryset.select_related("source", "destination")

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RouteListSerializer
        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                description="Filter by source (ex. ?source=Paris)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                "destination",
                description="Filter by destination (ex. ?destination=London)",
                required=False,
                type=str,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FlightViewSet(ModelViewSet):
    queryset = (
        Flight.objects.select_related("route__destination", "route__source", "airplane")
        .prefetch_related("crew")
        .annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats_in_row") - Count("tickets")
            )
        )
    )
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        date = self.request.query_params.get("date")

        if source:
            queryset = queryset.filter(
                route__source__closest_big_city__icontains=source
            )

        if destination:
            queryset = queryset.filter(
                route__destination__closest_big_city__icontains=destination
            )

        if date:
            queryset = queryset.filter(departure_time__date=date)

        return queryset.select_related(
            "airplane", "route__source", "route__destination"
        )

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                description="Filter by source (ex. ?source=Paris)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                "destination",
                description="Filter by destination (ex. ?destination=London)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                "date",
                description="Filter by departure_date (ex. ?date=24-10-08)",
                required=False,
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__source__name", "tickets__flight__destination__name"
    )
    serializer_class = OrderSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "tickets__flight__route"
        )

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
