from django.urls import path
from .views import LoginApiView, SendOTP


urlpatterns = [
     path("send-otp/", SendOTP.as_view(), name="admin_send_otp"),
    path('login/', LoginApiView.as_view(), name='admin_login')
]
