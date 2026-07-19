"""Europass-style CV PDF: adapted from the "Europass CV" design
(claude.ai/design project 2716d85c-6afc-4cf0-a0de-1f2663cad79b, "Europass
CV - Agus Setiawan.dc.html") — a classic Europass look: Georgia-serif name,
Arial body text, uppercase blue section headers with a 2px rule, a tabular
Personal Information block, and per-type publication lists.

Two substitutions from the source design, following the same reasoning as
pdf_elegant.py: ReportLab's built-in Times/Helvetica stand in for
Georgia/Arial (no network access at PDF-generation time to fetch web
fonts), and a few section titles/groupings were generalized from the
design's one-off example (a PhD-application CV) to plain data-driven
equivalents — e.g. "Research Interests & PhD Proposal Summary" becomes
"Research Profile" (profile.bio), matching the naming already used by the
academic and elegant styles.
"""

import datetime
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .pdf_elegant import PROFICIENCY_LABELS, CircularImage

# A4 page, 0.6in margins each side (matching the source design's doc-page
# size="a4" margin="0.6in"): usable content width in points.
CONTENT_WIDTH = A4[0] - 2 * 0.6 * inch

BLUE = colors.HexColor("#003399")
INK = colors.HexColor("#0a0a0a")
TEXT = colors.HexColor("#262626")
MUTED = colors.HexColor("#555555")
FAINT = colors.HexColor("#999999")
TABLE_HEAD_BG = colors.HexColor("#eef1fb")
TABLE_BORDER = colors.HexColor("#e1e6f2")

NAME_STYLE = ParagraphStyle("Name", fontName="Times-Bold", fontSize=22, leading=26, textColor=INK)
TAGLINE_STYLE = ParagraphStyle(
    "Tagline", fontName="Times-Italic", fontSize=11, leading=15, textColor=BLUE, spaceAfter=4
)
CONTACT_STYLE = ParagraphStyle(
    "Contact", fontName="Helvetica", fontSize=9, leading=15, textColor=TEXT
)
SECTION_STYLE = ParagraphStyle(
    "Section",
    fontName="Helvetica-Bold",
    fontSize=10.5,
    leading=13,
    textColor=BLUE,
    spaceBefore=14,
    spaceAfter=2,
)
LABEL_STYLE = ParagraphStyle("Label", fontName="Helvetica-Bold", fontSize=9.5, textColor=BLUE)
VALUE_STYLE = ParagraphStyle("Value", fontName="Helvetica", fontSize=9.5, textColor=colors.black)
BODY_STYLE = ParagraphStyle("Body", fontName="Helvetica", fontSize=9.5, leading=15, textColor=TEXT)
ENTRY_TITLE_STYLE = ParagraphStyle(
    "EntryTitle", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=INK
)
ENTRY_DATE_STYLE = ParagraphStyle(
    "EntryDate", fontName="Helvetica", fontSize=9, leading=13, textColor=MUTED, alignment=2
)
ENTRY_SUB_STYLE = ParagraphStyle(
    "EntrySub",
    fontName="Times-Italic",
    fontSize=9.5,
    leading=13,
    textColor=colors.HexColor("#444444"),
)
ENTRY_META_STYLE = ParagraphStyle(
    "EntryMeta", fontName="Helvetica", fontSize=9, leading=12.5, textColor=MUTED, spaceBefore=2
)
GROUP_LABEL_STYLE = ParagraphStyle(
    "GroupLabel",
    fontName="Helvetica-Bold",
    fontSize=9.5,
    textColor=INK,
    spaceBefore=6,
    spaceAfter=4,
)
PUB_STYLE = ParagraphStyle(
    "Pub",
    fontName="Helvetica",
    fontSize=8.5,
    leading=13,
    textColor=colors.HexColor("#333333"),
    spaceAfter=6,
)
SKILL_ITEM_STYLE = ParagraphStyle(
    "SkillItem", fontName="Helvetica", fontSize=9, leading=13, textColor=TEXT, leftIndent=10
)
IP_NOTE_STYLE = ParagraphStyle(
    "IPNote", fontName="Times-Italic", fontSize=8.5, leading=12, textColor=FAINT, spaceAfter=6
)
IP_ITEM_STYLE = ParagraphStyle(
    "IPItem",
    fontName="Helvetica",
    fontSize=9,
    leading=14,
    textColor=colors.HexColor("#333333"),
    leftIndent=10,
)
TABLE_HEAD_STYLE = ParagraphStyle(
    "TableHead", fontName="Helvetica-Bold", fontSize=8, textColor=BLUE
)
FOOTER_STYLE = ParagraphStyle(
    "Footer", fontName="Times-Italic", fontSize=8, textColor=FAINT, alignment=1, spaceBefore=16
)

LINK_COLOR = "#003399"


