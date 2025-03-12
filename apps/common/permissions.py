from rest_framework.permissions import BasePermission
from rest_framework.views import APIView

from apps.user.enums import UserRole, UserType
from rest_framework.exceptions import PermissionDenied


class IsDriverUser(BasePermission):
    """
    Permission to check if the user is a driver (role: USER, type: USER).
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role == UserRole.USER and user.type == UserType.USER:
            return True
        raise PermissionDenied("このアクションを実行する権限がありません。")


class IsAdminUser(BasePermission):
    """
    Permission to check if the user is an admin (role: ADMIN or SUPER_ADMIN, type: ADMIN).
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.CLIENT_ADMIN] and user.type == UserType.ADMIN:
            return True
        raise PermissionDenied("このアクションを実行する権限がありません。")


class IsSuperAdminUser(BasePermission):
    """
    Permission to check if the user is a super admin (role: SUPER_ADMIN, type: ADMIN).
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role == UserRole.SUPER_ADMIN and user.type == UserType.ADMIN:
            return True
        raise PermissionDenied("このアクションを実行する権限がありません。")


class AccessPermissionRequired(BasePermission):

    def has_permission(self, request, view):
        permission_required = getattr(view, "permission_required", None)

        if request.user.is_client_admin:
            return True

        if permission_required and not request.user.is_client_admin:
            user_permissions = request.user.permissions.values_list('permission__slug', flat=True)

            if not set(permission_required).intersection(user_permissions):
                raise PermissionDenied(f'アクセスする権限がありません {permission_required}')

            return True

        return False


class BranchPermissionRequired(BasePermission):
    """
    Permission to check if the user has permission to access a specific branch.
    """
    def get_branch_id(self, request):
        branch_id = request.headers.get('Branch-ID')
        if not branch_id:
            raise PermissionDenied('ブランチ ID が必要ですが、指定されていませんでした。')

        return branch_id

    def has_permission(self, request, view):
        branch_id = self.get_branch_id(request)
        if request.user.is_client_admin and branch_id == 'view_all':
            pass
        else:
            if not (request.user.user_branches.filter(branch_office_id=branch_id).exists() or request.user.is_client_admin):
                raise PermissionDenied('このブランチにアクセスする権限がありません。')

        return True
