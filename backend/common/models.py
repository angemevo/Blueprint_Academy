"""Modeles abstraits partages.

Abstraits uniquement : Django ne les enregistre pas, ils n'ont donc pas besoin
d'appartenir a une app installee.
"""

from django.db import models


class TimeStampedModel(models.Model):
    """Horodatage de creation et de derniere modification."""

    created_at = models.DateTimeField("cree le", auto_now_add=True)
    updated_at = models.DateTimeField("modifie le", auto_now=True)

    class Meta:
        abstract = True


class PublishableModel(models.Model):
    """Contenu pedagogique publiable depuis l'admin, sans toucher au code."""

    is_published = models.BooleanField("publie", default=False, db_index=True)

    class Meta:
        abstract = True


class OrderedModel(models.Model):
    """Element positionne dans une sequence (parcours, module, lecon...)."""

    order = models.PositiveIntegerField("position", default=0, db_index=True)

    class Meta:
        abstract = True
