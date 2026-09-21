"""Vues techniques transverses (hors domaine metier)."""

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    """Sonde de disponibilite du backend.

    Utilisee par docker compose, le monitoring et la page de verification du
    frontend. Volontairement sans acces base de donnees : elle repond « le
    process Django est debout », rien de plus.
    """

    permission_classes = [AllowAny]
    authentication_classes: list = []

    def get(self, request: Request) -> Response:
        return Response({"status": "ok"})
