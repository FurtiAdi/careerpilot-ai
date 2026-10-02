import fitz

from app.models.cover_letter_schema import (
    CoverLetterContent,
)
from app.services.cover_letter_export_service import (
    render_cover_letter_pdf,
)


def make_cover_letter_content() -> CoverLetterContent:
    return CoverLetterContent(
        opening="I am applying for the Software Engineer role.",
        evidence=[
            "Built Python applications.",
            "Collaborated with product stakeholders.",
        ],
        motivation=(
            "The role aligns with my backend experience."
        ),
        closing="Thank you for your consideration.",
    )


def test_render_cover_letter_pdf_returns_readable_pdf():
    pdf_bytes = render_cover_letter_pdf(
        make_cover_letter_content()
    )

    assert pdf_bytes.startswith(b"%PDF-")

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf",
    )
    extracted_text = "\n".join(
        page.get_text()
        for page in document
    )
    document.close()

    assert "COVER LETTER" in extracted_text
    assert "Software Engineer role" in extracted_text
    assert "Built Python applications." in extracted_text
    assert "Thank you for your consideration." in extracted_text


def test_render_cover_letter_pdf_escapes_special_characters():
    content = CoverLetterContent(
        opening="I use Python & SQL.",
        evidence=["Built <reliable> services."],
        motivation="I value clear communication.",
        closing="Thank you.",
    )

    pdf_bytes = render_cover_letter_pdf(content)

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf",
    )
    extracted_text = "\n".join(
        page.get_text()
        for page in document
    )
    document.close()

    assert "Python & SQL" in extracted_text
    assert "Built <reliable> services." in extracted_text