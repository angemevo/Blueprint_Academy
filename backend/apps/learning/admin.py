"""Admin de l'app learning : parcours, modules, lecons et skills."""

from django.contrib import admin

from common.admin import ContentAdmin, PublishableAdmin

from .models import LearningPath, Lesson, Module, Skill


@admin.register(Skill)
class SkillAdmin(ContentAdmin):
    list_display = ("name", "category", "difficulty", "is_active")
    list_filter = ("category", "difficulty", "is_active")
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("prerequisites",)


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0
    fields = ("title", "slug", "order", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    show_change_link = True


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("title", "slug", "order", "estimated_minutes", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    show_change_link = True


@admin.register(LearningPath)
class LearningPathAdmin(PublishableAdmin):
    list_display = ("title", "difficulty", "order", "is_published")
    list_filter = ("is_published", "difficulty")
    list_editable = ("order",)
    search_fields = ("title", "slug", "subtitle")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("required_skills",)
    inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(PublishableAdmin):
    list_display = ("title", "learning_path", "order", "is_published")
    list_filter = ("is_published", "learning_path")
    list_editable = ("order",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(PublishableAdmin):
    list_display = ("title", "module", "order", "is_published")
    list_filter = ("is_published", "module__learning_path", "module")
    list_editable = ("order",)
    search_fields = ("title", "slug", "summary")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("skills_taught", "required_skills")
