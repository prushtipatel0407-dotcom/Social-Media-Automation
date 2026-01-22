const form = document.getElementById("resetForm");
const message = document.getElementById("message");

const params = new URLSearchParams(window.location.search);
const token = params.get("token");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirmPassword").value;

  if (!token) {
    message.style.color = "red";
    message.textContent = "Invalid or missing token";
    return;
  }

  if (password !== confirmPassword) {
    message.style.color = "red";
    message.textContent = "Passwords do not match";
    return;
  }

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/auth/reset-password/", 
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          token: token,
          new_password: password, // ✅ REQUIRED BY BACKEND
        }),
      }
    );

    const data = await response.json();

    if (!response.ok) {
      message.style.color = "red";
      message.textContent = data.message || "Reset failed";
    } else {
      message.style.color = "green";
      message.textContent = "Password reset successful 🎉";
    }
  } catch (err) {
    message.style.color = "red";
    message.textContent = "Server error. Try again.";
  }
});
