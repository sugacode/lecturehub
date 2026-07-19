"""Elegant-style CV PDF: adapted from the "CV" design (claude.ai/design
project 1eac8d7d-e02e-4792-a5d9-0e87b792eea5, "CV.dc.html") — a classic
letter-press look with warm-ink serif body text, small-caps-style uppercase
sans-serif section labels under a thin rule, and right-aligned date columns.

The source design specifies EB Garamond and Jost via Google Fonts, which is
fine for the HTML pages (the browser fetches them) but PDFs are rendered
server-side by ReportLab, which only ships the 14 standard PDF fonts with no
network access at generation time. Following the same approach already used
by pdf_academic.py and pdf_europass.py, this substitutes ReportLab's built-in
Times (serif) and Helvetica (sans) families rather than bundling font files.
"""

import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# LETTER page, 0.85in margins each side: usable content width. Every table's
# colWidths below must sum to exactly this — they previously summed to
# slightly more (were sized in cm without checking against the actual page
# width), which pushed the right-hand column of every table (photo, contact
# links, dates, IP metadata, skill ratings) past the right margin.
CONTENT_WIDTH = 8.5 * inch - 2 * 0.85 * inch

INK = colors.HexColor("#1c1a17")
LABEL_INK = colors.HexColor("#2a3342")
MUTED = colors.HexColor("#5a6072")
SUBTEXT = colors.HexColor("#3d4252")
BODY_INK = colors.HexColor("#33323a")
RULE = colors.HexColor("#c9ccd4")
TABLE_RULE = colors.HexColor("#e4e2dc")
LINK_COLOR = "#0000FF"

PROFICIENCY_LABELS = {5: "Expert", 4: "Advanced", 3: "Intermediate", 2: "Basic", 1: "Beginner"}
CATEGORY_LABELS = {
    "technical": "Tools & Technical",
    "language": "Languages",
    "research": "Research & Methods",
}

NAME_STYLE = ParagraphStyle("Name", fontName="Times-Bold", fontSize=21, leading=24, textColor=INK)
TAGLINE_STYLE = ParagraphStyle(
    "Tagline", fontName="Helvetica", fontSize=9, leading=13, textColor=MUTED, spaceBefore=3
)
CONTACT_STYLE = ParagraphStyle(
    "Contact", fontName="Helvetica", fontSize=8, leading=15, textColor=MUTED, alignment=2
)
SECTION_STYLE = ParagraphStyle(
    "Section",
    fontName="Helvetica-Bold",
    fontSize=9.5,
    leading=13,
    textColor=LABEL_INK,
    spaceBefore=12,
    spaceAfter=2,
)
SUBSECTION_STYLE = ParagraphStyle(
    "Subsection",
    fontName="Helvetica-Bold",
    fontSize=8,
    leading=11,
    textColor=MUTED,
    spaceBefore=6,
    spaceAfter=3,
)
ENTRY_TITLE_STYLE = ParagraphStyle(
    "EntryTitle", fontName="Times-Bold", fontSize=10.5, leading=13, textColor=INK
)
ENTRY_DATE_STYLE = ParagraphStyle(
    "EntryDate", fontName="Helvetica", fontSize=8.5, leading=13, textColor=MUTED, alignment=2
)
ENTRY_SUB_STYLE = ParagraphStyle(
    "EntrySub", fontName="Times-Italic", fontSize=9.5, leading=12, textColor=SUBTEXT, spaceAfter=1
)
ENTRY_DESC_STYLE = ParagraphStyle(
    "EntryDesc",
    fontName="Times-Roman",
    fontSize=9,
    leading=12,
    textColor=colors.HexColor("#4a4e5c"),
)
BODY_STYLE = ParagraphStyle("Body", fontName="Times-Roman", fontSize=10, leading=15, textColor=INK)
PUB_STYLE = ParagraphStyle(
    "Pub", fontName="Times-Roman", fontSize=8.5, leading=13, textColor=BODY_INK, spaceAfter=5
)
TABLE_CELL_STYLE = ParagraphStyle(
    "TableCell", fontName="Times-Roman", fontSize=9, textColor=INK, leading=12
)
TABLE_META_STYLE = ParagraphStyle(
    "TableMeta", fontName="Times-Roman", fontSize=9, textColor=MUTED, alignment=2, leading=12
)
SKILL_NAME_STYLE = ParagraphStyle("SkillName", fontName="Times-Roman", fontSize=9, textColor=INK)
SKILL_RATING_STYLE = ParagraphStyle(
    "SkillRating", fontName="Times-Italic", fontSize=9, textColor=MUTED, alignment=2
)


