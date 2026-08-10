import tiktoken


class TokenChunker:
    """Splits clean text into token-based chunks with configurable size and overlap."""

    def __init__(
        self,
        chunk_size: int = 500,
        overlap_percentage: float = 0.1,
        encoding_name: str = "cl100k_base",
    ):
        """Args:

        chunk_size: Target token count per chunk (e.g., 200, 500, 1000).
        overlap_percentage: Percentage of overlap between consecutive chunks
        (0.0 to 0.5).
        encoding_name: Tiktoken encoding model (cl100k_base is standard for
        gpt-4/embeddings).
        """
        if not 0.0 <= overlap_percentage < 1.0:
            raise ValueError("overlap_percentage must be between 0.0 and 1.0")

        self.chunk_size = chunk_size
        self.overlap_percentage = overlap_percentage
        self.overlap_tokens = int(chunk_size * overlap_percentage)
        self.step_size = self.chunk_size - self.overlap_tokens

        if self.step_size <= 0:
            raise ValueError("Overlap is too large for the specified chunk size.")

        self.tokenizer = tiktoken.get_encoding(encoding_name)

    def chunk_text(self, text: str) -> list[dict[str, str | int]]:
        if not text.strip():
            return []

        tokens = self.tokenizer.encode(text)
        tokens_count = len(tokens)

        chunks = []
        chunk_id = 0
        start_idx = 0
        step_size = self.chunk_size - self.overlap_tokens

        while start_idx < tokens_count:
            end_idx = min(start_idx + self.chunk_size, tokens_count)

            # Slice token IDs
            chunk_tokens = tokens[start_idx:end_idx]

            # Decode tokens back to plain text
            chunk_text = self.tokenizer.decode(chunk_tokens)

            chunks.append(
                {
                    "chunk_index": chunk_id,
                    "content": chunk_text,
                    "token_count": len(chunk_tokens),
                }
            )

            chunk_id += 1
            start_idx += step_size

            if end_idx == tokens_count:
                break

        return chunks
