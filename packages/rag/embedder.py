import os, httpx

class EmbeddingPipeline:
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_BASE_URL","http://ollama:11434")
        self.model      = os.getenv("EMBED_MODEL","nomic-embed-text")

    async def embed_chunks(self, chunks: list) -> list:
        for chunk in chunks:
            chunk.embedding = await self.embed_query(chunk.content)
        return chunks

    async def embed_query(self, text: str) -> list:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={"model": self.model, "prompt": text[:2000]}
                )
                return r.json().get("embedding", [])
        except Exception:
            return [0.0] * 768
