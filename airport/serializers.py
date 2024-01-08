from rest_framework import serializers

from airport.models import AirplaneType, Airplane, Airport, Route


class AirplaneTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type = serializers.CharField(source="airplane_type.name")

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type", "capacity")


class AirportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")

    def validate(self, data):
        source = data.get("source")
        destination = data.get("destination")
        distance = data.get("distance")

        existing_routes = Route.objects.filter(source=source, destination=destination).only("source", "destination")
        if existing_routes.exists():
            raise serializers.ValidationError("Route with the same source and destination already exists.")

        reverse_routes = Route.objects.filter(source=destination, destination=source).only("source", "destination", "distance")
        if reverse_routes.exists() and reverse_routes[0].distance != distance:
            raise serializers.ValidationError("Reverse route has different distance. Please, provide correct distance.")

        if source == destination:
            raise serializers.ValidationError("Source and destination airports must be different.")

        return data


class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(source="source.name")
    destination = serializers.CharField(source="destination.name")
