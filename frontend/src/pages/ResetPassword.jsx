import { useState } from "react";
import "../App.css";

function ResetPassword({ onBack }) {

  // =========================
  // GET TOKEN FROM URL
  // =========================

  const token =
    window.location.pathname
      .split("/")
      .pop();


  const [password, setPassword] = useState("");

  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [message, setMessage] =
    useState("");

  const [error, setError] =
    useState("");


  // =========================
  // RESET PASSWORD
  // =========================

  const handleResetPassword = async (e) => {

    e.preventDefault();

    setError("");
    setMessage("");


    // Password check

    if (!password || !confirmPassword) {

      setError(
        "Please enter both passwords."
      );

      return;
    }


    // Confirm password

    if (password !== confirmPassword) {

      setError(
        "Passwords do not match."
      );

      return;
    }


    // Minimum length

    if (password.length < 6) {

      setError(
        "Password must be at least 6 characters."
      );

      return;
    }


    try {

      setLoading(true);


      // =========================
      // API REQUEST
      // =========================

      const response = await fetch(
        "http://127.0.0.1:8000/reset-password",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({

            token: token,

            new_password: password,

          }),
        }
      );


      const result =
        await response.json();


      if (!response.ok) {

        throw new Error(
          result.detail ||
          "Unable to reset password."
        );

      }


      // =========================
      // SUCCESS
      // =========================

      setMessage(
        "Password reset successfully!"
      );

      setPassword("");
      setConfirmPassword("");


      // 2 sec baad login page
      setTimeout(() => {

        onBack();

      }, 2000);


    } catch (err) {

      console.error(err);

      setError(
        err.message ||
        "Something went wrong."
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

            ✦ SkillRoute <span>AI</span>

          </div>


          <h1>

            Reset your <span>password</span>

          </h1>


          <p>

            Create a new password
            for your account.

          </p>

        </div>



        {/* =========================
            FORM
        ========================= */}

        <form
          className="auth-form"
          onSubmit={handleResetPassword}
        >


          {/* ERROR */}

          {error && (

            <div className="auth-error">

              ⚠️ {error}

            </div>

          )}



          {/* SUCCESS */}

          {message && (

            <div className="auth-success">

              ✓ {message}

            </div>

          )}



          {/* NEW PASSWORD */}

          <div className="form-group">

            <label>
              New Password
            </label>


            <input
              type="password"
              placeholder="Enter new password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              disabled={loading}
            />

          </div>



          {/* CONFIRM PASSWORD */}

          <div className="form-group">

            <label>
              Confirm Password
            </label>


            <input
              type="password"
              placeholder="Confirm new password"
              value={confirmPassword}
              onChange={(e) =>
                setConfirmPassword(e.target.value)
              }
              disabled={loading}
            />

          </div>



          {/* RESET BUTTON */}

          <button
            type="submit"
            className="auth-button"
            disabled={loading}
          >

            {loading
              ? "Resetting..."
              : "Reset Password →"}

          </button>



          {/* BACK */}

          <button
            type="button"
            className="auth-back"
            onClick={onBack}
          >

            ← Back to Login

          </button>


        </form>

      </div>

    </div>

  );

}

export default ResetPassword;