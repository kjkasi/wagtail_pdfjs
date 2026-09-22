from django.db import models

from wagtail.admin.panels import FieldPanel
from wagtail.models import Page


class PresentationPage(Page):
    """A page that renders one uploaded PDF as a slide presentation."""

    pdf = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [FieldPanel("pdf")]

    parent_page_types = ["home.HomePage"]
    subpage_types = []
