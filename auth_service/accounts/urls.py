from django.urls import path
from .views import SignupView,LoginView,MeView,TokenRefreshView,LogoutView,SendOtpView,   VerifyOtpView

# we register endpoint routes

urlpatterns = [
    path("signup/",SignupView.as_view(), name="signup"),
    path("login/" ,LoginView.as_view(),name="login"),
    path("me/", MeView.as_view(), name = "me"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("send-otp/", SendOtpView.as_view(), name ="send-otp"),
    path("verify-otp", VerifyOtpView.as_view(), name ="verify-otp")
]