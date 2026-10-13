import re
from html.parser import HTMLParser
from html import unescape

from .promall_category_faq import split_category_faq_html


class HTMLToText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("p", "div", "br", "li"):
            self.parts.append("\n")
        if tag == "li":
            self.parts.append("- ")

    def handle_data(self, data):
        self.parts.append(data)

    def get_text(self):
        text = unescape("".join(self.parts))
        lines = [line.strip() for line in text.splitlines()]
        return "\n".join(line for line in lines if line)


def parse_category_faqs(raw_html):
    result = []

    for section in split_category_faq_html(raw_html):
        # Find the first bold element, which normally contains the question.
        match = re.search(
            r"<strong\b[^>]*>(.*?)</strong>",
            section,
            flags=re.IGNORECASE | re.DOTALL,
        )

        if not match:
            # Preserve sections we cannot confidently parse.
            result.append({
                "question": "",
                "answer": HTMLToText().get_text() if not section else html_to_text(section),
            })
            continue

        question = html_to_text(match.group(1))

        # Remove the question itself from the answer HTML.
        answer_html = section[:match.start()] + section[match.end():]

        result.append({
            "question": question,
            "answer": html_to_text(answer_html),
        })

    return result


def html_to_text(value):
    parser = HTMLToText()
    parser.feed(str(value or ""))
    return parser.get_text()
