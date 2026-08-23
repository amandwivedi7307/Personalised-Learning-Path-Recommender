import { useState } from "react";
import "../App.css";

function Login({ onLogin, onSignup, onBack }) {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  // =========================
  // LOGIN
  // =========================

  const handleSubmit = async (e) => {

    e.preventDefault();

    setError("");


    // Validation
    if (!email.trim() || !password) {

      setError(
        "Please enter your email and password."
      );

      return;
    }


    setLoading(true);


    try {

      // =========================
      // CALL FASTAPI
      // =========================

      const response = await fetch(
        "http://127.0.0.1:8000/login",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            email: email.trim(),
            password: password,
          }),
        }
      );


      const data = await response.json();


      // =========================
      // LOGIN FAILED
      // =========================

      if (!response.ok) {

        throw new Error(
          data.detail ||
          "Invalid email or password."
        );

      }


      // =========================
      // LOGIN SUCCESS
      // =========================

      console.log(
        "Login successful:",
        data.user
      );


      // Save logged-in user
      localStorage.setItem(
        "skillroute_user",
        JSON.stringify(data.user)
      );


      // Send user to App.jsx
      onLogin(data.user);


    } catch (err) {

      console.error(
        "Login error:",
        err
      );


      setError(
        err.message ||
        "Unable to connect with server."
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
            Welcome back 👋
          </h1>

          <p>
            Continue your personalized
            learning journey.
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
              placeholder="Enter your password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              disabled={loading}
            />

          </div>


          {/* OPTIONS */}

          <div className="auth-options">

            <label>

              <input
                type="checkbox"
              />

              Remember me

            </label>


            <button
              type="button"
              className="forgot-password"
              onClick={() =>
                alert(
                  "Password reset will be added soon."
                )
              }
            >
              Forgot password?
            </button>

          </div>


          {/* LOGIN BUTTON */}

          <button
            type="submit"
            className="auth-submit"
            disabled={loading}
          >

            {loading ? (

              "Signing in..."

            ) : (

              <>
                Sign In
                <span>→</span>
              </>

            )}

          </button>


        </form>


        {/* =========================
            DIVIDER
        ========================= */}

        <div className="auth-divider">

          <span>
            OR
          </span>

        </div>


        {/* =========================
            SIGNUP
        ========================= */}

        <div className="auth-switch">

          <span>
            Don't have an account?
          </span>

          <button
            onClick={onSignup}
            disabled={loading}
          >
            Create account
          </button>

        </div>


        {/* =========================
            BACK
        ========================= */}

        <button
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

export default Login;