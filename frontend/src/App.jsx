import { useState } from "react";
import GoalInput from "./pages/GoalInput";
import "./App.css";

function App() {
  const [showGoalInput, setShowGoalInput] = useState(false);

  // Show Goal Input page
  if (showGoalInput) {
    return <GoalInput />;
  }

  // Landing Page
  return (
    <div className="app">

      {/* NAVBAR */}
      <nav className="navbar">
        <div className="logo">
          <div className="logo-icon">✦</div>
          SkillRoute <span>AI</span>
        </div>

        <div className="nav-links">
          <a href="#product">Product</a>
          <a href="#how-it-works">How It Works</a>
          <a href="#features">Features</a>
        </div>

        <div className="nav-actions">
          <button
            className="signin-btn"
            onClick={() => setShowGoalInput(true)}
          >
            Sign In
          </button>

          <button
            className="nav-cta"
            onClick={() => setShowGoalInput(true)}
          >
            Get Started <span>→</span>
          </button>
        </div>
      </nav>


      {/* HERO */}
      <section className="hero" id="product">

        <div className="hero-left">

          <div className="eyebrow">
            ✨ AI Powered. Personalized. Purposeful.
          </div>

          <h1>
            AI that builds your
            <span> learning path,</span>
            <br />
            not just a course list.
          </h1>

          <p className="hero-text">
            Tell us your goal. We analyze your skills, find your gaps
            and create a personalized roadmap to get you career ready.
          </p>

          <div className="hero-buttons">

            <button
              className="primary-btn"
              onClick={() => setShowGoalInput(true)}
            >
              Build My Learning Path
              <span>✦</span>
            </button>

            <button className="secondary-btn">
              <span className="play">▶</span>
              See how it works
            </button>

          </div>

        </div>


        {/* RIGHT ROADMAP CARD */}
        <div className="hero-right">

          <div className="glow"></div>

          <div className="roadmap-card">

            <h2>How SkillRoute AI Works</h2>

            <div className="roadmap-step">
              <div className="step-icon purple">🎯</div>

              <div>
                <h3>You Tell Us Your Goal</h3>
                <p>e.g. Become a Data Scientist</p>
              </div>
            </div>

            <div className="arrow">↓</div>

            <div className="roadmap-step">
              <div className="step-icon blue">▥</div>

              <div>
                <h3>We Analyze Your Skills</h3>
                <p>Identify your strengths & gaps</p>
              </div>
            </div>

            <div className="arrow">↓</div>

            <div className="roadmap-step">
              <div className="step-icon green">◈</div>

              <div>
                <h3>AI Builds Your Roadmap</h3>
                <p>Personalized just for you</p>
              </div>
            </div>

            <div className="arrow">↓</div>

            <div className="roadmap-step">
              <div className="step-icon orange">🚀</div>

              <div>
                <h3>You Learn. We Guide.</h3>
                <p>Track progress. Get better. Achieve more.</p>
              </div>
            </div>

          </div>
        </div>

      </section>


      {/* FEATURES */}
      <section className="features" id="features">

        <Feature
          icon="🧠"
          title="AI Personalized Roadmaps"
          text="Your goals. Your pace. Your perfect path."
          color="purple"
        />

        <Feature
          icon="◔"
          title="Skill Gap Analysis"
          text="Know what you know. Discover what to learn."
          color="blue"
        />

        <Feature
          icon="ϟ"
          title="Adaptive Learning"
          text="Recommendations that adapt as you improve."
          color="green"
        />

        <Feature
          icon="💬"
          title="AI Learning Assistant"
          text="24/7 help, doubts and career guidance."
          color="orange"
        />

      </section>


      {/* BOTTOM INFO */}
      <section className="info-section">

        <p>YOUR LEARNING JOURNEY, REIMAGINED</p>

        <div className="info-grid">

          <div>
            <strong>01</strong>
            <span>Tell us your goal</span>
          </div>

          <div>
            <strong>02</strong>
            <span>Discover your skill gaps</span>
          </div>

          <div>
            <strong>03</strong>
            <span>Follow your AI roadmap</span>
          </div>

          <div>
            <strong>04</strong>
            <span>Become career ready</span>
          </div>

        </div>

      </section>

    </div>
  );
}


/* Feature Component */
function Feature({ icon, title, text, color }) {
  return (
    <div className="feature-card">

      <div className={`feature-icon ${color}`}>
        {icon}
      </div>

      <div>
        <h3>{title}</h3>
        <p>{text}</p>
      </div>

    </div>
  );
}

export default App;