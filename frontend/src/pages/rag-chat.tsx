import React, { useState, useRef, useEffect } from 'react';
import Layout from '@theme/Layout';
import styles from './chatbot.module.css';
import { chatService, ChatMessage } from '../services/chatService';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: any[];
}

export default function RAGChat(): React.ReactElement {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    const query = input;
    setInput('');
    setLoading(true);

    try {
      // Use the working chatService (same as navbar ChatWidget)
      const response = await chatService.query({
        query: query,
        conversation_id: conversationId || undefined,
      });

      // Update conversation ID
      setConversationId(response.conversation_id);

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
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

  return (
    <Layout
      title="RAG Chat"
      description="Chat with your documents using RAG"
    >
      <div className={styles.chatContainer}>
        <div className={styles.chatHeader}>
          <h1>📚 AI Tutor - RAG Chat</h1>
          <p className={styles.subtitle}>Ask questions about Physical AI & Humanoid Robotics</p>
        </div>

        <div className={styles.messagesContainer}>
          {messages.length === 0 ? (
            <div className={styles.emptyState}>
              <h2>👋 Welcome to AI Tutor!</h2>
              <p>Ask me anything about ROS 2, Gazebo, NVIDIA Isaac, or VLA!</p>
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
                          <strong>Source {sidx + 1}:</strong> {source.module} - {source.chapter}
                          <a href={source.url} target="_blank" rel="noopener noreferrer">View Source</a>
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
            placeholder="Ask a question about Physical AI & Robotics..."
            className={styles.input}
            rows={3}
            disabled={loading}
          />
          <button
            onClick={handleSendMessage}
            disabled={loading || !input.trim()}
            className={styles.sendButton}
          >
            {loading ? '⏳' : '🚀'} Send
          </button>
        </div>
      </div>
    </Layout>
  );
}
