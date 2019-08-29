import json
import os

from django.conf import settings

from roman_numerals import convert_to_numeral

from .models import Chapter, Section, Verse, Version


LIBRARY_DATA_PATH = os.path.join(settings.PROJECT_ROOT, "data", "library")
LIBRARY_METADATA_PATH = os.path.join(LIBRARY_DATA_PATH, "metadata.json")


def _prepare_verse_html(previous_state, new_state, verse, tokens):  # noqa
    previous_section = previous_state["section"]
    previous_chapter = previous_state["chapter"]
    section = new_state["section"]
    chapter = new_state["chapter"]

    html = ""
    if previous_section != section:
        if previous_section is not None:
            html += "</div>\n"
            html += "</div>\n"
        html += """<div class="section">\n"""
        previous_chapter = None

    if previous_chapter != chapter:
        if previous_chapter is not None:
            if previous_chapter == 0:
                if section is None:
                    html += "</div>\n"
            else:
                html += "</div>\n"
        if chapter == 0:
            if section is None:
                html += """<div class="preamble">\n"""
        else:
            if chapter == "SB":
                html += """<div class="subscription">\n"""
            elif chapter == "EP":
                html += """<div class="epilogue">\n"""
            else:
                numeral = convert_to_numeral(chapter)
                html += """<div class="chapter">\n"""
                html += f"""<h3 class="chapter_ref">{numeral}</h3>\n"""

    if chapter == 0 and verse == 0:
        html += f"""<h2 class="section_title">{tokens}</h2>\n"""
    else:
        if chapter == "EP" and verse == 0:
            html += f"""<h3 class="epilogue_title">{tokens}</h3>\n"""
        else:
            if verse != 1:
                html += f"""<span class="verse_ref">{verse}</span>&nbsp;"""
            html += f"{tokens}\n"

    return html


def _prepare_line_obj(
    version_obj,
    section_lookup,
    chapter_lookup,
    section_idx,
    chapter_idx,
    line,
    line_idx,
    previous_state,
):
    new_state = {"section": None, "chapter": None}
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
            new_state["section"] = section_position
            section_idx += 1
        else:
            new_state["section"] = section_obj.position

    chapter_obj = chapter_lookup.get(chapter_ref)
    if chapter_obj is None:

        # TODO: Non-numeric position! Hacked around.
        try:
            chapter_position = int(chapter_ref)
        except ValueError:
            chapter_position = previous_state["chapter"] + 1

        chapter_obj, _ = Chapter.objects.get_or_create(
            version=version_obj, position=chapter_position, idx=chapter_idx
        )
        chapter_lookup[chapter_ref] = chapter_obj
        new_state["chapter"] = chapter_position
        chapter_idx += 1
    else:
        new_state["chapter"] = chapter_obj.position

    verse_position = int(verse_ref)
    html = _prepare_verse_html(previous_state, new_state, verse_position, tokens)

    return (
        Verse(
            text_content=tokens,
            position=verse_position,
            idx=line_idx,
            chapter=chapter_obj,
            version=version_obj,
            html_content=html,
        ),
        new_state,
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
    previous_state = {"section": None, "chapter": None}

    full_content_path = os.path.join(LIBRARY_DATA_PATH, data["content_path"])
    with open(full_content_path, "r") as f:
        for line_idx, line in enumerate(f):
            line_obj, new_state = _prepare_line_obj(
                version_obj,
                section_lookup,
                chapter_lookup,
                section_idx,
                chapter_idx,
                line,
                line_idx,
                previous_state,
            )
            lines_to_create.append(line_obj)
            previous_state = new_state
    created_count = len(Verse.objects.bulk_create(lines_to_create))
    assert created_count == line_idx + 1


def import_versions(reset=False):
    if reset:
        # Delete all previous Version instances.
        Version.objects.all().delete()

    library_metadata = json.load(open(LIBRARY_METADATA_PATH))
    for version_data in library_metadata["versions"]:
        _import_version(version_data)
