from django.db import models

from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, MultiFieldPanel
from wagtail.core import blocks
from wagtail.core.blocks import PageChooserBlock, StructValue
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page


def validate_url(value: str):
    if value.startswith("http"):
        check_absolute_url = URLValidator(schemes=["http", "https"])
        check_absolute_url(value)
    elif not value.startswith("/"):
        raise ValidationError(
            f"{value} is not a valid relative URL. It should start with /."
        )


class URLPlusBlock(blocks.CharBlock):
    def __init__(
        self, required=True, help_text=None, max_length=None, min_length=None, **kwargs
    ):
        super().__init__(
            required, help_text, max_length, min_length, (validate_url,), **kwargs
        )


class LinkStructValue(StructValue):
    def url(self):
        page = self.get("page")
        if page:
            return page.url
        else:
            return self.get("link")


class LinkBlock(blocks.StructBlock):
    page = PageChooserBlock(required=False, label="Page")
    link = URLPlusBlock(max_length=255, required=False, label="Link")

    class Meta:
        icon = "link"
        help_text = "Choose only one to add a link"
        form_classname = "admin-link admin-flex"
        value_class = LinkStructValue

    def clean(self, value):
        result = super().clean(value)

        errors = {}
        if result.get("page") and result.get("link"):
            errors["page"] = errors["link"] = ErrorList(["Select page OR add a link."])
            raise ValidationError(
                "Select page OR add a link.", params=errors
            )


class TitleLinkBlock(blocks.StructBlock):
	title = blocks.CharBlock(required=False, max_length=255)
	link = LinkBlock(required=True)


class OutsidePage(Page):
    body = StreamField([
		('title_and_link', TitleLinkBlock()),
    ])

    # Search and editor panels configuration
    search_fields = []

    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
    ]

    template = "page.html"


class HomePage(Page):
    pass

