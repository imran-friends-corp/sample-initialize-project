# rest framework
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import status
from rest_framework.response import Response

# internal imports
from apps.user.enums import UserRole, UserType, UserStatus
from apps.common.otp import InvalidOTPException


class AdminRequiredMixin:

    permission_classes = [IsAuthenticated]

    def check_permissions(self, request):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.
        """
        super().check_permissions(request)

        user = request.user

        if user.status != UserStatus.ACTIVE.value:
            raise PermissionDenied("User not active")

        if user.role != UserRole.ADMIN.value or user.type != UserType.ADMIN.value:
            raise PermissionDenied("User does not have permission to perform the action")


class OTPExceptionMixin:
    def handle_exception(self, exc):
        if isinstance(exc, InvalidOTPException):
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return super().handle_exception(exc)
