import { useState } from "react";
import ReactMarkdown from "react-markdown";

function AIAssistant({
  goal = "",
  skills = [],
  roadmap = [],
}) {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const [messages, setMessages] = useState([
    {
      role: "ai",
      text: "Hi! I'm SkillRoute AI 👋\nAsk me anything about your learning path, skills, courses or career.",
    },
  ]);

  // =========================
  // ASK AI
  // =========================

  const askAI = async () => {
    if (!question.trim() || loading) {
      return;
    }

    const userQuestion = question.trim();

    // Add user message
    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        text: userQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(
        "https://skillroute-ai-qpwc.onrender.com/assistant",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            question: userQuestion,
            goal: goal || "",
            skills: skills || [],
            roadmap: roadmap || [],
          }),
        }
      );

      console.log("Assistant status:", response.status);

      const responseText = await response.text();

      console.log(
        "Assistant response:",
        responseText
      );

      if (!response.ok) {
        throw new Error(
          `Backend Error ${response.status}`
        );
      }

      let data;

      try {
        data = JSON.parse(responseText);
      } catch {
        throw new Error(
          "Backend returned invalid JSON."
        );
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          text:
            data.answer ||
            data.message ||
            "Sorry, I could not generate an answer.",
        },
      ]);

    } catch (error) {

      console.error(
        "AI Assistant Error:",
        error
      );

      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          text:
            "⚠️ Unable to respond right now.\n\nPlease make sure the FastAPI backend is running.",
        },
      ]);

    } finally {
      setLoading(false);
    }
  };


  // =========================
  // ENTER KEY
  // =========================

  const handleKeyDown = (e) => {
    if (
      e.key === "Enter" &&
      !e.shiftKey
    ) {
      e.preventDefault();
      askAI();
    }
  };


  // =========================
  // AI TEXT FORMAT
  // =========================

  const formatAIText = (text) => {
    if (!text) {
      return null;
    }

    return text
      .split("\n")
      .map((line, index) => {

        const trimmedLine = line.trim();

        if (!trimmedLine) {
          return (
            <div
              key={index}
              className="ai-space"
            />
          );
        }

        // Bullet
        if (
          trimmedLine.startsWith("- ") ||
          trimmedLine.startsWith("* ")
        ) {
          return (
            <div
              key={index}
              className="ai-bullet"
            >
              <span>•</span>
              <span>
                {trimmedLine.substring(2)}
              </span>
            </div>
          );
        }

        // Numbered list
        const numberMatch =
          trimmedLine.match(
            /^(\d+)\.\s+(.*)$/
          );

        if (numberMatch) {
          return (
            <div
              key={index}
              className="ai-numbered"
            >
              <span className="ai-number">
                {numberMatch[1]}
              </span>

              <span>
                {numberMatch[2]}
              </span>
            </div>
          );
        }

        return (
          <p
            key={index}
            className="ai-paragraph"
          >
            {trimmedLine}
          </p>
        );
      });
  };


  // =========================
  // UI
  // =========================

  return (
    <>
      {/* Floating Button */}

      {!open && (
        <button
          className="ai-floating-btn"
          onClick={() => setOpen(true)}
          title="Ask SkillRoute AI"
        >
          ✦
        </button>
      )}


      {/* Chat Window */}

      {open && (
        <div className="ai-assistant">

          {/* Header */}

          <div className="ai-header">

            <div className="ai-header-info">

              <strong>
                ✦ SkillRoute AI
              </strong>

              <span>
                Your Learning Assistant
              </span>

            </div>

            <button
              className="ai-close"
              onClick={() => setOpen(false)}
            >
              ×
            </button>

          </div>


          {/* Messages */}

          <div className="ai-messages">

            {messages.map((message, index) => (

              <div
                key={index}
                className={
                  message.role === "user"
                    ? "ai-message user-message"
                    : "ai-message bot-message"
                }
              >

                <ReactMarkdown>
                  {message.text}
                </ReactMarkdown>

              </div>

            ))}


            {/* Loading */}

            {loading && (
              <div className="ai-message bot-message">

                <div className="ai-thinking">

                  <span></span>
                  <span></span>
                  <span></span>

                  <label>
                    Thinking...
                  </label>

                </div>

              </div>
            )}

          </div>


          {/* Input */}

          <div className="ai-input-area">

            <textarea
              value={question}
              onChange={(e) =>
                setQuestion(
                  e.target.value
                )
              }
              onKeyDown={handleKeyDown}
              placeholder="Ask about your learning path..."
              rows={1}
            />

            <button
              onClick={askAI}
              disabled={
                loading ||
                !question.trim()
              }
            >
              ➤
            </button>

          </div>

        </div>
      )}
    </>
  );
}

export default AIAssistant;