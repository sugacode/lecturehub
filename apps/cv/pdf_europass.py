"""Europass-style CV PDF: classic dates-in-a-narrow-left-column layout with
grey section bars, distinct from the accent-color academic style.
"""

import io

from reportlab.graphics.shapes import Circle, Drawing, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Small circular brand-color monogram icons, since ReportLab has no built-in
# icon set and pulling in an SVG-rasterizing dependency (svglib) just for
# four glyphs isn't worth it. Each is a 10pt Drawing: solid circle + a 1-2
# letter mark that reads at CV-header size, in the platform's brand color.
_ICON_SIZE = 10
_ICON_SPECS = {
    "whatsapp": ("#25D366", "W", colors.white),
    "orcid": ("#A6CE39", "iD", colors.white),
    "scholar": ("#4285F4", "S", colors.white),
    "linkedin": ("#0A66C2", "in", colors.white),
}


def _icon(kind: str) -> Drawing:
    bg, mark, fg = _ICON_SPECS[kind]
    d = Drawing(_ICON_SIZE, _ICON_SIZE)
    d.add(
        Circle(
            _ICON_SIZE / 2,
            _ICON_SIZE / 2,
            _ICON_SIZE / 2,
            fillColor=colors.HexColor(bg),
            strokeColor=None,
        )
    )
    font_size = 6 if len(mark) == 1 else 4.6
    d.add(
        String(
            _ICON_SIZE / 2,
            _ICON_SIZE / 2 - font_size / 2.8,
            mark,
            fontName="Helvetica-Bold",
            fontSize=font_size,
            fillColor=fg,
            textAnchor="middle",
        )
    )
    return d


BAR_BG = colors.HexColor("#003366")
BAR_TEXT = colors.white
LABEL_COLOR = colors.HexColor("#003366")
TEXT_COLOR = colors.HexColor("#1A1A1A")

TITLE_STYLE = ParagraphStyle(
    "EPTitle", fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=BAR_BG
)
NAME_STYLE = ParagraphStyle(
    "EPName", fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=TEXT_COLOR
)
BAR_STYLE = ParagraphStyle(
    "EPBar", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=BAR_TEXT
)
DATE_STYLE = ParagraphStyle(
    "EPDate", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=LABEL_COLOR
)
CONTENT_TITLE_STYLE = ParagraphStyle(
    "EPContentTitle", fontName="Helvetica-Bold", fontSize=9.5, leading=12.5, textColor=TEXT_COLOR
)
CONTENT_SUB_STYLE = ParagraphStyle(
    "EPContentSub", fontName="Helvetica-Oblique", fontSize=9, leading=12, textColor=colors.grey
)
BODY_STYLE = ParagraphStyle(
    "EPBody", fontName="Helvetica", fontSize=9, textColor=TEXT_COLOR, leading=12
)
LABEL_STYLE = ParagraphStyle(
    "EPLabel", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=LABEL_COLOR
)


def _bar(title: str) -> Table:
    table = Table([[Paragraph(title.upper(), BAR_STYLE)]], colWidths=[17 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), BAR_BG),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def _row(date_text: str, content: list) -> Table:
    table = Table([[Paragraph(date_text, DATE_STYLE), content]], colWidths=[3.2 * cm, 13.8 * cm])
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
            ]
        )
    )
    return table


def _flatten_publications_by_year(publications_by_type: list) -> list:
    """Europass lists all publications in one chronological list (no per-type
    headers), so flatten the type groups and re-sort newest-first across the
    whole set rather than relying on the type-then-year order pdf_data.py builds."""
    publications = [pub for _, group in publications_by_type for pub in group]
    publications.sort(key=lambda p: (-p.year, p.title))
    return publications


