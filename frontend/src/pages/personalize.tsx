import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import styles from './personalize.module.css';

export default function Personalize() {
  return (
    <Layout
      title="Personalize Your Learning"
      description="Customize your Physical AI learning journey"
    >
      <main>
        <section className={styles.hero}>
          <div className={styles.container}>
            <h1>🎯 Personalize Your Learning</h1>
            <p className={styles.subtitle}>
              Tailor your Physical AI learning experience based on your background, goals, and hardware
            </p>
          </div>
        </section>

        <section className={styles.profileSection}>
          <div className={styles.container}>
            <h2>Choose Your Learning Path</h2>
            <div className={styles.profileGrid}>

              <div className={styles.profileCard}>
                <div className={styles.profileIcon}>🎓</div>
                <h3>Undergraduate</h3>
                <p>New to robotics? Start with fundamentals and build your way up.</p>
                <ul className={styles.featureList}>
                  <li>✓ Step-by-step tutorials</li>
                  <li>✓ Extensive code examples</li>
                  <li>✓ Simplified explanations</li>
                  <li>✓ Guided projects</li>
                </ul>
                <Link to="/signup?profile=undergraduate" className={styles.selectButton}>
                  Choose This Path
                </Link>
              </div>

              <div className={styles.profileCard}>
                <div className={styles.profileIcon}>🔬</div>
                <h3>Graduate</h3>
                <p>Advanced topics, research papers, and cutting-edge techniques.</p>
                <ul className={styles.featureList}>
                  <li>✓ Research paper references</li>
                  <li>✓ Advanced algorithms</li>
                  <li>✓ Optimization techniques</li>
                  <li>✓ Academic rigor</li>
                </ul>
                <Link to="/signup?profile=graduate" className={styles.selectButton}>
                  Choose This Path
                </Link>
              </div>

              <div className={styles.profileCard}>
                <div className={styles.profileIcon}>💼</div>
                <h3>Professional</h3>
                <p>Industry best practices and production deployment.</p>
                <ul className={styles.featureList}>
                  <li>✓ Production-ready code</li>
                  <li>✓ Industry standards</li>
                  <li>✓ Scalability patterns</li>
                  <li>✓ Deployment strategies</li>
                </ul>
                <Link to="/signup?profile=professional" className={styles.selectButton}>
                  Choose This Path
                </Link>
              </div>

            </div>
          </div>
        </section>

        <section className={styles.cta}>
          <div className={styles.container}>
            <h2>Start Your Personalized Journey</h2>
            <p>Create an account to unlock personalized learning and AI assistance</p>
            <div className={styles.ctaButtons}>
              <Link to="/signup" className={styles.ctaPrimary}>
                Sign Up Now
              </Link>
              <Link to="/docs/intro" className={styles.ctaSecondary}>
                Browse Content First
              </Link>
            </div>
          </div>
        </section>

      </main>
    </Layout>
  );
}
