import { useState } from "react";
import "../App.css";

function ForgotPassword({ onBack }) {

  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {

    e.preventDefault();

    if (!email.trim()) {
      setMessage("Please enter your email address.");
      return;
    }

    try {

      setLoading(true);
      setMessage("");

      const response = await fetch(
        "http://127.0.0.1:8000/forgot-password",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            email: email,
          }),
        }
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(
          result.detail || "Unable to process request."
        );
      }

      setMessage(
        "If this email is registered, a password reset link has been sent."
      );

    } catch (error) {

      console.error(error);

      setMessage(
        "Unable to connect with the server."
      );

    } finally {

      setLoading(false);

    }
  };


  return (

    <div className="auth-page">

      <div className="auth-card">

        {/* LOGO */}

        <div className="auth-logo">

          <div className="logo-icon">
            ✦
          </div>

          SkillRoute <span>AI</span>

        </div>


        {/* HEADING */}

        <div className="auth-heading">

          <div className="auth-badge">
            🔐 ACCOUNT RECOVERY
          </div>

          <h1>
            Forgot your <span>password?</span>
          </h1>

          <p>
            Enter your registered email address
            and we'll help you reset your password.
          </p>

        </div>


        {/* FORM */}

        <form onSubmit={handleSubmit}>

          <div className="form-group">

            <label>
              Email Address
            </label>

            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />

          </div>


          <button
            type="submit"
            className="auth-submit-btn"
            disabled={loading}
          >

            {loading
              ? "Sending..."
              : "Send Reset Link →"}

          </button>

        </form>


        {/* MESSAGE */}

        {message && (

          <div className="auth-message">
            {message}
          </div>

        )}


        {/* BACK */}

        <button
          type="button"
          className="back-login-btn"
          onClick={onBack}
        >
          ← Back to Login
        </button>

      </div>

    </div>

  );
}

export default ForgotPassword;