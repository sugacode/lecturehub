import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.documents.models import Document, SharedLink, validate_file_size


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


@pytest.mark.django_db
def test_shared_link_auto_generates_slug_from_name():
    link = SharedLink.objects.create(name="My CV", original_url="https://example.com/cv.pdf")
    assert link.slug == "my-cv"


@pytest.mark.django_db
def test_shared_link_auto_generated_slug_is_unique():
    SharedLink.objects.create(name="My CV", original_url="https://example.com/a.pdf")
    second = SharedLink.objects.create(name="My CV", original_url="https://example.com/b.pdf")
    assert second.slug == "my-cv-2"


@pytest.mark.django_db
def test_shared_link_respects_custom_slug():
    link = SharedLink.objects.create(
        name="My CV", original_url="https://example.com/cv.pdf", slug="resume-2026"
    )
    assert link.slug == "resume-2026"


@pytest.mark.django_db
def test_shared_link_redirect_is_public_and_unauthenticated(client):
    SharedLink.objects.create(
        name="My CV", original_url="https://example.com/cv.pdf", slug="my-cv"
    )
    response = client.get(reverse("shared_link_redirect", args=["my-cv"]))
    assert response.status_code == 302
    assert response.url == "https://example.com/cv.pdf"


@pytest.mark.django_db
def test_shared_link_redirect_404s_for_unknown_slug(client):
    response = client.get(reverse("shared_link_redirect", args=["does-not-exist"]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_shared_link_list_requires_login(client):
    response = client.get(reverse("documents:shared_link_list"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_shared_link_create_view_with_only_name_and_url(auth_client):
    """The whole point: creating a share link needs just a name and a URL —
    the slug is optional and auto-generated."""
    response = auth_client.post(
        reverse("documents:shared_link_create"),
        {"name": "Weekly Schedule", "original_url": "https://example.com/schedule.pdf"},
    )
    assert response.status_code == 302
    link = SharedLink.objects.get(name="Weekly Schedule")
    assert link.slug == "weekly-schedule"


@pytest.mark.django_db
def test_shared_link_create_view_with_custom_slug(auth_client):
    response = auth_client.post(
        reverse("documents:shared_link_create"),
        {
            "name": "Weekly Schedule",
            "original_url": "https://example.com/schedule.pdf",
            "slug": "sched",
        },
    )
    assert response.status_code == 302
    assert SharedLink.objects.get(name="Weekly Schedule").slug == "sched"


@pytest.mark.django_db
def test_shared_link_delete_via_htmx_returns_toast_header(auth_client):
    link = SharedLink.objects.create(name="To Delete", original_url="https://example.com/x")
    response = auth_client.post(
        reverse("documents:shared_link_delete", args=[link.pk]), HTTP_HX_REQUEST="true"
    )
    assert response.status_code == 200
    assert "HX-Trigger" in response.headers
    assert not SharedLink.objects.filter(pk=link.pk).exists()


@pytest.mark.django_db
def test_shared_link_qr_requires_login(client):
    link = SharedLink.objects.create(name="My CV", original_url="https://example.com/cv.pdf")
    response = client.get(reverse("documents:shared_link_qr", args=[link.pk]))
    assert response.status_code == 302


@pytest.mark.django_db
def test_shared_link_qr_returns_downloadable_png(auth_client):
    link = SharedLink.objects.create(
        name="My CV", original_url="https://example.com/cv.pdf", slug="my-cv"
    )
    response = auth_client.get(reverse("documents:shared_link_qr", args=[link.pk]))
    assert response.status_code == 200
    assert response["Content-Type"] == "image/png"
    assert response["Content-Disposition"] == 'attachment; filename="my-cv-qr.png"'
    assert response.content.startswith(b"\x89PNG")


@pytest.mark.django_db
def test_shared_link_qr_view_calls_qrcode_with_the_share_url(auth_client, monkeypatch):
    """Scanning the QR should land on /s/<slug>/ (which then redirects), not
    jump straight to original_url — verify the exact string handed to
    qrcode.make() rather than round-tripping through a QR decoder, which
    would need a new system-level dependency (zbar) just for this test."""
    import apps.documents.views as views_module

    link = SharedLink.objects.create(
        name="My CV", original_url="https://example.com/cv.pdf", slug="my-cv"
    )
    captured = {}
    original_make = views_module.qrcode.make

    def spy_make(data):
        captured["data"] = data
        return original_make(data)

    monkeypatch.setattr(views_module.qrcode, "make", spy_make)
    response = auth_client.get(reverse("documents:shared_link_qr", args=[link.pk]))
    assert response.status_code == 200
    assert captured["data"].endswith("/s/my-cv/")
    assert "example.com" not in captured["data"]
