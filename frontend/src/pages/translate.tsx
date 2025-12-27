import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';
import styles from './translate.module.css';

export default function TranslateContent() {
  const [content, setContent] = useState('');
  const [translatedContent, setTranslatedContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [cached, setCached] = useState(false);

  const handleTranslate = async () => {
    if (!content.trim()) {
      setError('Please enter some content to translate');
      return;
    }

    setLoading(true);
    setError('');
    setTranslatedContent('');
    setCached(false);

    try {
      const API_URL = process.env.NODE_ENV === 'production'
        ? 'https://asma-yaseen-hackathon-book-api.hf.space/api'
        : 'http://localhost:8000/api';

      const response = await fetch(`${API_URL}/translate/urdu`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: content,
          target_lang: 'ur',
          preserve_code: true
        })
      });

      if (!response.ok) {
        throw new Error('Failed to translate content');
      }

      const data = await response.json();
      setTranslatedContent(data.translated);
      setCached(data.cached || false);
    } catch (err) {
      console.error('Translation error:', err);
      if (err instanceof TypeError && err.message.includes('fetch')) {
        setError('Cannot connect to server. Make sure backend is running on port 8000.');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to translate content');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setContent('');
    setTranslatedContent('');
    setError('');
    setCached(false);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(translatedContent);
    alert('Translation copied to clipboard!');
  };

  return (
    <Layout
      title="Urdu Translation"
      description="Translate content to Urdu"
    >
      <div className={styles.container}>
        <div className={styles.header}>
          <h1>🌐 Urdu Translation</h1>
          <p className={styles.subtitle}>
            Translate your learning content to Urdu while preserving code and technical terms
          </p>
        </div>

        <div className={styles.mainContent}>
          <div className={styles.inputSection}>
            <div className={styles.sectionHeader}>
              <h2>English Content</h2>
              <span className={styles.badge}>EN</span>
            </div>
            <textarea
              className={styles.textArea}
              placeholder="Enter the content you want to translate to Urdu..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={15}
              dir="ltr"
            />
            <div className={styles.buttonGroup}>
              <button
                onClick={handleTranslate}
                disabled={loading || !content.trim()}
                className={styles.primaryButton}
              >
                {loading ? '⏳ Translating...' : '🌐 Translate to Urdu'}
              </button>
              <button
                onClick={handleReset}
                disabled={loading}
                className={styles.secondaryButton}
              >
                🔄 Reset
              </button>
            </div>
          </div>

          {error && (
            <div className={styles.errorBox}>
              ❌ {error}
            </div>
          )}

          {translatedContent && (
            <div className={styles.resultSection}>
              <div className={styles.sectionHeader}>
                <h2>Urdu Translation</h2>
                <div className={styles.badgeGroup}>
                  <span className={styles.badge}>UR</span>
                  {cached && <span className={styles.cacheBadge}>📦 Cached</span>}
                </div>
              </div>

              <div className={styles.translatedText} dir="rtl">
                <pre>{translatedContent}</pre>
              </div>

              <div className={styles.actionButtons}>
                <button onClick={handleCopy} className={styles.copyButton}>
                  📋 Copy Translation
                </button>
              </div>

              <div className={styles.infoBox}>
                ℹ️ <strong>Note:</strong> Code blocks, technical terms (ROS 2, URDF, Gazebo, API, Docker, Kubernetes),
                and markdown formatting are automatically preserved during translation.
              </div>
            </div>
          )}
        </div>

        <div className={styles.features}>
          <h3>✨ Translation Features</h3>
          <div className={styles.featureGrid}>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🔒</div>
              <h4>Code Protection</h4>
              <p>Code blocks remain untouched</p>
            </div>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🔧</div>
              <h4>Technical Terms</h4>
              <p>Preserves technical terminology</p>
            </div>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>⚡</div>
              <h4>Fast & Cached</h4>
              <p>30-day translation cache</p>
            </div>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🎯</div>
              <h4>Context-Aware</h4>
              <p>Maintains educational context</p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
