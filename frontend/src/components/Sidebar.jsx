import React from 'react';
import { BookOpen, HelpCircle, PlusCircle, Sparkles, FileUp, GraduationCap } from 'lucide-react';

const SUGGESTED_QUESTIONS = [
  '¿Con cuántas faltas pierdo una materia por inasistencia?',
  '¿Cuál es la nota mínima para aprobar una asignatura?',
  '¿Cómo se solicita un segundo calificador?',
  '¿Cuáles son los requisitos para cancelar el semestre?',
  '¿Qué tipos de matrícula existen en la universidad?'
];

export default function Sidebar({ onSelectQuestion, onNewChat, onOpenDocModal, isStreaming }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo-badge">
          <GraduationCap size={24} />
        </div>
        <div className="sidebar-header-text">
          <h1>UniPacífico</h1>
          <p>Reglamento Estudiantil</p>
        </div>
      </div>

      <div className="sidebar-content">
        <div>
          <button 
            className="action-btn action-btn-primary" 
            onClick={onNewChat}
            disabled={isStreaming}
          >
            <PlusCircle size={18} />
            <span>Nueva Consulta</span>
          </button>
        </div>

        <div>
          <div className="sidebar-section-title">Consultas Frecuentes</div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {SUGGESTED_QUESTIONS.map((q, idx) => (
              <button
                key={idx}
                className="quick-question-btn"
                onClick={() => onSelectQuestion(q)}
                disabled={isStreaming}
              >
                <HelpCircle size={15} style={{ flexShrink: 0, opacity: 0.7 }} />
                <span>{q}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="sidebar-footer">
        <button
          className="action-btn action-btn-secondary"
          onClick={onOpenDocModal}
          disabled={isStreaming}
        >
          <FileUp size={16} />
          <span>Actualizar Reglamento</span>
        </button>
        <div style={{ fontSize: '0.72rem', color: '#64748b', textAlign: 'center', marginTop: '4px' }}>
          Acuerdo No. 029 (3 de Marzo de 2006)
        </div>
      </div>
    </aside>
  );
}
