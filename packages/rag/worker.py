import asyncio, json, os
import aio_pika
from packages.rag.engine import RAGEngine

async def main():
    engine = RAGEngine()
    url    = os.getenv("RABBITMQ_URL", "amqp://aura:aura_secret@rabbitmq:5672/")
    conn   = await aio_pika.connect_robust(url)
    async with conn:
        ch    = await conn.channel()
        queue = await ch.declare_queue("rag_ingestion", durable=True)
        print("RAG worker ready...")
        async with queue.iterator() as q:
            async for msg in q:
                async with msg.process():
                    payload = json.loads(msg.body)
                    try:
                        doc_id = await engine.ingest(payload["file_path"], payload["user_id"])
                        print(f"Ingested: {doc_id}")
                    except Exception as e:
                        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
