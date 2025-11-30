import React, { useState } from 'react';
import styles from './ChatWidget.module.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI assistant for Physical AI & Humanoid Robotics. Ask me anything about ROS 2, Gazebo, NVIDIA Isaac, or VLA models!'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    // Demo response (backend not connected yet)
    setTimeout(() => {
      const demoResponse: Message = {
        role: 'assistant',
        content: `Great question about "${input}"!

🔧 **Demo Mode Active** - Backend API not connected yet.

To activate full RAG functionality:
1. Deploy backend to Render
2. Add OpenAI API key
3. Seed Qdrant vector database
4. Update API_URL in frontend

**Example Answer**: This topic is covered in detail in Module 1 (ROS 2 Fundamentals). Check the sidebar for relevant chapters!

📚 **Related Modules**:
- Module 1: ROS 2 architecture
- Module 2: Gazebo simulation
- Module 3: NVIDIA Isaac
- Module 4: VLA integration`
      };
      setMessages(prev => [...prev, demoResponse]);
      setLoading(false);
    }, 1000);
  };

  return (
    <>
      {/* Chat Toggle Button */}
      <button
        className={styles.chatToggle}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle chat"
      >
        💬
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className={styles.chatWindow}>
          <div className={styles.chatHeader}>
            <h3>🤖 AI Assistant</h3>
            <button onClick={() => setIsOpen(false)}>✕</button>
          </div>

          <div className={styles.chatMessages}>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`${styles.message} ${styles[msg.role]}`}
              >
                <div className={styles.messageContent}>
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && (
              <div className={`${styles.message} ${styles.assistant}`}>
                <div className={styles.messageContent}>
                  <div className={styles.typing}>Thinking...</div>
                </div>
              </div>
            )}
          </div>

          <div className={styles.chatInput}>
            <input
              type="text"
              placeholder="Ask about ROS 2, Gazebo, Isaac..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            />
            <button onClick={handleSend} disabled={loading}>
              Send
            </button>
          </div>

          <div className={styles.chatFooter}>
            <small>Demo Mode - Full RAG available after deployment</small>
          </div>
        </div>
      )}
    </>
  );
}
