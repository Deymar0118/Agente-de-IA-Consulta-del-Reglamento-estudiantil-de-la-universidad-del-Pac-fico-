"""
Módulo de gestión del Vector Store con FAISS.
Responsabilidad: Crear, guardar y cargar el índice vectorial de los documentos.
"""
import os
from functools import lru_cache
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS


# Ruta donde se guardará el índice en disco
FAISS_INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss_index")


@lru_cache(maxsize=1)
def obtener_embeddings(api_key: str) -> GoogleGenerativeAIEmbeddings:
    """Inicializa el modelo de embeddings (cacheado: se crea UNA sola vez por proceso)."""
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
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
    print("[VectorStore] Generando embeddings y construyendo índice FAISS en lotes...")
    embeddings = obtener_embeddings(api_key)
    import time
    batch_size = 50
    vectorstore = None
    total_lotes = (len(chunks) + batch_size - 1) // batch_size
    for idx, i in enumerate(range(0, len(chunks), batch_size), start=1):
        batch = chunks[i:i + batch_size]
        print(f"[VectorStore] Procesando lote {idx}/{total_lotes} ({len(batch)} fragmentos)...")
        if vectorstore is None:
            vectorstore = FAISS.from_documents(batch, embeddings)
        else:
            vectorstore.add_documents(batch)
        if i + batch_size < len(chunks):
            print("[VectorStore] Pausa de 65s para reiniciar ventana de 1 minuto del Free Tier de Google...")
            time.sleep(65)

    vectorstore.save_local(FAISS_INDEX_PATH)
    print(f"[VectorStore] Índice guardado en: {FAISS_INDEX_PATH}")
    return vectorstore


def cargar_vectorstore(api_key: str) -> FAISS | None:
    """
    Carga el índice FAISS desde disco si existe.
    Si el índice está corrupto o incompleto, lo detecta de forma segura
    y retorna None para que el sistema lo reconstruya limpiamente.

    Returns:
        El objeto FAISS cargado, o None si no existe o no se pudo cargar.
    """
    if os.path.exists(FAISS_INDEX_PATH):
        print("[VectorStore] Cargando índice FAISS existente desde disco...")
        try:
            embeddings = obtener_embeddings(api_key)
            return FAISS.load_local(
                FAISS_INDEX_PATH,
                embeddings,
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            print(f"[VectorStore] Advertencia: Error al cargar índice FAISS ({e}). Se reconstruirá.")
            try:
                import shutil
                shutil.rmtree(FAISS_INDEX_PATH, ignore_errors=True)
            except Exception:
                pass
            return None
    return None


def obtener_o_crear_vectorstore(chunks: list, api_key: str, force_rebuild: bool = False) -> FAISS:
    """
    Punto de entrada principal: intenta cargar el índice desde disco.
    Si no existe o se fuerza la reconstrucción, lo crea desde los chunks y lo guarda.

    Args:
        chunks: Fragmentos del PDF (solo se usan si hay que crear el índice).
        api_key: Clave de API de Google.
        force_rebuild: Si es True, recrea el índice aunque ya exista en disco.
                       Útil tras cambios en el chunking o el documento fuente.

    Returns:
        El objeto FAISS listo para búsquedas.
    """
    if not force_rebuild:
        vectorstore = cargar_vectorstore(api_key)
        if vectorstore is not None:
            return vectorstore
    else:
        print("[VectorStore] Regenerando índice FAISS (force_rebuild=True)...")

    # Si chunks vino vacío (por ejemplo tras fallo de lectura de índice), cargarlos automáticamente
    if not chunks:
        from loaders.pdf_loader import cargar_y_trocear_pdf
        pdf_path = os.path.join(os.path.dirname(__file__), '..', '..', 'documentos', 'Reglamento.pdf')
        chunks = cargar_y_trocear_pdf(pdf_path)

    return crear_y_guardar_vectorstore(chunks, api_key)
