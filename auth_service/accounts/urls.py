from django.urls import path
from .views import SignupView,LoginView,MeView,TokenRefreshView

# we register endpoint routes

urlpatterns = [
    path("signup/",SignupView.as_view(), name="signup"),
    path("login/" ,LoginView.as_view(),name="login"),
    path("me/", MeView.as_view(), name = "me"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

]