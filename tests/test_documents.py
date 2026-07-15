import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.documents.models import Document, validate_file_size


def make_pdf(name="doc.pdf"):
    return SimpleUploadedFile(name, b"%PDF-1.4 fake content", content_type="application/pdf")


@pytest.mark.django_db
def test_document_str_and_tag_list():
    doc = Document.objects.create(title="SK Jabatan", file=make_pdf(), tags="sk, jabatan , 2026")
    assert str(doc) == "SK Jabatan"
    assert doc.tag_list() == ["sk", "jabatan", "2026"]


def test_validate_file_size_rejects_large_file():
    big_file = SimpleUploadedFile("big.pdf", b"x" * (11 * 1024 * 1024))
    with pytest.raises(ValidationError):
        validate_file_size(big_file)


def test_validate_file_size_accepts_small_file():
    small_file = SimpleUploadedFile("small.pdf", b"x" * 1024)
    validate_file_size(small_file)


@pytest.mark.django_db
def test_document_list_requires_login(client):
    response = client.get(reverse("documents:document_list"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_document_list_filters_by_category(auth_client):
    Document.objects.create(title="SK One", file=make_pdf("a.pdf"), category=Document.Category.SK)
    Document.objects.create(
        title="Cert One", file=make_pdf("b.pdf"), category=Document.Category.CERTIFICATE
    )
    response = auth_client.get(reverse("documents:document_list"), {"category": "sk"})
    titles = [d.title for d in response.context["documents"]]
    assert titles == ["SK One"]


@pytest.mark.django_db
def test_document_list_search_by_tags(auth_client):
    Document.objects.create(title="Alpha", file=make_pdf("a.pdf"), tags="research")
    Document.objects.create(title="Beta", file=make_pdf("b.pdf"), tags="teaching")
    response = auth_client.get(reverse("documents:document_list"), {"q": "research"})
    titles = [d.title for d in response.context["documents"]]
    assert titles == ["Alpha"]


@pytest.mark.django_db
def test_document_create_view(auth_client):
    response = auth_client.post(
        reverse("documents:document_create"),
        {"title": "New Doc", "category": "other", "file": make_pdf(), "tags": ""},
    )
    assert response.status_code == 302
    assert Document.objects.filter(title="New Doc").exists()


@pytest.mark.django_db
def test_document_delete_via_htmx_returns_toast_header(auth_client):
    doc = Document.objects.create(title="To Delete", file=make_pdf())
    response = auth_client.post(
        reverse("documents:document_delete", args=[doc.pk]), HTTP_HX_REQUEST="true"
    )
    assert response.status_code == 200
    assert "HX-Trigger" in response.headers
    assert not Document.objects.filter(pk=doc.pk).exists()


@pytest.mark.django_db
def test_document_delete_non_htmx_redirects(auth_client):
    doc = Document.objects.create(title="To Delete Too", file=make_pdf())
    response = auth_client.post(reverse("documents:document_delete", args=[doc.pk]))
    assert response.status_code == 302
    assert not Document.objects.filter(pk=doc.pk).exists()
