import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# Configuración inicial
PDF_PATH = os.path.join(os.path.dirname(__file__), '..', 'documentos', 'Reglamento.pdf')

def extraer_texto_pdf(ruta_pdf):
    """
    Fase 1: Extraer texto del documento PDF usando LangChain.
    """
    print(f"Leyendo el documento: {ruta_pdf}")
    try:
        loader = PyPDFLoader(ruta_pdf)
        documentos = loader.load()
        # Unir el texto de todas las páginas
        texto = "\n".join([doc.page_content for doc in documentos])
        return texto
    except Exception as e:
        print(f"Error al leer el PDF: {e}")
        return ""

def consultar_gemini(texto_contexto, pregunta):
    """
    Fase 2: Enviar la pregunta y el contexto a la API usando LangChain.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "tu_api_key_aqui":
        return "Error: No se configuró una API Key válida en el archivo .env."
    
    try:
        # Inicializar el modelo LLM de Google
        llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest", 
            google_api_key=api_key, 
            temperature=0
        )
        
        # Crear la plantilla del Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Eres un asistente virtual de la Universidad del Pacífico. Tu tarea es responder a las preguntas basándote ÚNICAMENTE en el siguiente reglamento oficial. Si la respuesta no está en el reglamento, debes decir: 'Lo siento, no encuentro información sobre eso en el reglamento oficial.'\n\nREGLAMENTO:\n{contexto}"),
            ("human", "{pregunta}")
        ])
        
        # Crear la cadena (Chain) uniendo prompt y LLM
        chain = prompt | llm
        
        # Ejecutar la cadena
        response = chain.invoke({
            "contexto": texto_contexto,
            "pregunta": pregunta
        })
        
        return response.content
    except Exception as e:
        return f"Error al consultar Gemini con LangChain: {e}"

if __name__ == "__main__":
    print("--- Asistente de IA - Universidad del Pacífico ---")
    print("Iniciando sistema y leyendo el reglamento...\n")
    
    # 1. Extraer texto
    texto_reglamento = extraer_texto_pdf(PDF_PATH)
    
    if not texto_reglamento.strip():
        print("Error: No se pudo extraer texto del documento.")
        exit()
        
    print("¡Sistema listo! Puedes hacer preguntas sobre el reglamento.")
    print("Escribe 'salir' para terminar la conversación.\n")
    
    # 2. Bucle interactivo
    while True:
        try:
            pregunta_usuario = input("\n👤 Tú: ")
            
            if pregunta_usuario.lower() in ['salir', 'exit', 'quit']:
                print("¡Hasta luego!")
                break
            
            if not pregunta_usuario.strip():
                continue
                
            respuesta = consultar_gemini(texto_reglamento, pregunta_usuario)
            print(f"\n🤖 Asistente:\n{respuesta}")
            
        except KeyboardInterrupt:
            print("\n¡Hasta luego!")
            break
        except Exception as e:
            print(f"\nOcurrió un error: {e}")
