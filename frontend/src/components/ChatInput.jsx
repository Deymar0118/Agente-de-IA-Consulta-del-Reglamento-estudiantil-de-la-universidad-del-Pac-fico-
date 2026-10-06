import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

export default function ChatInput({ onSendMessage, isStreaming }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [text]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    const trimmed = text.trim();
    if (!trimmed || isStreaming) return;
    onSendMessage(trimmed);
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  return (
    <div className="chat-input-wrapper">
      <div className="input-container">
        <textarea
          ref={textareaRef}
          className="chat-textarea"
          placeholder="Formula tu pregunta sobre la normativa estudiantil..."
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isStreaming}
        />
        <button
          className="send-btn"
          onClick={handleSubmit}
          disabled={!text.trim() || isStreaming}
          title="Enviar pregunta"
        >
          {isStreaming ? (
            <Loader2 size={18} className="spin-animation" />
          ) : (
            <Send size={18} />
          )}
        </button>
      </div>
    </div>
  );
}
