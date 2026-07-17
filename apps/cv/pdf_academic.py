"""Academic-style CV PDF, visually modeled on a classic accent-blue LaTeX CV:
sans-serif accent headings with a rule underneath, hanging title/date entry
blocks, and numbered publications grouped by type and sorted by year desc.
"""

import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ACCENT = colors.HexColor("#1F6FB2")
INK = colors.HexColor("#222222")
MUTED = colors.HexColor("#6A6A6A")

NAME_STYLE = ParagraphStyle(
    "Name", fontName="Helvetica-Bold", fontSize=22, leading=26, textColor=ACCENT
)
TAGLINE_STYLE = ParagraphStyle(
    "Tagline", fontName="Helvetica", fontSize=10, leading=13, textColor=MUTED
)
CONTACT_STYLE = ParagraphStyle(
    "Contact", fontName="Helvetica", fontSize=9, leading=12, textColor=INK
)
SECTION_STYLE = ParagraphStyle(
    "Section",
    fontName="Helvetica-Bold",
    fontSize=13,
    leading=16,
    textColor=ACCENT,
    spaceBefore=10,
    spaceAfter=4,
)
SUBSECTION_STYLE = ParagraphStyle(
    "Subsection",
    fontName="Helvetica-Bold",
    fontSize=10,
    leading=13,
    textColor=ACCENT,
    spaceBefore=6,
    spaceAfter=3,
)
ENTRY_TITLE_STYLE = ParagraphStyle(
    "EntryTitle", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=INK
)
ENTRY_DATE_STYLE = ParagraphStyle(
    "EntryDate", fontName="Helvetica", fontSize=9, leading=13, textColor=MUTED, alignment=2
)
ENTRY_SUB_STYLE = ParagraphStyle(
    "EntrySub",
    fontName="Helvetica-Oblique",
    fontSize=9.5,
    leading=12,
    textColor=MUTED,
    spaceAfter=2,
)
BODY_STYLE = ParagraphStyle("Body", fontName="Helvetica", fontSize=9.5, textColor=INK, leading=13)
PUB_STYLE = ParagraphStyle(
    "Pub", fontName="Helvetica", fontSize=9, textColor=INK, leading=12.5, spaceAfter=5
)


def _section(title: str) -> list:
    return [
        Paragraph(title, SECTION_STYLE),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#B9D3E8"), spaceAfter=6),
    ]


