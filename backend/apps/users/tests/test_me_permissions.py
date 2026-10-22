import pytest
from django.test import RequestFactory
from rest_framework.test import APIClient

from apps.users.models import Profile, Role, User
from apps.users.permissions import (
    IsInstructor,
    IsInstructorOrAdmin,
    IsPlatformAdmin,
    IsStudent,
)

PWD = "Zx9!longpassword42"


def make(role, **kw):
    user = User.objects.create_user(username=role, password=PWD, role=role, **kw)
    Profile.objects.create(user=user)
    return user


def auth(user):
    c = APIClient()
    c.force_authenticate(user)
    return c


def allowed(perm, user):
    request = RequestFactory().get("/")
    request.user = user
    return perm().has_permission(request, None)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "perm,expected",
    [
        (IsStudent, {Role.STUDENT}),
        (IsInstructor, {Role.INSTRUCTOR}),
        (IsPlatformAdmin, {Role.ADMIN}),
        (IsInstructorOrAdmin, {Role.INSTRUCTOR, Role.ADMIN}),
    ],
)
def test_permissions_per_role(perm, expected):
    for role in Role.values:
        user = User.objects.create_user(username=f"u-{role}", role=role)
        assert allowed(perm, user) == (role in expected)


@pytest.mark.django_db
def test_permissions_ignore_is_staff():
    user = User.objects.create_user(username="s", role=Role.STUDENT, is_staff=True)
    assert not allowed(IsPlatformAdmin, user)


def test_permissions_anonymous():
    from django.contrib.auth.models import AnonymousUser

    assert not allowed(IsStudent, AnonymousUser())


@pytest.mark.django_db
def test_me_requires_auth():
    assert APIClient().get("/api/users/me/").status_code == 401
    assert APIClient().patch("/api/users/me/", {}).status_code == 401


@pytest.mark.django_db
def test_me_get():
    r = auth(make(Role.STUDENT)).get("/api/users/me/")
    assert r.status_code == 200
    body = r.json()
    assert body["role"] == "student"
    assert body["profile"]["level"] == 1
    assert body["profile"]["onboarding_completed"] is False


@pytest.mark.django_db
def test_me_patch_editable_fields():
    user = make(Role.STUDENT)
    r = auth(user).patch(
        "/api/users/me/",
        {"display_name": "Ada", "bio": "hi", "onboarding_completed": True},
    )
    assert r.status_code == 200
    user.profile.refresh_from_db()
    assert user.profile.display_name == "Ada"
    assert user.profile.onboarding_completed is True


@pytest.mark.django_db
def test_me_patch_read_only_unchanged():
    user = make(Role.STUDENT)
    r = auth(user).patch(
        "/api/users/me/",
        {"total_xp": 9999, "level": 50, "current_streak": 9, "role": "admin"},
    )
    assert r.status_code == 200
    user.refresh_from_db()
    user.profile.refresh_from_db()
    assert user.role == Role.STUDENT
    assert user.profile.total_xp == 0
    assert user.profile.level == 1
    assert user.profile.current_streak == 0
