import re
from html import escape, unescape

SEPARATOR = re.compile(
    r"<p\b[^>]*>\s*(?:<strong\b[^>]*>\s*)?\*{3}\s*(?:</strong>\s*)?</p>",
    re.IGNORECASE,
)


def split_category_faq_html(raw_html):
    """Split FAQ HTML into sections without stripping answer formatting."""
    if not raw_html:
        return []

    return [
        section.strip()
        for section in SEPARATOR.split(str(raw_html))
        if section.strip()
    ]


def extract_category_faq_sections(raw_html):
    """Return editable FAQ sections, preserving their original HTML."""
    sections = split_category_faq_html(raw_html)

    return [
        {
            "html": section,
        }
        for section in sections
    ]


def serialize_category_faq_sections(sections):
    """Combine edited sections into the existing HTML FAQ format."""
    cleaned = [
        section.strip()
        for section in sections
        if section and section.strip()
    ]

    return "\n<p><strong>***</strong></p>\n".join(cleaned)
