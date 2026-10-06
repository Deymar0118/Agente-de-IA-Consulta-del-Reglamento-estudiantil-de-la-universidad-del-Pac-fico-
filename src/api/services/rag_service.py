"""
Servicio RAG para la API FastAPI.
Conecta los endpoints con la lógica de recuperación de FAISS y el modelo Gemini.
"""
import os
import sys
import asyncio
from typing import List, Dict, Any, AsyncGenerator
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Asegurar que el directorio raíz de 'src' esté en sys.path para importar módulos existentes
src_path = str(Path(__file__).resolve().parent.parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from llm.gemini_chain import (
    _obtener_llm,
    _obtener_prompt,
    contextualizar_pregunta,
    _es_respuesta_afirmativa,
    _manejar_error
)
from vectorstore.faiss_store import (
    cargar_vectorstore,
    obtener_o_crear_vectorstore,
    crear_y_guardar_vectorstore,
    FAISS_INDEX_PATH
)
from loaders.pdf_loader import cargar_y_trocear_pdf
from langchain_core.output_parsers import StrOutputParser


class RAGService:
    _instance = None
    _vectorstore = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._inicializar_vectorstore()

    def _inicializar_vectorstore(self):
        """Carga el vectorstore existente si la clave API está configurada."""
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "tu_api_key_aqui":
            try:
                self._vectorstore = cargar_vectorstore(api_key)
                if self._vectorstore is None:
                    # Intenta crear si existe el PDF por defecto
                    docs_dir = Path(__file__).resolve().parent.parent.parent.parent / "documentos"
                    default_pdf = docs_dir / "Reglamento.pdf"
                    if default_pdf.exists():
                        chunks = cargar_y_trocear_pdf(str(default_pdf))
                        self._vectorstore = obtener_o_crear_vectorstore(chunks, api_key)
            except Exception as e:
                print(f"[RAGService] Error al inicializar vectorstore: {e}")
                self._vectorstore = None

    def is_ready(self) -> bool:
        return self._vectorstore is not None

    def _convert_history(self, history_list) -> List[Dict[str, str]]:
        """Convierte los mensajes recibidos a formato LangChain / dict."""
        formato_historial = []
        for msg in history_list:
            if hasattr(msg, "role") and hasattr(msg, "content"):
                formato_historial.append({"role": msg.role, "content": msg.content})
            elif isinstance(msg, dict):
                formato_historial.append(msg)
        return formato_historial

    def consultar(self, pregunta: str, historial: list = None) -> Dict[str, Any]:
        """Realiza una consulta RAG síncrona/completa y retorna la respuesta con metadatos."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "tu_api_key_aqui":
            return {
                "answer": "Error: No se configuró una API Key válida de Google Gemini en el servidor.",
                "pages": [],
                "sources": [],
                "success": False
            }

        if self._vectorstore is None:
            self._inicializar_vectorstore()
            if self._vectorstore is None:
                return {
                    "answer": "Error: La base de conocimiento no está inicializada.",
                    "pages": [],
                    "sources": [],
                    "success": False
                }

        historial_dict = self._convert_history(historial or [])

        try:
            # 1. Contextualizar
            pregunta_busqueda = contextualizar_pregunta(pregunta, historial_dict, api_key)

            # 2. Recuperar fragmentos
            retriever = self._vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 8, "fetch_k": 25}
            )
            fragmentos = retriever.invoke(pregunta_busqueda)
            contexto = "\n\n---\n\n".join([f.page_content for f in fragmentos])
            paginas = sorted(list(set([f.metadata.get("page", 0) + 1 for f in fragmentos])))
            sources = [
                {
                    "page": f.metadata.get("page", 0) + 1,
                    "content": f.page_content[:200] + "...",
                    "document": Path(f.metadata.get("source", "Reglamento.pdf")).name
                }
                for f in fragmentos
            ]

            # 3. Invocar LLM
            llm = _obtener_llm(api_key)
            prompt = _obtener_prompt()
            chain = prompt | llm | StrOutputParser()

            respuesta = chain.invoke({
                "contexto": contexto,
                "historial": historial_dict,
                "pregunta": pregunta
            })

            # 4. Formatear fuentes en la respuesta si aplica
            if _es_respuesta_afirmativa(respuesta) and paginas:
                paginas_str = ", ".join(map(str, paginas))
                respuesta_con_fuentes = f"{respuesta}\n\n*📄 Fuentes: Reglamento Estudiantil (Pág. {paginas_str})*"
            else:
                respuesta_con_fuentes = respuesta

            return {
                "answer": respuesta_con_fuentes,
                "pages": paginas if _es_respuesta_afirmativa(respuesta) else [],
                "sources": sources if _es_respuesta_afirmativa(respuesta) else [],
                "success": True
            }
        except Exception as e:
            return {
                "answer": _manejar_error(e),
                "pages": [],
                "sources": [],
                "success": False
            }

    async def consultar_stream(self, pregunta: str, historial: list = None) -> AsyncGenerator[str, None]:
        """
        Generador asíncrono que produce eventos de texto para streaming (SSE).
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "tu_api_key_aqui":
            yield "data: [ERROR] No se configuró una API Key válida de Google Gemini.\n\n"
            return

        if self._vectorstore is None:
            self._inicializar_vectorstore()
            if self._vectorstore is None:
                yield "data: [ERROR] El índice vectorial no está listo.\n\n"
                return

        historial_dict = self._convert_history(historial or [])

        try:
            # 1. Contextualizar
            pregunta_busqueda = contextualizar_pregunta(pregunta, historial_dict, api_key)

            # 2. Recuperar fragmentos
            retriever = self._vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 8, "fetch_k": 25}
            )
            fragmentos = retriever.invoke(pregunta_busqueda)
            contexto = "\n\n---\n\n".join([f.page_content for f in fragmentos])
            paginas = sorted(list(set([f.metadata.get("page", 0) + 1 for f in fragmentos])))

            # 3. Invocar en stream
            llm = _obtener_llm(api_key)
            prompt = _obtener_prompt()
            chain = prompt | llm | StrOutputParser()

            texto_acumulado = []
            for chunk in chain.stream({
                "contexto": contexto,
                "historial": historial_dict,
                "pregunta": pregunta
            }):
                texto_acumulado.append(chunk)
                yield chunk

            respuesta_completa = "".join(texto_acumulado)
            if _es_respuesta_afirmativa(respuesta_completa) and paginas:
                paginas_str = ", ".join(map(str, paginas))
                yield f"\n\n*📄 Fuentes: Reglamento Estudiantil (Pág. {paginas_str})*"

        except Exception as e:
            yield _manejar_error(e)

    def reindexar_documento(self, ruta_pdf: str) -> int:
        """Carga y trocea un PDF, construyendo un nuevo índice FAISS."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no configurada")

        chunks = cargar_y_trocear_pdf(ruta_pdf)
        self._vectorstore = crear_y_guardar_vectorstore(chunks, api_key)
        return len(chunks)

    def listar_documentos(self) -> List[Dict[str, Any]]:
        """Lista los documentos PDFs disponibles en la carpeta documentos/."""
        docs_dir = Path(__file__).resolve().parent.parent.parent.parent / "documentos"
        docs = []
        if docs_dir.exists():
            for f in docs_dir.glob("*.pdf"):
                docs.append({
                    "filename": f.name,
                    "size_bytes": f.stat().st_size,
                    "path": str(f)
                })
        return docs
