from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from home.models import HomePage
from wagtail.documents import get_document_model

from .models import PresentationPage


class PresentationPageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.home = HomePage.objects.get(slug="home")
        cls.document = get_document_model().objects.create(
            title="Demo presentation",
            file=SimpleUploadedFile(
                "demo.pdf",
                b"%PDF-1.4\n%%EOF\n",
                content_type="application/pdf",
            ),
        )
        cls.page = PresentationPage(title="PDF demo", slug="pdf-demo", pdf=cls.document)
        cls.home.add_child(instance=cls.page)
        cls.page.save_revision().publish()

    def test_presentation_page_can_reference_document(self):
        self.assertEqual(self.page.pdf, self.document)

    def test_published_page_renders_successfully(self):
        response = self.client.get(self.page.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "presentation/presentation_page.html")
        self.assertContains(response, "Описание слайда")

    def test_document_url_is_passed_in_data_attribute(self):
        response = self.client.get(self.page.url)

        self.assertContains(response, f'data-pdf-url="{self.document.url}"')
        self.assertNotContains(response, "<iframe")
