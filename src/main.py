import os
from pypdf import PdfReader
import google.generativeai as genai

# Configuración inicial
PDF_PATH = os.path.join(os.path.dirname(__file__), '..', 'documentos', 'Reglamento.pdf')

def extraer_texto_pdf(ruta_pdf):
    """
    Fase 1: Extraer texto del documento PDF.
    """
    print(f"Leyendo el documento: {ruta_pdf}")
    # TODO: Implementar la lógica para leer el PDF y retornar el texto
    texto = ""
    return texto

def consultar_gemini(texto_contexto, pregunta):
    """
    Fase 2: Enviar la pregunta y el contexto a la API de Gemini.
    """
    print("Consultando a la IA...")
    # TODO: Configurar la API Key de Google
    # TODO: Llamar al modelo de Gemini para generar la respuesta
    respuesta = "Respuesta de prueba (Falta implementar)"
    return respuesta

if __name__ == "__main__":
    print("--- Asistente de IA - Universidad del Pacífico (Fase Inicial) ---")
    
    # 1. Extraer texto
    texto_reglamento = extraer_texto_pdf(PDF_PATH)
    
    # 2. Hacer pregunta de prueba
    pregunta_prueba = "¿Cuáles son los deberes de los estudiantes?"
    respuesta = consultar_gemini(texto_reglamento, pregunta_prueba)
    
    print("\nPregunta:", pregunta_prueba)
    print("Respuesta:", respuesta)
