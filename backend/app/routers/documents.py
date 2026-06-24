import os
import re
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.deps import get_db, verify_token
from app.models import Document, KnowledgeItem
from app.schemas import DocumentDetail, DocumentOut, MessageResponse
from app.services.document_chunker import build_chunk_content, chunk_text
from app.services.document_parser import DocumentParseError, parse_document

router = APIRouter(prefix="/api/documents", tags=["documents"], dependencies=[Depends(verify_token)])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".txt", ".md"}
ALLOWED_MIME_TYPES = {
    ".pdf": {"application/pdf", "application/octet-stream"},
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/octet-stream",
    },
    ".xlsx": {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/octet-stream",
    },
    ".txt": {"text/plain", "application/octet-stream"},
    ".md": {"text/markdown", "text/plain", "application/octet-stream"},
}

UNSUPPORTED_TYPE_MESSAGE = "文件类型不支持，请上传 PDF、DOCX、XLSX、TXT 或 Markdown 文件。"
FILE_TOO_LARGE_MESSAGE = "文件超过 10 MB，请压缩文件或拆分后重新上传。"
EMPTY_CONTENT_MESSAGE = "文件内容为空，无法建立知识库。"
PARSE_FAILED_MESSAGE = "文件解析失败，请确认文件未损坏或更换格式后重试。"


def get_upload_dir() -> Path:
    upload_dir = Path(os.getenv("UPLOAD_DIR", "storage/uploads"))
    if not upload_dir.is_absolute():
        base_dir = Path.cwd().parent if Path.cwd().name == "backend" else Path.cwd()
        upload_dir = base_dir / upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def get_max_upload_size_bytes() -> int:
    try:
        size_mb = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))
    except ValueError:
        size_mb = 10
    return max(size_mb, 1) * 1024 * 1024


def normalize_original_filename(filename: str | None) -> str:
    original = Path(filename or "").name.strip()
    if not original:
        raise HTTPException(status_code=400, detail=UNSUPPORTED_TYPE_MESSAGE)
    if len(original) > 120:
        raise HTTPException(status_code=400, detail="文件名最大 120 个字符，请重命名后重新上传。")
    return original


def validate_file_type(original_filename: str, mime_type: str) -> str:
    extension = Path(original_filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=UNSUPPORTED_TYPE_MESSAGE)

    normalized_mime = (mime_type or "application/octet-stream").lower()
    if normalized_mime not in ALLOWED_MIME_TYPES[extension]:
        raise HTTPException(status_code=400, detail=UNSUPPORTED_TYPE_MESSAGE)
    return extension


def make_safe_filename(original_filename: str) -> str:
    path_name = Path(original_filename).name
    stem = Path(path_name).stem[:90].strip() or "document"
    suffix = Path(path_name).suffix.lower()
    safe_stem = re.sub(r"[^\w\u4e00-\u9fff.-]+", "_", stem).strip("._")
    if not safe_stem:
        safe_stem = "document"
    return f"{safe_stem}{suffix}"


def save_failed_status(db: Session, document: Document, message: str) -> None:
    try:
        document.parse_status = "failed"
        document.parse_error = message
        document.chunk_count = 0
        db.commit()
        db.refresh(document)
    except SQLAlchemyError:
        db.rollback()


def build_document_detail(document: Document, db: Session) -> DocumentDetail:
    chunks = (
        db.query(KnowledgeItem)
        .filter(KnowledgeItem.source_document_id == document.id)
        .order_by(KnowledgeItem.chunk_index.asc())
        .limit(5)
        .all()
    )
    preview_text = "\n\n".join(chunk.content for chunk in chunks)[:5000]
    return DocumentDetail(
        **DocumentOut.model_validate(document).model_dump(),
        text_preview=preview_text,
        knowledge_preview=chunks,
    )


