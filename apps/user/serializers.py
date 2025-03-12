# django imports
from datetime import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

# external imports
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import  PermissionDenied

# internal imports
from apps.common.email import EmailManager
from django.conf import settings
from .enums import UserStatus
from apps.common.exception import CustomValidationError
from apps.common.otp import OTP
from .enums import UserStatus, UserType, UserRole

User = get_user_model()


class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        user_email = attrs.get('email', None)

        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            raise CustomValidationError({
                'detail': 'User with this email does not exist',
                'detail_jp': 'ユーザーは存在しません。'
            })

        if user.status != UserStatus.ACTIVE:
            raise CustomValidationError({
                'detail': 'User is not active',
                'detail_jp': 'ユーザーがアクティブではありません。'
            })
        if not (
                (user.type == UserType.ADMIN and (user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.CLIENT_ADMIN])) or
                user.is_staff or
                user.is_superuser
        ):
            raise CustomValidationError({
                'detail': 'Only admin users are allowed to login',
                'detail_jp': '管理者ユーザーのみがログインできます。'
            })

        if user.status == UserStatus.PENDING_INVITATION:
            raise CustomValidationError({
                'detail': "User\'s invitation is still pending and not accepted",
                'detail_jp': "ユーザーへの招待はまだ承認されていません。"
            })

        return attrs

    def validate_email(self, email):
        is_valid, message = EmailManager.is_valid_emails(emails=[email])

        if not is_valid:
            raise CustomValidationError(message)
        return email


class UserSerializer(serializers.ModelSerializer):

 

    class Meta:
        model = User
        fields = [
            "id", "email", "username", "display_name"
        ]

    def validate_email(self, email):
        is_valid, message = EmailManager.is_valid_emails(emails=[email])

        if not is_valid:
            raise serializers.ValidationError(message)
        return email
    


class LoginSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password']
        self.fields["otp"] = serializers.CharField()

    def validate_email(self, email):
        is_valid, message = EmailManager.is_valid_emails(emails=[email])
        if not is_valid:
            raise CustomValidationError(message)

        return email

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token

    def validate(self, attrs):
        email = attrs[self.username_field]
        if not (settings.DEFAULT_OTP and int(attrs["otp"]) == settings.DEFAULT_OTP):
            OTP.is_valid(email, int(attrs["otp"]))
        OTP.create_verified(email)

        user = get_object_or_404(User, email=email)

        if user.status == UserStatus.SOFT_DELETED.value:
            raise PermissionDenied("あなたのアカウントが停止されています。システム管理者に連絡してください。")

        refresh = self.get_token(user)
        OTP.delete_verified(email)

        user.last_login = datetime.now()
        user.save()

      

       
        return {
            "user": {
                **UserSerializer(user).data,
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
