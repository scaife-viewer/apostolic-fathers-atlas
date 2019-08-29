from django.contrib.postgres.fields import JSONField
from django.db import models


class Version(models.Model):
    """
    urn:cts:greekLit:tlg1271.tlg001.1st1K-grc1
    """

    urn = models.CharField(max_length=255)
    name = models.CharField(blank=True, null=True, max_length=255)
    metadata = JSONField(encoder="", default=dict, blank=True)
    """
    {
        "work_urn": "urn:cts:greekLit:tlg1271.tlg001.1st1K-grc1",
        "work_title": "The First Epistle of Clement",
        "type": "version"
    }
    """

    class Meta:
        ordering = ["urn"]

    def __str__(self):
        return self.name


class Section(models.Model):
    """
    urn:cts:greekLit:tlg1271.tlg001.1st1K-grc1:1
    """

    position = models.IntegerField()
    idx = models.IntegerField(help_text="0-based index")

    version = models.ForeignKey(
        "library.Version", related_name="sections", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["idx"]

    @property
    def label(self):
        return f"{self.position}"

    def __str__(self):
        return f"{self.version} [section={self.position}]"


class Chapter(models.Model):
    """
    urn:cts:greekLit:tlg1271.tlg001.1st1K-grc1:1.1
    """

    position = models.IntegerField()
    idx = models.IntegerField(help_text="0-based index")

    section = models.ForeignKey(
        "library.Section",
        related_name="chapters",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    version = models.ForeignKey(
        "library.Version", related_name="chapters", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["idx"]

    @property
    def label(self):
        if self.section:
            return f"{self.section.position}:{self.position}"
        return f"1:{self.position}"

    def __str__(self):
        return f"{self.version} [chapter={self.label}]"


class Verse(models.Model):
    """
    urn:cts:greekLit:tlg1271.tlg001.1st1K-grc1:1.1.1
    """

    text_content = models.TextField(blank=True)
    html_content = models.TextField(blank=True)

    position = models.IntegerField()
    idx = models.IntegerField(help_text="0-based index")

    chapter = models.ForeignKey(
        "library.Chapter", related_name="verses", on_delete=models.CASCADE
    )
    section = models.ForeignKey(
        "library.Section",
        related_name="verses",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    version = models.ForeignKey(
        "library.Version", related_name="verses", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["idx"]

    @property
    def label(self):
        if self.section:
            return f"{self.section.position}:{self.chapter.position}:{self.position}"
        return f"{self.chapter.position}:{self.position}"

    def __str__(self):
        return f"{self.version} [verse={self.label}]"
