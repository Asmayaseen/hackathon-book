import React, { useState, useRef, useEffect } from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './chatbot.module.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Array<{
    module: string;
    chapter: string;
    url: string;
    relevance_score: number;
  }>;
  timestamp?: string;
}

export default function Chatbot() {
  const { siteConfig } = useDocusaurusContext();
  // Runtime detection: check if we're on GitHub Pages
  const isGitHubPages = typeof window !== 'undefined' && window.location.hostname.includes('github.io');
  const baseUrl = isGitHubPages ? '/hackathon-book/' : siteConfig.baseUrl;

  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI tutor for Physical AI & Humanoid Robotics. Ask me anything about ROS 2, Gazebo, NVIDIA Isaac, or VLA models!',
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const API_URL = process.env.NODE_ENV === 'production'
        ? 'https://asma-yaseen-hackathon-book-api.hf.space/api'
        : 'http://localhost:8000/api';

      const response = await fetch(`${API_URL}/chat/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: input,
          module_filter: null
        })
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        timestamp: data.timestamp
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chatbot error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure the backend server is running on port 8000.',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout title="AI Chatbot" description="Ask questions about Physical AI & Robotics">
      <div className={styles.chatContainer}>
        <div className={styles.chatHeader}>
          <h1>🤖 AI Tutor</h1>
          <p>Ask questions about the course content</p>
        </div>

        <div className={styles.messagesContainer}>
          {messages.map((message, index) => (
            <div
              key={index}
              className={`${styles.message} ${
                message.role === 'user' ? styles.userMessage : styles.assistantMessage
              }`}
            >
              <div className={styles.messageHeader}>
                <span className={styles.messageRole}>
                  {message.role === 'user' ? '👤 You' : '🤖 AI Tutor'}
                </span>
                {message.timestamp && (
                  <span className={styles.messageTime}>
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                )}
              </div>
              <div className={styles.messageContent}>
                {message.content}
              </div>
              {message.sources && message.sources.length > 0 && (
                <div className={styles.sources}>
                  <div className={styles.sourcesHeader}>📚 Sources:</div>
                  {message.sources.map((source, idx) => {
                    // Construct full path with baseUrl
                    const cleanUrl = source.url.startsWith('/') ? source.url.substring(1) : source.url;
                    const fullPath = `${baseUrl}${cleanUrl}`;
                    return (
                      <div key={idx} className={styles.source}>
                        <a
                          href={fullPath}
                          className={styles.sourceLink}
                        >
                          {source.module} - {source.chapter}
                        </a>
                        <span className={styles.relevance}>
                          {Math.round(source.relevance_score * 100)}% relevant
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className={`${styles.message} ${styles.assistantMessage}`}>
              <div className={styles.messageHeader}>
                <span className={styles.messageRole}>🤖 AI Tutor</span>
              </div>
              <div className={styles.loadingDots}>
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className={styles.inputForm}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about ROS 2, Gazebo, Isaac, VLA models..."
            className={styles.input}
            disabled={loading}
          />
          <button
            type="submit"
            className={styles.sendButton}
            disabled={loading || !input.trim()}
          >
            {loading ? '⏳' : '➤'}
          </button>
        </form>
      </div>
    </Layout>
  );
}
