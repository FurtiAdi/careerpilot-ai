from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from app.models.tailored_resume_schema import (
    TailoredResumeContent,
)


def _paragraph_text(value: str | None) -> str:
    return escape(value or "")


def _date_range(
    start_date: str | None,
    end_date: str | None,
) -> str:
    return " - ".join(
        value
        for value in (start_date, end_date)
        if value
    )


def _build_styles() -> dict[str, ParagraphStyle]:
    base_styles = getSampleStyleSheet()

    return {
        "name": ParagraphStyle(
            "ResumeName",
            parent=base_styles["Title"],
            alignment=TA_CENTER,
            fontSize=18,
            leading=22,
            spaceAfter=6,
        ),
        "contact": ParagraphStyle(
            "ResumeContact",
            parent=base_styles["Normal"],
            alignment=TA_CENTER,
            textColor=colors.HexColor("#4B5563"),
            fontSize=9,
            leading=12,
            spaceAfter=14,
        ),
        "section": ParagraphStyle(
            "ResumeSection",
            parent=base_styles["Heading2"],
            fontSize=11,
            leading=14,
            spaceBefore=12,
            spaceAfter=5,
            textColor=colors.HexColor("#1F2937"),
        ),
        "body": ParagraphStyle(
            "ResumeBody",
            parent=base_styles["BodyText"],
            fontSize=10,
            leading=14,
            spaceAfter=5,
        ),
        "item_title": ParagraphStyle(
            "ResumeItemTitle",
            parent=base_styles["BodyText"],
            fontSize=10,
            leading=13,
            spaceAfter=1,
        ),
        "muted": ParagraphStyle(
            "ResumeMuted",
            parent=base_styles["BodyText"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#4B5563"),
            spaceAfter=4,
        ),
    }


def _add_bullets(
    story: list,
    bullets: list[str],
    styles: dict[str, ParagraphStyle],
) -> None:
    if not bullets:
        return

    story.append(
        ListFlowable(
            [
                ListItem(
                    Paragraph(
                        _paragraph_text(bullet),
                        styles["body"],
                    ),
                )
                for bullet in bullets
            ],
            bulletType="bullet",
            leftIndent=18,
            spaceAfter=4,
        )
    )


def render_tailored_resume_pdf(
    content: TailoredResumeContent,
) -> bytes:
    buffer = BytesIO()
    styles = _build_styles()

    document = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title=content.contact.full_name or "Tailored Resume",
    )

    story = []

    story.append(
        Paragraph(
            _paragraph_text(
                content.contact.full_name
                or "Tailored Resume"
            ),
            styles["name"],
        )
    )

    contact_details = [
        value
        for value in (
            content.contact.email,
            content.contact.phone,
            content.contact.location,
        )
        if value
    ] + content.contact.links

    if contact_details:
        story.append(
            Paragraph(
                " | ".join(
                    _paragraph_text(value)
                    for value in contact_details
                ),
                styles["contact"],
            )
        )
    else:
        story.append(Spacer(1, 8))

    if content.summary:
        story.append(
            Paragraph(
                "PROFESSIONAL SUMMARY",
                styles["section"],
            )
        )
        story.append(
            Paragraph(
                _paragraph_text(content.summary),
                styles["body"],
            )
        )

    if content.skills:
        story.append(
            Paragraph("SKILLS", styles["section"])
        )
        story.append(
            Paragraph(
                _paragraph_text(
                    " | ".join(content.skills)
                ),
                styles["body"],
            )
        )

    if content.experience:
        story.append(
            Paragraph("EXPERIENCE", styles["section"])
        )

        for item in content.experience:
            story.append(
                Paragraph(
                    (
                        f"<b>{_paragraph_text(item.title)}</b>"
                        f" - {_paragraph_text(item.employer)}"
                    ),
                    styles["item_title"],
                )
            )

            details = [
                value
                for value in (
                    item.location,
                    _date_range(
                        item.start_date,
                        item.end_date,
                    ),
                )
                if value
            ]

            if details:
                story.append(
                    Paragraph(
                        _paragraph_text(
                            " | ".join(details)
                        ),
                        styles["muted"],
                    )
                )

            _add_bullets(
                story,
                item.bullets,
                styles,
            )

    if content.education:
        story.append(
            Paragraph("EDUCATION", styles["section"])
        )

        for item in content.education:
            story.append(
                Paragraph(
                    (
                        f"<b>{_paragraph_text(item.institution)}</b>"
                    ),
                    styles["item_title"],
                )
            )

            education_details = [
                value
                for value in (
                    item.degree,
                    item.field_of_study,
                    _date_range(
                        item.start_date,
                        item.end_date,
                    ),
                )
                if value
            ]

            if education_details:
                story.append(
                    Paragraph(
                        _paragraph_text(
                            " | ".join(education_details)
                        ),
                        styles["muted"],
                    )
                )

            _add_bullets(
                story,
                item.details,
                styles,
            )

    if content.projects:
        story.append(
            Paragraph("PROJECTS", styles["section"])
        )

        for project in content.projects:
            story.append(
                Paragraph(
                    (
                        f"<b>{_paragraph_text(project.name)}</b>"
                    ),
                    styles["item_title"],
                )
            )

            if project.description:
                story.append(
                    Paragraph(
                        _paragraph_text(
                            project.description
                        ),
                        styles["body"],
                    )
                )

            if project.technologies:
                story.append(
                    Paragraph(
                        _paragraph_text(
                            " | ".join(
                                project.technologies
                            )
                        ),
                        styles["muted"],
                    )
                )

            _add_bullets(
                story,
                project.bullets,
                styles,
            )

    for section in content.optional_sections:
        story.append(
            Paragraph(
                _paragraph_text(
                    section.heading.upper()
                ),
                styles["section"],
            )
        )
        _add_bullets(
            story,
            section.items,
            styles,
        )

    document.build(story)

    return buffer.getvalue()