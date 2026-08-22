import "../App.css";

function GoalAnalysis() {
  const data = {
    goal: "Data Scientist",
    timeline_days: 100,
    current_level: "Beginner",
    current_readiness: 28,

    skills: [
      {
        name: "Python",
        current: 70,
        required: 90,
        status: "Strong",
        type: "strong",
      },
      {
        name: "Statistics",
        current: 25,
        required: 80,
        status: "Needs Work",
        type: "warning",
      },
      {
        name: "SQL",
        current: 20,
        required: 80,
        status: "Needs Work",
        type: "warning",
      },
      {
        name: "Machine Learning",
        current: 10,
        required: 90,
        status: "Major Gap",
        type: "danger",
      },
      {
        name: "Data Visualization",
        current: 30,
        required: 75,
        status: "Needs Work",
        type: "warning",
      },
      {
        name: "Deep Learning",
        current: 0,
        required: 65,
        status: "Not Started",
        type: "danger",
      },
    ],

    insight:
      "Your strongest foundation is Python. Your biggest gaps are Machine Learning, Statistics and SQL. These skills will be prioritized in your personalized roadmap.",
  };

  return (
    <div className="analysis-page">

      {/* TOP BAR */}
      <div className="analysis-top">

        <div className="analysis-logo">
          <div className="logo-icon">✦</div>
          SkillRoute <span>AI</span>
        </div>

        <div className="analysis-status">
          ✨ AI Analysis Complete
        </div>

      </div>


      {/* HEADING */}
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


      {/* SUMMARY CARDS */}
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
          title="CURRENT LEVEL"
          value={data.current_level}
          color="green"
        />

      </div>


      {/* SKILL GAP SECTION */}
      <div className="skill-section">

        <div className="section-title">

          <div>

            <div className="section-badge">
              AI SKILL GAP ANALYSIS
            </div>

            <h2>What you need to learn</h2>

            <p>
              Based on your goal, AI mapped the skills required
              to reach your target.
            </p>

          </div>

          <div className="overall-score">

            <strong>
              {data.current_readiness}%
            </strong>

            <span>
              Current Readiness
            </span>

          </div>

        </div>


        {/* SKILL LIST */}
        <div className="skills-card">

          {data.skills.map((skill, index) => (
            <Skill
              key={index}
              name={skill.name}
              current={skill.current}
              required={skill.required}
              status={skill.status}
              type={skill.type}
            />
          ))}

        </div>

      </div>


      {/* AI INSIGHT */}
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


      {/* ROADMAP ACTION */}
      <div className="analysis-action">

        <div>

          <h3>
            Ready to build your roadmap?
          </h3>

          <p>
            We'll turn these skill gaps into a
            personalized learning journey.
          </p>

        </div>

        <button className="roadmap-btn">

          Generate My {data.timeline_days}-Day Roadmap

          <span>
            →
          </span>

        </button>

      </div>

    </div>
  );
}


/* ================= SUMMARY CARD ================= */

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


/* ================= SKILL COMPONENT ================= */

function Skill({
  name,
  current,
  required,
  status,
  type,
}) {
  return (
    <div className="skill-row">

      {/* Skill Name */}
      <div className="skill-name">

        <strong>
          {name}
        </strong>

        <span className={`skill-status ${type}`}>
          {status}
        </span>

      </div>


      {/* Progress Bar */}
      <div className="skill-progress">

        <div className="progress-track">

          <div
            className={`progress-fill ${type}`}
            style={{
              width: `${current}%`,
            }}
          ></div>

        </div>

      </div>


      {/* Percentage */}
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


export default GoalAnalysis;