from rest_framework import serializers

from .models import Exercise
from .services import catalog


class ExerciseDetailSerializer(serializers.ModelSerializer):
    """Vue publique d'un exercice : ni `solution`, ni texte des `hints`."""

    content = serializers.SerializerMethodField()
    xp_reward = serializers.IntegerField(source="effective_xp_reward", read_only=True)
    hints_count = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = [
            "id", "type", "title", "content", "difficulty",
            "time_limit_seconds", "max_attempts", "xp_reward", "hints_count",
        ]

    def get_content(self, obj):
        return catalog.public_content(obj)

    def get_hints_count(self, obj) -> int:
        return len(obj.hints or [])


class ExerciseLessonItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ["id", "title", "type"]
