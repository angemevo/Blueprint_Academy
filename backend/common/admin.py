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

    def save_formset(self, request, form, formset, change):
        # Cases is_published des inlines : meme regle, message au lieu d'un 500.
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for obj in instances:
            try:
                obj.save()
            except ValidationError as exc:
                self.message_user(
                    request, f"« {obj} » : " + " ".join(exc.messages), level=messages.ERROR
                )
        formset.save_m2m()



class PublishableAdmin(ContentAdmin):
    """Admin des contenus publiables : actions Publier / Depublier."""

    actions = ["publier", "depublier"]

    @admin.action(description="Publier (avec controle d'integrite)")
    def publier(self, request, queryset):
        from apps.learning.services.publication import publish

        done = 0
        for obj in queryset:
            problems = publish(obj)
            for p in problems:
                self.message_user(request, p, level=messages.ERROR)
            done += not problems
        if done:
            self.message_user(request, f"{done} element(s) publie(s).")

    @admin.action(description="Depublier")
    def depublier(self, request, queryset):
        from apps.learning.services.publication import unpublish

        for obj in queryset:
            unpublish(obj)
        self.message_user(request, f"{queryset.count()} element(s) depublie(s).")