@router.get("", response_model=list[DocumentOut])
def list_documents(
    status: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[Document]:
    query = db.query(Document).order_by(Document.created_at.desc())
    if status:
        query = query.filter(Document.parse_status == status)
    if keyword:
        like = f"%{keyword.strip()}%"
        query = query.filter(Document.original_filename.ilike(like))
    return query.all()


@router.post("/upload", response_model=DocumentDetail)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)) -> DocumentDetail:
    original_filename = normalize_original_filename(file.filename)
    mime_type = file.content_type or "application/octet-stream"
    extension = validate_file_type(original_filename, mime_type)

    content = await file.read()
    if len(content) > get_max_upload_size_bytes():
        raise HTTPException(status_code=400, detail=FILE_TOO_LARGE_MESSAGE)
    if not content:
        raise HTTPException(status_code=400, detail=EMPTY_CONTENT_MESSAGE)

    document = Document(
        original_filename=original_filename,
        stored_filename="",
        file_extension=extension,
        mime_type=mime_type,
        file_size=len(content),
        storage_path="",
        parse_status="pending",
        parse_error="",
    )

    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="创建文件记录失败，请稍后重试") from exc

    upload_dir = get_upload_dir()
    safe_filename = make_safe_filename(original_filename)
    stored_filename = f"{document.id}_{uuid4().hex[:8]}_{safe_filename}"
    storage_path = upload_dir / stored_filename

    try:
        storage_path.write_bytes(content)
        document.stored_filename = stored_filename
        document.storage_path = str(storage_path)
        document.parse_status = "parsing"
        db.commit()
        db.refresh(document)
    except OSError as exc:
        db.rollback()
        save_failed_status(db, document, "保存上传文件失败，请稍后重试")
        raise HTTPException(status_code=500, detail="保存上传文件失败，请稍后重试") from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="更新文件记录失败，请稍后重试") from exc

    try:
        extracted_text = parse_document(storage_path, original_filename, extension)
        chunks = chunk_text(extracted_text)
        if not chunks:
            raise DocumentParseError(EMPTY_CONTENT_MESSAGE)

        for index, chunk in enumerate(chunks, start=1):
            db.add(
                KnowledgeItem(
                    title=f"{original_filename} 片段 {index}",
                    category="文件知识库",
                    content=build_chunk_content(original_filename, index, chunk),
                    keywords=f"{original_filename}, 文件知识库, {extension.lstrip('.')}",
                    status="active",
                    source_type="document",
                    source_document_id=document.id,
                    source_file_name=original_filename,
                    chunk_index=index,
                )
            )

        document.parse_status = "success"
        document.parse_error = ""
        document.extracted_text_length = len(extracted_text)
        document.chunk_count = len(chunks)
        db.commit()
        db.refresh(document)
    except DocumentParseError as exc:
        db.rollback()
        save_failed_status(db, document, exc.message)
        raise HTTPException(status_code=400, detail=exc.message) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        save_failed_status(db, document, "写入文件知识片段失败，请稍后重试")
        raise HTTPException(status_code=500, detail="写入文件知识片段失败，请稍后重试") from exc
    except Exception as exc:
        db.rollback()
        save_failed_status(db, document, PARSE_FAILED_MESSAGE)
        raise HTTPException(status_code=400, detail=PARSE_FAILED_MESSAGE) from exc

    return build_document_detail(document, db)


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(document_id: int, db: Session = Depends(get_db)) -> DocumentDetail:
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文件不存在")
    return build_document_detail(document, db)


@router.delete("/{document_id}", response_model=MessageResponse)
def delete_document(document_id: int, db: Session = Depends(get_db)) -> MessageResponse:
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文件不存在")

    storage_path = Path(document.storage_path) if document.storage_path else None
    try:
        db.query(KnowledgeItem).filter(KnowledgeItem.source_document_id == document.id).delete(
            synchronize_session=False
        )
        db.delete(document)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="删除文件知识库失败，请稍后重试") from exc

    if storage_path and storage_path.exists() and storage_path.is_file():
        try:
            storage_path.unlink()
        except OSError:
            pass

    return MessageResponse(message="文件知识库删除成功")
