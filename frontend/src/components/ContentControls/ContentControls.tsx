
/**
 * Content Controls Component
 * - Personalization Button (+50 points)
 * - Urdu Translation Button (+50 points)
 */

import React, { useState, useEffect } from 'react';
import styles from './ContentControls.module.css';

interface ContentControlsProps {
  contentId: string;
  originalContent: string;
}

export default function ContentControls({ contentId, originalContent }: ContentControlsProps) {
  const [user, setUser] = useState<any>(null);
  const [isPersonalized, setIsPersonalized] = useState(false);
  const [isTranslated, setIsTranslated] = useState(false);
  const [loading, setLoading] = useState(false);
  const [pageContent, setPageContent] = useState('');

  useEffect(() => {
    // Get user from localStorage
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    }

    // Extract actual page content from the DOM
    setTimeout(() => {
      const contentElement = document.querySelector('.markdown') ||
                            document.querySelector('article') ||
                            document.querySelector('.theme-doc-markdown');
      if (contentElement) {
        setPageContent(contentElement.innerHTML || contentElement.textContent || originalContent);
      }
    }, 1000);
  }, [originalContent]);

  const handlePersonalize = async () => {
    if (!user) {
      alert('Please sign in to personalize content');
      window.location.href = '/signin';
      return;
    }

    setLoading(true);
    try {
      const API_URL = process.env.NODE_ENV === 'production'
        ? 'https://hackathon-book-api.onrender.com/api'
        : 'http://localhost:8000/api';

      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/personalize/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          content: pageContent || originalContent,
          software_experience: user.software_experience,
          hardware_experience: user.hardware_experience
        })
      });

      if (!response.ok) throw new Error('Personalization failed');

      const data = await response.json();

      // Replace content on page
      const contentElement = document.querySelector('.markdown');
      if (contentElement) {
        contentElement.innerHTML = data.personalized_content;
        setIsPersonalized(true);
      }
    } catch (error) {
      console.error('Personalization error:', error);
      alert('Personalization failed. Using default content.');
    } finally {
      setLoading(false);
    }
  };

  const handleTranslate = async () => {
    setLoading(true);
    try {
      const API_URL = process.env.NODE_ENV === 'production'
        ? 'https://hackathon-book-api.onrender.com/api'
        : 'http://localhost:8000/api';

      const response = await fetch(`${API_URL}/translate/urdu`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: pageContent || originalContent,
          preserve_code: true
        })
      });

      if (!response.ok) throw new Error('Translation failed');

      const data = await response.json();

      // Replace content on page
      const contentElement = document.querySelector('.markdown');
      if (contentElement) {
        contentElement.innerHTML = data.translated;
        contentElement.style.direction = 'rtl';
        contentElement.style.textAlign = 'right';
        setIsTranslated(true);
      }
    } catch (error) {
      console.error('Translation error:', error);
      alert('Translation failed. Using English content.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    window.location.reload();
  };

  return (
    <div className={styles.controls}>
      <div className={styles.buttonGroup}>
        {!isPersonalized && !isTranslated && (
          <>
            <button
              onClick={handlePersonalize}
              disabled={loading}
              className={styles.personalizeBtn}
              title="Adjust content based on your experience level"
            >
              {loading ? '⏳ Personalizing...' : '⚡ Personalize for Me'}
            </button>

            <button
              onClick={handleTranslate}
              disabled={loading}
              className={styles.translateBtn}
              title="Translate to Urdu while preserving technical terms"
            >
              {loading ? '⏳ Translating...' : '🌐 Urdu Translation'}
            </button>
          </>
        )}

        {(isPersonalized || isTranslated) && (
          <button
            onClick={handleReset}
            className={styles.resetBtn}
          >
            ↺ Reset to Original
          </button>
        )}
      </div>

      {isPersonalized && (
        <div className={styles.badge}>
          ✨ Personalized for {user?.software_experience} level
        </div>
      )}

      {isTranslated && (
        <div className={styles.badge}>
          🌐 Urdu Translation (Technical terms preserved)
        </div>
      )}
    </div>
  );
}
