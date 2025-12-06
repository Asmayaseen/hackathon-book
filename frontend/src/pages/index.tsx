import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import styles from './index.module.css';

export default function Home() {
  return (
    <Layout
      title="Physical AI & Humanoid Robotics"
      description="Master the Future of Embodied Intelligence - From ROS 2 to NVIDIA Isaac"
    >
      <main>
        {/* Hero Section */}
        <section className={styles.hero}>
          <div className={styles.heroContent}>
            <h1 className={styles.heroTitle}>
              Physical AI & Humanoid Robotics
            </h1>
            <p className={styles.heroSubtitle}>
              Master the Future of Embodied Intelligence - From ROS 2 to NVIDIA Isaac
            </p>

            {/* Technology Tags */}
            <div className={styles.techTags}>
              <span className={styles.tag}>ROS 2</span>
              <span className={styles.tag}>Isaac Sim</span>
              <span className={styles.tag}>Gazebo</span>
              <span className={styles.tag}>VLA Models</span>
            </div>

            <div className={styles.heroButtons}>
              <Link to="docs/intro" className={styles.ctaPrimary}>
                Get Started
              </Link>
              <Link to="docs/intro" className={styles.ctaSecondary}>
                Browse Content
              </Link>
            </div>
          </div>
        </section>

        {/* Why This Matters Section */}
        <section className={styles.whyMatters}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>🎯 Why This Matters</h2>
            <div className={styles.valueGrid}>
              <div className={styles.valueCard}>
                <div className={styles.valueIcon}>🤖</div>
                <h3>Embodied Intelligence</h3>
                <p>AI systems that understand and interact with the physical world, bridging digital and physical realms.</p>
              </div>
              <div className={styles.valueCard}>
                <div className={styles.valueIcon}>👥</div>
                <h3>Human-Centered Design</h3>
                <p>Humanoid robots excel in our world because they share our form and can learn from human environments.</p>
              </div>
              <div className={styles.valueCard}>
                <div className={styles.valueIcon}>⚡</div>
                <h3>Production-Ready Skills</h3>
                <p>Learn industry-standard tools: ROS 2, NVIDIA Isaac, and modern robotics frameworks used in production.</p>
              </div>
              <div className={styles.valueCard}>
                <div className={styles.valueIcon}>💬</div>
                <h3>Conversational Robotics</h3>
                <p>Integrate GPT models for natural language understanding and voice-driven robot control.</p>
              </div>
              <div className={styles.valueCard}>
                <div className={styles.valueIcon}>🔄</div>
                <h3>Sim-to-Real Transfer</h3>
                <p>Train in simulation with photorealistic environments, then deploy to real robots seamlessly.</p>
              </div>
              <div className={styles.valueCard}>
                <div className={styles.valueIcon}>🎓</div>
                <h3>Interactive Learning</h3>
                <p>Hands-on projects, browser-to-production workflow, and personalized learning paths.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Course Overview */}
        <section className={styles.overview}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>🎯 Course Overview</h2>
            <p className={styles.overviewText}>
              The future of AI extends beyond digital spaces into the physical world.
              This comprehensive course introduces <strong>Physical AI</strong>—AI systems
              that function in reality and comprehend physical laws. You'll learn to design,
              simulate, and deploy humanoid robots capable of natural human interactions.
            </p>
          </div>
        </section>

        {/* Modules Grid */}
        <section className={styles.modules}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>📚 Course Modules</h2>
            <div className={styles.moduleGrid}>

              {/* Module 1 */}
              <div className={styles.moduleCard}>
                <div className={styles.moduleIcon}>🤖</div>
                <h3>Module 1: ROS 2</h3>
                <p className={styles.moduleWeeks}>Weeks 3-5</p>
                <p className={styles.moduleDesc}>
                  Master the robotic nervous system - ROS 2 architecture, nodes,
                  topics, services, and real-time control.
                </p>
                <Link to="docs/module-01-ros2/intro" className={styles.moduleLink}>
                  Start Module →
                </Link>
              </div>

              {/* Module 2 */}
              <div className={styles.moduleCard}>
                <div className={styles.moduleIcon}>🌐</div>
                <h3>Module 2: Gazebo & Unity</h3>
                <p className={styles.moduleWeeks}>Weeks 6-7</p>
                <p className={styles.moduleDesc}>
                  Create digital twins with physics simulation, high-fidelity rendering,
                  and sensor simulation.
                </p>
                <Link to="docs/module-02-simulation/intro" className={styles.moduleLink}>
                  Start Module →
                </Link>
              </div>

              {/* Module 3 */}
              <div className={styles.moduleCard}>
                <div className={styles.moduleIcon}>🧠</div>
                <h3>Module 3: NVIDIA Isaac</h3>
                <p className={styles.moduleWeeks}>Weeks 8-10</p>
                <p className={styles.moduleDesc}>
                  Harness NVIDIA's robotics platform for photorealistic simulation,
                  synthetic data generation, and hardware-accelerated VSLAM.
                </p>
                <Link to="docs/module-03-isaac/intro" className={styles.moduleLink}>
                  Start Module →
                </Link>
              </div>

              {/* Module 4 */}
              <div className={styles.moduleCard}>
                <div className={styles.moduleIcon}>💬</div>
                <h3>Module 4: VLA Models</h3>
                <p className={styles.moduleWeeks}>Weeks 11-13</p>
                <p className={styles.moduleDesc}>
                  Connect language models to physical actions - voice-to-action,
                  cognitive planning, and conversational robotics.
                </p>
                <Link to="docs/module-04-vla/intro" className={styles.moduleLink}>
                  Start Module →
                </Link>
              </div>

            </div>
          </div>
        </section>

        {/* Learning Outcomes */}
        <section className={styles.outcomes}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>🎓 Learning Outcomes</h2>
            <div className={styles.outcomeGrid}>
              <div className={styles.outcome}>
                <span className={styles.checkmark}>✓</span>
                <span>Understand Physical AI principles and embodied intelligence</span>
              </div>
              <div className={styles.outcome}>
                <span className={styles.checkmark}>✓</span>
                <span>Master ROS 2 (Robot Operating System) for robotic control</span>
              </div>
              <div className={styles.outcome}>
                <span className={styles.checkmark}>✓</span>
                <span>Simulate robots with Gazebo and Unity</span>
              </div>
              <div className={styles.outcome}>
                <span className={styles.checkmark}>✓</span>
                <span>Develop with NVIDIA Isaac AI robot platform</span>
              </div>
              <div className={styles.outcome}>
                <span className={styles.checkmark}>✓</span>
                <span>Design humanoid robots for natural interactions</span>
              </div>
              <div className={styles.outcome}>
                <span className={styles.checkmark}>✓</span>
                <span>Integrate GPT models for conversational robotics</span>
              </div>
            </div>
          </div>
        </section>

        {/* Hardware Requirements */}
        <section className={styles.hardware}>
          <div className={styles.container}>
            <h2 className={styles.sectionTitle}>💻 Hardware Requirements</h2>
            <p className={styles.hardwareIntro}>
              Choose your deployment tier based on your budget and learning goals
            </p>
            <div className={styles.hardwareGrid}>
              {/* Full Workstation */}
              <div className={styles.hardwareCard}>
                <div className={styles.hardwareTier}>🖥️ Full Workstation</div>
                <div className={styles.hardwarePrice}>~$2,500+</div>
                <ul className={styles.hardwareList}>
                  <li>✓ NVIDIA RTX 4070 Ti (12GB+)</li>
                  <li>✓ 64GB RAM</li>
                  <li>✓ Ubuntu 22.04 LTS</li>
                  <li>✓ Local Isaac Sim</li>
                  <li>✓ Full ROS 2 stack</li>
                  <li>✓ Zero latency</li>
                </ul>
                <div className={styles.hardwareBadge}>Best for Production</div>
              </div>

              {/* Hybrid Cloud */}
              <div className={styles.hardwareCard}>
                <div className={styles.hardwareTier}>☁️ Hybrid Cloud</div>
                <div className={styles.hardwarePrice}>~$700 + $205/quarter</div>
                <ul className={styles.hardwareList}>
                  <li>✓ Jetson Orin Nano ($249)</li>
                  <li>✓ RealSense D435i ($349)</li>
                  <li>✓ AWS g5.2xlarge for sim</li>
                  <li>✓ Cloud Isaac Sim</li>
                  <li>✓ Edge deployment</li>
                  <li>⚠️ Network latency</li>
                </ul>
                <div className={styles.hardwareBadge}>Recommended</div>
              </div>

              {/* Cloud-Only */}
              <div className={styles.hardwareCard}>
                <div className={styles.hardwareTier}>🌐 Cloud-Only</div>
                <div className={styles.hardwarePrice}>$205/quarter</div>
                <ul className={styles.hardwareList}>
                  <li>✓ Browser access only</li>
                  <li>✓ AWS/Azure instances</li>
                  <li>✓ Simulation training</li>
                  <li>✓ No local hardware</li>
                  <li>⚠️ No physical deployment</li>
                  <li>⚠️ OpEx costs</li>
                </ul>
                <div className={styles.hardwareBadge}>Budget-Friendly</div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className={styles.cta}>
          <div className={styles.container}>
            <h2>Ready to Build the Future?</h2>
            <p>Join the Physical AI revolution and master humanoid robotics</p>
            <div className={styles.ctaButtons}>
              <Link to="docs/intro" className={styles.ctaPrimary}>
                Start Learning Now
              </Link>
              <Link to="https://github.com/Asmayaseen/hackathon-book" className={styles.ctaSecondary}>
                View on GitHub
              </Link>
            </div>
          </div>
        </section>

      </main>
    </Layout>
  );
}
