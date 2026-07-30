# Chrome Verification Checklist

- Open `chrome://extensions`
- Enable Developer mode
- Load the repository's `extension` directory
- Confirm Chrome reports no manifest or service-worker errors
- Start the local backend
- Enable tracking from the popup
- Visit an HTTP/HTTPS page
- Generate page-view, click, input-change, and form-submit activity
- Confirm the events appear in `GET /api/events`
- Enter a password and confirm the stored value is `[redacted]`
- Pause tracking and confirm no new records are added
