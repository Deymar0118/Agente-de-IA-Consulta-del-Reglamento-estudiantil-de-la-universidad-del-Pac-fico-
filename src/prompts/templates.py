"""
Plantillas de Prompts del sistema.
Responsabilidad: Centralizar las instrucciones que se le dan al modelo de lenguaje.
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def obtener_prompt_rag() -> ChatPromptTemplate:
    """
    Retorna la plantilla del prompt para el sistema RAG.
    El contexto recibido serán los fragmentos recuperados del vectorstore,
    no el documento completo.
    """
    return ChatPromptTemplate.from_messages([
        (
            "system",
            "Eres un asistente virtual oficial de la Universidad del Pacífico. "
            "Tu tarea es responder preguntas basándote ÚNICAMENTE en los fragmentos "
            "del reglamento estudiantil que se te proporcionan a continuación. "
            "Si la respuesta no se encuentra en esos fragmentos, debes responder: "
            "'Lo siento, no encuentro información sobre eso en el reglamento oficial.'\n\n"
            "FRAGMENTOS RELEVANTES DEL REGLAMENTO:\n{contexto}"
        ),
        MessagesPlaceholder(variable_name="historial"),
        ("human", "{pregunta}"),
    ])
