import "../App.css";
import AIAssistant from "../components/AIAssistant";

function Roadmap({ data, onBack }) {
  return (
    <div className="analysis-page">

      <div className="analysis-top">

        <div className="analysis-logo">
          <div className="logo-icon">✦</div>
          SkillRoute <span>AI</span>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
          }}
        >

          <button
            className="roadmap-back-btn"
            onClick={onBack}
          >
            ← Dashboard
          </button>

          <div className="analysis-status">
            🚀 Personalized Roadmap
          </div>

        </div>

      </div>

      <div className="analysis-heading">

        <div className="analysis-badge">
          ✨ AI LEARNING ROADMAP
        </div>

        <h1>
          Your personalized <span>learning path.</span>
        </h1>

        <p>
          Follow these courses step-by-step to reach your goal.
        </p>

      </div>

      <div className="skill-section">

        <div className="section-title">

          <div>
            <div className="section-badge">
              {data.timeline_days}-DAY ROADMAP
            </div>

            <h2>
              Become a {data.goal}
            </h2>

            <p>
              Courses are prioritized according to your skill gaps.
            </p>
          </div>

          <div className="overall-score">
            <strong>
              {data.learning_roadmap?.length || 0}
            </strong>

            <span>
              Learning Steps
            </span>
          </div>

        </div>


        <div className="skills-card">

          {data.learning_roadmap &&
          data.learning_roadmap.length > 0 ? (

            data.learning_roadmap.map((item, index) => (

              <div
                className="skill-row"
                key={`${item.course_id}-${index}`}
              >

                <div className="skill-name">

                  <strong>
                    Step {item.step}
                  </strong>

                  <span className="skill-status strong">
                    {item.skill}
                  </span>

                </div>


                <div className="skill-progress">

                  <div>
                    <strong>
                      {item.course_name}
                    </strong>

                    <p>
                      Level: {item.level} | Duration:{" "}
                      {item.duration_hours} hours
                    </p>
                  </div>

                </div>


                <div className="skill-values">

                  <div className="roadmap-links">

                    <a
                      href={item.youtube_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="youtube-btn"
                    >
                      ▶ YouTube
                    </a>

                    <a
                      href={item.course_search_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="course-btn"
                    >
                      📚 Course
                    </a>

                  </div>

                </div>

              </div>

            ))

          ) : (

            <div style={{ padding: "30px", textAlign: "center" }}>
              <h3>No courses found in the dataset.</h3>

              <p>
                We identified the required skills, but matching
                courses are not available in the current dataset.
              </p>
            </div>

          )}

        </div>

      </div>


      {/* MISSING SKILLS */}

      {data.missing_skills &&
      data.missing_skills.length > 0 && (

        <div className="ai-insight">

          <div className="insight-icon">
            ✦
          </div>

          <div>

            <small>
              SKILLS WITHOUT DATASET COURSES
            </small>

            {data.missing_skills.map(
              (skill, index) => (

                <p key={index}>
                  <strong>
                    {skill.skill}
                  </strong>{" "}
                  — course not found in dataset.{" "}

                  <a
                    href={skill.learning_link}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Find Learning Resource →
                  </a>
                </p>

              )
            )}

          </div>

        </div>

      )}
      <AIAssistant
        goal={data.goal}
        skills={data.skills}
        roadmap={data.learning_roadmap}
      />

    </div>
  );
}

export default Roadmap;