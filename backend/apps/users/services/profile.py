"""Mise a jour du profil courant."""

from apps.users.models import Profile

EDITABLE_FIELDS = ("display_name", "bio", "avatar_url", "onboarding_completed")


def get_or_create_profile(user) -> Profile:
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def update_profile(user, data: dict) -> Profile:
    profile = get_or_create_profile(user)
    changed = [f for f in EDITABLE_FIELDS if f in data]
    for field in changed:
        setattr(profile, field, data[field])
    if changed:
        profile.save(update_fields=[*changed, "updated_at"])
    return profile
