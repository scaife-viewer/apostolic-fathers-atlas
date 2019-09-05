from django.contrib import admin

from .models import Chapter, Section, Verse, Version


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ("id", "urn", "name", "metadata")
    search_fields = ("name",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("id", "position", "idx", "version")
    list_filter = ("version",)


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("id", "position", "idx", "section", "version")
    list_filter = ("section", "version")


@admin.register(Verse)
class VerseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "text_content",
        "position",
        "idx",
        "chapter",
        "section",
        "version",
    )
    list_filter = ("chapter", "section", "version")
