from django.urls import path
from user.views import ActivateUserView

urlpatterns = [
s    path("activate/<str:uid>/<str:token>", ActivateUserView.as_view({"get": "activation"}), name="activation")
]

app_name = "user"
