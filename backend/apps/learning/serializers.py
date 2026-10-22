from rest_framework import serializers

from .models import LearningPath, Lesson, Module, Skill


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name", "slug", "category", "difficulty"]


class LessonTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "slug", "summary", "order", "estimated_minutes"]


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonTitleSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ["id", "title", "slug", "description", "order", "lessons"]


class LearningPathListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningPath
        fields = [
            "id", "title", "slug", "subtitle", "description", "difficulty",
            "estimated_hours", "cover_image_url", "order",
        ]


class LearningPathDetailSerializer(LearningPathListSerializer):
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta(LearningPathListSerializer.Meta):
        fields = LearningPathListSerializer.Meta.fields + ["modules"]


class LessonDetailSerializer(serializers.ModelSerializer):
    skills_taught = SkillSerializer(many=True, read_only=True)
    required_skills = SkillSerializer(many=True, read_only=True)
    module_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id", "title", "slug", "summary", "content", "estimated_minutes",
            "xp_reward", "order", "module_id", "skills_taught", "required_skills",
        ]
