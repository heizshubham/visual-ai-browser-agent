const API_URL = "http://localhost:8787/api/events";

const ensureSettings = async () => {
  const settings = await chrome.storage.local.get(["trackingEnabled", "sessionId"]);
  const defaults = {};
  if (typeof settings.trackingEnabled !== "boolean") defaults.trackingEnabled = false;
  if (!settings.sessionId) defaults.sessionId = crypto.randomUUID();
  if (Object.keys(defaults).length) await chrome.storage.local.set(defaults);
  return { ...settings, ...defaults };
};

chrome.runtime.onInstalled.addListener(ensureSettings);
chrome.runtime.onStartup.addListener(ensureSettings);

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type !== "TRACK_EVENT") return;
  ensureSettings().then(async (settings) => {
    if (!settings.trackingEnabled) return sendResponse({ skipped: true });
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...message.payload, sessionId: settings.sessionId })
      });
      const body = await response.json().catch(() => ({}));
      sendResponse({ ok: response.ok, status: response.status, body });
    } catch (error) {
      console.error("Visual Agent API unavailable", error);
      sendResponse({ ok: false, error: error.message });
    }
  });
  return true;
});
