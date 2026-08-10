from abc import ABC, abstractmethod
from pathlib import Path
from bs4 import BeautifulSoup
import markdown
import pypdf


class BaseLoader(ABC):
    """Abstract Base Class defining the standard interface for all document loaders."""

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

    @abstractmethod
    def load(self) -> str:
        """Extracts and returns raw text content from the file."""

        pass


class TextLoader(BaseLoader):
    """Loader for standard plain text (.txt) files."""

    def load(self) -> str:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return f.read()


class MarkdownLoader(BaseLoader):
    """Loader for Markdown (.md) files.

    Converts Markdown syntax to HTML and strips formatting tags to isolate plain text.
    """

    def load(self) -> str:
        with open(self.file_path, "r", encoding="utf-8") as f:
            md_content = f.read()

            # Convert Markdown syntax to HTML AST
            html_content = markdown.markdown(md_content)

            # Strip HTML tags using BeautifulSoup to get raw text
            soup = BeautifulSoup(html_content, "html.parser")
            return soup.get_text(separator="\n")


class PDFLoader(BaseLoader):
    """Loader for PDF (.pdf) documents using pypdf."""

    def load(self) -> str:
        reader = pypdf.PdfReader(self.file_path)
        extracted_pages = []

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                extracted_pages.append(page_text)

        return "\n\n".join(extracted_pages)


class LoaderFactory:
    """Factory to instantiate the appropriate loader based on file extension."""

    LOADER_MAPPING = {
        ".txt": TextLoader,
        ".md": MarkdownLoader,
        ".pdf": PDFLoader,
    }

    @classmethod
    def get_loader(cls, file_path: str | Path) -> BaseLoader:
        path = Path(file_path)

        ext = path.suffix.lower()

        if ext not in cls.LOADER_MAPPING:
            raise ValueError(
                f"Unsupported file extension '{ext}'. "
                f"Supported types: {list(cls.LOADER_MAPPING.keys())}"
            )

        loader_cls = cls.LOADER_MAPPING[ext] # return class from the dict
        return loader_cls(path)


if __name__ == "__main__":
    loader = LoaderFactory.get_loader("../documents/sample.md")

    print(loader.load())



