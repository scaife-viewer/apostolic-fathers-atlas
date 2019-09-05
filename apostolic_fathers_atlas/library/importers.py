import json
import os

from django.conf import settings

from .models import Chapter, Section, Verse, Version


LIBRARY_DATA_PATH = os.path.join(settings.PROJECT_ROOT, "data", "library")
LIBRARY_METADATA_PATH = os.path.join(LIBRARY_DATA_PATH, "metadata.json")


def _prepare_line_obj(
    version_obj,
    section_lookup,
    chapter_lookup,
    section_idx,
    chapter_idx,
    line,
    line_idx,
):
    ref, tokens = line.strip().split(maxsplit=1)
    split = ref.split(".")
    try:
        section_ref, chapter_ref, verse_ref = split
    except ValueError:
        section_ref = None
        chapter_ref, verse_ref = split

    if section_ref:
        section_obj = section_lookup.get(section_ref)
        if section_obj is None:
            section_position = int(section_ref)
            section_obj, _ = Section.objects.get_or_create(
                version=version_obj, position=section_position, idx=section_idx
            )
            section_lookup[section_ref] = section_obj
            section_idx += 1

    chapter_obj = chapter_lookup.get(chapter_ref)
    if chapter_obj is None:
        try:
            chapter_position = int(chapter_ref)
            chapter_identifier = None
        except ValueError:
            chapter_position = chapter_idx + 1
            chapter_identifier = chapter_ref
        chapter_obj, _ = Chapter.objects.get_or_create(
            version=version_obj,
            identifier=chapter_identifier,
            position=chapter_position,
            idx=chapter_idx,
        )
        chapter_lookup[chapter_ref] = chapter_obj
        chapter_idx += 1

    return (
        Verse(
            text_content=tokens,
            position=int(verse_ref),
            idx=line_idx,
            chapter=chapter_obj,
            section=None if not section_ref else section_obj,
            version=version_obj,
        ),
        section_idx,
        chapter_idx,
    )


def _import_version(data):
    version_obj, _ = Version.objects.update_or_create(
        urn=data["urn"],
        defaults=dict(name=data["metadata"]["work_title"], metadata=data["metadata"]),
    )

    section_lookup = {}
    chapter_lookup = {}
    section_idx = 0
    chapter_idx = 0
    lines_to_create = []

    full_content_path = os.path.join(LIBRARY_DATA_PATH, data["content_path"])
    with open(full_content_path, "r") as f:
        for line_idx, line in enumerate(f):
            line_obj, inc_section_idx, inc_chapter_idx = _prepare_line_obj(
                version_obj,
                section_lookup,
                chapter_lookup,
                section_idx,
                chapter_idx,
                line,
                line_idx,
            )
            lines_to_create.append(line_obj)
            section_idx = inc_section_idx
            chapter_idx = inc_chapter_idx
    created_count = len(Verse.objects.bulk_create(lines_to_create))
    assert created_count == line_idx + 1


def import_versions(reset=False):
    if reset:
        # Delete all previous Version instances.
        Version.objects.all().delete()

    library_metadata = json.load(open(LIBRARY_METADATA_PATH))
    for version_data in library_metadata["versions"]:
        _import_version(version_data)
