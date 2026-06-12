from dataclasses import dataclass, field

@dataclass
class Chunk:
    chunk_id: str; doc_id: str; content: str
    chunk_index: int; token_count: int; metadata: dict
    embedding: list = field(default_factory=list)

class SemanticChunker:
    def __init__(self, default_chunk_size=512, default_overlap=64, min_chunk_size=100):
        self.default_chunk_size = default_chunk_size
        self.default_overlap    = default_overlap
        self.min_chunk_size     = min_chunk_size

    def chunk(self, doc) -> list:
        words = doc.content.split()
        chunks, step, i, idx = [], self.default_chunk_size - self.default_overlap, 0, 0
        while i < len(words):
            text = " ".join(words[i: i + self.default_chunk_size])
            if len(text.strip()) >= self.min_chunk_size:
                chunks.append(Chunk(
                    chunk_id=f"{doc.doc_id}_{idx}", doc_id=doc.doc_id,
                    content=text, chunk_index=idx,
                    token_count=len(text.split()), metadata={**doc.metadata,"chunk_index":idx}
                ))
                idx += 1
            i += step
        return chunks
