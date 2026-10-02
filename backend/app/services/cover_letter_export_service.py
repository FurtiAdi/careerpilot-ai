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

from app.models.cover_letter_schema import (
    CoverLetterContent,
)


def _paragraph_text(value: str) -> str:
    return escape(value)


def _build_styles() -> dict[str, ParagraphStyle]:
    base_styles = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "CoverLetterTitle",
            parent=base_styles["Title"],
            alignment=TA_CENTER,
            fontSize=16,
            leading=20,
            spaceAfter=18,
            textColor=colors.HexColor("#1F2937"),
        ),
        "body": ParagraphStyle(
            "CoverLetterBody",
            parent=base_styles["BodyText"],
            fontSize=11,
            leading=16,
            spaceAfter=12,
            textColor=colors.HexColor("#1F2937"),
        ),
    }


def render_cover_letter_pdf(
    content: CoverLetterContent,
) -> bytes:
    buffer = BytesIO()
    styles = _build_styles()

    document = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=0.9 * inch,
        leftMargin=0.9 * inch,
        topMargin=0.8 * inch,
        bottomMargin=0.8 * inch,
        title="Cover Letter",
    )

    story = [
        Paragraph("COVER LETTER", styles["title"]),
        Paragraph(
            _paragraph_text(content.opening),
            styles["body"],
        ),
    ]

    if content.evidence:
        story.append(
            ListFlowable(
                [
                    ListItem(
                        Paragraph(
                            _paragraph_text(item),
                            styles["body"],
                        )
                    )
                    for item in content.evidence
                ],
                bulletType="bullet",
                leftIndent=18,
                spaceAfter=8,
            )
        )

    story.extend(
        [
            Paragraph(
                _paragraph_text(content.motivation),
                styles["body"],
            ),
            Spacer(1, 6),
            Paragraph(
                _paragraph_text(content.closing),
                styles["body"],
            ),
        ]
    )

    document.build(story)

    return buffer.getvalue()