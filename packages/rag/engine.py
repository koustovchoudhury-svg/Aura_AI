import hashlib, os
from .processor    import DocumentProcessor
from .chunker      import SemanticChunker
from .embedder     import EmbeddingPipeline
from .vector_store import VectorStore
from .retriever    import HybridRetriever

class RAGEngine:
    def __init__(self):
        self.processor = DocumentProcessor()
        self.chunker   = SemanticChunker()
        self.embedder  = EmbeddingPipeline()
        self.store     = VectorStore(url=os.getenv("QDRANT_URL","http://qdrant:6333"))
        self.retriever = HybridRetriever(self.store, self.embedder)

    async def ingest(self, file_path: str, user_id: str) -> str:
        doc    = await self.processor.process(file_path)
        chunks = self.chunker.chunk(doc)
        chunks = await self.embedder.embed_chunks(chunks)
        await self.store.upsert_chunks(chunks)
        try:
            from packages.db.connection import AsyncSessionFactory
            from packages.db.models import Document
            from sqlalchemy import select
            import uuid
            async with AsyncSessionFactory() as session:
                existing = await session.execute(
                    select(Document).where(Document.user_id == user_id)
                    .where(Document.checksum == doc.checksum)
                )
                if not existing.scalar_one_or_none():
                    db_doc = Document(
                        id=uuid.UUID(doc.doc_id.ljust(32,'0')[:32]) if len(doc.doc_id)==32 else uuid.uuid4(),
                        user_id=user_id, filename=os.path.basename(file_path),
                        source_path=file_path, doc_type=doc.doc_type.value,
                        checksum=doc.checksum, chunk_count=len(chunks),
                        size_bytes=doc.metadata.get("size_bytes",0)
                    )
                    session.add(db_doc)
                    await session.commit()
        except Exception as e:
            print(f"DB save warning: {e}")
        return doc.doc_id

    async def retrieve(self, query: str, user_id: str, top_k: int = 5) -> list:
        chunks = await self.retriever.retrieve(query, filters={"user_id": user_id})
        return [f"[{c.get('filename','unknown')}]\n{c['content']}" for c in chunks[:top_k]]
