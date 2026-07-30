const status = document.querySelector("#status");
const toggle = document.querySelector("#toggle");
const render = (enabled) => {
  status.textContent = enabled ? "Tracking is active for browser pages." : "Tracking is paused.";
  toggle.textContent = enabled ? "Pause tracking" : "Start tracking";
  toggle.className = enabled ? "on" : "off";
};
chrome.storage.local.get("trackingEnabled", ({ trackingEnabled }) => render(Boolean(trackingEnabled)));
toggle.addEventListener("click", () => chrome.storage.local.get("trackingEnabled", ({ trackingEnabled }) => {
  chrome.storage.local.set({ trackingEnabled: !trackingEnabled }, () => render(!trackingEnabled));
}));
