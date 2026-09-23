"""
Módulo de conexión al LLM (Gemini) y construcción de la cadena RAG.
Responsabilidad: Ejecutar la consulta al modelo usando fragmentos recuperados del vectorstore.
"""
import os
from functools import lru_cache
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from prompts.templates import obtener_prompt_rag, obtener_prompt_contextualizacion

# ---------------------------------------------------------------------------
# Instancias cacheadas a nivel de módulo: se crean UNA sola vez por proceso.
# Esto elimina el overhead de construcción en cada llamada a consultar_con_rag.
# ---------------------------------------------------------------------------
_PROMPT_CACHE = None           # ChatPromptTemplate RAG
_PROMPT_CONTEXT_CACHE = None   # ChatPromptTemplate contextualización


@lru_cache(maxsize=1)
def _obtener_llm(api_key: str) -> ChatGoogleGenerativeAI:
    """Retorna la instancia del LLM cacheada para la API key dada."""
    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=api_key,
        temperature=0.1
    )


def _obtener_prompt():
    """Retorna la instancia cacheada del ChatPromptTemplate RAG."""
    global _PROMPT_CACHE
    if _PROMPT_CACHE is None:
        _PROMPT_CACHE = obtener_prompt_rag()
    return _PROMPT_CACHE


def _obtener_prompt_context():
    """Retorna la instancia cacheada del ChatPromptTemplate de contextualización."""
    global _PROMPT_CONTEXT_CACHE
    if _PROMPT_CONTEXT_CACHE is None:
        _PROMPT_CONTEXT_CACHE = obtener_prompt_contextualizacion()
    return _PROMPT_CONTEXT_CACHE


def contextualizar_pregunta(pregunta: str, historial: list, api_key: str) -> str:
    """
    Si hay historial conversacional previo, reformula la pregunta para que sea
    autocontenida y capture el tema discutido (History-Aware Retriever).
    Si no hay historial, retorna la pregunta original.
    """
    if not historial:
        return pregunta

    try:
        llm = _obtener_llm(api_key)
        prompt_ctx = _obtener_prompt_context()
        chain_ctx = prompt_ctx | llm | StrOutputParser()
        pregunta_reformulada = chain_ctx.invoke({
            "historial": historial,
            "pregunta": pregunta
        }).strip()

        if pregunta_reformulada and len(pregunta_reformulada) > 3:
            return pregunta_reformulada
    except Exception as e:
        print(f"[RAG] Advertencia al contextualizar: {e}. Usando pregunta original.")

    return pregunta


def _es_respuesta_afirmativa(respuesta: str) -> bool:
    """Verifica si la respuesta aportó información sustantiva o si indicó desconocimiento/fuera de ámbito."""
    resp_norm = respuesta.lower()
    # Normalizar tildes para evitar falsos negativos por acentuación
    for ac, sin in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u")]:
        resp_norm = resp_norm.replace(ac, sin)

    frases_negativas = [
        "no encuentro informacion",
        "no se encuentra informacion",
        "no he encontrado informacion",
        "no hay informacion sobre eso",
        "no dispongo de informacion",
        "el reglamento no contempla",
        "el reglamento no especifica",
        "el reglamento no menciona",
        "solo estoy capacitado para responder sobre normativa",
        "solo puedo responder consultas relacionadas",
    ]
    for frase in frases_negativas:
        if frase in resp_norm:
            return False
    return True


