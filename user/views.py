from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


class ActivateUserView(UserViewSet):
    """ Custom authentication system via Email verification link"""

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())

        kwargs["data"] = {
            "uid": self.kwargs["uid"],
            "token": self.kwargs["token"],
        }

        return serializer_class(*args, **kwargs)

    @action(["post"], detail=False)
    def activation(self, request, uid, token, *args, **kwargs):
        super().activation(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)
