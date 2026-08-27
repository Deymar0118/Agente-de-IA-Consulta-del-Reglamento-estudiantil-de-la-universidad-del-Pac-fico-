"""
Módulo de carga y troceado de documentos PDF.
Responsabilidad: Leer el archivo PDF y dividirlo en fragmentos manejables.
"""
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def cargar_y_trocear_pdf(ruta_pdf: str) -> list:
    """
    Carga un PDF y lo divide en fragmentos (chunks) para procesamiento RAG.
    Los separadores están ordenados semánticamente para respetar la estructura
    del reglamento (Capítulos, Artículos, Parágrafos).

    Args:
        ruta_pdf: Ruta absoluta al archivo PDF.

    Returns:
        Lista de documentos (chunks) con texto y metadatos de página.
    """
    print(f"[Loader] Cargando documento: {ruta_pdf}")
    loader = PyPDFLoader(ruta_pdf)
    documentos = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        # Separadores ordenados de mayor a menor semántica, priorizando
        # los límites naturales del reglamento (artículos, parágrafos)
        separators=[
            "\nCAPÍTULO",
            "\nArtículo",
            "\nArt\u00edculo",   # variante con tilde escapada
            "\nParágrafo",
            "\n\n",
            "\n",
            " ",
            "",
        ],
        chunk_size=1200,      # Mayor tamaño para preservar artículos completos
        chunk_overlap=250,    # Mayor solapamiento para no perder contexto entre fragmentos
        length_function=len,
    )

    chunks = splitter.split_documents(documentos)
    print(f"[Loader] Documento dividido en {len(chunks)} fragmentos.")
    return chunks