def _manejar_error(e: Exception) -> str:
    """Mapea excepciones a mensajes explicativos claros para el usuario."""
    error_msg = str(e).lower()

    if "429" in str(e) or "resource_exhausted" in error_msg or "rate limit" in error_msg:
        return (
            "⏳ El asistente ha recibido demasiadas consultas en poco tiempo. "
            "Por favor, espera unos 60 segundos e intenta de nuevo."
        )

    if "quota" in error_msg or "daily limit" in error_msg:
        return (
            "📋 Se ha alcanzado el límite de consultas diarias de la API. "
            "El servicio se restablecerá automáticamente mañana. "
            "No se realizará ningún cargo económico."
        )

    if "api_key" in error_msg or "401" in str(e) or "403" in str(e) or "unauthenticated" in error_msg:
        return (
            "🔑 Error de autenticación: la API Key configurada no es válida o ha expirado. "
            "Por favor, verifica el archivo .env o los Secrets de Streamlit Cloud."
        )

    if "404" in str(e) or "not_found" in error_msg:
        return (
            "🚫 El modelo de IA no está disponible en este momento. "
            "Puede ser un problema temporal del servicio de Google."
        )

    return f"❌ Ocurrió un error inesperado al procesar tu consulta. Intenta de nuevo. (Detalle: {e})"


def consultar_con_rag_stream(vectorstore: FAISS, pregunta: str, historial: list = None):
    """
    Generador que emite fragmentos de texto (tokens) en tiempo real para Streamlit.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "tu_api_key_aqui":
        yield "Error: No se configuró una API Key válida en el archivo .env."
        return

    if historial is None:
        historial = []

    try:
        # 1. Contextualizar la pregunta con el historial si aplica
        pregunta_busqueda = contextualizar_pregunta(pregunta, historial, api_key)

        # 2. Recuperar fragmentos relevantes con MMR
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 8,
                "fetch_k": 25,
            }
        )
        fragmentos = retriever.invoke(pregunta_busqueda)
        contexto = "\n\n---\n\n".join([f.page_content for f in fragmentos])
        paginas = sorted(list(set([f.metadata.get("page", 0) + 1 for f in fragmentos])))

        # 3. Preparar LLM y prompt
        llm = _obtener_llm(api_key)
        prompt = _obtener_prompt()
        chain = prompt | llm | StrOutputParser()

        # 4. Emitir tokens en streaming
        texto_acumulado = []
        for chunk in chain.stream({
            "contexto": contexto,
            "historial": historial,
            "pregunta": pregunta
        }):
            texto_acumulado.append(chunk)
            yield chunk

        # 5. Agregar fuentes si la respuesta fue sustantiva
        respuesta_completa = "".join(texto_acumulado)
        if _es_respuesta_afirmativa(respuesta_completa) and paginas:
            paginas_str = ", ".join(map(str, paginas))
            yield f"\n\n*📄 Fuentes: Reglamento Estudiantil (Pág. {paginas_str})*"

    except Exception as e:
        yield _manejar_error(e)


def consultar_con_rag(vectorstore: FAISS, pregunta: str, historial: list = None) -> str:
    """
    Realiza una consulta síncrona al LLM usando el patrón RAG completo.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "tu_api_key_aqui":
        return "Error: No se configuró una API Key válida en el archivo .env."

    if historial is None:
        historial = []

    try:
        # 1. Contextualizar la pregunta con el historial si aplica
        pregunta_busqueda = contextualizar_pregunta(pregunta, historial, api_key)

        # 2. Recuperar fragmentos relevantes con MMR
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 8,
                "fetch_k": 25,
            }
        )
        fragmentos = retriever.invoke(pregunta_busqueda)
        contexto = "\n\n---\n\n".join([f.page_content for f in fragmentos])
        paginas = sorted(list(set([f.metadata.get("page", 0) + 1 for f in fragmentos])))

        # 3. Invocar LLM
        llm = _obtener_llm(api_key)
        prompt = _obtener_prompt()
        chain = prompt | llm | StrOutputParser()

        respuesta = chain.invoke({
            "contexto": contexto,
            "historial": historial,
            "pregunta": pregunta
        })

        # 4. Añadir fuentes si la respuesta fue sustantiva
        if _es_respuesta_afirmativa(respuesta) and paginas:
            paginas_str = ", ".join(map(str, paginas))
            respuesta += f"\n\n*📄 Fuentes: Reglamento Estudiantil (Pág. {paginas_str})*"

        return respuesta

    except Exception as e:
        return _manejar_error(e)

