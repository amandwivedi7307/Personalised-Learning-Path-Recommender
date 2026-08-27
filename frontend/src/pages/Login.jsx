import { useState } from "react";
import "../App.css";

function Login({
  onLogin,
  onSignup,
  onBack,
  onForgotPassword,
}) {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  // =========================
  // LOGIN
  // =========================

  const handleLogin = async (e) => {

    e.preventDefault();

    setError("");


    if (!email || !password) {

      setError(
        "Please enter your email and password."
      );

      return;
    }


    try {

      setLoading(true);


      const response = await fetch(
        "https://skillroute-ai-qpwc.onrender.com/login",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            email: email,
            password: password,
          }),
        }
      );


      const result =
        await response.json();


      if (!response.ok) {

        throw new Error(
          result.detail ||
          "Invalid email or password."
        );

      }


      // =========================
      // LOGIN SUCCESS
      // =========================

      onLogin(result.user);


    } catch (err) {

      console.error(err);

      setError(
        err.message ||
        "Unable to login."
      );

    } finally {

      setLoading(false);

    }

  };


  return (

    <div className="auth-page">

      <div className="auth-container">


        {/* =========================
            HEADER
        ========================= */}

        <div className="auth-header">

          <div className="auth-logo">

            <div className="logo-icon">
              ✦
            </div>

            SkillRoute <span>AI</span>

          </div>


          <h1>
            Welcome <span>back.</span>
          </h1>


          <p>
            Sign in to continue your
            personalized learning journey.
          </p>

        </div>



        {/* =========================
            FORM
        ========================= */}

        <form
          className="auth-form"
          onSubmit={handleLogin}
        >


          {/* ERROR */}

          {error && (

            <div className="auth-error">

              ⚠️ {error}

            </div>

          )}



          {/* EMAIL */}

          <div className="form-group">

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

          <div className="form-group">

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



          {/* =========================
              OPTIONS
          ========================= */}

          <div className="auth-options">

            <label>

              <input
                type="checkbox"
              />

              Remember me

            </label>


            {/* FORGOT PASSWORD */}

            <button
              type="button"
              className="forgot-password"
              onClick={onForgotPassword}
              disabled={loading}
            >

              Forgot password?

            </button>

          </div>



          {/* =========================
              LOGIN BUTTON
          ========================= */}

          <button
            type="submit"
            className="auth-button"
            disabled={loading}
          >

            {loading
              ? "Signing in..."
              : "Sign In →"}

          </button>



          {/* =========================
              SIGNUP
          ========================= */}

          <div className="auth-switch">

            Don't have an account?

            <button
              type="button"
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
            type="button"
            className="auth-back"
            onClick={onBack}
            disabled={loading}
          >

            ← Back to Home

          </button>


        </form>

      </div>

    </div>

  );

}

export default Login;