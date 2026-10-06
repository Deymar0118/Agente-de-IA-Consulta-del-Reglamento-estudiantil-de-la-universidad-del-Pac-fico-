"""
Rutas para gestión de documentos oficiales e indexación vectorial.
"""
import os
import shutil
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from api.schemas import DocumentInfo, UploadResponse, RebuildIndexResponse
from api.services.rag_service import RAGService

router = APIRouter(prefix="/documents", tags=["Documentos"])


@router.get("", response_model=List[DocumentInfo], summary="Listar documentos disponibles")
async def listar_documentos():
    """
    Retorna la lista de archivos PDF almacenados en el sistema.
    """
    rag_service = RAGService.get_instance()
    docs = rag_service.listar_documentos()
    return [
        DocumentInfo(
            filename=doc["filename"],
            size_bytes=doc["size_bytes"]
        )
        for doc in docs
    ]


@router.post("/upload", response_model=UploadResponse, summary="Subir nuevo documento PDF y reindexar")
async def subir_documento(file: UploadFile = File(...)):
    """
    Permite subir una nueva versión del reglamento u otro documento oficial en PDF,
    lo almacena y actualiza el índice FAISS.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Solo se admiten archivos en formato PDF."
        )

    # Directorio de almacenamiento de documentos
    docs_dir = Path(__file__).resolve().parent.parent.parent.parent / "documentos"
    docs_dir.mkdir(parents=True, exist_ok=True)
    target_path = docs_dir / file.filename

    try:
        # Guardar archivo en disco
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Reindexar el documento subido
        rag_service = RAGService.get_instance()
        total_chunks = rag_service.reindexar_documento(str(target_path))

        return UploadResponse(
            filename=file.filename,
            status="success",
            message=f"Documento '{file.filename}' subido e indexado exitosamente.",
            chunks_indexed=total_chunks
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar y reindexar el documento: {str(e)}"
        )


@router.post("/rebuild-index", response_model=RebuildIndexResponse, summary="Reconstruir índice FAISS")
async def reconstruir_indice():
    """
    Fuerza la reconstrucción completa del índice vectorial a partir de los documentos actuales.
    """
    docs_dir = Path(__file__).resolve().parent.parent.parent.parent / "documentos"
    default_pdf = docs_dir / "Reglamento.pdf"

    if not default_pdf.exists():
        raise HTTPException(
            status_code=404,
            detail="No se encontró el documento 'Reglamento.pdf' base para reconstruir el índice."
        )

    try:
        rag_service = RAGService.get_instance()
        total_chunks = rag_service.reindexar_documento(str(default_pdf))
        return RebuildIndexResponse(
            status="success",
            message="Índice FAISS reconstruido con éxito.",
            total_chunks=total_chunks
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al reconstruir el índice: {str(e)}"
        )
