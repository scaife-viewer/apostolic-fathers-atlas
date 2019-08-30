from graphene import ObjectType, String, relay
from graphene.types import generic
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Chapter, Section, Verse, Version


class VersionNode(DjangoObjectType):
    metadata = generic.GenericScalar()

    sections = DjangoFilterConnectionField(lambda: SectionNode)
    chapters = DjangoFilterConnectionField(lambda: ChapterNode)
    verses = DjangoFilterConnectionField(lambda: VerseNode)

    class Meta:
        model = Version
        interfaces = (relay.Node,)
        filter_fields = ["name", "urn"]


class SectionNode(DjangoObjectType):
    label = String()

    chapters = DjangoFilterConnectionField(lambda: ChapterNode)
    verses = DjangoFilterConnectionField(lambda: VerseNode)

    class Meta:
        model = Section
        interfaces = (relay.Node,)
        filter_fields = ["position", "version__urn"]


class ChapterNode(DjangoObjectType):
    label = String()

    verses = DjangoFilterConnectionField(lambda: VerseNode)

    class Meta:
        model = Chapter
        interfaces = (relay.Node,)
        filter_fields = ["position", "section__position", "version__urn"]


class VerseNode(DjangoObjectType):
    label = String()

    class Meta:
        model = Verse
        interfaces = (relay.Node,)
        filter_fields = [
            "position",
            "chapter__position",
            "section__position",
            "version__urn",
        ]


class Query(ObjectType):
    version = relay.Node.Field(VersionNode)
    versions = DjangoFilterConnectionField(VersionNode)

    section = relay.Node.Field(SectionNode)
    sections = DjangoFilterConnectionField(SectionNode)

    chapter = relay.Node.Field(ChapterNode)
    chapters = DjangoFilterConnectionField(ChapterNode)

    verse = relay.Node.Field(VerseNode)
    verses = DjangoFilterConnectionField(VerseNode)