def _section(title: str) -> list:
    return [
        Paragraph(title.upper(), SECTION_STYLE),
        HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=6),
    ]


def _entry(date_text: str, title: str, subtitle: str, description: str = "") -> list:
    row = Table(
        [[Paragraph(title, ENTRY_TITLE_STYLE), Paragraph(date_text, ENTRY_DATE_STYLE)]],
        colWidths=[CONTENT_WIDTH * 0.72, CONTENT_WIDTH * 0.28],
    )
    row.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    flowables = [row]
    if subtitle:
        flowables.append(Paragraph(subtitle, ENTRY_SUB_STYLE))
    if description:
        flowables.append(Paragraph(description, ENTRY_DESC_STYLE))
    flowables.append(Spacer(1, 7))
    return flowables


def build_elegant_cv_pdf(context: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
    )
    story: list = []
    profile = context["profile"]

    # Header: photo, name + role tagline, contact block — mirrors the
    # design's photo-left / name-middle / contact-right three-column row.
    full_name = profile.full_name if profile else "Lecturer"
    if profile:
        title_line = f"{profile.title_prefix} {full_name} {profile.title_suffix}".strip()
    else:
        title_line = full_name
    name_cell = [Paragraph(title_line, NAME_STYLE)]
    if profile and profile.current_position:
        name_cell.append(Paragraph(profile.current_position.upper(), TAGLINE_STYLE))

    contact_lines = []
    if profile and profile.institution:
        contact_lines.append(profile.institution)
    if profile and profile.email:
        contact_lines.append(
            f'<a href="mailto:{profile.email}" color="{LINK_COLOR}">{profile.email}</a>'
        )
    if profile and profile.phone:
        if profile.whatsapp_url:
            contact_lines.append(
                f'<a href="{profile.whatsapp_url}" color="{LINK_COLOR}">{profile.phone}</a>'
            )
        else:
            contact_lines.append(profile.phone)
    link_bits = []
    if profile and profile.linkedin_url:
        link_bits.append(f'<a href="{profile.linkedin_url}" color="{LINK_COLOR}">LinkedIn</a>')
    if profile and profile.orcid:
        link_bits.append(f'<a href="{profile.orcid_url}" color="{LINK_COLOR}">ORCID</a>')
    if profile and profile.google_scholar_id:
        link_bits.append(
            f'<a href="{profile.google_scholar_url}" color="{LINK_COLOR}">Google Scholar</a>'
        )
    if link_bits:
        contact_lines.append(" &middot; ".join(link_bits))
    contact_cell = [Paragraph(line, CONTACT_STYLE) for line in contact_lines]

    # Photo left of the name, matching the source design's flex row (photo |
    # name, flex:1 | contact, right-aligned) exactly. The earlier "not in
    # line" bug wasn't this — a photo column to the left of the name is the
    # design's intent, and every section below the header starts at the same
    # left margin the photo (not the name) sits flush against. The actual bug
    # was the column widths summing to more than the page's content width
    # (fixed below with CONTENT_WIDTH-based fractions), which let the photo
    # and contact block bleed past the right margin.
    header_row = [name_cell, contact_cell]
    col_widths = [CONTENT_WIDTH * 0.625, CONTENT_WIDTH * 0.375]
    header_style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (-1, 0), (-1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]
    if profile and profile.photo:
        try:
            photo_width = 0.9 * inch
            photo_gap = 0.2 * inch
            photo = Image(profile.photo.path, width=photo_width, height=photo_width)
            header_row = [photo, *header_row]
            remaining = CONTENT_WIDTH - photo_width - photo_gap
            col_widths = [photo_width + photo_gap, remaining * 0.68, remaining * 0.32]
            header_style.append(("RIGHTPADDING", (0, 0), (0, 0), photo_gap))
        except (OSError, ValueError):
            pass

    header_table = Table([header_row], colWidths=col_widths)
    header_table.setStyle(TableStyle(header_style))
    story.append(header_table)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.1, color=LABEL_INK, spaceAfter=12))

    if profile and profile.bio:
        story.extend(_section("Research Profile"))
        story.append(Paragraph(profile.bio, BODY_STYLE))

    # Education
    educations = list(context["educations"])
    if educations:
        story.extend(_section("Education"))
        for edu in educations:
            years = f"{edu.start_year}–{edu.end_year or 'present'}"
            subtitle = f"{edu.institution}, {edu.country}" if edu.country else edu.institution
            details = []
            if edu.thesis_title:
                details.append(f"Thesis: {edu.thesis_title}")
            if edu.gpa:
                details.append(f"GPA {edu.gpa}")
            degree_title = f"{edu.get_degree_level_display()} — {edu.program}"
            story.extend(_entry(years, degree_title, subtitle, " · ".join(details)))

    # Positions
    positions = list(context["positions"])
    if positions:
        story.extend(_section("Positions & Professional Experience"))
        for position in positions:
            end = position.end_date.isoformat() if position.end_date else "present"
            date_text = f"{position.start_date.isoformat()}–{end}"
            story.extend(
                _entry(date_text, position.title, position.organization, position.description or "")
            )

    # Publications — numbered continuously across type groups, on their own page.
    if context["publications_by_type"]:
        story.append(PageBreak())
        story.extend(_section("Publications"))
        counter = 0
        for label, group in context["publications_by_type"]:
            story.append(Paragraph(f"{label} ({len(group)})".upper(), SUBSECTION_STYLE))
            for pub in group:
                counter += 1
                cite = f"{pub.authors} ({pub.year}). {pub.title}. <i>{pub.venue}</i>"
                if pub.volume:
                    cite += f", {pub.volume}"
                if pub.issue:
                    cite += f"({pub.issue})"
                if pub.pages:
                    cite += f", {pub.pages}"
                cite += "."
                if pub.doi:
                    doi_url = f"https://doi.org/{pub.doi}"
                    cite += f' <a href="{doi_url}" color="{LINK_COLOR}">doi:{pub.doi}</a>'
                story.append(Paragraph(f"{counter}. {cite}", PUB_STYLE))

    # Intellectual Property — table, on its own page.
    intellectual_properties = list(context["intellectual_properties"])
    if intellectual_properties:
        story.append(PageBreak())
        story.extend(_section("Intellectual Property"))
        rows = []
        for ip in intellectual_properties:
            meta = f"{ip.get_ip_type_display()}"
            if ip.registration_number:
                meta += f" No. {ip.registration_number}"
            meta += f" · {ip.registration_date.year}"
            rows.append([Paragraph(ip.title, TABLE_CELL_STYLE), Paragraph(meta, TABLE_META_STYLE)])
        ip_table = Table(rows, colWidths=[CONTENT_WIDTH * 0.675, CONTENT_WIDTH * 0.325])
        ip_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LINEBELOW", (0, 0), (-1, -2), 0.5, TABLE_RULE),
                ]
            )
        )
        story.append(ip_table)

    # Grants
    grants = list(context["grants"])
    if grants:
        story.extend(_section("Grants"))
        for grant in grants:
            end = grant.end_date.isoformat() if grant.end_date else "present"
            date_text = f"{grant.start_date.isoformat()}–{end}"
            subtitle = f"{grant.funder} — {grant.get_role_display()}"
            story.extend(_entry(date_text, grant.title, subtitle))

    # Service
    services = list(context["community_services"])
    roles = list(context["organizational_roles"])
    if services or roles:
        story.extend(_section("Service"))
        for role in roles:
            end = role.end_date.isoformat() if role.end_date else "present"
            date_text = f"{role.start_date.isoformat()}–{end}"
            story.extend(_entry(date_text, role.role, role.organization))
        for service in services:
            story.extend(_entry(service.date.isoformat(), service.title, service.partner))

    # Achievements
    achievements = list(context["achievements"])
    if achievements:
        story.extend(_section("Achievements & Awards"))
        for achievement in achievements:
            story.extend(
                _entry(achievement.date.isoformat(), achievement.title, achievement.issuer)
            )

    # Skills — grouped by category into a two-column name/rating grid.
    skills = list(context["skills"])
    if skills:
        story.extend(_section("Skills"))
        by_category: dict[str, list] = {}
        for skill in skills:
            by_category.setdefault(skill.category, []).append(skill)
        for category, items in by_category.items():
            story.append(
                Paragraph(CATEGORY_LABELS.get(category, category).upper(), SUBSECTION_STYLE)
            )
            rows = []
            for i in range(0, len(items), 2):
                pair = items[i : i + 2]
                row = []
                for skill in pair:
                    rating = PROFICIENCY_LABELS.get(skill.proficiency, "")
                    row.append(Paragraph(skill.name, SKILL_NAME_STYLE))
                    row.append(Paragraph(rating, SKILL_RATING_STYLE))
                if len(pair) == 1:
                    row.extend([Paragraph("", SKILL_NAME_STYLE), Paragraph("", SKILL_RATING_STYLE)])
                rows.append(row)
            col = CONTENT_WIDTH / 2
            skills_table = Table(rows, colWidths=[col * 0.68, col * 0.32, col * 0.68, col * 0.32])
            skills_table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 2),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ]
                )
            )
            story.append(skills_table)
            story.append(Spacer(1, 6))

    doc.build(story)
    return buffer.getvalue()
