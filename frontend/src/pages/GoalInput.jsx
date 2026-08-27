import { useState } from "react";
import GoalAnalysis from "./GoalAnalysis";


function GoalInput({ user, onAnalysisComplete }) {
  const [goal, setGoal] = useState("");
  const [showAnalysis, setShowAnalysis] = useState(false);

  if (showAnalysis) {
    return (
      <GoalAnalysis
        goal={goal}
        onAnalysisComplete={onAnalysisComplete}
      />
    );
  }

  return (
    <div className="goal-page">

      <div className="goal-container">

        {/* Progress */}
        <div className="step-progress">

          <div className="step active">
            <span>1</span>
            <p>Goal Input</p>
          </div>

          <div className="line"></div>

          <div className="step">
            <span>2</span>
            <p>AI Analysis</p>
          </div>

          <div className="line"></div>

          <div className="step">
            <span>3</span>
            <p>Skill Gaps</p>
          </div>

          <div className="line"></div>

          <div className="step">
            <span>4</span>
            <p>Roadmap</p>
          </div>

        </div>


        {/* Heading */}
        <div className="goal-heading">

          <div className="small-badge">
            ✨ AI understands natural language
          </div>

          <h1>
            Tell us your <span>goal</span>
          </h1>

          <p>
            Just describe what you want to achieve in your own words.
            <br />
            Our AI will understand the rest.
          </p>

        </div>


        {/* Goal Input Card */}
        <div className="goal-card">

          <label>Describe your goal</label>

          <textarea
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            maxLength={500}
            placeholder="e.g. I want to become a Data Scientist in 100 days. I know basic Python..."
          />

          <div className="input-bottom">

            <span>
              ✨ AI will extract your goal, timeline and skills
            </span>

            <span>
              {goal.length} / 500
            </span>

          </div>


          {/* Analyze Button */}
          <button
            className="analyze-btn"
            onClick={() => {
              if (goal.trim()) {
                setShowAnalysis(true);
              }
            }}
          >
            ✨ Analyze My Goal
            <span>→</span>
          </button>

        </div>


        {/* Examples */}
        <div className="examples">

          <p>NEED INSPIRATION?</p>

          <div className="example-list">

            <button
              onClick={() =>
                setGoal(
                  "I want to become a Data Scientist in 100 days. I know basic Python."
                )
              }
            >
              “I want to become a Data Scientist in 100 days.”
            </button>


            <button
              onClick={() =>
                setGoal(
                  "I want to become an AI Engineer in 6 months."
                )
              }
            >
              “I want to become an AI Engineer in 6 months.”
            </button>


            <button
              onClick={() =>
                setGoal(
                  "I want to learn Web Development and get a job in 90 days."
                )
              }
            >
              “I want to learn Web Development and get a job in 90 days.”
            </button>

          </div>

        </div>


        {/* Privacy */}
        <div className="privacy">
          🔒 Your information is used only to personalize your learning path.
        </div>

      </div>

    </div>
  );
}

export default GoalInput;