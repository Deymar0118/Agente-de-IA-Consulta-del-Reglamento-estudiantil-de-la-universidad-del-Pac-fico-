"""
Modelos y esquemas de validación de datos con Pydantic para la API.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="Rol del emisor ('user' o 'assistant')")
    content: str = Field(..., description="Contenido del mensaje")


class ChatRequest(BaseModel):
    message: str = Field(..., description="Pregunta o consulta del estudiante")
    history: Optional[List[ChatMessage]] = Field(
        default=[],
        description="Historial previo de la conversación para contextualización"
    )


class SourceItem(BaseModel):
    page: int = Field(..., description="Número de página en el documento oficial")
    content: Optional[str] = Field(default=None, description="Extracto del fragmento recuperado")
    document: str = Field(default="Reglamento.pdf", description="Nombre del archivo fuente")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="Respuesta generada por el agente")
    pages: List[int] = Field(default=[], description="Páginas consultadas")
    sources: List[SourceItem] = Field(default=[], description="Metadatos detallados de las fuentes")
    success: bool = Field(default=True, description="Indica si la consulta fue exitosa")


class DocumentInfo(BaseModel):
    filename: str = Field(..., description="Nombre del archivo")
    size_bytes: int = Field(..., description="Tamaño del archivo en bytes")
    pages_estimated: Optional[int] = Field(default=None, description="Páginas estimadas")


class UploadResponse(BaseModel):
    filename: str = Field(..., description="Nombre del archivo procesado")
    status: str = Field(..., description="Estado de la operación ('success' o 'error')")
    message: str = Field(..., description="Mensaje explicativo")
    chunks_indexed: int = Field(default=0, description="Cantidad de fragmentos indexados")


class RebuildIndexResponse(BaseModel):
    status: str = Field(..., description="Estado de la reconstrucción ('success' o 'error')")
    message: str = Field(..., description="Mensaje explicativo")
    total_chunks: int = Field(..., description="Total de fragmentos en el índice")


class HealthResponse(BaseModel):
    status: str = Field(default="ok", description="Estado del servicio")
    index_loaded: bool = Field(..., description="Indica si el índice vectorial FAISS está cargado")
    version: str = Field(default="1.0.0", description="Versión de la API")
