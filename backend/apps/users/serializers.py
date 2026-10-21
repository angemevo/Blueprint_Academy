from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    """Le champ `role` n'existe pas : tout `role` envoye est ignore."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_username(self, value):
        if get_user_model().objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est deja pris.")
        return value

    def validate_email(self, value):
        if get_user_model().objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Cet email est deja utilise.")
        return value

    def validate(self, attrs):
        user = get_user_model()(username=attrs["username"], email=attrs["email"])
        try:
            validate_password(attrs["password"], user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "role")
        read_only_fields = fields
