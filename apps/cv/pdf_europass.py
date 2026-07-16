"""Europass-style CV PDF: classic dates-in-a-narrow-left-column layout with
grey section bars, distinct from the accent-color academic style.
"""

import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

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

    full_name = profile.full_name if profile else "Lecturer"
    personal_rows = [[Paragraph("Name", LABEL_STYLE), Paragraph(full_name, NAME_STYLE)]]
    if profile:
        if profile.email:
            personal_rows.append(
                [Paragraph("Email", LABEL_STYLE), Paragraph(profile.email, BODY_STYLE)]
            )
        if profile.phone:
            personal_rows.append(
                [Paragraph("Phone", LABEL_STYLE), Paragraph(profile.phone, BODY_STYLE)]
            )
        if profile.current_position:
            personal_rows.append(
                [
                    Paragraph("Position", LABEL_STYLE),
                    Paragraph(profile.current_position, BODY_STYLE),
                ]
            )
        if profile.institution:
            personal_rows.append(
                [Paragraph("Institution", LABEL_STYLE), Paragraph(profile.institution, BODY_STYLE)]
            )
    personal_table = Table(personal_rows, colWidths=[3.2 * cm, 11 * cm])
    personal_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
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
        for label, group in context["publications_by_type"]:
            for pub in group:
                cite = f"{pub.authors} ({pub.year}). {pub.title}. {pub.venue}."
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
