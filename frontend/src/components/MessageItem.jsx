import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot, User, Copy, Check } from 'lucide-react';

export default function MessageItem({ message, isStreamingMessage }) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      {!isUser && (
        <div className="avatar avatar-bot">
          <Bot size={20} />
        </div>
      )}

      <div className="message-bubble">
        {isUser ? (
          <div>{message.content}</div>
        ) : (
          <div>
            <div className="markdown-body">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>
              {isStreamingMessage && <span className="streaming-cursor"></span>}
            </div>

            {!isStreamingMessage && message.content && (
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '10px' }}>
                <button
                  onClick={handleCopy}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#94a3b8',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    fontSize: '0.75rem',
                    padding: '4px 8px',
                    borderRadius: '4px'
                  }}
                  title="Copiar respuesta"
                >
                  {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
                  <span>{copied ? 'Copiado' : 'Copiar'}</span>
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="avatar avatar-user">
          <User size={20} />
        </div>
      )}
    </div>
  );
}
