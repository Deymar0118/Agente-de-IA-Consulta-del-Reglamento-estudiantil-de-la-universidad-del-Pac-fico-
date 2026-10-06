import React, { useEffect, useRef } from 'react';
import MessageItem from './MessageItem';
import { BookOpen, HelpCircle } from 'lucide-react';

export default function ChatContainer({ messages, isStreaming, currentStreamMessage, onSelectQuestion }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentStreamMessage]);

  const hasMessages = messages.length > 0 || isStreaming;

  return (
    <div className="chat-messages">
      {!hasMessages ? (
        <div className="welcome-hero">
          <div className="welcome-icon">
            <BookOpen size={32} />
          </div>
          <h2>¿En qué puedo orientarte hoy?</h2>
          <p>
            Escribe cualquier duda sobre deberes, derechos, matrículas, exámenes, faltas o procesos disciplinarios según el Reglamento Estudiantil Oficial.
          </p>

          <div style={{ marginTop: '28px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button
              className="quick-question-btn"
              style={{ background: '#ffffff', color: '#1e293b', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}
              onClick={() => onSelectQuestion('¿Con cuántas faltas pierdo una materia por inasistencia?')}
            >
              <HelpCircle size={16} color="#0284c7" />
              <span>¿Con cuántas faltas pierdo una materia por inasistencia?</span>
            </button>
            <button
              className="quick-question-btn"
              style={{ background: '#ffffff', color: '#1e293b', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}
              onClick={() => onSelectQuestion('¿Cómo se solicita un segundo calificador y qué plazo hay?')}
            >
              <HelpCircle size={16} color="#0284c7" />
              <span>¿Cómo se solicita un segundo calificador y qué plazo hay?</span>
            </button>
          </div>
        </div>
      ) : (
        <>
          {messages.map((msg, index) => (
            <MessageItem key={index} message={msg} isStreamingMessage={false} />
          ))}

          {isStreaming && (
            <MessageItem
              message={{
                role: 'assistant',
                content: currentStreamMessage || 'Consultando el reglamento...',
              }}
              isStreamingMessage={true}
            />
          )}
          <div ref={bottomRef} />
        </>
      )}
    </div>
  );
}
