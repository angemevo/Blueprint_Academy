import pytest
from django.conf import settings
from rest_framework.test import APIClient

from apps.users.models import Profile, Role, User

COOKIE = settings.JWT_REFRESH_COOKIE["NAME"]
PWD = "Zx9!longpassword42"


@pytest.fixture
def client():
    return APIClient()


def register(client, **extra):
    body = {"username": "ada", "email": "ada@example.com", "password": PWD, **extra}
    return client.post("/api/auth/register/", body)


def login(client):
    return client.post("/api/auth/login/", {"username": "ada", "password": PWD})


@pytest.mark.django_db
def test_register_creates_student_and_profile(client):
    r = register(client)
    assert r.status_code == 201
    assert "password" not in r.json()
    user = User.objects.get(username="ada")
    assert user.role == Role.STUDENT
    assert Profile.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_register_ignores_role(client):
    r = register(client, role="admin", is_staff=True)
    assert r.status_code == 201
    user = User.objects.get(username="ada")
    assert user.role == Role.STUDENT
    assert not user.is_staff


@pytest.mark.django_db
@pytest.mark.parametrize("password", ["short", "12345678901234", "password"])
def test_register_rejects_weak_password(client, password):
    r = register(client, password=password)
    assert r.status_code == 400
    assert "password" in r.json()
    assert not User.objects.exists()


@pytest.mark.django_db
def test_register_rejects_duplicates(client):
    register(client)
    assert register(client).status_code == 400


@pytest.mark.django_db
def test_login_sets_cookie_and_hides_refresh(client):
    register(client)
    r = login(client)
    assert r.status_code == 200
    assert set(r.json()) == {"access"}
    cookie = r.cookies[COOKIE]
    assert cookie["httponly"]
    assert cookie["path"] == settings.JWT_REFRESH_COOKIE["PATH"]
    assert cookie.value not in r.content.decode()


@pytest.mark.django_db
def test_login_wrong_password(client):
    register(client)
    r = client.post("/api/auth/login/", {"username": "ada", "password": "nope"})
    assert r.status_code == 401
    assert COOKIE not in r.cookies


@pytest.mark.django_db
def test_refresh_without_cookie(client):
    assert client.post("/api/auth/refresh/").status_code == 401


@pytest.mark.django_db
def test_refresh_rotates_and_old_token_is_blacklisted(client):
    register(client)
    login(client)
    old = client.cookies[COOKIE].value
    r = client.post("/api/auth/refresh/")
    assert r.status_code == 200
    assert set(r.json()) == {"access"}
    new = r.cookies[COOKIE].value
    assert new != old
    assert new not in r.content.decode()

    replay = APIClient()
    replay.cookies[COOKIE] = old
    assert replay.post("/api/auth/refresh/").status_code == 401


@pytest.mark.django_db
def test_refresh_with_garbage_cookie(client):
    client.cookies[COOKIE] = "garbage"
    assert client.post("/api/auth/refresh/").status_code == 401


@pytest.mark.django_db
def test_logout_clears_cookie_and_revokes_refresh(client):
    register(client)
    login(client)
    token = client.cookies[COOKIE].value
    r = client.post("/api/auth/logout/")
    assert r.status_code == 204
    assert r.cookies[COOKIE].value == ""
    replay = APIClient()
    replay.cookies[COOKIE] = token
    assert replay.post("/api/auth/refresh/").status_code == 401


@pytest.mark.django_db
def test_logout_without_cookie(client):
    assert client.post("/api/auth/logout/").status_code == 204
