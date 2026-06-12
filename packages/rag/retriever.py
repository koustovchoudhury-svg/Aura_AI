class HybridRetriever:
    def __init__(self, vector_store, embedder, top_k_final=5):
        self.vector_store = vector_store
        self.embedder     = embedder
        self.top_k_final  = top_k_final

    async def retrieve(self, query: str, filters: dict = None) -> list:
        vector = await self.embedder.embed_query(query)
        hits   = await self.vector_store.search(vector, top_k=20, filters=filters)
        return [hit.payload for hit in hits[:self.top_k_final]]
