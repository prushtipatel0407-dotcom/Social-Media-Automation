document.getElementById("resetForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const password = document.getElementById("password").value;
  const confirm = document.getElementById("confirmPassword").value;
  const messageEl = document.getElementById("message");

  messageEl.textContent = "";

  if (password !== confirm) {
    messageEl.textContent = "Passwords do not match";
    messageEl.style.color = "red";
    return;
  }

  const params = new URLSearchParams(window.location.search);
  const token = params.get("token");

  if (!token) {
    messageEl.textContent = "Invalid or missing reset token";
    messageEl.style.color = "red";
    return;
  }

  try {
    const response = await fetch("/api/auth/reset-password/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        token: token,
        new_password: password,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      messageEl.textContent = data.message || "Password reset failed";
      messageEl.style.color = "red";
      return;
    }

    messageEl.textContent = "✅ Password reset successful!";
    messageEl.style.color = "green";

    setTimeout(() => {
      window.location.href = "/login.html"; // optional
    }, 2000);

  } catch (error) {
    messageEl.textContent = "Server error. Try again.";
    messageEl.style.color = "red";
    console.error(error);
  }
});
