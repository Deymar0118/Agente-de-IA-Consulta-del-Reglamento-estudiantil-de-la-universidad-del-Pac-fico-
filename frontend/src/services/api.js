/**
 * Servicio de comunicación con el backend FastAPI.
 */

const API_BASE_URL = '/api';

/**
 * Consulta el estado de salud de la API y vectorstore.
 */
export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('[API] Error verificando salud:', err);
    return { status: 'error', index_loaded: false };
  }
}

/**
 * Obtiene la lista de documentos PDFs indexados.
 */
export async function listDocuments() {
  const res = await fetch(`${API_BASE_URL}/documents`);
  if (!res.ok) throw new Error('Error al obtener la lista de documentos');
  return await res.json();
}

/**
 * Sube un archivo PDF al backend y procesa su reindexación.
 */
export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Error en la subida' }));
    throw new Error(errorData.detail || 'Error al subir el archivo');
  }

  return await res.json();
}

/**
 * Envía un mensaje con streaming en tiempo real usando Server-Sent Events (SSE).
 * 
 * @param {string} message - Pregunta del usuario
 * @param {Array} history - Historial de mensajes previos
 * @param {Function} onToken - Callback para cada token recibido
 * @param {Function} onError - Callback ante errores
 * @param {Function} onDone - Callback al finalizar el streaming
 */
export async function sendMessageStream(message, history, onToken, onError, onDone) {
  try {
    const formattedHistory = history.map(h => ({
      role: h.role,
      content: h.content
    }));

    const response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        history: formattedHistory,
      }),
    });

    if (!response.ok) {
      throw new Error(`Error en el servidor: ${response.status} ${response.statusText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop(); // Mantener fragmentos incompletos en el buffer

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || !trimmed.startsWith('data:')) continue;

        const dataStr = trimmed.replace(/^data:\s*/, '');
        if (dataStr === '[DONE]') {
          if (onDone) onDone();
          return;
        }

        try {
          const parsed = JSON.parse(dataStr);
          if (parsed.error) {
            if (onError) onError(new Error(parsed.error));
            return;
          }
          if (parsed.token !== undefined && onToken) {
            onToken(parsed.token);
          }
        } catch (e) {
          // Si no es JSON puro, emitir el texto crudo
          if (onToken) onToken(dataStr);
        }
      }
    }

    if (onDone) onDone();
  } catch (error) {
    console.error('[API] Error en el streaming:', error);
    if (onError) onError(error);
  }
}