def _link(url: str, caption: str) -> str:
    return f'<a href="{url}" color="{LINK_COLOR}">{caption}</a>'


def _section(title: str) -> list:
    return [
        Paragraph(title.upper(), SECTION_STYLE),
        HRFlowable(width="100%", thickness=1.4, color=BLUE, spaceAfter=8),
    ]


def _entry_row(date_text: str, title: str, subtitle: str, meta: str = "") -> list:
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
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    flowables = [row]
    if subtitle:
        flowables.append(Paragraph(subtitle, ENTRY_SUB_STYLE))
    if meta:
        flowables.append(Paragraph(meta, ENTRY_META_STYLE))
    flowables.append(Spacer(1, 10))
    return flowables


def build_europass_cv_pdf(context: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
    )
    story: list = []
    profile = context["profile"]

    # Header: name + tagline + contact line, photo on the right.
    full_name = profile.full_name if profile else "Lecturer"
    left_cell = [Paragraph(full_name, NAME_STYLE)]
    if profile and profile.current_position:
        left_cell.append(Paragraph(profile.current_position, TAGLINE_STYLE))

    contact_bits = []
    if profile and profile.email:
        contact_bits.append(_link("mailto:" + profile.email, profile.email))
    if profile and profile.phone:
        contact_bits.append(
            _link(profile.whatsapp_url, profile.phone) if profile.whatsapp_url else profile.phone
        )
    if profile and profile.linkedin_url:
        contact_bits.append(_link(profile.linkedin_url, profile.linkedin_label))
    if profile and profile.orcid:
        contact_bits.append(_link(profile.orcid_url, profile.orcid))
    if profile and profile.google_scholar_id:
        contact_bits.append(_link(profile.google_scholar_url, "Google Scholar"))
    if contact_bits:
        left_cell.append(Paragraph(" &middot; ".join(contact_bits), CONTACT_STYLE))

    header_row = [left_cell]
    col_widths = [CONTENT_WIDTH]
    if profile and profile.photo:
        try:
            photo_diameter = 1.15 * inch
            photo = CircularImage(profile.photo.path, photo_diameter)
            header_row = [left_cell, photo]
            col_widths = [CONTENT_WIDTH - photo_diameter - 0.2 * inch, photo_diameter + 0.2 * inch]
        except (OSError, ValueError):
            pass
    header_table = Table([header_row], colWidths=col_widths)
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (-1, 0), (-1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(header_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=2.2, color=BLUE, spaceAfter=14))

    # Personal Information — whichever identity/institutional fields exist;
    # the design's Date of birth/Nationality aren't fields this app collects.
    if profile:
        info_rows = []
        if profile.nidn:
            info_rows.append([Paragraph("NIDN", LABEL_STYLE), Paragraph(profile.nidn, VALUE_STYLE)])
        if profile.nip:
            info_rows.append([Paragraph("NIP", LABEL_STYLE), Paragraph(profile.nip, VALUE_STYLE)])
        if profile.institution:
            info_rows.append(
                [Paragraph("Institution", LABEL_STYLE), Paragraph(profile.institution, VALUE_STYLE)]
            )
        if profile.faculty:
            info_rows.append(
                [Paragraph("Faculty", LABEL_STYLE), Paragraph(profile.faculty, VALUE_STYLE)]
            )
        if profile.department:
            info_rows.append(
                [Paragraph("Department", LABEL_STYLE), Paragraph(profile.department, VALUE_STYLE)]
            )
        if info_rows:
            story.extend(_section("Personal Information"))
            info_table = Table(info_rows, colWidths=[CONTENT_WIDTH * 0.25, CONTENT_WIDTH * 0.75])
            info_table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ]
                )
            )
            story.append(info_table)

    if profile and profile.bio:
        story.extend(_section("Research Profile"))
        story.append(Paragraph(profile.bio, BODY_STYLE))

    # Education and Training
    educations = list(context["educations"])
    if educations:
        story.extend(_section("Education and Training"))
        for edu in educations:
            years = f"{edu.start_year} – {edu.end_year or 'present'}"
            subtitle = f"{edu.institution}, {edu.country}" if edu.country else edu.institution
            meta_bits = []
            if edu.thesis_title:
                meta_bits.append(f"Thesis: “{edu.thesis_title}”")
            if edu.gpa:
                meta_bits.append(f"GPA: {edu.gpa} / 4.00")
            degree_title = f"{edu.get_degree_level_display()} — {edu.program}"
            story.extend(_entry_row(years, degree_title, subtitle, " · ".join(meta_bits)))

    # Positions, split into Research vs Professional Experience — our
    # Position.category field describes institutional type (structural/
    # functional/organizational/professional), not research-vs-teaching, so
    # this splits on whether "research" appears in the title instead, which
    # matches how the source design's own example grouped its entries.
    positions = list(context["positions"])
    research_positions = [p for p in positions if "research" in p.title.lower()]
    professional_positions = [p for p in positions if p not in research_positions]

    def position_entry(position):
        end = position.end_date.isoformat() if position.end_date else "Present"
        date_text = f"{position.start_date.isoformat()} – {end}"
        return _entry_row(date_text, position.title, position.organization, position.description)

    if research_positions:
        story.extend(_section("Research Experience"))
        for position in research_positions:
            story.extend(position_entry(position))

    if professional_positions:
        story.extend(_section("Professional Experience"))
        for position in professional_positions:
            story.extend(position_entry(position))

    # Grants, Scholarships & Awards — the design combines Grants and
    # Achievements into one section.
    grants = list(context["grants"])
    achievements = list(context["achievements"])
    if grants or achievements:
        story.extend(_section("Grants, Scholarships & Awards"))
        for grant in grants:
            end = grant.end_date.isoformat() if grant.end_date else "Present"
            date_text = f"{grant.start_date.isoformat()} – {end}"
            story.extend(
                _entry_row(date_text, grant.title, f"{grant.funder} — {grant.get_role_display()}")
            )
        for achievement in achievements:
            story.extend(
                _entry_row(achievement.date.isoformat(), achievement.title, achievement.issuer)
            )

    # Intellectual Property Rights
    intellectual_properties = list(context["intellectual_properties"])
    if intellectual_properties:
        story.extend(_section("Intellectual Property Rights"))
        story.append(
            Paragraph(
                "Registered with the Directorate General of Intellectual Property (DJKI), "
                "Ministry of Law and Human Rights, Republic of Indonesia.",
                IP_NOTE_STYLE,
            )
        )
        for i, ip in enumerate(intellectual_properties, start=1):
            meta = f"{ip.get_ip_type_display()}"
            if ip.registration_number:
                meta += f" — Reg. No. {ip.registration_number}"
            meta += f" · DJKI, Indonesia · {ip.registration_date.year}"
            story.append(Paragraph(f"{i}. <b>{ip.title}</b> — {meta}", IP_ITEM_STYLE))
        story.append(Spacer(1, 6))

    # Digital Skills & Competencies — Research Methods (category=research)
    # and Software & Tools (category=technical) side by side, matching the
    # design's two-column layout.
    skills = list(context["skills"])
    research_skills = [s for s in skills if s.category == "research"]
    technical_skills = [s for s in skills if s.category == "technical"]
    if research_skills or technical_skills:
        story.extend(_section("Digital Skills & Competencies"))
        col_a = [Paragraph("Research Methods", GROUP_LABEL_STYLE)]
        col_a += [Paragraph(f"• {s.name}", SKILL_ITEM_STYLE) for s in research_skills]
        col_b = [Paragraph("Software & Tools", GROUP_LABEL_STYLE)]
        col_b += [Paragraph(f"• {s.name}", SKILL_ITEM_STYLE) for s in technical_skills]
        skills_grid = Table([[col_a, col_b]], colWidths=[CONTENT_WIDTH * 0.5, CONTENT_WIDTH * 0.5])
        skills_grid.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
        story.append(skills_grid)
        story.append(Spacer(1, 6))

    # Language Skills
    language_skills = [s for s in skills if s.category == "language"]
    if language_skills:
        story.extend(_section("Language Skills"))
        rows = [
            [
                Paragraph("Language", TABLE_HEAD_STYLE),
                Paragraph("Self-assessed level", TABLE_HEAD_STYLE),
            ]
        ]
        for skill in language_skills:
            level = PROFICIENCY_LABELS.get(skill.proficiency, "")
            rows.append([Paragraph(skill.name, VALUE_STYLE), Paragraph(level, VALUE_STYLE)])
        lang_table = Table(rows, colWidths=[CONTENT_WIDTH * 0.5, CONTENT_WIDTH * 0.5])
        lang_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEAD_BG),
                    ("GRID", (0, 0), (-1, -1), 0.5, TABLE_BORDER),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(lang_table)
        story.append(Spacer(1, 6))

    # Publications — grouped by type, numbering restarts at 1 for each
    # group (unlike the Elegant style's continuous numbering), matching
    # the source design.
    if context["publications_by_type"]:
        story.extend(_section("Publications"))
        for label, group in context["publications_by_type"]:
            story.append(Paragraph(f"{label}s ({len(group)})", GROUP_LABEL_STYLE))
            for i, pub in enumerate(group, start=1):
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
                    cite += f" {_link(doi_url, f'doi.org/{pub.doi}')}"
                story.append(Paragraph(f"{i}. {cite}", PUB_STYLE))

    footer_name = profile.full_name if profile else "Lecturer"
    updated = datetime.date.today().strftime("%B %Y")
    story.append(
        Paragraph(f"Curriculum Vitae — {footer_name} — Last updated: {updated}", FOOTER_STYLE)
    )

    doc.build(story)
    return buffer.getvalue()
