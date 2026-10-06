import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatContainer from './components/ChatContainer';
import ChatInput from './components/ChatInput';
import DocumentModal from './components/DocumentModal';
import { checkHealth, sendMessageStream } from './services/api';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentStreamMessage, setCurrentStreamMessage] = useState('');
  const [isOnline, setIsOnline] = useState(true);
  const [isDocModalOpen, setIsDocModalOpen] = useState(false);

  // Verificar conexión con FastAPI al cargar
  useEffect(() => {
    const verificarSalud = async () => {
      const health = await checkHealth();
      setIsOnline(health.status === 'ok');
    };

    verificarSalud();
    const interval = setInterval(verificarSalud, 30000); // Cada 30 seg
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = async (text) => {
    if (!text.trim() || isStreaming) return;

    const userMessage = { role: 'user', content: text };
    const newMessagesHistory = [...messages, userMessage];
    setMessages(newMessagesHistory);
    setIsStreaming(true);
    setCurrentStreamMessage('');

    let accumulatedText = '';

    await sendMessageStream(
      text,
      messages,
      (token) => {
        accumulatedText += token;
        setCurrentStreamMessage(accumulatedText);
      },
      (error) => {
        console.error('Error durante streaming:', error);
        const errorMessage = {
          role: 'assistant',
          content: '❌ Ocurrió un inconveniente al consultar el asistente. Por favor, intenta de nuevo.'
        };
        setMessages([...newMessagesHistory, errorMessage]);
        setIsStreaming(false);
        setCurrentStreamMessage('');
      },
      () => {
        if (accumulatedText) {
          setMessages([...newMessagesHistory, { role: 'assistant', content: accumulatedText }]);
        }
        setIsStreaming(false);
        setCurrentStreamMessage('');
      }
    );
  };

  const handleNewChat = () => {
    setMessages([]);
    setCurrentStreamMessage('');
    setIsStreaming(false);
  };

  return (
    <div className="app-container">
      <Sidebar
        onSelectQuestion={handleSendMessage}
        onNewChat={handleNewChat}
        onOpenDocModal={() => setIsDocModalOpen(true)}
        isStreaming={isStreaming}
      />

      <main className="main-chat">
        <Header
          isOnline={isOnline}
          isStreaming={isStreaming}
          onOpenDocModal={() => setIsDocModalOpen(true)}
        />

        <ChatContainer
          messages={messages}
          isStreaming={isStreaming}
          currentStreamMessage={currentStreamMessage}
          onSelectQuestion={handleSendMessage}
        />

        <ChatInput
          onSendMessage={handleSendMessage}
          isStreaming={isStreaming}
        />
      </main>

      <DocumentModal
        isOpen={isDocModalOpen}
        onClose={() => setIsDocModalOpen(false)}
      />
    </div>
  );
}
