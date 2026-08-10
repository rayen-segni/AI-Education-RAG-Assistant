import re
import unicodedata


class TextCleaner:
    """Utility class to sanitize and normalize raw extracted text before chunking."""

    @staticmethod
    def normalize_unicode(text: str) -> str:
        """Converts Unicode characters to standard NFKC compatibility form.
        
        Fixes curly quotes, non-standard hyphens, ligatures, and accented variants.
        """
        # NFKC converts characters like 'smart quotes' and ligatures to standard ascii equivalents where possible
        return unicodedata.normalize("NFKC", text)


    @staticmethod
    def remove_control_characters(text: str) -> str:
        """Removes non-printable control characters while keeping standard newlines and tabs."""
        return "".join(
            ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in ("\n", "\r", "\t")
        )

    @staticmethod
    def clean_html_and_artifacts(text: str) -> str:
        """Strips leftover HTML tags and repetitive page dividers."""
        # Strip basic HTML tags if text was extracted from web/PDF webviews
        text = re.sub(r"<[^>]+>", "", text)
        
        # Replace repetitive dividers like '---', '***', '===' with a clean break
        text = re.sub(r"[-*=]{3,}", "\n", text)
        return text

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Standardizes non-breaking spaces and reduces multiple blank lines down to a double newline."""
        # Replace non-breaking spaces (\xa0) with standard spaces
        text = text.replace("\xa0", " ")

        # Replace 3 or more consecutive newlines with exactly 2 newlines (paragraph boundary)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Replace multiple horizontal spaces/tabs with a single space per line
        text = re.sub(r"[ \t]+", " ", text)

        # Strip trailing/leading white space on each line
        lines = [line.strip() for line in text.splitlines()]
        return "\n".join(lines).strip()

    @classmethod
    def clean(cls, raw_text: str) -> str:
        """Applies the full cleaning pipeline sequentially."""
        if not raw_text:
            return ""

        text = cls.normalize_unicode(raw_text)
        text = cls.remove_control_characters(text)
        text = cls.clean_html_and_artifacts(text)
        text = cls.normalize_whitespace(text)
        return text