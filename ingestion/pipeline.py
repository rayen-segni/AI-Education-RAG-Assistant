from pathlib import Path
from ingestion.loaders import LoaderFactory
from ingestion.cleaner import TextCleaner
from ingestion.chunker import TokenChunker


class DocumentIngestionPipeline:
    """Orchestrates document loading, cleaning, and token chunking."""

    def __init__(
        self,
        chunk_size: int = 500,
        overlap_percentage: float = 0.1,
        encoding_name: str = "cl100k_base",
    ):
        self.chunker = TokenChunker(
            chunk_size=chunk_size,
            overlap_percentage=overlap_percentage,
            encoding_name=encoding_name,
        )

    def process_file(self, file_path: str | Path) -> list[dict[str, str | int]]:
        """Processes a single file through Loader -> Cleaner -> Chunker.

        Returns:
            List of chunk dictionaries with metadata.
        """
        path = Path(file_path)

        # Step 1: Load Raw Text
        loader = LoaderFactory.get_loader(path)
        raw_text = loader.load()

        # Step 2: Clean Text
        clean_text = TextCleaner.clean(raw_text)

        # Step 3: Chunk Clean Text
        chunks = self.chunker.chunk_text(clean_text)

        return chunks

    def process_directory(self, dir_path: str | Path) -> list[dict[str, str | int]]:
        """Processes all supported documents in a given directory."""
        directory = Path(dir_path)
        if not directory.exists() or not directory.is_dir():
            raise FileNotFoundError(f"Directory not found: {directory}")

        all_chunks = []
        supported_extensions = set(LoaderFactory.LOADER_MAPPING.keys())

        for file_path in directory.iterdir():
            if file_path.suffix.lower() in supported_extensions:
                file_chunks = self.process_file(file_path)
                all_chunks.extend(file_chunks)

        return all_chunks