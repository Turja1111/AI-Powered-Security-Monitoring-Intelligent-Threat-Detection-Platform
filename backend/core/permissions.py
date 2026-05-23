from rest_framework import permissions
from rest_framework_api_key.permissions import BaseHasAPIKey
from rest_framework_api_key.models import APIKey


class HasIngestionAPIKey(BaseHasAPIKey):
    """Permission class checking for a valid custom API key for log ingestion."""

    model = APIKey


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to perform write actions.
    """

    def has_permission(self, request, view):
        # Read-only methods are safe
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff
