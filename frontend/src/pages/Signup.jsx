import { useState } from "react";
import "../App.css";

function Signup({ onSignup, onLogin, onBack }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    setError("");

    // =========================
    // BASIC VALIDATION
    // =========================

    if (
      !name.trim() ||
      !email.trim() ||
      !password ||
      !confirmPassword
    ) {
      setError("Please fill in all fields.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setLoading(true);

    try {
      // =========================
      // SIGNUP API
      // =========================

      const response = await fetch(
        "https://skillroute-ai-qpwc.onrender.com/signup",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            name: name.trim(),
            email: email.trim(),
            password: password,
          }),
        }
      );

      const data = await response.json();

      console.log("Signup status:", response.status);
      console.log("Signup response:", data);

      if (!response.ok) {
        throw new Error(
          data.detail || "Unable to create account."
        );
      }

      // =========================
      // SIGNUP SUCCESS
      // =========================

      onSignup(data.user);

    } catch (err) {
      console.error("Signup error:", err);

      setError(
        err.message ||
        "Unable to connect with the server."
      );

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">

      <div className="auth-card">

        {/* =========================
            LOGO
        ========================= */}

        <div className="auth-logo">

          <div className="logo-icon">
            ✦
          </div>

          SkillRoute <span>AI</span>

        </div>


        {/* =========================
            HEADER
        ========================= */}

        <div className="auth-header">

          <h1>
            Create your account 🚀
          </h1>

          <p>
            Start your personalized learning journey.
          </p>

        </div>


        {/* =========================
            ERROR
        ========================= */}

        {error && (
          <div className="auth-error">
            ⚠️ {error}
          </div>
        )}


        {/* =========================
            FORM
        ========================= */}

        <form onSubmit={handleSubmit}>

          {/* NAME */}

          <div className="auth-field">

            <label>
              Name
            </label>

            <input
              type="text"
              placeholder="Enter your name"
              value={name}
              onChange={(e) =>
                setName(e.target.value)
              }
              disabled={loading}
            />

          </div>


          {/* EMAIL */}

          <div className="auth-field">

            <label>
              Email
            </label>

            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
              disabled={loading}
            />

          </div>


          {/* PASSWORD */}

          <div className="auth-field">

            <label>
              Password
            </label>

            <input
              type="password"
              placeholder="Create a password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              disabled={loading}
            />

          </div>


          {/* CONFIRM PASSWORD */}

          <div className="auth-field">

            <label>
              Confirm Password
            </label>

            <input
              type="password"
              placeholder="Confirm your password"
              value={confirmPassword}
              onChange={(e) =>
                setConfirmPassword(e.target.value)
              }
              disabled={loading}
            />

          </div>


          {/* =========================
              SUBMIT
          ========================= */}

          <button
            type="submit"
            className="auth-submit"
            disabled={loading}
          >

            {loading ? (
              "Creating account..."
            ) : (
              <>
                Create Account
                <span>→</span>
              </>
            )}

          </button>

        </form>


        {/* =========================
            LOGIN
        ========================= */}

        <div className="auth-divider">
          <span>OR</span>
        </div>


        <div className="auth-switch">

          <span>
            Already have an account?
          </span>

          <button
            type="button"
            onClick={onLogin}
            disabled={loading}
          >
            Sign in
          </button>

        </div>


        {/* =========================
            BACK
        ========================= */}

        <button
          type="button"
          className="auth-back"
          onClick={onBack}
          disabled={loading}
        >
          ← Back to home
        </button>

      </div>

    </div>
  );
}

export default Signup;