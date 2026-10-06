import React from 'react';
import { Bot, Sparkles, Upload, RefreshCw, FileText } from 'lucide-react';

export default function Header({ isOnline, isStreaming, onOpenDocModal }) {
  return (
    <header className="chat-header">
      <div className="header-info">
        <h2 className="header-title">Orientador Normativo IA</h2>
        <div className={`status-badge ${isOnline ? 'online' : 'offline'}`}>
          <span className={`status-dot ${isOnline ? 'pulse' : ''}`}></span>
          <span>{isOnline ? 'Reglamento Activo' : 'Desconectado'}</span>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <button
          className="action-btn action-btn-secondary"
          onClick={onOpenDocModal}
          style={{ padding: '8px 14px', fontSize: '0.82rem' }}
          title="Gestionar documentos del reglamento"
        >
          <FileText size={16} />
          <span>Normativa PDF</span>
        </button>
      </div>
    </header>
  );
}
