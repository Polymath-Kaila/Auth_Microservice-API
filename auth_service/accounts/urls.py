from django.urls import path
from .views import SignupView

# we register endpoint routes

urlpatterns = [
    path("signup/",SignupView.as_view(), name="signup")
]