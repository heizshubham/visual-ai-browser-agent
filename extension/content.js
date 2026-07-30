const selectorFor = (element) => {
  if (!element || !element.tagName) return "unknown";
  const id = element.id ? `#${element.id}` : "";
  const classes = [...element.classList].slice(0, 2).map((name) => `.${name}`).join("");
  return `${element.tagName.toLowerCase()}${id}${classes}`;
};

const emit = (eventType, target, extra = {}) => {
  chrome.runtime.sendMessage({
    type: "TRACK_EVENT",
    payload: {
      eventType,
      pageUrl: location.href,
      pageTitle: document.title,
      target: selectorFor(target),
      metadata: { viewport: `${innerWidth}x${innerHeight}`, ...extra }
    }
  }).catch(() => {});
};

emit("page_view", document.documentElement);
document.addEventListener("click", (event) => emit("click", event.target, { x: event.clientX, y: event.clientY }), true);
document.addEventListener("submit", (event) => emit("form_submit", event.target), true);
document.addEventListener("change", (event) => {
  const target = event.target;
  const safeValue = target.type === "password" ? "[redacted]" : String(target.value || "").slice(0, 120);
  chrome.runtime.sendMessage({ type: "TRACK_EVENT", payload: {
    eventType: "input_change", pageUrl: location.href, pageTitle: document.title,
    target: selectorFor(target), textValue: safeValue, metadata: { inputType: target.type || target.tagName }
  }}).catch(() => {});
}, true);
