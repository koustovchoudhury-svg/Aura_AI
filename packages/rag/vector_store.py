import os
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

COLLECTION = "aura_knowledge"
VECTOR_DIM  = 768

class VectorStore:
    def __init__(self, url: str = "http://qdrant:6333"):
        self.client = AsyncQdrantClient(url=url)

    async def init_collection(self):
        try:
            if not await self.client.collection_exists(COLLECTION):
                await self.client.create_collection(
                    collection_name=COLLECTION,
                    vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE)
                )
        except Exception as e:
            print(f"Qdrant init: {e}")

    async def upsert_chunks(self, chunks: list) -> None:
        points = [
            PointStruct(id=abs(hash(c.chunk_id)) % (2**63), vector=c.embedding,
                        payload={"chunk_id":c.chunk_id,"doc_id":c.doc_id,
                                 "content":c.content,**c.metadata})
            for c in chunks if c.embedding
        ]
        if points:
            await self.client.upsert(collection_name=COLLECTION, points=points)

    async def search(self, query_vector: list, top_k: int = 10, filters: dict = None):
        if not query_vector or all(v == 0 for v in query_vector):
            return []
        q_filter = None
        if filters:
            q_filter = Filter(must=[FieldCondition(key=k, match=MatchValue(value=v)) for k,v in filters.items()])
        try:
            return await self.client.search(collection_name=COLLECTION, query_vector=query_vector, limit=top_k, query_filter=q_filter, with_payload=True)
        except Exception:
            return []

    async def delete_by_doc_id(self, doc_id: str) -> None:
        from qdrant_client.models import FilterSelector
        try:
            await self.client.delete(collection_name=COLLECTION, points_selector=FilterSelector(
                filter=Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))])))
        except Exception:
            pass
