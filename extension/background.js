const API_URL = "http://localhost:8787/api/events";

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({ trackingEnabled: false, sessionId: crypto.randomUUID() });
});

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type !== "TRACK_EVENT") return;
  chrome.storage.local.get(["trackingEnabled", "sessionId"], async (settings) => {
    if (!settings.trackingEnabled) return sendResponse({ skipped: true });
    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...message.payload, sessionId: settings.sessionId })
      });
      sendResponse({ ok: response.ok });
    } catch (error) {
      console.error("Visual Agent API unavailable", error);
      sendResponse({ ok: false, error: error.message });
    }
  });
  return true;
});
