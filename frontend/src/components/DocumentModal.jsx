import React, { useState, useEffect } from 'react';
import { X, UploadCloud, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { listDocuments, uploadDocument } from '../services/api';

export default function DocumentModal({ isOpen, onClose }) {
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    if (isOpen) {
      cargarDocumentos();
      setFeedback(null);
    }
  }, [isOpen]);

  const cargarDocumentos = async () => {
    try {
      setLoadingDocs(true);
      const docs = await listDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingDocs(false);
    }
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setFeedback({ type: 'error', message: 'Solo se permiten archivos en formato PDF.' });
      return;
    }

    try {
      setUploading(true);
      setFeedback(null);
      const res = await uploadDocument(file);
      setFeedback({
        type: 'success',
        message: `${res.message} (${res.chunks_indexed} fragmentos indexados)`
      });
      cargarDocumentos();
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Error al subir el archivo.' });
    } finally {
      setUploading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Gestión del Reglamento Oficial</h3>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div>
          <label className="dropzone" style={{ display: 'block' }}>
            <input
              type="file"
              accept=".pdf"
              style={{ display: 'none' }}
              onChange={handleFileChange}
              disabled={uploading}
            />
            <div className="dropzone-icon">
              {uploading ? (
                <Loader2 size={36} className="spin-animation" style={{ margin: '0 auto' }} />
              ) : (
                <UploadCloud size={36} style={{ margin: '0 auto' }} />
              )}
            </div>
            <p style={{ fontWeight: 600, color: '#0f172a', marginBottom: '4px' }}>
              {uploading ? 'Procesando e indexando PDF en FAISS...' : 'Haz clic para subir una nueva versión del Reglamento'}
            </p>
            <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
              Formato admitido: PDF (Acuerdos, Resoluciones)
            </span>
          </label>

          {feedback && (
            <div
              style={{
                marginTop: '16px',
                padding: '12px 14px',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '0.86rem',
                backgroundColor: feedback.type === 'success' ? '#dcfce7' : '#fee2e2',
                color: feedback.type === 'success' ? '#15803d' : '#b91c1c',
              }}
            >
              {feedback.type === 'success' ? (
                <CheckCircle2 size={18} style={{ flexShrink: 0 }} />
              ) : (
                <AlertCircle size={18} style={{ flexShrink: 0 }} />
              )}
              <span>{feedback.message}</span>
            </div>
          )}

          <div style={{ marginTop: '24px' }}>
            <h4 style={{ fontSize: '0.88rem', color: '#64748b', marginBottom: '10px' }}>
              Documentos Activos en el Sistema
            </h4>
            {loadingDocs ? (
              <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Cargando lista...</p>
            ) : documents.length === 0 ? (
              <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>No hay documentos registrados.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {documents.map((doc, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '10px 14px',
                      background: '#f8fafc',
                      borderRadius: '8px',
                      border: '1px solid #e2e8f0',
                      fontSize: '0.85rem',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <FileText size={18} color="#0284c7" />
                      <span style={{ fontWeight: 600, color: '#1e293b' }}>{doc.filename}</span>
                    </div>
                    <span style={{ fontSize: '0.78rem', color: '#64748b' }}>
                      {(doc.size_bytes / 1024).toFixed(1)} KB
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