def build_europass_cv_pdf(context: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
    )
    story: list = []
    profile = context["profile"]

    story.append(Paragraph("Curriculum Vitae", TITLE_STYLE))
    story.append(Spacer(1, 8))

    def link(url: str, caption: str) -> str:
        return f'<a href="{url}" color="#003366"><u>{caption}</u></a>'

    full_name = profile.full_name if profile else "Lecturer"
    personal_rows = [["", Paragraph("Name", LABEL_STYLE), Paragraph(full_name, NAME_STYLE)]]
    if profile:
        if profile.email:
            personal_rows.append(
                [
                    "",
                    Paragraph("Email", LABEL_STYLE),
                    Paragraph(link("mailto:" + profile.email, profile.email), BODY_STYLE),
                ]
            )
        if profile.phone:
            if profile.whatsapp_url:
                personal_rows.append(
                    [
                        _icon("whatsapp"),
                        Paragraph("WhatsApp", LABEL_STYLE),
                        Paragraph(link(profile.whatsapp_url, profile.phone), BODY_STYLE),
                    ]
                )
            else:
                personal_rows.append(
                    ["", Paragraph("Phone", LABEL_STYLE), Paragraph(profile.phone, BODY_STYLE)]
                )
        if profile.orcid:
            personal_rows.append(
                [
                    _icon("orcid"),
                    Paragraph("ORCID", LABEL_STYLE),
                    Paragraph(link(profile.orcid_url, profile.orcid), BODY_STYLE),
                ]
            )
        if profile.google_scholar_id:
            personal_rows.append(
                [
                    _icon("scholar"),
                    Paragraph("Google Scholar", LABEL_STYLE),
                    Paragraph(
                        link(profile.google_scholar_url, profile.google_scholar_id), BODY_STYLE
                    ),
                ]
            )
        if profile.linkedin_url:
            personal_rows.append(
                [
                    _icon("linkedin"),
                    Paragraph("LinkedIn", LABEL_STYLE),
                    Paragraph(link(profile.linkedin_url, profile.linkedin_label), BODY_STYLE),
                ]
            )
        if profile.current_position:
            personal_rows.append(
                [
                    "",
                    Paragraph("Position", LABEL_STYLE),
                    Paragraph(profile.current_position, BODY_STYLE),
                ]
            )
        if profile.institution:
            personal_rows.append(
                [
                    "",
                    Paragraph("Institution", LABEL_STYLE),
                    Paragraph(profile.institution, BODY_STYLE),
                ]
            )
    personal_table = Table(personal_rows, colWidths=[0.55 * cm, 2.65 * cm, 11 * cm])
    personal_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (0, -1), 0),
                ("RIGHTPADDING", (0, 0), (0, -1), 2),
            ]
        )
    )
    if profile and profile.photo:
        try:
            photo = Image(profile.photo.path, width=2.8 * cm, height=2.8 * cm)
            wrapper = Table([[personal_table, photo]], colWidths=[14.2 * cm, 2.8 * cm])
            wrapper.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
            story.append(wrapper)
        except (OSError, ValueError):
            story.append(personal_table)
    else:
        story.append(personal_table)
    story.append(Spacer(1, 10))

    def add_section(title, items, row_builder):
        if not items:
            return
        story.append(_bar(title))
        story.append(Spacer(1, 4))
        for item in items:
            story.append(row_builder(item))
        story.append(Spacer(1, 8))

    def position_content(position):
        parts = [Paragraph(position.title, CONTENT_TITLE_STYLE)]
        parts.append(Paragraph(position.organization, CONTENT_SUB_STYLE))
        if position.description:
            parts.append(Paragraph(position.description, BODY_STYLE))
        return parts

    def position_row(position):
        end = position.end_date.isoformat() if position.end_date else "Present"
        date_text = f"{position.start_date.isoformat()}\n{end}"
        return _row(date_text, position_content(position))

    add_section("Work Experience", list(context["positions"]), position_row)

    def education_content(edu):
        return [
            Paragraph(f"{edu.get_degree_level_display()} — {edu.program}", CONTENT_TITLE_STYLE),
            Paragraph(edu.institution, CONTENT_SUB_STYLE),
        ]

    def education_row(edu):
        date_text = f"{edu.start_year} - {edu.end_year or 'present'}"
        return _row(date_text, education_content(edu))

    add_section("Education and Training", list(context["educations"]), education_row)

    skills = list(context["skills"])
    if skills:
        story.append(_bar("Personal Skills"))
        story.append(Spacer(1, 4))
        by_category: dict[str, list] = {}
        for skill in skills:
            by_category.setdefault(skill.get_category_display(), []).append(
                f"{skill.name} ({skill.proficiency}/5)"
            )
        rows = [
            [Paragraph(category, LABEL_STYLE), Paragraph(", ".join(items), BODY_STYLE)]
            for category, items in by_category.items()
        ]
        skills_table = Table(rows, colWidths=[3.2 * cm, 13.8 * cm])
        skills_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(skills_table)
        story.append(Spacer(1, 8))

    if context["publications_by_type"]:
        story.append(_bar("Publications"))
        story.append(Spacer(1, 4))
        for pub in _flatten_publications_by_year(context["publications_by_type"]):
            cite = f"{pub.authors} ({pub.year}). {pub.title}. {pub.venue}."
            if pub.doi:
                cite += f' <a href="https://doi.org/{pub.doi}" color="#003366"><u>{pub.doi}</u></a>'
            story.append(_row(str(pub.year), [Paragraph(cite, BODY_STYLE)]))
        story.append(Spacer(1, 8))

    grants = list(context["grants"])
    if grants:

        def grant_row(grant):
            end = grant.end_date.isoformat() if grant.end_date else "Present"
            date_text = f"{grant.start_date.isoformat()}\n{end}"
            content = [
                Paragraph(grant.title, CONTENT_TITLE_STYLE),
                Paragraph(f"{grant.funder} — {grant.get_role_display()}", CONTENT_SUB_STYLE),
            ]
            return _row(date_text, content)

        add_section("Grants", grants, grant_row)

    doc.build(story)
    return buffer.getvalue()
