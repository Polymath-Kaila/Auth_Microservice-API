from django.urls import path
from .views import SignupView,LoginView,MeView

# we register endpoint routes

urlpatterns = [
    path("signup/",SignupView.as_view(), name="signup"),
    path("login/" ,LoginView.as_view(),name="login"),
    path("me/", MeView.as_view(), name = "me")
]