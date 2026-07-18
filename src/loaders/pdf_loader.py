"""
Módulo de carga y troceado de documentos PDF.
Responsabilidad: Leer el archivo PDF y dividirlo en fragmentos manejables.
"""
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def cargar_y_trocear_pdf(ruta_pdf: str) -> list:
    """
    Carga un PDF y lo divide en fragmentos (chunks) para procesamiento RAG.

    Args:
        ruta_pdf: Ruta absoluta al archivo PDF.

    Returns:
        Lista de documentos (chunks) con texto y metadatos de página.
    """
    print(f"[Loader] Cargando documento: {ruta_pdf}")
    loader = PyPDFLoader(ruta_pdf)
    documentos = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,      # Tamaño de cada fragmento en caracteres
        chunk_overlap=200,    # Solapamiento para no perder contexto entre fragmentos
        length_function=len,
    )

    chunks = splitter.split_documents(documentos)
    print(f"[Loader] Documento dividido en {len(chunks)} fragmentos.")
    return chunks
