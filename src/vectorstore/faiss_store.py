"""
Módulo de gestión del Vector Store con FAISS.
Responsabilidad: Crear, guardar y cargar el índice vectorial de los documentos.
"""
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS


# Ruta donde se guardará el índice en disco
FAISS_INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss_index")


def obtener_embeddings(api_key: str) -> GoogleGenerativeAIEmbeddings:
    """Inicializa el modelo de embeddings de Google."""
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key
    )


def crear_y_guardar_vectorstore(chunks: list, api_key: str) -> FAISS:
    """
    Genera embeddings para todos los chunks y crea el índice FAISS.
    Guarda el índice en disco para reutilizarlo en inicios posteriores.

    Args:
        chunks: Lista de documentos divididos por pdf_loader.
        api_key: Clave de API de Google.

    Returns:
        El objeto FAISS con el índice creado.
    """
    print("[VectorStore] Generando embeddings y construyendo índice FAISS...")
    embeddings = obtener_embeddings(api_key)
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(FAISS_INDEX_PATH)
    print(f"[VectorStore] Índice guardado en: {FAISS_INDEX_PATH}")
    return vectorstore


def cargar_vectorstore(api_key: str) -> FAISS | None:
    """
    Carga el índice FAISS desde disco si existe.

    Returns:
        El objeto FAISS cargado, o None si el índice no existe todavía.
    """
    if os.path.exists(FAISS_INDEX_PATH):
        print("[VectorStore] Cargando índice FAISS existente desde disco...")
        embeddings = obtener_embeddings(api_key)
        return FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )
    return None


def obtener_o_crear_vectorstore(chunks: list, api_key: str) -> FAISS:
    """
    Punto de entrada principal: intenta cargar el índice desde disco.
    Si no existe, lo crea desde los chunks y lo guarda.

    Args:
        chunks: Fragmentos del PDF (solo se usan si hay que crear el índice).
        api_key: Clave de API de Google.

    Returns:
        El objeto FAISS listo para búsquedas.
    """
    vectorstore = cargar_vectorstore(api_key)
    if vectorstore is None:
        vectorstore = crear_y_guardar_vectorstore(chunks, api_key)
    return vectorstore
