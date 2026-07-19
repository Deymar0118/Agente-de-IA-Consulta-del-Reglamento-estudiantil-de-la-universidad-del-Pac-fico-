"""
Módulo de conexión al LLM (Gemini) y construcción de la cadena RAG.
Responsabilidad: Ejecutar la consulta al modelo usando fragmentos recuperados del vectorstore.
"""
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from prompts.templates import obtener_prompt_rag


def consultar_con_rag(vectorstore: FAISS, pregunta: str, historial: list = None) -> str:
    """
    Realiza una consulta al LLM usando el patrón RAG completo.

    Flujo:
    1. Recupera los 4 fragmentos más relevantes del vectorstore.
    2. Combina esos fragmentos como contexto.
    3. Envía al LLM: contexto + historial + pregunta.
    4. Retorna la respuesta limpia como texto.

    Args:
        vectorstore: El índice FAISS con los embeddings del documento.
        pregunta: La pregunta del usuario.
        historial: Lista de mensajes previos (HumanMessage / AIMessage).

    Returns:
        Respuesta del modelo como string.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "tu_api_key_aqui":
        return "Error: No se configuró una API Key válida en el archivo .env."

    if historial is None:
        historial = []

    try:
        # 1. Recuperar fragmentos relevantes (la "R" de RAG)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
        fragmentos = retriever.invoke(pregunta)
        contexto = "\n\n---\n\n".join([f.page_content for f in fragmentos])

        # Extraer números de página únicos (1-indexed)
        paginas = sorted(list(set([f.metadata.get("page", 0) + 1 for f in fragmentos])))

        # 2. Inicializar el LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            google_api_key=api_key,
            temperature=0
        )

        # 3. Construir la cadena con el prompt centralizado
        prompt = obtener_prompt_rag()
        chain = prompt | llm | StrOutputParser()

        # 4. Ejecutar y retornar la respuesta
        respuesta = chain.invoke({
            "contexto": contexto,
            "historial": historial,
            "pregunta": pregunta
        })
        
        # Añadir las fuentes al final si la respuesta es afirmativa
        if "no encuentro información sobre eso" not in respuesta.lower() and paginas:
            paginas_str = ", ".join(map(str, paginas))
            respuesta += f"\n\n*📄 Fuentes: Reglamento Estudiantil (Pág. {paginas_str})*"
            
        return respuesta

    except Exception as e:
        error_msg = str(e).lower()

        # Error de límite de velocidad (demasiadas peticiones por minuto)
        if "429" in str(e) or "resource_exhausted" in error_msg or "rate limit" in error_msg:
            return (
                "⏳ El asistente ha recibido demasiadas consultas en poco tiempo. "
                "Por favor, espera unos 60 segundos e intenta de nuevo."
            )

        # Error de cuota diaria agotada
        if "quota" in error_msg or "daily limit" in error_msg:
            return (
                "📋 Se ha alcanzado el límite de consultas diarias de la API. "
                "El servicio se restablecerá automáticamente mañana. "
                "No se realizará ningún cargo económico."
            )

        # Error de API Key inválida o no encontrada
        if "api_key" in error_msg or "401" in str(e) or "403" in str(e) or "unauthenticated" in error_msg:
            return (
                "🔑 Error de autenticación: la API Key configurada no es válida o ha expirado. "
                "Por favor, verifica el archivo .env o los Secrets de Streamlit Cloud."
            )

        # Error de modelo no encontrado
        if "404" in str(e) or "not_found" in error_msg:
            return (
                "🚫 El modelo de IA no está disponible en este momento. "
                "Puede ser un problema temporal del servicio de Google."
            )

        # Cualquier otro error inesperado
        return f"❌ Ocurrió un error inesperado al procesar tu consulta. Intenta de nuevo. (Detalle: {e})"

