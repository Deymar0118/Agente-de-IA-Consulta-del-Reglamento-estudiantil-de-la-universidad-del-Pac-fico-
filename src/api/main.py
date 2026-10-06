"""
Punto de entrada de la aplicación FastAPI.
Configura middlewares (CORS), routers de endpoints y ciclo de vida de la aplicación.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Cargar variables de entorno
load_dotenv()

# Asegurar que el directorio raíz de 'src' esté en sys.path
src_dir = Path(__file__).resolve().parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from api.routes.chat import router as chat_router
from api.routes.documents import router as documents_router
from api.schemas import HealthResponse
from api.services.rag_service import RAGService

app = FastAPI(
    title="API de Consulta de Reglamento Estudiantil - Universidad del Pacífico",
    description="API REST y Streaming RAG para responder preguntas basadas en la normativa estudiantil.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para permitir comunicación con React (Vite / Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React / Next dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"                       # Permisivo para desarrollo
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar Routers
app.include_router(chat_router, prefix="/api")
app.include_router(documents_router, prefix="/api")


@app.get("/api/health", response_model=HealthResponse, tags=["Salud"])
async def check_health():
    """
    Endpoint de verificación de estado y preparación del vectorstore.
    """
    rag_service = RAGService.get_instance()
    return HealthResponse(
        status="ok",
        index_loaded=rag_service.is_ready(),
        version="1.0.0"
    )


@app.get("/", tags=["Inicio"])
async def root():
    """
    Ruta raíz con información del servicio y enlace a la documentación interactiva.
    """
    return {
        "message": "Bienvenido a la API del Agente de IA - Universidad del Pacífico",
        "docs": "/docs",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    # Puerto 8000 por defecto
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=True)
