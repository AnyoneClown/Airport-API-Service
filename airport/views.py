from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from airport.models import AirplaneType, Airplane
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers import AirplaneTypeSerializer, AirplaneSerializer, AirplaneListSerializer


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
