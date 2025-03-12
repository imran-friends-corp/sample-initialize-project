# rest framework
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.common.email import EmailManager
from .serializers import OTPSerializer
from rest_framework.views import APIView
from apps.common.otp import OTP
from rest_framework.response import Response
# django imports

# internal imports
from .serializers import  LoginSerializer
from .mixins import OTPExceptionMixin


class SendOTP(APIView):
    """
    Send OTP to user's registered email address.
    """

    permission_classes = [AllowAny]
    serializer_class = OTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = self.request.data.get("email")

        otp, expired_min = OTP.create(email)

        language = request.headers.get('Htt-Language', 'en')
        EmailManager.send_otp(email=email, otp=otp, expired_min=expired_min, language=language)

        return Response({
            'detail': "Email Sent Successfully",
            'detail_jp': "メールが正常に送信されました。"
            })

class LoginApiView(OTPExceptionMixin, TokenObtainPairView):
    """
    This url handles user login.
    It allows any user to obtain a JWT token by providing a valid email and OTP.
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer