import React, { JSX, useState } from 'react';
import Navbar from '@theme-original/Navbar';
import type NavbarType from '@theme/Navbar';
import type { WrapperProps } from '@docusaurus/types';
import styles from './styles.module.css';

type Props = WrapperProps<typeof NavbarType>;

export default function NavbarWrapper(props: Props): JSX.Element {
  const [user, setUser] = useState<any>(() => {
    if (typeof window !== 'undefined') {
      const userData = localStorage.getItem('user');
      return userData ? JSON.parse(userData) : null;
    }
    return null;
  });

  const [loading, setLoading] = useState(false);

  const handlePersonalize = async () => {
    if (!user) {
      alert('Please sign in to personalize content');
      window.location.href = '/hackathon-book/signin';
      return;
    }

    setLoading(true);
    try {
      const contentElement = document.querySelector('.markdown');
      if (!contentElement) {
        alert('No content found to personalize');
        return;
      }

      const pageContent = contentElement.textContent || '';

      const API_URL = process.env.NODE_ENV === 'production'
        ? 'https://hackathon-book-api.onrender.com/api'
        : 'http://172.24.5.28:8000/api';

      const token = localStorage.getItem('token');
      const response = await fetch(`${API_URL}/personalize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          content: pageContent,
          software_experience: user.software_experience,
          hardware_experience: user.hardware_experience
        })
      });

      if (!response.ok) throw new Error('Personalization failed');

      const data = await response.json();
      contentElement.innerHTML = data.personalized_content;
      alert('✨ Content personalized for your experience level!');
    } catch (error) {
      console.error('Personalization error:', error);
      alert('Personalization failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTranslate = async () => {
    setLoading(true);
    try {
      const contentElement = document.querySelector('.markdown');
      if (!contentElement) {
        alert('No content found to translate');
        return;
      }

      const pageContent = contentElement.textContent || '';

      const API_URL = process.env.NODE_ENV === 'production'
        ? 'https://hackathon-book-api.onrender.com/api'
        : 'http://172.24.5.28:8000/api';

      const response = await fetch(`${API_URL}/translate/urdu`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: pageContent,
          target_lang: 'ur',
          preserve_code: true
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Translation failed');
      }

      const data = await response.json();
      contentElement.innerHTML = data.translated;
      contentElement.style.direction = 'rtl';
      contentElement.style.textAlign = 'right';
      alert('🌐 Content translated to Urdu!');
    } catch (error) {
      console.error('Translation error:', error);
      alert('Translation failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar {...props} />
      <div className={styles.navbarControls}>
        <button
          onClick={handlePersonalize}
          disabled={loading}
          className={styles.personalizeBtn}
          title="Personalize content based on your experience level"
        >
          {loading ? '⏳' : '⚡ Personalize'}
        </button>
        <button
          onClick={handleTranslate}
          disabled={loading}
          className={styles.translateBtn}
          title="Translate to Urdu"
        >
          {loading ? '⏳' : '🌐 اردو'}
        </button>
      </div>
    </>
  );
}
