import { useEffect, useState } from "react";
import "../App.css";
import AIAssistant from "../components/AIAssistant";


function Dashboard({ data, user }) {

  /* =====================================================
     SIDEBAR SECTION
  ===================================================== */

  const [activeSection, setActiveSection] = useState("overview");


  /* =====================================================
     COURSES FROM AI ROADMAP
  ===================================================== */

  const [courses, setCourses] = useState([]);


  /* =====================================================
     LOAD AI RECOMMENDED COURSES
  ===================================================== */

  useEffect(() => {

    if (
      !data ||
      !data.learning_roadmap ||
      data.learning_roadmap.length === 0
    ) {
      return;
    }

    const loadCoursesAndProgress = async () => {

      try {

        // User ID safely get karo
        const userId =
          user?.id ||
          user?.user_id ||
          localStorage.getItem("user_id");

        // ---------------------------------
        // FORMAT COURSES FIRST
        // ---------------------------------

        const formattedCourses =
          data.learning_roadmap.map((item, index) => {

            const courseId = String(
              item.course_id ??
              `${item.course_name}-${index}`
            );

            return {

              id: courseId,

              title:
                item.course_name ||
                "Recommended Course",

              skill:
                item.skill ||
                "General",

              level:
                item.level ||
                "Beginner",

              duration:
                item.duration_hours
                  ? `${item.duration_hours} hours`
                  : "Self paced",

              youtube_link:
                item.youtube_link ||
                "",

              course_search_link:
                item.course_search_link ||
                "",

              step:
                item.step ||
                index + 1,

              completed: false,

            };

          });


        // ---------------------------------
        // GET SAVED PROGRESS
        // ---------------------------------

        if (!userId) {

          console.warn(
            "User ID not available. Loading courses without saved progress."
          );

          setCourses(formattedCourses);

          return;
        }


        const response = await fetch(
          `http://127.0.0.1:8000/progress/${userId}`
        );


        if (!response.ok) {

          console.warn(
            "Could not load saved progress."
          );

          setCourses(formattedCourses);

          return;
        }


        const result = await response.json();

        console.log(
          "Progress API response:",
          result
        );


        const savedProgress =
          result.progress || {};


        // ---------------------------------
        // RESTORE PROGRESS
        // ---------------------------------

        const coursesWithProgress =
          formattedCourses.map((course) => ({

            ...course,

            completed:
              savedProgress[String(course.id)] === true,

          }));


        console.log(
          "Courses with restored progress:",
          coursesWithProgress
        );


        setCourses(coursesWithProgress);


      } catch (error) {

        console.error(
          "Error loading courses/progress:",
          error
        );

        // Error hone par bhi courses gayab nahi honge
        setCourses(
          data.learning_roadmap.map(
            (item, index) => ({

              id: String(
                item.course_id ??
                `${item.course_name}-${index}`
              ),

              title:
                item.course_name ||
                "Recommended Course",

              skill:
                item.skill ||
                "General",

              level:
                item.level ||
                "Beginner",

              duration:
                item.duration_hours
                  ? `${item.duration_hours} hours`
                  : "Self paced",

              youtube_link:
                item.youtube_link ||
                "",

              course_search_link:
                item.course_search_link ||
                "",

              step:
                item.step ||
                index + 1,

              completed: false,

            })
          )
        );

      }

    };


    loadCoursesAndProgress();

  }, [data, user]);


  /* =====================================================
     PROGRESS
  ===================================================== */

  const completedCourses =
    courses.filter(
      (course) => course.completed
    ).length;


  const totalCourses =
    courses.length;


  const progress =
    totalCourses === 0
      ? 0
      : Math.round(
          (completedCourses / totalCourses) * 100
        );


  /* =====================================================
     MARK COURSE COMPLETE
  ===================================================== */

  const toggleCourse = async (id) => {

    // =====================================
    // GET USER ID
    // =====================================

    const userId =
      user?.id ||
      user?.user_id ||
      localStorage.getItem("user_id");


    if (!userId) {

      console.error(
        "User ID is missing. Cannot save progress."
      );

      alert(
        "User information is missing. Please login again."
      );

      return;
    }


    // =====================================
    // FIND COURSE
    // =====================================

    const selectedCourse = courses.find(
      (course) =>
        String(course.id) === String(id)
    );


    if (!selectedCourse) {

      console.error(
        "Course not found:",
        id
      );

      return;
    }


    // =====================================
    // NEW STATUS
    // =====================================

    const newCompletedStatus =
      !selectedCourse.completed;


    // =====================================
    // UPDATE UI
    // =====================================

    setCourses((previousCourses) =>

      previousCourses.map((course) =>

        String(course.id) === String(id)

          ? {
              ...course,
              completed: newCompletedStatus,
            }

          : course

      )

    );


    // =====================================
    // SAVE TO BACKEND
    // =====================================

    try {

      const progressData = {

        user_id: Number(userId),

        course_id: String(id),

        completed: newCompletedStatus,

      };


      console.log(
        "SENDING PROGRESS:",
        progressData
      );


      const response = await fetch(
        "http://127.0.0.1:8000/progress",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify(
            progressData
          ),

        }
      );


      const result =
        await response.json();


      console.log(
        "Progress API response:",
        result
      );


      if (!response.ok) {

        throw new Error(
          JSON.stringify(result)
        );

      }


      console.log(
        "Course progress saved successfully."
      );


    } catch (error) {

      console.error(
        "FULL PROGRESS ERROR:",
        error
      );


      // Backend save fail hua
      // to UI rollback karo

      setCourses((previousCourses) =>

        previousCourses.map((course) =>

          String(course.id) === String(id)

            ? {
                ...course,
                completed:
                  selectedCourse.completed,
              }

            : course

        )

      );

    }

  };


  /* =====================================================
     OVERVIEW
  ===================================================== */

  const renderOverview = () => {

    return (

      <div className="dashboard-content">

        {/* HEADER */}

        <div className="dashboard-header">

          <div>

            <div className="dashboard-badge">
              ✨ LEARNING DASHBOARD
            </div>

            <h1>
              Welcome back,{" "}
              <span>
                {user?.name || data?.user || "Learner"}!
              </span>
            </h1>

            <p>
              Track your personalized learning journey
              and achieve your goal.
            </p>

          </div>

        </div>


        {/* GOAL CARD */}

        <div className="dashboard-goal-card">

          <div>

            <small>
              YOUR CURRENT GOAL
            </small>

            <h2>
              {data?.goal || "Your learning goal"}
            </h2>

          </div>


          <div className="goal-timeline">

            <span>
              ⏱ Timeline
            </span>

            <strong>
              {data?.timeline_days || 0} Days
            </strong>

          </div>

        </div>


        {/* PROGRESS SUMMARY */}

        <div className="progress-summary">


          {/* OVERALL */}

          <div className="progress-card main-progress">

            <div className="progress-card-top">

              <div>

                <small>
                  OVERALL PROGRESS
                </small>

                <h2>
                  {progress}%
                </h2>

              </div>


              <div className="progress-circle">

                {progress}%

              </div>

            </div>


            <div className="progress-track">

              <div
                className="progress-fill"
                style={{
                  width: `${progress}%`,
                }}
              />

            </div>


            <p>
              {completedCourses} of {totalCourses} courses
              completed
            </p>

          </div>


          {/* COMPLETED */}

          <div className="progress-card">

            <div className="stat-icon">
              ✓
            </div>

            <small>
              COMPLETED
            </small>

            <h2>
              {completedCourses}
            </h2>

            <p>
              Courses completed
            </p>

          </div>


          {/* REMAINING */}

          <div className="progress-card">

            <div className="stat-icon">
              ▶
            </div>

            <small>
              REMAINING
            </small>

            <h2>
              {totalCourses - completedCourses}
            </h2>

            <p>
              Courses remaining
            </p>

          </div>


          {/* READINESS */}

          <div className="progress-card">

            <div className="stat-icon">
              ✦
            </div>

            <small>
              AI READINESS
            </small>

            <h2>
              {data?.overall_readiness ?? 0}%
            </h2>

            <p>
              Current skill readiness
            </p>

          </div>

        </div>


        {/* NEXT COURSE */}

        {courses.length > 0 && (

          <div className="next-course-card">

            <div>

              <div className="section-badge">
                CONTINUE LEARNING
              </div>

              <h2>
                {courses.find(
                  (course) => !course.completed
                )?.title ||
                  "All courses completed!"}
              </h2>

              <p>
                Continue with your next recommended
                course from the AI learning path.
              </p>

            </div>


            <button
              className="dashboard-primary-btn"
              onClick={() =>
                setActiveSection("courses")
              }
            >
              View Courses →
            </button>

          </div>

        )}


        {/* AI INSIGHT */}

        {data?.insight && (

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

        )}
        {/* AI ASSISTANT */}

        <div className="dashboard-ai-section">

          <AIAssistant
            goal={data?.goal}
            skills={data?.skills}
            roadmap={data?.learning_roadmap}
          />

        </div>


        {/* COMPLETION */}

        {progress === 100 && (

          <div className="completion-message">

            <div className="completion-icon">
              🎉
            </div>

            <div>

              <h3>
                Congratulations!
              </h3>

              <p>
                You have completed your entire
                personalized learning path.
              </p>

            </div>

          </div>

        )}

      </div>

    );

  };


  /* =====================================================
     COURSES
  ===================================================== */

  const renderCourses = () => {

    return (

      <div className="dashboard-content">

        <div className="dashboard-header">

          <div>

            <div className="dashboard-badge">
              ✨ YOUR LEARNING PATH
            </div>

            <h1>
              Recommended <span>Courses</span>
            </h1>

            <p>
              These courses were selected according
              to your goal and identified skill gaps.
            </p>

          </div>


          <div className="course-count">
            {completedCourses}/{totalCourses}
          </div>

        </div>


        {/* COURSE LIST */}

        <div className="dashboard-course-list">

          {courses.length > 0 ? (

            courses.map((course, index) => (

              <div
                className={`dashboard-course ${
                  course.completed
                    ? "course-completed"
                    : ""
                }`}
                key={course.id}
              >

                {/* NUMBER */}

                <div className="course-number">

                  {course.completed
                    ? "✓"
                    : index + 1}

                </div>
                


                {/* COURSE INFO */}

                <div className="dashboard-course-info">

                  <h3>
                    {course.title}
                  </h3>


                  <div className="course-meta">

                    <span>
                      🎯 {course.skill}
                    </span>

                    <span>
                      📊 {course.level}
                    </span>

                    <span>
                      ⏱ {course.duration}
                    </span>


                    <span
                      className={
                        course.completed
                          ? "status-completed"
                          : "status-pending"
                      }
                    >
                      {course.completed
                        ? "Completed"
                        : "Not Completed"}
                    </span>

                  </div>


                  {/* YOUTUBE */}

                  {course.youtube_link && (

                    <div className="course-links">

                      <a
                        href={course.youtube_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="youtube-btn"
                      >
                        ▶ Watch on YouTube
                      </a>


                      {course.course_search_link && (

                        <a
                          href={
                            course.course_search_link
                          }
                          target="_blank"
                          rel="noopener noreferrer"
                          className="course-btn"
                        >
                          📚 Course
                        </a>

                      )}

                    </div>

                  )}

                </div>


                {/* ACTION */}

                <div className="course-actions">

                  <button
                    className={
                      course.completed
                        ? "completed-btn"
                        : "complete-btn"
                    }
                    onClick={() =>
                      toggleCourse(course.id)
                    }
                  >

                    {course.completed
                      ? "✓ Completed"
                      : "Mark Complete"}

                  </button>

                </div>

              </div>

            ))

          ) : (

            <div className="empty-courses">

              <h3>
                No recommended courses found.
              </h3>

              <p>
                AI could not find matching courses
                for this goal.
              </p>

            </div>

          )}

        </div>
        {/* ================================
            AI ASSISTANT FOR COURSES
        ================================= */}

        <div className="dashboard-ai-box">

          <AIAssistant
            goal={data?.goal}
            skills={data?.skills}
            roadmap={data?.learning_roadmap}
            context="courses"
          />

        </div>

      </div>

    );

  };


  /* =====================================================
     MILESTONES
  ===================================================== */

  const renderMilestones = () => {

    return (

      <div className="dashboard-content">

        <div className="dashboard-header">

          <div>

            <div className="dashboard-badge">
              ✨ AI LEARNING MILESTONES
            </div>

            <h1>
              Your Learning <span>Journey</span>
            </h1>

            <p>
              Follow your personalized roadmap
              step by step.
            </p>

          </div>


          <div className="timeline-badge">

            {data?.timeline_days || 0} Days

          </div>

        </div>


        <div className="milestones-card">

          {data?.learning_roadmap?.length > 0 ? (

            data.learning_roadmap.map(
              (item, index) => (

                <div
                  className={`milestone-item ${
                    courses[index]?.completed
                      ? "milestone-completed"
                      : ""
                  }`}
                  key={`${item.course_id}-${index}`}
                >

                  <div className="milestone-number">

                    {courses[index]?.completed
                      ? "✓"
                      : item.step || index + 1}

                  </div>


                  <div className="milestone-content">

                    <span className="milestone-skill">
                      {item.skill}
                    </span>

                    <h3>
                      {item.course_name}
                    </h3>


                    <div className="milestone-meta">

                      <span>
                        📊 {item.level}
                      </span>

                      <span>
                        ⏱ {item.duration_hours} hours
                      </span>

                    </div>


                    {item.youtube_link && (

                      <a
                        href={item.youtube_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="milestone-youtube"
                      >
                        ▶ Start Learning
                      </a>

                    )}

                  </div>

                </div>

              )
            )

          ) : (

            <div className="empty-courses">

              <h3>
                No milestones available.
              </h3>

            </div>

          )}

        </div>
        {/* ================================
            AI ASSISTANT FOR COURSES
        ================================= */}

        <div className="dashboard-ai-box">

          <AIAssistant
            goal={data?.goal}
            skills={data?.skills}
            roadmap={data?.learning_roadmap}
            context="courses"
          />

        </div>

      </div>

    );

  };


  /* =====================================================
     SKILLS
  ===================================================== */

  const renderSkills = () => {

    return (

      <div className="dashboard-content">

        <div className="dashboard-header">

          <div>

            <div className="dashboard-badge">
              ✨ AI SKILL DEVELOPMENT
            </div>

            <h1>
              Your <span>Skills</span>
            </h1>

            <p>
              Track your current skills against
              your goal requirements.
            </p>

          </div>


          <div className="readiness-badge">

            <strong>
              {data?.overall_readiness ?? 0}%
            </strong>

            <span>
              Readiness
            </span>

          </div>

        </div>


        <div className="dashboard-skills-card">

          {data?.skills?.length > 0 ? (

            data.skills.map(
              (skill, index) => {

                const current =
                  Number(
                    skill.current_percentage || 0
                  );

                const required =
                  Number(
                    skill.required_percentage || 0
                  );

                return (

                  <div
                    className="dashboard-skill"
                    key={`${skill.name}-${index}`}
                  >

                    <div className="dashboard-skill-header">

                      <div>

                        <h3>
                          {skill.name}
                        </h3>

                        <span
                          className={`skill-status ${getSkillType(
                            skill.status
                          )}`}
                        >
                          {skill.status}
                        </span>

                      </div>


                      <div className="dashboard-skill-percentage">

                        <strong>
                          {current}%
                        </strong>

                        <span>
                          / {required}%
                        </span>

                      </div>

                    </div>


                    <div className="dashboard-skill-track">

                      <div
                        className={`dashboard-skill-fill ${getSkillType(
                          skill.status
                        )}`}
                        style={{
                          width: `${Math.min(
                            current,
                            100
                          )}%`,
                        }}
                      />

                    </div>


                    <div className="dashboard-skill-footer">

                      <span>
                        Current: {current}%
                      </span>

                      <span>
                        Required: {required}%
                      </span>

                    </div>

                  </div>

                );

              }

            )

          ) : (

            <div className="empty-courses">

              <h3>
                No skill data available.
              </h3>

            </div>

          )}

        </div>
        {/* ================================
            AI ASSISTANT FOR COURSES
        ================================= */}

        <div className="dashboard-ai-box">

          <AIAssistant
            goal={data?.goal}
            skills={data?.skills}
            roadmap={data?.learning_roadmap}
            context="courses"
          />

        </div>

      </div>

    );

  };


  /* =====================================================
     PROGRESS
  ===================================================== */

  const renderProgress = () => {

    return (

      <div className="dashboard-content">

        <div className="dashboard-header">

          <div>

            <div className="dashboard-badge">
              📊 LEARNING PROGRESS
            </div>

            <h1>
              Your <span>Progress</span>
            </h1>

            <p>
              Keep learning consistently to reach
              your goal.
            </p>

          </div>

        </div>


        {/* MAIN PROGRESS */}

        <div className="large-progress-card">

          <div className="large-progress-header">

            <div>

              <small>
                COURSE COMPLETION
              </small>

              <h2>
                {progress}%
              </h2>

            </div>


            <div className="large-progress-circle">

              {progress}%

            </div>

          </div>


          <div className="large-progress-track">

            <div
              className="large-progress-fill"
              style={{
                width: `${progress}%`,
              }}
            />

          </div>


          <p>

            You completed{" "}
            <strong>
              {completedCourses}
            </strong>{" "}
            out of{" "}
            <strong>
              {totalCourses}
            </strong>{" "}
            recommended courses.

          </p>

        </div>


        {/* STATS */}

        <div className="progress-grid">

          <div className="progress-stat-card">

            <span>
              📚
            </span>

            <small>
              TOTAL COURSES
            </small>

            <strong>
              {totalCourses}
            </strong>

          </div>


          <div className="progress-stat-card">

            <span>
              ✓
            </span>

            <small>
              COMPLETED
            </small>

            <strong>
              {completedCourses}
            </strong>

          </div>


          <div className="progress-stat-card">

            <span>
              ⏳
            </span>

            <small>
              REMAINING
            </small>

            <strong>
              {totalCourses - completedCourses}
            </strong>

          </div>


          <div className="progress-stat-card">

            <span>
              🎯
            </span>

            <small>
              AI READINESS
            </small>

            <strong>
              {data?.overall_readiness ?? 0}%
            </strong>

          </div>

        </div>


        {/* COMPLETION */}

        {progress === 100 && (

          <div className="completion-message">

            <div className="completion-icon">
              🎉
            </div>

            <div>

              <h3>
                Congratulations!
              </h3>

              <p>
                You completed your entire
                personalized learning path.
              </p>

            </div>

          </div>

        )}
        {/* ================================
            AI ASSISTANT FOR COURSES
        ================================= */}

        <div className="dashboard-ai-box">

          <AIAssistant
            goal={data?.goal}
            skills={data?.skills}
            roadmap={data?.learning_roadmap}
            context="courses"
          />

        </div>

      </div>

    );

  };


  /* =====================================================
     MAIN RETURN
  ===================================================== */

  return (

    <div className="dashboard-layout">


      {/* =================================================
          SIDEBAR
      ================================================= */}

      <aside className="dashboard-sidebar">


        {/* LOGO */}

        <div className="sidebar-logo">

          <div className="logo-icon">
            ✦
          </div>

          SkillRoute{" "}
          <span>
            AI
          </span>

        </div>


        {/* MENU */}

        <div className="sidebar-menu">


          <button
            className={
              activeSection === "overview"
                ? "sidebar-item active"
                : "sidebar-item"
            }
            onClick={() =>
              setActiveSection("overview")
            }
          >
            <span>⌂</span>
            Dashboard
          </button>


          <button
            className={
              activeSection === "courses"
                ? "sidebar-item active"
                : "sidebar-item"
            }
            onClick={() =>
              setActiveSection("courses")
            }
          >
            <span>▣</span>
            Courses
          </button>


          <button
            className={
              activeSection === "milestones"
                ? "sidebar-item active"
                : "sidebar-item"
            }
            onClick={() =>
              setActiveSection("milestones")
            }
          >
            <span>♧</span>
            Milestones
          </button>


          <button
            className={
              activeSection === "skills"
                ? "sidebar-item active"
                : "sidebar-item"
            }
            onClick={() =>
              setActiveSection("skills")
            }
          >
            <span>✦</span>
            Skills
          </button>


          <button
            className={
              activeSection === "progress"
                ? "sidebar-item active"
                : "sidebar-item"
            }
            onClick={() =>
              setActiveSection("progress")
            }
          >
            <span>◔</span>
            Progress
          </button>

        </div>

      </aside>


      {/* =================================================
          MAIN
      ================================================= */}

      <main className="dashboard-main">


        {activeSection === "overview" &&
          renderOverview()}


        {activeSection === "courses" &&
          renderCourses()}


        {activeSection === "milestones" &&
          renderMilestones()}


        {activeSection === "skills" &&
          renderSkills()}


        {activeSection === "progress" &&
          renderProgress()}


        {activeSection === "assistant" && (

          <div className="dashboard-content">

            <div className="dashboard-header">

              <div>

                <div className="dashboard-badge">
                  ✨ AI LEARNING ASSISTANT
                </div>

                <h1>
                  Your AI <span>Assistant</span>
                </h1>

                <p>
                  Ask questions about your goal,
                  courses and learning roadmap.
                </p>

              </div>

            </div>


            <AIAssistant
              goal={data?.goal}
              skills={data?.skills}
              roadmap={data?.learning_roadmap}
            />

          </div>

        )}

      </main>

    </div>

  );

}


/* =====================================================
   SKILL STATUS
===================================================== */

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


export default Dashboard;