def _entry(date_text: str, title: str, subtitle: str, bullets: list) -> list:
    row = Table(
        [[Paragraph(title, ENTRY_TITLE_STYLE), Paragraph(date_text, ENTRY_DATE_STYLE)]],
        colWidths=[12 * cm, 5 * cm],
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
    for bullet in bullets:
        flowables.append(Paragraph(f"&bull;&nbsp;&nbsp;{bullet}", BODY_STYLE))
    flowables.append(Spacer(1, 6))
    return flowables


def build_academic_cv_pdf(context: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
        leftMargin=1.9 * cm,
        rightMargin=1.9 * cm,
    )
    story: list = []
    profile = context["profile"]

    # Header
    full_name = profile.full_name if profile else "Lecturer"
    if profile:
        title_line = f"{profile.title_prefix} {full_name} {profile.title_suffix}".strip()
    else:
        title_line = full_name
    header_cells = [Paragraph(title_line, NAME_STYLE)]
    if profile and profile.current_position:
        header_cells.append(Paragraph(profile.current_position, TAGLINE_STYLE))
    if profile and profile.photo:
        try:
            photo = Image(profile.photo.path, width=2.6 * cm, height=2.6 * cm)
            header_table = Table(
                [[header_cells, photo]], colWidths=[13.2 * cm, 2.6 * cm]
            )
            header_table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )
            story.append(header_table)
        except (OSError, ValueError):
            story.extend(header_cells)
    else:
        story.extend(header_cells)
    story.append(Spacer(1, 6))

    if profile:
        # Each ID is a live hyperlink whose visible caption is just the ID itself.
        def link(url: str, caption: str) -> str:
            return f'<a href="{url}" color="#1F6FB2">{caption}</a>'

        contact_bits = []
        if profile.email:
            contact_bits.append(f"Email: {link('mailto:' + profile.email, profile.email)}")
        if profile.phone:
            if profile.whatsapp_url:
                contact_bits.append(f"WA: {link(profile.whatsapp_url, profile.phone)}")
            else:
                contact_bits.append(f"Phone: {profile.phone}")
        if profile.linkedin_url:
            contact_bits.append(
                f"LinkedIn: {link(profile.linkedin_url, profile.linkedin_label)}"
            )
        if profile.orcid:
            contact_bits.append(f"ORCID: {link(profile.orcid_url, profile.orcid)}")
        if profile.google_scholar_id:
            contact_bits.append(
                "Google Scholar: "
                + link(profile.google_scholar_url, profile.google_scholar_id)
            )
        if profile.institution:
            contact_bits.append(profile.institution)
        if contact_bits:
            story.append(Paragraph(" &nbsp;&bull;&nbsp; ".join(contact_bits), CONTACT_STYLE))
        story.append(Spacer(1, 4))
        if profile.bio:
            story.extend(_section("Research Profile"))
            story.append(Paragraph(profile.bio, BODY_STYLE))

    # Education
    educations = list(context["educations"])
    if educations:
        story.extend(_section("Education"))
        for edu in educations:
            years = f"{edu.start_year} – {edu.end_year or 'present'}"
            subtitle = f"{edu.institution}, {edu.country}" if edu.country else edu.institution
            bullets = []
            if edu.thesis_title:
                bullets.append(f"Thesis: {edu.thesis_title}")
            if edu.gpa:
                bullets.append(f"GPA: {edu.gpa}")
            degree_title = f"{edu.get_degree_level_display()} — {edu.program}"
            story.extend(_entry(years, degree_title, subtitle, bullets))

    # Positions
    positions = list(context["positions"])
    if positions:
        story.extend(_section("Positions & Professional Experience"))
        for position in positions:
            end = position.end_date.isoformat() if position.end_date else "present"
            date_text = f"{position.start_date.isoformat()} – {end}"
            bullets = [position.description] if position.description else []
            story.extend(_entry(date_text, position.title, position.organization, bullets))

    # Publications
    if context["publications_by_type"]:
        story.extend(_section("Publications"))
        counter = 0
        for label, group in context["publications_by_type"]:
            story.append(Paragraph(f"{label} ({len(group)})", SUBSECTION_STYLE))
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
                    cite += f' <a href="https://doi.org/{pub.doi}" color="#1F6FB2">{pub.doi}</a>'
                label = f'<font color="#1F6FB2">[{counter}]</font>&nbsp;&nbsp;{cite}'
                story.append(Paragraph(label, PUB_STYLE))

    # Intellectual Property
    intellectual_properties = list(context["intellectual_properties"])
    if intellectual_properties:
        story.extend(_section("Intellectual Property"))
        for ip in intellectual_properties:
            subtitle = ip.get_ip_type_display()
            if ip.registration_number:
                subtitle += f" — No. {ip.registration_number}"
            story.extend(_entry(ip.registration_date.isoformat(), ip.title, subtitle, []))

    # Grants
    grants = list(context["grants"])
    if grants:
        story.extend(_section("Grants"))
        for grant in grants:
            end = grant.end_date.isoformat() if grant.end_date else "present"
            date_text = f"{grant.start_date.isoformat()} – {end}"
            subtitle = f"{grant.funder} — {grant.get_role_display()}"
            story.extend(_entry(date_text, grant.title, subtitle, []))

    # Supervision
    story.extend(_section("Supervision"))
    story.append(
        Paragraph(
            f"{context['student_count']} thesis students supervised in total, "
            f"{context['active_student_count']} currently active.",
            BODY_STYLE,
        )
    )

    # Service
    services = list(context["community_services"])
    roles = list(context["organizational_roles"])
    if services or roles:
        story.extend(_section("Service"))
        for service in services:
            story.extend(_entry(service.date.isoformat(), service.title, service.partner, []))
        for role in roles:
            end = role.end_date.isoformat() if role.end_date else "present"
            date_text = f"{role.start_date.isoformat()} – {end}"
            story.extend(_entry(date_text, role.role, role.organization, []))

    # Achievements
    achievements = list(context["achievements"])
    if achievements:
        story.extend(_section("Achievements & Awards"))
        for achievement in achievements:
            story.extend(
                _entry(achievement.date.isoformat(), achievement.title, achievement.issuer, [])
            )

    # Skills
    skills = list(context["skills"])
    if skills:
        story.extend(_section("Skills"))
        by_category: dict[str, list] = {}
        for skill in skills:
            by_category.setdefault(skill.get_category_display(), []).append(
                f"{skill.name} ({skill.proficiency}/5)"
            )
        for category, items in by_category.items():
            story.append(Paragraph(f"<b>{category}:</b> {', '.join(items)}", BODY_STYLE))

    doc.build(story)
    return buffer.getvalue()
