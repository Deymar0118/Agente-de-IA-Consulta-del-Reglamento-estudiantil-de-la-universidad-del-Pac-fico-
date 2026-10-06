"""
Rutas para la interacción del chat y streaming de respuestas del agente.
"""
import json
import asyncio
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from api.schemas import ChatRequest, ChatResponse
from api.services.rag_service import RAGService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse, summary="Consulta síncrona RAG")
async def consultar_chat(request: ChatRequest):
    """
    Recibe la pregunta del usuario y el historial previo.
    Retorna la respuesta completa con el listado de páginas y fuentes consultadas.
    """
    rag_service = RAGService.get_instance()
    resultado = rag_service.consultar(
        pregunta=request.message,
        historial=request.history
    )
    return ChatResponse(**resultado)


@router.post("/stream", summary="Consulta RAG en tiempo real (Streaming / SSE)")
async def consultar_chat_stream(request: ChatRequest):
    """
    Transmite la respuesta token por token en tiempo real utilizando Server-Sent Events (SSE).
    """
    rag_service = RAGService.get_instance()

    async def event_generator():
        try:
            async for token in rag_service.consultar_stream(request.message, request.history):
                # Formato SSE estándar data: <contenido>\n\n
                payload = json.dumps({"token": token}, ensure_ascii=False)
                yield f"data: {payload}\n\n"
                await asyncio.sleep(0.01)  # Pequeña pausa para fluidez visual
            yield "data: [DONE]\n\n"
        except Exception as e:
            error_payload = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {error_payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
