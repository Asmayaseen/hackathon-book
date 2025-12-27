import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';
import styles from './personalize-content.module.css';

interface UserProfile {
  software_experience: string;
  hardware_experience: string;
  name: string;
}

export default function PersonalizeContent() {
  const [content, setContent] = useState('');
  const [personalizedContent, setPersonalizedContent] = useState('');
  const [adjustments, setAdjustments] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);

  // Load user profile from localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const user = JSON.parse(storedUser);
        setUserProfile(user);
      } catch (e) {
        console.error('Failed to parse user data:', e);
      }
    }
  }, []);

  const handlePersonalize = async () => {
    if (!content.trim()) {
      setError('Please enter some content to personalize');
      return;
    }

    setLoading(true);
    setError('');
    setPersonalizedContent('');
    setAdjustments([]);

    try {
      const API_URL = process.env.NODE_ENV === 'production'
        ? 'https://hackathon-book-api.onrender.com/api'
        : 'http://localhost:8000/api';

      // Use user profile if available, otherwise use defaults
      const softwareExp = userProfile?.software_experience || 'intermediate';
      const hardwareExp = userProfile?.hardware_experience || 'intermediate';

      const response = await fetch(`${API_URL}/personalize/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: content,
          software_experience: softwareExp,
          hardware_experience: hardwareExp
        })
      });

      if (!response.ok) {
        throw new Error('Failed to personalize content');
      }

      const data = await response.json();
      setPersonalizedContent(data.personalized_content);
      setAdjustments(data.adjustments_made || []);
    } catch (err) {
      console.error('Personalization error:', err);
      if (err instanceof TypeError && err.message.includes('fetch')) {
        setError('Cannot connect to server. Make sure backend is running on port 8000.');
      } else {
        setError(err instanceof Error ? err.message : 'Failed to personalize content');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setContent('');
    setPersonalizedContent('');
    setAdjustments([]);
    setError('');
  };

  return (
    <Layout
      title="Personalize Content"
      description="Get content adapted to your experience level"
    >
      <div className={styles.container}>
        <div className={styles.header}>
          <h1>🎯 Personalize Your Learning Content</h1>
          <p className={styles.subtitle}>
            Content will be adapted based on your {userProfile ? 'profile' : 'selected experience level'}
          </p>
          {userProfile && (
            <div className={styles.profileBadge}>
              <span>👤 {userProfile.name}</span>
              <span>💻 Software: {userProfile.software_experience}</span>
              <span>🤖 Hardware: {userProfile.hardware_experience}</span>
            </div>
          )}
          {!userProfile && (
            <div className={styles.warningBadge}>
              ⚠️ Not logged in. Default experience level (intermediate) will be used.
              <a href="/signin"> Sign in</a> for personalized experience.
            </div>
          )}
        </div>

        <div className={styles.mainContent}>
          <div className={styles.inputSection}>
            <h2>Original Content</h2>
            <textarea
              className={styles.textArea}
              placeholder="Paste the chapter content you want to personalize here..."
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows={15}
            />
            <div className={styles.buttonGroup}>
              <button
                onClick={handlePersonalize}
                disabled={loading || !content.trim()}
                className={styles.primaryButton}
              >
                {loading ? '⏳ Personalizing...' : '✨ Personalize Content'}
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

          {personalizedContent && (
            <div className={styles.resultSection}>
              <h2>Personalized Content</h2>

              {adjustments.length > 0 && (
                <div className={styles.adjustmentsBox}>
                  <h3>📝 Adjustments Made:</h3>
                  <ul>
                    {adjustments.map((adjustment, idx) => (
                      <li key={idx}>{adjustment}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className={styles.personalizedText}>
                <pre>{personalizedContent}</pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
