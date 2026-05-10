# Brain API Gallery Deployment

HF Space `cupcake777/tg-webapp-demo` is **DELETED**. Gallery is served by Brain API only.

## Architecture

- **Host**: Brain API at VPS:8080
- **Gallery page**: `/gallery` — renders `gallery_lite.html` via `gallery_page()` in `templates.py`
- **Demo images**: `/gallery/static/` — FastAPI StaticFiles mount pointing to `03_plotting-library/demo_fig/`
- **Feedback API**: `POST /api/gallery/feedback` — writes to `03_plotting-library/gallery_feedback.jsonl`
- **Auth**: Brain token auth (cookie-based for browser, Bearer for API). Unauthenticated → 401.

## Brain API Routes (all auth-protected)

| Endpoint | Purpose |
|----------|---------|
| /login | Login page |
| /review | Proposal review queue |
| /review/{id} | Proposal detail with action buttons |
| /dashboard | Overview (state counts, oldest pending, exports) |
| /pools?tab=cpa | CPA (OpenAI) account pool |
| /pools?tab=grok | Grok (xAI) token pool |
| /gallery | Sci-Fig template gallery with interactive buttons |
| /gallery/static/*.png | Demo images |
| /api/gallery/feedback | POST {chart, action, suggestion} |
| /api/quota | JSON API for CPA data |
| /api/grok | JSON API for Grok data |
| /api/review/* | JSON API for proposals |

Old URLs: `/quota` → 307 → `/pools?tab=cpa`, `/grok` → 307 → `/pools?tab=grok`, `/exports/` removed (merged into dashboard).

## Gallery Interactive Buttons

Each card with a demo image has three buttons backed by `/api/gallery/feedback`:
- **✓ Approve** → POST `{action: "approve"}`
- **✎ Suggest** → expands textarea → POST `{action: "suggest", suggestion: "..."}`
- **✕ Reject** → POST `{action: "reject"}`

Auth: Browser `fetch()` with `credentials: 'same-origin'` (same-origin cookie + Origin header passes CSRF). Bearer token also works.

## CRITICAL: JavaScript in Brain Templates

Python f-strings mangle JS `{{`/`}}`. ALL interactive JS must go in `extra_js` parameter of `_page()` as a **plain string**, NOT inside f-string body:

```python
# WRONG - f-string destroys JS object literals:
body = f"""...<script>fetch({{method: 'POST'}})</script>..."""
# This produces: <script>fetch({method: 'POST'})</script> — BROKEN

# RIGHT - extra_js is a plain string, no escaping issues:
body = "...<div id='app'></div>..."  # HTML in f-string is fine
js_code = """
function myAction() {
  fetch('/api/endpoint', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({key: 'value'})})
}
"""
return _page("Title", body, extra_js=js_code)
```

Also: auth cookie `hermes_auth` is `httponly=True` — JS cannot read it via `document.cookie`. Use `credentials: 'same-origin'` in fetch calls instead of injecting `Authorization: Bearer` from cookies.

## Update Procedure

```bash
# 1. Re-render demo images
cd ../03_plotting-library
for f in templates/*.R; do Rscript "$f"; done

# 2. Restart Brain API to pick up changes
systemctl restart hermes-serve

# 3. Verify
curl -s -H "Authorization: Bearer <token>" http://127.0.0.1:8080/gallery | head -5
```

## Pitfalls

1. **Don't create HF Space for Gallery** — Brain API serves it with auth.
2. **Don't open new VPS ports** — Brain API at 8080 is the single web entry point.
3. **Gallery images use `/gallery/static/{filename}`** — not base64, not relative.
4. **JS must go in `extra_js`** — never inside f-string body, `{{`/`}}` destroys JS syntax.
5. **`credentials: 'same-origin'`** — browser auto-sends auth cookie + Origin header, passes CSRF.
6. **CSRF check**: POST requests need either (a) valid Bearer token, (b) matching Origin/Referer header, or (c) X-CSRF-Token header. Browser fetch with `credentials: 'same-origin'` satisfies (b).
