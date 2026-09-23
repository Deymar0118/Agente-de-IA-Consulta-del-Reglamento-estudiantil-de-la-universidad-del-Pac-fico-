"""
Punto de entrada para ejecución local en consola.
Orquesta los módulos RAG para una interfaz de texto interactiva.
"""
import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

# Añadir el directorio src al path para importaciones relativas
sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()

from loaders.pdf_loader import cargar_y_trocear_pdf
from vectorstore.faiss_store import obtener_o_crear_vectorstore, FAISS_INDEX_PATH
from llm.gemini_chain import consultar_con_rag_stream

# Ruta al documento PDF
PDF_PATH = os.path.join(os.path.dirname(__file__), '..', 'documentos', 'Reglamento.pdf')


if __name__ == "__main__":
    print("--- Asistente de IA - Universidad del Pacífico ---")
    print("Iniciando sistema RAG...\n")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "tu_api_key_aqui":
        print("Error: Configura tu GEMINI_API_KEY en el archivo .env")
        sys.exit(1)

    # 1. Obtener o crear el vectorstore FAISS (carga instantánea si ya existe en disco)
    if os.path.exists(FAISS_INDEX_PATH):
        vectorstore = obtener_o_crear_vectorstore(chunks=[], api_key=api_key)
    else:
        chunks = cargar_y_trocear_pdf(PDF_PATH)
        vectorstore = obtener_o_crear_vectorstore(chunks, api_key)

    print("\n¡Sistema listo! Puedes hacer preguntas sobre el reglamento.")
    print("Escribe 'salir' para terminar.\n")

    historial = []

    while True:
        try:
            pregunta = input("\n👤 Tú: ")

            if pregunta.lower() in ['salir', 'exit', 'quit']:
                print("¡Hasta luego!")
                break

            if not pregunta.strip():
                continue

            print("\n🤖 Asistente: ", end="", flush=True)
            texto_acumulado = []
            for chunk in consultar_con_rag_stream(vectorstore, pregunta, historial):
                print(chunk, end="", flush=True)
                texto_acumulado.append(chunk)
            print()

            respuesta = "".join(texto_acumulado)

            # Guardar en historial (memoria conversacional)
            historial.append(HumanMessage(content=pregunta))
            historial.append(AIMessage(content=respuesta))

        except KeyboardInterrupt:
            print("\n¡Hasta luego!")
            break
        except Exception as e:
            print(f"\nOcurrió un error: {e}")
