document.addEventListener("DOMContentLoaded", () => {
  const open = document.getElementById("aiOpen");
  const panel = document.getElementById("aiPanel");
  const close = document.getElementById("aiClose");
  const form = document.getElementById("aiForm");
  const input = document.getElementById("aiInput");
  const messages = document.getElementById("aiMessages");

  if (!open || !panel) return;
  open.addEventListener("click", () => {
    panel.classList.add("open");
    panel.setAttribute("aria-hidden", "false");
    input?.focus();
  });
  close?.addEventListener("click", () => {
    panel.classList.remove("open");
    panel.setAttribute("aria-hidden", "true");
  });

  form?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message) return;
    addMessage(message, "user");
    input.value = "";
    const loading = addMessage("Thinking...", "bot");

    try {
      const response = await fetch("/api/ai", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          message,
          language: window.SHADOWNET_LANGUAGE || "Programming"
        })
      });
      const data = await response.json();
      loading.textContent = data.answer || data.error || "The assistant returned no response.";
    } catch (error) {
      loading.textContent = "Connection error. Check the server and try again.";
    }
    messages.scrollTop = messages.scrollHeight;
  });

  function addMessage(text, type) {
    const node = document.createElement("div");
    node.className = `ai-msg ${type}`;
    node.textContent = text;
    messages.appendChild(node);
    messages.scrollTop = messages.scrollHeight;
    return node;
  }
});
