import hashlib, os
from dataclasses import dataclass
from enum import Enum

class DocType(str, Enum):
    PDF="pdf"; DOCX="docx"; MARKDOWN="markdown"
    EXCEL="excel"; CODE="code"; EMAIL="email"; MEETING="meeting"

@dataclass
class RawDocument:
    doc_id: str; source_path: str; doc_type: DocType
    content: str; metadata: dict; checksum: str

class DocumentProcessor:
    async def process(self, file_path: str) -> RawDocument:
        suffix   = os.path.splitext(file_path)[1].lower()
        type_map = {".pdf": DocType.PDF, ".docx": DocType.DOCX,
                    ".md": DocType.MARKDOWN, ".py": DocType.CODE,
                    ".xlsx": DocType.EXCEL, ".eml": DocType.EMAIL}
        doc_type = type_map.get(suffix, DocType.MARKDOWN)
        try:
            content = open(file_path, "r", encoding="utf-8", errors="ignore").read()
        except Exception:
            content = ""
        checksum = hashlib.sha256(content.encode()).hexdigest()
        return RawDocument(
            doc_id=checksum[:16], source_path=file_path, doc_type=doc_type,
            content=content, checksum=checksum,
            metadata={"filename": os.path.basename(file_path),
                      "doc_type": doc_type.value,
                      "size_bytes": os.path.getsize(file_path) if os.path.exists(file_path) else 0}
        )
