"""Permissions DRF par role applicatif (`User.role`, jamais `is_staff`)."""

from rest_framework.permissions import BasePermission

from .models import Role


class _HasRole(BasePermission):
    roles: tuple[str, ...] = ()

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role in self.roles)


class IsStudent(_HasRole):
    roles = (Role.STUDENT,)


class IsInstructor(_HasRole):
    roles = (Role.INSTRUCTOR,)


class IsPlatformAdmin(_HasRole):
    roles = (Role.ADMIN,)


class IsInstructorOrAdmin(_HasRole):
    roles = (Role.INSTRUCTOR, Role.ADMIN)
