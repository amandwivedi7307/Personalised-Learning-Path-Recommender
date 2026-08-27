import { useEffect, useState } from "react";
import "../App.css";
import Roadmap from "./Roadmap";
import Dashboard from "./Dashboard";
import AIAssistant from "../components/AIAssistant";

function GoalAnalysis({ goal, onAnalysisComplete }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showRoadmap, setShowRoadmap] = useState(false);
  const [showDashboard, setShowDashboard] = useState(false);

  useEffect(() => {
    const analyzeGoal = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/recommend",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              name: "Learner",
              goal: goal,
              current_skills: {},
            }),
          }
        );

        if (!response.ok) {
          throw new Error("Backend request failed");
        }

        const result = await response.json();
        

        if (result.error) {
          throw new Error(result.error);
        }

        setData(result);

      } catch (err) {
        console.error(err);
        setError("Unable to connect with AI backend.");

      } finally {
        setLoading(false);
      }
    };

    analyzeGoal();
  }, [goal]);


  // =========================
  // LOADING
  // =========================

  if (loading) {
    return (
      <div className="analysis-page">

        <div className="analysis-heading">

          <div className="analysis-badge">
            ✨ AI ANALYZING
          </div>

          <h1>
            Understanding your <span>goal...</span>
          </h1>

          <p>
            Our AI is identifying the skills you need
            and building your personalized analysis.
          </p>

        </div>

      </div>
    );
  }


  // =========================
  // ERROR
  // =========================

  if (error) {
    return (
      <div className="analysis-page">

        <div className="analysis-heading">

          <div className="analysis-badge">
            ⚠️ ERROR
          </div>

          <h1>
            Something went <span>wrong.</span>
          </h1>

          <p>
            {error}
          </p>

          <p>
            Make sure your FastAPI backend is running on
            http://127.0.0.1:8000
          </p>

        </div>

      </div>
    );
  }


  // =========================
  // ROADMAP
  // =========================

  if (showDashboard) {
    return (
      <Dashboard
        data={data}
        user={{ name: "Learner" }}
      />
    );
  }

  if (showRoadmap) {
    return (
      <Roadmap
        data={data}
        onBack={() => setShowRoadmap(false)}
      />
    );
  }


  // =========================
  // ANALYSIS
  // =========================

  return (
    <div className="analysis-page">

      {/* =========================
          TOP BAR
      ========================= */}

      <div className="analysis-top">

        <div className="analysis-logo">

          <div className="logo-icon">
            ✦
          </div>

          SkillRoute <span>AI</span>

        </div>

        <div className="analysis-status">
          ✨ AI Analysis Complete
        </div>

      </div>


      {/* =========================
          HEADING
      ========================= */}

      <div className="analysis-heading">

        <div className="analysis-badge">
          ✨ PERSONALIZED ANALYSIS
        </div>

        <h1>
          Here's what we
          <span> understood.</span>
        </h1>

        <p>
          Our AI analyzed your goal and identified the skills
          you need to reach it.
        </p>

      </div>


      {/* =========================
          SUMMARY CARDS
      ========================= */}

      <div className="analysis-summary">

        <SummaryCard
          icon="🎯"
          title="YOUR GOAL"
          value={data.goal}
          color="purple"
        />

        <SummaryCard
          icon="◷"
          title="TIMELINE"
          value={`${data.timeline_days} Days`}
          color="blue"
        />

        <SummaryCard
          icon="⚡"
          title="CURRENT READINESS"
          value={`${data.overall_readiness}%`}
          color="green"
        />

      </div>


      {/* =========================
          SKILL GAP
      ========================= */}

      <div className="skill-section">

        <div className="section-title">

          <div>

            <div className="section-badge">
              AI SKILL GAP ANALYSIS
            </div>

            <h2>
              What you need to learn
            </h2>

            <p>
              Based on your goal, AI mapped the skills required
              to reach your target.
            </p>

          </div>

          <div className="overall-score">

            <strong>
              {data.overall_readiness}%
            </strong>

            <span>
              Current Readiness
            </span>

          </div>

        </div>


        {/* =========================
            SKILLS
        ========================= */}

        <div className="skills-card">

          {data.skills?.map((skill, index) => (

            <Skill
              key={index}
              name={skill.name}
              current={skill.current_percentage}
              required={skill.required_percentage}
              status={skill.status}
              type={getSkillType(skill.status)}
            />

          ))}

        </div>

      </div>


      {/* =========================
          AI INSIGHT
      ========================= */}

      <div className="ai-insight">

        <div className="insight-icon">
          ✦
        </div>

        <div>

          <small>
            AI INSIGHT
          </small>

          <p>
            {data.insight}
          </p>

        </div>

      </div>


      {/* =========================
          DASHBOARD ACTION
      ========================= */}

      <div className="analysis-action">

        <div>

          <h3>
            {data.recommended_courses?.length || 0} courses found
          </h3>

          <p>
            AI matched courses from your learning dataset
            with your skill gaps.
          </p>

        </div>

        <button
          className="roadmap-btn"
          onClick={() => setShowDashboard(true)}
        >
          View My Dashboard
          <span>→</span>
        </button>

      </div>


      {/* =========================
          AI ASSISTANT
      ========================= */}

      <AIAssistant
        goal={data.goal}
        skills={data.skills}
        roadmap={data.learning_roadmap}
      />

    </div>
  );
}


/* =========================
   SUMMARY CARD
========================= */

function SummaryCard({
  icon,
  title,
  value,
  color,
}) {

  return (
    <div className="summary-card">

      <div className={`summary-icon ${color}`}>
        {icon}
      </div>

      <div>

        <small>
          {title}
        </small>

        <h3>
          {value}
        </h3>

      </div>

    </div>
  );
}


/* =========================
   SKILL
========================= */

function Skill({
  name,
  current,
  required,
  status,
  type,
}) {

  return (
    <div className="skill-row">

      <div className="skill-name">

        <strong>
          {name}
        </strong>

        <span className={`skill-status ${type}`}>
          {status}
        </span>

      </div>


      <div className="skill-progress">

        <div className="progress-track">

          <div
            className={`progress-fill ${type}`}
            style={{
              width: `${current}%`,
            }}
          />

        </div>

      </div>


      <div className="skill-values">

        <span>
          {current}%
        </span>

        <small>
          / {required}%
        </small>

      </div>

    </div>
  );
}


/* =========================
   STATUS COLOR
========================= */

function getSkillType(status) {

  switch (status) {

    case "Strong":
      return "strong";

    case "Needs Work":
      return "warning";

    case "Major Gap":
      return "danger";

    case "Not Started":
      return "danger";

    default:
      return "warning";
  }
}


export default GoalAnalysis;