const form = document.getElementById("chat-form");
const input = document.getElementById("message-input");
const messages = document.getElementById("messages");
const send = document.getElementById("send");
const reset = document.getElementById("reset");

function addMessage(role, text) {
  const row = document.createElement("div");
  row.className = `message ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  row.appendChild(bubble);
  messages.appendChild(row);
  messages.scrollTop = messages.scrollHeight;
  return row;
}
function setBusy(busy) {
  send.disabled = busy;
  input.disabled = busy;
  send.textContent = busy ? "…" : "↑";
}
async function sendMessage(text) {
  const message = text.trim();
  if (!message || send.disabled) return;
  addMessage("user", message);
  input.value = "";
  setBusy(true);
  const typing = addMessage("assistant", "Thinking…");
  typing.querySelector(".bubble").classList.add("typing");
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message})
    });
    const data = await response.json();
    typing.remove();
    if (!response.ok) throw new Error(data.error || "Request failed.");
    addMessage("assistant", data.answer + (data.sources?.length ? "\n\nReference notes: " + data.sources.join(", ") : ""));
  } catch (error) {
    typing.remove();
    addMessage("assistant", error.message || "Something went wrong. Please try again.");
  } finally {
    setBusy(false);
    input.focus();
  }
}
form.addEventListener("submit", event => {
  event.preventDefault();
  sendMessage(input.value);
});
input.addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});
document.querySelectorAll("[data-prompt]").forEach(button => {
  button.addEventListener("click", () => sendMessage(button.dataset.prompt));
});
reset.addEventListener("click", async () => {
  try { await fetch("/api/reset", {method: "POST"}); } catch (_) {}
  messages.innerHTML = "";
  addMessage("assistant", "New chat started. What would you like to know about buying or maintaining a car?");
  input.focus();
});
