"""Vues d'auth : valident, delèguent aux services, posent le cookie."""

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from .serializers import RegisterSerializer, UserSerializer
from .services import auth as auth_service


class _AuthView(APIView):
    # JWTAuthentication fournit l'en-tete WWW-Authenticate : 401 et non 403.
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]


class RegisterView(_AuthView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = auth_service.register_user(**serializer.validated_data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(_AuthView):
    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(exc.args[0]) from exc
        data = serializer.validated_data
        response = Response({"access": data["access"]})
        auth_service.set_refresh_cookie(response, data["refresh"])
        return response


class RefreshView(_AuthView):
    def post(self, request):
        refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE["NAME"])
        if not refresh:
            return Response(
                {"detail": "Refresh token absent."}, status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = TokenRefreshSerializer(data={"refresh": refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as exc:
            raise InvalidToken(exc.args[0]) from exc
        data = serializer.validated_data
        response = Response({"access": data["access"]})
        if "refresh" in data:
            auth_service.set_refresh_cookie(response, data["refresh"])
        return response


class LogoutView(_AuthView):
    def post(self, request):
        auth_service.revoke_refresh(
            request.COOKIES.get(settings.JWT_REFRESH_COOKIE["NAME"])
        )
        response = Response(status=status.HTTP_204_NO_CONTENT)
        auth_service.clear_refresh_cookie(response)
        return response
