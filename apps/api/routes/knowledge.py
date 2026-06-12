import os
from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
from pydantic import BaseModel
from packages.rag.engine import RAGEngine
from packages.db.connection import get_session
from .auth import get_current_user
import uuid

router     = APIRouter()
rag_engine = RAGEngine()

class QueryRequest(BaseModel):
    query:  str
    top_k:  int = 5

@router.post("/ingest")
async def ingest_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    upload_dir = "/tmp/aura_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path  = f"{upload_dir}/{uuid.uuid4()}_{file.filename}"
    with open(file_path,"wb") as f:
        f.write(await file.read())
    background_tasks.add_task(rag_engine.ingest, file_path, str(user.id))
    return {"status":"queued","filename":file.filename}

@router.post("/query")
async def query_knowledge(req: QueryRequest, user=Depends(get_current_user)):
    chunks = await rag_engine.retrieve(req.query, str(user.id), req.top_k)
    return {"results": chunks}

@router.get("/documents")
async def list_documents(user=Depends(get_current_user), session=Depends(get_session)):
    from sqlalchemy import select
    from packages.db.models import Document
    result = await session.execute(
        select(Document).where(Document.user_id == str(user.id))
        .order_by(Document.ingested_at.desc())
    )
    docs = result.scalars().all()
    return {"documents": [
        {"id":str(d.id),"filename":d.filename,"doc_type":d.doc_type,
         "chunk_count":d.chunk_count,"ingested_at":str(d.ingested_at)}
        for d in docs
    ]}
