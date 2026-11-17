## Why

The project's main feature, real-time collaborative editing, is broken and insecure in the current code:

- The FastAPI collaboration channel crashes when it starts. `FileConnectionManager.__init__` calls `typing.Dict[...]()`, which raises `TypeError`.
- Even with that fixed, `get_file_manager()` creates a new manager for every request, so connections never share state and broadcasts reach nobody.
- The frontend opens its fallback channel at `/api/v1/files/{id}/ws`, but the backend serves `/api/v1/ws/{id}`, so the channel never connects.
- Live editing actually runs through a separate Node `y-websocket` server hard-coded to `ws://127.0.0.1:1234`. It has **no authentication**: anyone who can reach it can read or write any document by guessing its room name. It does not run in the deployed environment, and it saves nothing.
- Every client that opens a document clears the shared Yjs text and re-inserts the document as plain text. This removes formatting and can duplicate content when two people open the document at once.
- `GET /api/v1/file/{id}/users` and `POST /api/v1/file/{id}/broadcast` need no authentication.
- The editor un-escapes `&lt;`/`&gt;` in saved HTML, and view mode renders that HTML with `v-html`. Anyone with edit access, including someone holding a share link, can store a script that runs in the owner's browser.

This project is the work sample for a job application. A reviewer who opens it should find working, authenticated collaboration that matches how it is described.

## What Changes

- Serve Yjs document sync from FastAPI at `/api/v1/collab/{file_id}` (using `pycrdt-websocket`). This replaces the separate Node `y-websocket` server.
- Check every collaboration connection: a user access token that owns the file, or an unexpired share token whose `file_id` claim matches. Otherwise close with a specific close code.
- Save the Yjs document state to Postgres (a new nullable `file.yjs_state` column), so edits survive server restarts and reloads.
- Load the initial content once, keeping formatting: only when the saved shared document is empty after the first sync, and never by clearing existing shared content.
- **BREAKING** Remove the broken legacy JSON channel: `WS /api/v1/ws/{file_id}`, `GET /api/v1/file/{file_id}/users`, `POST /api/v1/file/{file_id}/broadcast`, `FileConnectionManager`, and the frontend `connectWebSocket` fallback. Yjs awareness handles presence and cursors.
- Show the signed-in user's name and a stable colour in collaborator cursors, instead of `"User"` with a random colour.
- Stop un-escaping HTML entities in the editor, and sanitize document HTML (DOMPurify) before it is rendered with `v-html`.
- Remove the Node collaboration server scripts and `COLLAB_WS_*` settings, and point `VITE_COLLAB_WS` at the backend.
- Add focused pytest tests for collaboration authorization and the removed endpoints.

## Capabilities

### New Capabilities
- `realtime-collaboration`: authenticated, saved real-time co-editing of a document over the backend's Yjs WebSocket endpoint, including access rules, saving, initial loading and presence.
- `document-content-safety`: document HTML is stored and displayed without running content that users wrote.

### Modified Capabilities
<!-- No existing specs in openspec/specs/. -->

## Impact

- **Backend:**
  - `app/api/routes/websocket.py` (replaced by the collaboration route);
  - `app/services/websocket_manager.py` (removed) and a new `app/services/collab.py`;
  - `app/api/deps.py` and `app/api/main.py`;
  - `app/models.py` and a new Alembic migration in `app/alembic/versions/`;
  - `requirements.txt` (adds `pycrdt` and `pycrdt-websocket`);
  - new `tests/`.
- **Frontend:**
  - `src/components/QuillEditor.vue` (provider URL, auth params, loading, awareness, entity handling);
  - `src/views/FileEditor.vue` (remove the legacy WebSocket, sanitize `v-html`);
  - `package.json` (adds `dompurify`, removes the `collab:server*` scripts);
  - `start-collab*.sh` (removed).
- **Config and deploy:**
  - `env.production.example` and `docker-compose.prod.yml` (the `VITE_COLLAB_WS` default and removing `COLLAB_WS_*`).
  - The production frontend must point `VITE_COLLAB_WS` at the backend's `wss://<backend>/api/v1/collab`.
- **API:** removes three endpoints (above). Nothing in the frontend uses them successfully today.
- **Out of scope** (later changes): broader test coverage and honest CI, repo cleanup, viewer/editor roles for share links, migrating to TypeScript or React.
