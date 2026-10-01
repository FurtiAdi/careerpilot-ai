import fitz

from app.models.tailored_resume_schema import (
    TailoredResumeContent,
)
from app.services.tailored_resume_export_service import (
    render_tailored_resume_pdf,
)


def make_tailored_resume_content() -> TailoredResumeContent:
    return TailoredResumeContent(
        contact={
            "full_name": "Ada Lovelace",
            "email": "ada@example.com",
            "location": "London, United Kingdom",
        },
        summary=(
            "Software engineer with Python experience."
        ),
        experience=[
            {
                "employer": "Real Company",
                "title": "Software Engineer",
                "start_date": "2022",
                "end_date": "2024",
                "bullets": [
                    "Built Python applications.",
                ],
            }
        ],
        skills=["Python", "FastAPI"],
    )


def test_render_tailored_resume_pdf_returns_readable_pdf():
    pdf_bytes = render_tailored_resume_pdf(
        make_tailored_resume_content()
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

    assert "Ada Lovelace" in extracted_text
    assert "Software Engineer" in extracted_text
    assert "Real Company" in extracted_text
    assert "Python" in extracted_text

def test_render_tailored_resume_pdf_includes_all_sections():
    content = TailoredResumeContent(
        contact={
            "full_name": "Ada & Bob",
            "links": ["https://example.com/<portfolio>"],
        },
        education=[
            {
                "institution": "University of Science",
                "degree": "BSc",
                "field_of_study": "Computer Science",
                "start_date": "2018",
                "end_date": "2021",
                "details": ["Graduated with distinction."],
            }
        ],
        projects=[
            {
                "name": "Data <Analysis>",
                "description": "Built an analytics tool.",
                "technologies": ["Python", "SQL"],
                "bullets": ["Reduced reporting time."],
            }
        ],
        optional_sections=[
            {
                "heading": "Certifications",
                "items": ["AWS Certified Developer"],
            }
        ],
    )

    pdf_bytes = render_tailored_resume_pdf(content)

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf",
    )
    extracted_text = "\n".join(
        page.get_text()
        for page in document
    )
    document.close()

    assert "Ada & Bob" in extracted_text
    assert "EDUCATION" in extracted_text
    assert "University of Science" in extracted_text
    assert "PROJECTS" in extracted_text
    assert "Data <Analysis>" in extracted_text
    assert "CERTIFICATIONS" in extracted_text
    assert "AWS Certified Developer" in extracted_text