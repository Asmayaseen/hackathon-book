import React, { useState } from 'react';
import Layout from '@theme/Layout';
import styles from './auth.module.css';

export default function Signup() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    softwareExperience: 'beginner',
    hardwareExperience: 'beginner',
    learningGoal: ''
  });

  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    try {
      const API_URL = process.env.NODE_ENV === 'production'
        ? 'https://hackathon-book-api.onrender.com/api'
        : 'http://localhost:8000/api';

      const response = await fetch(`${API_URL}/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          password: formData.password.substring(0, 72),
          software_experience: formData.softwareExperience,
          hardware_experience: formData.hardwareExperience,
          learning_goal: formData.learningGoal
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Signup failed');
      }

      setSuccess(true);
      setTimeout(() => {
        window.location.href = '/signin';
      }, 2000);
    } catch (err) {
      console.error('Signup error:', err);
      if (err instanceof TypeError && err.message.includes('fetch')) {
        setError('Cannot connect to server. Make sure backend is running on port 8000.');
      } else {
        setError(err instanceof Error ? err.message : 'Signup failed');
      }
    }
  };

  return (
    <Layout title="Sign Up" description="Create your account">
      <div className={styles.authContainer}>
        <div className={styles.authCard}>
          <h1>Create Account</h1>
          <p className={styles.subtitle}>Join Physical AI & Humanoid Robotics learning community</p>

          {error && <div className={styles.error}>{error}</div>}
          {success && <div className={styles.success}>Account created! Redirecting to login...</div>}

          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.formGroup}>
              <label htmlFor="name">Full Name *</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder="Enter your full name"
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="email">Email *</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="your.email@example.com"
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="password">Password *</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                minLength={8}
                placeholder="Minimum 8 characters"
              />
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="confirmPassword">Confirm Password *</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                placeholder="Re-enter your password"
              />
            </div>

            <div className={styles.divider}>
              <span>Background Information</span>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="softwareExperience">Software Programming Experience *</label>
              <select
                id="softwareExperience"
                name="softwareExperience"
                value={formData.softwareExperience}
                onChange={handleChange}
                required
              >
                <option value="beginner">Beginner - New to programming</option>
                <option value="intermediate">Intermediate - Some Python/C++ experience</option>
                <option value="advanced">Advanced - Professional developer</option>
              </select>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="hardwareExperience">Hardware/Robotics Experience *</label>
              <select
                id="hardwareExperience"
                name="hardwareExperience"
                value={formData.hardwareExperience}
                onChange={handleChange}
                required
              >
                <option value="beginner">Beginner - No robotics experience</option>
                <option value="intermediate">Intermediate - Some Arduino/Raspberry Pi work</option>
                <option value="advanced">Advanced - Built robots before</option>
              </select>
            </div>

            <div className={styles.formGroup}>
              <label htmlFor="learningGoal">What do you want to learn? *</label>
              <textarea
                id="learningGoal"
                name="learningGoal"
                value={formData.learningGoal}
                onChange={handleChange}
                required
                rows={3}
                placeholder="E.g., Build humanoid robots, work in robotics industry, research AI..."
              />
            </div>

            <button type="submit" className={styles.submitBtn}>
              Create Account
            </button>

            <p className={styles.switchLink}>
              Already have an account? <a href="/signin">Sign In</a>
            </p>
          </form>
        </div>
      </div>
    </Layout>
  );
}
