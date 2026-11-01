"""Briques d'admin partagees : zone JSON lisible, sauvegarde sans erreur 500."""

import json

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import models


class PrettyJSONField(forms.JSONField):
    """Champ JSON affiche indente, dans une zone de texte a chasse fixe."""

    widget = forms.Textarea(
        attrs={"rows": 18, "cols": 100, "style": "font-family: monospace;"}
    )

    def prepare_value(self, value):
        if isinstance(value, str):
            return value  # Saisie invalide renvoyee telle quelle.
        return json.dumps(value, indent=2, ensure_ascii=False)


class ContentAdmin(admin.ModelAdmin):
    """Base des admins de contenu."""

    formfield_overrides = {models.JSONField: {"form_class": PrettyJSONField}}
    save_on_top = True

    def save_model(self, request, obj, form, change):
        # Les garde-fous du modele (ex. publication refusee) ne doivent jamais
        # produire une erreur 500 : message clair, rien n'est enregistre.
        try:
            super().save_model(request, obj, form, change)
        except ValidationError as exc:
            self.message_user(request, " ".join(exc.messages), level=messages.ERROR)
