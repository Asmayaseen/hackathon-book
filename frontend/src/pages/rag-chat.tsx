import React, { useState, useRef, useEffect } from 'react';
import Layout from '@theme/Layout';
import styles from './chatbot.module.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

interface Source {
  content: string;
  source: string;
  metadata: any;
}

export default function RAGChat(): React.ReactElement {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [ragStatus, setRagStatus] = useState<any>(null);
  const [uploadingFile, setUploadingFile] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const API_BASE = process.env.NODE_ENV === 'production'
    ? 'https://your-backend-url.com/api'
    : 'http://localhost:8000/api';

  // Fetch RAG system status on mount
  useEffect(() => {
    fetchRagStatus();
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchRagStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/rag/status`);
      const data = await response.json();
      setRagStatus(data);
    } catch (error) {
      console.error('Error fetching RAG status:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/rag/chat/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: input,
          k: 4,
          model: 'gpt-3.5-turbo',
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['.pdf', '.txt', '.md'];
    const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

    if (!allowedTypes.includes(fileExt)) {
      alert(`Unsupported file type. Allowed: ${allowedTypes.join(', ')}`);
      return;
    }

    setUploadingFile(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE}/rag/ingest/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload file');
      }

      const data = await response.json();
      alert(`File uploaded successfully!\nDocuments: ${data.documents_loaded}\nChunks: ${data.chunks_created}`);

      // Refresh status
      await fetchRagStatus();

    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload file. Please try again.');
    } finally {
      setUploadingFile(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <Layout
      title="RAG Chat"
      description="Chat with your documents using RAG"
    >
      <div className={styles.chatContainer}>
        <div className={styles.chatHeader}>
          <h1>📚 RAG Document Chat</h1>
          {ragStatus && (
            <div className={styles.statusBadge}>
              <span className={ragStatus.is_initialized ? styles.statusGreen : styles.statusRed}>
                {ragStatus.is_initialized ? '● Ready' : '● Not Initialized'}
              </span>
              {ragStatus.vectorstore_stats?.total_vectors > 0 && (
                <span className={styles.statusInfo}>
                  {ragStatus.vectorstore_stats.total_vectors} chunks indexed
                </span>
              )}
            </div>
          )}
        </div>

        <div className={styles.uploadSection}>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt,.md"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className={styles.uploadButton}
            disabled={uploadingFile}
          >
            {uploadingFile ? '⏳ Uploading...' : '📄 Upload Document'}
          </button>
          <small>Supported: PDF, TXT, MD</small>
        </div>

        <div className={styles.messagesContainer}>
          {messages.length === 0 ? (
            <div className={styles.emptyState}>
              <h2>👋 Welcome to RAG Chat!</h2>
              <p>Upload documents and ask questions about them.</p>
              <div className={styles.suggestions}>
                <h3>Try asking:</h3>
                <button onClick={() => setInput('What is ROS 2?')} className={styles.suggestionButton}>
                  "What is ROS 2?"
                </button>
                <button onClick={() => setInput('Explain Isaac Sim')} className={styles.suggestionButton}>
                  "Explain Isaac Sim"
                </button>
                <button onClick={() => setInput('How does SLAM work?')} className={styles.suggestionButton}>
                  "How does SLAM work?"
                </button>
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`${styles.message} ${styles[msg.role]}`}>
                <div className={styles.messageContent}>
                  {msg.content}
                </div>
                {msg.sources && msg.sources.length > 0 && (
                  <details className={styles.sources}>
                    <summary>📖 Sources ({msg.sources.length})</summary>
                    <div className={styles.sourcesList}>
                      {msg.sources.map((source, sidx) => (
                        <div key={sidx} className={styles.source}>
                          <strong>Source {sidx + 1}:</strong> {source.source}
                          <p>{source.content.substring(0, 200)}...</p>
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>
            ))
          )}
          {loading && (
            <div className={`${styles.message} ${styles.assistant}`}>
              <div className={styles.loadingDots}>
                <span>●</span><span>●</span><span>●</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className={styles.inputContainer}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about your documents..."
            className={styles.input}
            rows={3}
            disabled={loading || !ragStatus?.is_initialized}
          />
          <button
            onClick={handleSendMessage}
            disabled={loading || !input.trim() || !ragStatus?.is_initialized}
            className={styles.sendButton}
          >
            {loading ? '⏳' : '🚀'} Send
          </button>
        </div>
      </div>
    </Layout>
  );
}
