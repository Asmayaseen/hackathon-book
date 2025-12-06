import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import styles from './labs.module.css';

export default function Labs() {
  return (
    <Layout
      title="Robotics Labs"
      description="Hands-on robotics labs and experiments for Physical AI"
    >
      <main>
        <section className={styles.hero}>
          <div className={styles.container}>
            <h1>🔬 Robotics Labs</h1>
            <p className={styles.subtitle}>
              Hands-on experiments and practical labs for mastering Physical AI and Humanoid Robotics
            </p>
          </div>
        </section>

        <section className={styles.labsSection}>
          <div className={styles.container}>
            <div className={styles.labsGrid}>

              {/* ROS 2 Labs */}
              <div className={styles.labCard}>
                <div className={styles.labIcon}>🤖</div>
                <h3>ROS 2 Fundamentals Labs</h3>
                <p>Hands-on practice with nodes, topics, services, and real-time robot control</p>
                <ul className={styles.labList}>
                  <li>✓ Build your first ROS 2 node</li>
                  <li>✓ Publisher-Subscriber communication</li>
                  <li>✓ Service and Action servers</li>
                  <li>✓ URDF robot modeling</li>
                </ul>
                <Link to="/docs/module-01-ros2/intro" className={styles.labButton}>
                  Start Labs →
                </Link>
              </div>

              {/* Simulation Labs */}
              <div className={styles.labCard}>
                <div className={styles.labIcon}>🌐</div>
                <h3>Simulation Labs</h3>
                <p>Create and test robots in Gazebo and Unity virtual environments</p>
                <ul className={styles.labList}>
                  <li>✓ Gazebo world creation</li>
                  <li>✓ Physics simulation setup</li>
                  <li>✓ Sensor integration (LiDAR, Camera, IMU)</li>
                  <li>✓ Unity Robotics Hub</li>
                </ul>
                <Link to="/docs/module-02-simulation/intro" className={styles.labButton}>
                  Start Labs →
                </Link>
              </div>

              {/* Isaac Labs */}
              <div className={styles.labCard}>
                <div className={styles.labIcon}>🧠</div>
                <h3>NVIDIA Isaac Labs</h3>
                <p>Advanced AI robotics with Isaac Sim and synthetic data generation</p>
                <ul className={styles.labList}>
                  <li>✓ Isaac Sim environment setup</li>
                  <li>✓ Synthetic data generation</li>
                  <li>✓ VSLAM and perception pipelines</li>
                  <li>✓ Nav2 navigation stack</li>
                </ul>
                <Link to="/docs/module-03-isaac/intro" className={styles.labButton}>
                  Start Labs →
                </Link>
              </div>

              {/* VLA Labs */}
              <div className={styles.labCard}>
                <div className={styles.labIcon}>💬</div>
                <h3>Vision-Language-Action Labs</h3>
                <p>Integrate LLMs with robotics for conversational and multimodal interaction</p>
                <ul className={styles.labList}>
                  <li>✓ Voice-to-action with Whisper</li>
                  <li>✓ LLM task planning</li>
                  <li>✓ Gesture recognition</li>
                  <li>✓ Multimodal perception</li>
                </ul>
                <Link to="/docs/module-04-vla/intro" className={styles.labButton}>
                  Start Labs →
                </Link>
              </div>

            </div>
          </div>
        </section>

        {/* Hardware Labs */}
        <section className={styles.hardwareLabs}>
          <div className={styles.container}>
            <h2>💻 Hardware Lab Setups</h2>
            <p className={styles.subtitle}>
              Choose your hardware configuration for hands-on Physical AI experiments
            </p>
            <div className={styles.setupGrid}>

              <div className={styles.setupCard}>
                <h3>🖥️ Full Workstation Lab</h3>
                <p>Complete local setup for maximum performance</p>
                <ul>
                  <li>NVIDIA RTX 4070 Ti+ GPU</li>
                  <li>64GB RAM, Ubuntu 22.04</li>
                  <li>Local Isaac Sim</li>
                  <li>Zero latency</li>
                </ul>
              </div>

              <div className={styles.setupCard}>
                <h3>☁️ Hybrid Cloud Lab</h3>
                <p>Best balance of cost and capability</p>
                <ul>
                  <li>Jetson Orin Nano edge device</li>
                  <li>Cloud GPU for simulation</li>
                  <li>RealSense camera</li>
                  <li>Production-ready workflow</li>
                </ul>
              </div>

              <div className={styles.setupCard}>
                <h3>🌐 Cloud-Only Lab</h3>
                <p>Browser-based learning, no local hardware</p>
                <ul>
                  <li>AWS/Azure GPU instances</li>
                  <li>Remote Isaac Sim access</li>
                  <li>Budget-friendly OpEx model</li>
                  <li>Simulation-focused learning</li>
                </ul>
              </div>

            </div>
          </div>
        </section>

        <section className={styles.cta}>
          <div className={styles.container}>
            <h2>Ready to Get Hands-On?</h2>
            <p>Start with Module 1 labs and build your way to advanced Physical AI</p>
            <Link to="/docs/intro" className={styles.ctaButton}>
              Begin Learning →
            </Link>
          </div>
        </section>

      </main>
    </Layout>
  );
}
