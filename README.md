# Visual AI Browser Agent

A consent-first Chrome Manifest V3 extension that observes browser interactions and sends structured activity events to a local Python API backed by SQLite.

## What it tracks

- Page views, clicks, form submissions, and input changes
- Page URL/title, CSS-like target selector, viewport, and click coordinates
- Password values are always replaced with `[redacted]`
- Tracking is disabled by default and must be enabled from the extension popup

## Architecture

```text
Chrome page
  └─ content.js captures DOM events
      └─ background.js checks opt-in state
          └─ POST /api/events
              └─ Python HTTP API validates payload
                  └─ SQLite events table
```

The extension behaves as the browser-side visual agent sensor. It converts visible UI activity into structured observations. The service worker is the policy and transport layer, while the backend provides validation, logging, persistence, and a query API.

## Run locally

Requirements: Python 3.10+ and Google Chrome.

1. Start the API:

   ```bash
   python3 backend/app.py
   ```

2. Open `chrome://extensions`, enable **Developer mode**, choose **Load unpacked**, and select the `extension` folder.
3. Open the extension popup and click **Start tracking**.
4. Browse a normal HTTP/HTTPS page and interact with it.
5. Inspect captured events:

   ```bash
   curl http://localhost:8787/api/events
   ```

The SQLite database is created at `backend/activity.db`.

## API

### `POST /api/events`

Required JSON fields: `sessionId`, `eventType`, and `pageUrl`. Optional fields include `pageTitle`, `target`, `textValue`, and `metadata`.

### `GET /api/events?limit=100`

Returns recent events in reverse chronological order. The maximum limit is 500.

### `GET /health`

Returns API and database status.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Demo flow

1. Start the backend and load the unpacked extension.
2. Enable tracking in the popup.
3. Visit `https://example.com` and click the page.
4. Call `GET /api/events` and confirm `page_view` and `click` records exist.
5. Pause tracking and verify new activity is no longer stored.

## Deployment

- **Backend:** Run `python3 backend/app.py` behind an HTTPS reverse proxy or container platform. Set `PORT` and `VISUAL_AGENT_DB` as needed.
- **Extension:** Replace `API_URL` in `extension/background.js` with the deployed HTTPS endpoint and update `host_permissions` in `extension/manifest.json`.
- **Production hardening:** Add authentication, per-user tenancy, encrypted storage, retention controls, explicit domain allowlists, rate limiting, and a privacy policy before collecting real user data.

## Design choices

- Manifest V3 for current Chrome compatibility
- No third-party runtime dependencies for simple setup
- SQLite for a portable, inspectable database
- Opt-in collection and password redaction for safer defaults
- Separate content, policy/transport, API, and persistence layers for easy extension

## Repository history

The project is intentionally developed through multiple focused commits so reviewers can inspect the full implementation history. Commits should not be squashed.
