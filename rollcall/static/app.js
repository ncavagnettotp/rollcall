// Rollcall's only JavaScript besides htmx. No inline scripts: the content security policy
// allows scripts from this server only.
"use strict";

// htmx 2 ignores 4xx/5xx responses by default, so a failed save would look like nothing
// happened. Let them swap: the server aims error fragments at #messages (HX-Retarget).
document.addEventListener("htmx:beforeSwap", (event) => {
  if (event.detail.xhr.status >= 400) {
    event.detail.shouldSwap = true;
    event.detail.isError = false;
  }
});

// The server could not be reached at all (network down, server restarting).
document.addEventListener("htmx:sendError", () => {
  const messages = document.getElementById("messages");
  if (!messages) return;
  const notice = document.createElement("article");
  notice.setAttribute("role", "alert");
  notice.className = "error-message";
  notice.textContent = "Rollcall could not be reached. Check the connection and try again.";
  messages.replaceChildren(notice);
});
