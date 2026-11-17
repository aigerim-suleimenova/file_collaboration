## Context

See proposal.md (Why) for the defects. These facts about the current code shape the approach:

- **Backend:** FastAPI 0.109 on Python 3.11 (Docker), SQLModel with a **synchronous** `Session` (`app/core/db.py`), and Alembic at `app/alembic` (the location set in `alembic.ini`).
  - JWT is HS256 from `app/core/security.py`.
  - User access tokens carry `sub=<user id>`. Share tokens carry `file_id=<id>` and no `sub`.
  - Uvicorn runs as a single process (`CMD uvicorn ...` with no `--workers`).
- **Frontend:** Vue 3 + Quill 2 + `yjs` 13, `y-quill` and `y-websocket` 1.5 (client).
  - `QuillEditor.vue` builds a `WebsocketProvider(host, room, ydoc)`, where `host` defaults to `ws://127.0.0.1:1234`.
  - After creating the provider, it calls `ytext.delete(0, len)` and inserts `textContent`. This is the cause of formatting loss and duplication.
  - The Vite dev server already proxies `/api/v1` with `ws: true`.
- **Who can edit:** only the owner can reach a file through the REST API (`get_file_by_id_for_user`). Other people collaborate through share links (`?share_token=` in `FileEditor.vue`).
- **Missing field:** `UserPublic` exposes `id`, `email` and `is_superuser`, but not `full_name`.

## Goals / Non-Goals

**Goals:**
- One backend process handles REST and Yjs sync, with authorization checked before any document bytes are sent.
- The Yjs wire protocol stays compatible with the existing `y-websocket` client, so the frontend keeps `WebsocketProvider` and `y-quill`.
- Collaborative state survives restarts, and initial content is loaded once with formatting kept.
- Focused automated tests prove the authorization rules.

**Non-Goals:**
- Viewer vs editor roles for share links. In this change, share tokens grant edit access, matching the existing "share for collaboration" flow. Roles come in a later change.
- Revoking access on a socket that is already open when its token expires. Tokens are checked at connect time only.
- Running several backend processes (see Risks).
- Converting Yjs state to HTML on the server.
- Broad test coverage, CI hardening, and moving to TypeScript or React (later changes).

## Decisions

### 1. Yjs sync in FastAPI using `pycrdt-websocket`
Add `pycrdt` and `pycrdt-websocket`. Pin their exact versions at implementation time to the newest releases that support Python 3.11, and record them in `requirements.txt`. A new `app/services/collab.py` owns one module-level `WebsocketServer` (`auto_clean_rooms=False`), started and stopped from the FastAPI lifespan. The route `@router.websocket("/collab/{file_id}")` authenticates first, then wraps the Starlette `WebSocket` in a small adapter (`path`, `send(bytes)`, `recv() -> bytes`, `__aiter__`) and calls `server.serve(adapter)`. The room name is the `file_id`.

- *Why:* pycrdt is built on Yrs and speaks the same y-sync and awareness protocol as `y-websocket`, so the client changes are limited to the URL and parameters.
- *Alternatives considered:*
  - (a) Keep the Node server and add JWT checks. The user chose against this: it keeps two services, saves nothing to the database, and leaves the project description inaccurate.
  - (b) Write the y-sync protocol by hand. More code, and easy to get wrong.

### 2. Authorization before the hand-off, with accept-then-close for error codes
In the route:
1. Read `token` or `share_token` from the query string.
2. Decode with `jose`.
3. Load the `File` through a session from the overridable `get_db` dependency.
4. Apply the rules from `specs/realtime-collaboration`.

Browsers cannot see close codes if the handshake is rejected (they get 1006). So on failure the route calls `websocket.accept()` and then immediately `websocket.close(code=4001|4003|4004)`, before any Yjs message. Only an authorized socket is passed to the Yjs server.

- `user_id` (or `None` for a share token) is stored on the adapter for logging.
- An access token must also map to an active `User`, or the connection gets `4001`.

### 3. Client stops reconnecting on auth failures
`y-websocket` reconnects automatically. `QuillEditor.vue` listens for `provider.on('connection-close', ev => ...)`. When the code is 4001, 4003 or 4004, it calls `provider.disconnect()` and shows "You don't have access to live editing" or "Session expired", instead of retrying forever.

### 4. Saving to Postgres via a `yjs_state` column with debounced snapshots
Add `File.yjs_state: bytes | None` (`LargeBinary`, nullable) in a new Alembic revision chained after the current head. Existing rows are left alone.

- **Load:** when a room is first created for `file_id`, load `yjs_state` from the database and `ydoc.apply_update(state)` it before the room starts serving.
- **Save:** observe the room's `ydoc` and, after a change, save within 2 s. This is throttled, not debounced: continuous typing still saves every 2 s, while a debounce would wait until typing stops. When the last client leaves a room, save immediately and then remove the room. On lifespan shutdown, save all rooms.
- **What is saved:** the full state `ydoc.get_update()` (a snapshot, not an append-only log). The database write runs through `anyio.to_thread.run_sync` with a fresh `Session`, because the database layer is synchronous.

- *Why snapshots over a per-update `YStore`:* documents are small, rows stay bounded, there is no compaction job, and there is one column instead of a new table.
- *Alternative:* `pycrdt_websocket.ystore.SQLiteYStore`. Rejected because it adds a second database next to Postgres.
- *Trade-off:* up to about 2 s of edits can be lost if the process crashes (not a clean shutdown). Acceptable for this app.

### 5. Initial content loaded on the client, after sync, through the binding
Remove the `ytext.delete/insert(plainText)` block. Create the `QuillBinding` immediately (no 5 s "connected" race). Then, on the provider's first `sync` event with `isSynced === true`: if `ytext.length === 0` and the stored HTML (`modelValue`) is not empty, run `quill.setContents(quill.clipboard.convert({ html }), 'user')`. The binding sends this to Yjs with formatting.

- After that, the saved `yjs_state` is the source of truth, so the load never happens again.
- *Why on the client:* converting HTML to a Quill Delta needs Quill's parser, which exists only in the browser.
- *Risk:* see "Two first-openers".

### 6. Remove the legacy JSON channel
Delete:
- `app/services/websocket_manager.py`;
- the routes in `app/api/routes/websocket.py` (`/ws/{file_id}`, `/file/{id}/users`, `/file/{id}/broadcast`);
- `FileManagerDep` and `get_file_manager` in `deps.py`;
- in `FileEditor.vue`: `connectWebSocket`, `disconnectWebSocket`, `wsRef` and the `content_update` sender.

The backend never sent the `live_preview` messages that this channel handled, and the frontend connected to the wrong path, so nothing that works today depends on it. Presence and cursors come from Yjs awareness.

- *Alternative:* fix the `Dict()` crash and make the manager a singleton. Rejected: it would be a second real-time channel that duplicates awareness and has no consumer.

### 7. Presence identity
- Add `full_name` to `UserPublic`. This is additive and does not break anything.
- `QuillEditor` takes a `user` prop `{ id, name }` from `authStore.user`, using `full_name || email`. For share-token sessions it uses `{ id: <random id kept in sessionStorage>, name: 'Guest' }`.
- The colour is a deterministic HSL hue from a hash of `id`, so it is stable across reconnects.
- Awareness is set **before** connecting, so the first awareness update already carries the name.

### 8. Content safety on the frontend
- Remove every `&lt;`/`&gt;`/`&amp;` → character replacement in `QuillEditor.vue` (in both `setQuillContent` and the `text-change` handler).
- Emit `quill.root.innerHTML` (Quill already escapes typed text) for `update:modelValue`. `getSemanticHTML()` was considered and rejected: in Quill 2.0.3 it turns every space into `&nbsp;`, and those would come back as non-breaking spaces when the content is re-seeded.
- Add `dompurify`, and replace `v-html="file.content"` in `FileEditor.vue` with a computed value from `DOMPurify.sanitize(html, { USE_PROFILES: { html: true } })`. Its defaults remove `<script>`, `on*` attributes and `javascript:` URLs.
- Do the same for any other `v-html` found at implementation time (currently only one).
- *Why sanitize on the client and not the server:* every place that renders HTML is in the client, and DOMPurify is the established tool. Server-side sanitizing of `quill_content` can be added later as defence in depth.

### 9. URLs and configuration
- `VITE_COLLAB_WS` defaults to `` `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/api/v1/collab` ``. This works in dev through the Vite proxy and in Docker through the nginx `/api` proxy.
- The standalone Render frontend sets `VITE_COLLAB_WS=wss://<backend-host>/api/v1/collab`.
- The provider gets `params: { token }` or `params: { share_token }`, so the URL becomes `/api/v1/collab/<file_id>?token=...`.
- Remove the `collab:server*` npm scripts, `start-collab*.sh`, `collab.config.js` (if nothing else uses it) and `COLLAB_WS_HOST/PORT`.

### 10. Tests
Add `backend/tests/` with a `conftest.py`:
- an in-memory SQLite engine (`StaticPool`) that overrides `get_db`, plus the session factory used by the save code;
- `TestClient`;
- fixtures for `user_a`, `user_b`, `file_of_a`, `access_token(user)` and `share_token(file)`.

The tests use `client.websocket_connect(...)` and check the close code (`WebSocketDisconnect.code`) for each spec scenario. They check that accepted connections receive a y-sync message (the first byte is message type `0`). They also cover the 404s on the removed routes and a save/load round trip using pycrdt directly. Frontend behaviour is checked manually here (the checklist is in tasks.md). Vitest and Playwright come in later changes.

## Risks / Trade-offs

- **[Tokens in the query string]** → Browsers can't set headers on WebSockets. Mitigation: access tokens are short-lived, and uvicorn access logs do not log query strings by default for WebSocket upgrades. Check this during implementation, and if they do, document turning them off. A later change can switch to a one-time ticket endpoint.
- **[Rooms live in one process's memory]** → With more than one worker, users on different workers would not see each other. Mitigation: keep a single uvicorn worker (current setup) and add a comment next to `CMD` explaining why. A Redis-backed fan-out is a later change.
- **[Two first-openers]** → If two clients open a document with no saved state within the same sync round-trip, both may load the initial content and duplicate it. The window is tiny and only happens once per document. Mitigation: load only after `synced`, and record this in the README's known limitations.
- **[Share tokens grant edit access and are not revoked mid-session]** → A leaked link allows edits until it expires (default 4 h). Mitigation: expiry is enforced at connect time. Roles and revocation come in a later change.
- **[HTML snapshot can lag behind live state]** → View mode and `/public/files` read `quill_content`, which updates only when the owner saves. Guest edits show in the editor but not in view mode until then. Recorded as a known limitation, to be addressed later with server-side rendering or periodic saves.
- **[pycrdt-websocket API changes between minor versions]** → Mitigation: pin exact versions and keep all use of the library inside `app/services/collab.py`.

## Migration Plan

1. Deploy the backend: install the new dependencies and run `alembic upgrade head`, which adds the nullable `yjs_state` column. This is safe for existing rows.
2. Deploy the frontend with `VITE_COLLAB_WS` pointing at the backend (`wss://<backend>/api/v1/collab` on Render).
3. Stop and remove any running Node `y-websocket` process.
4. Documents load their initial content the first time someone opens them.
5. **Rollback:** redeploy the previous images. `alembic downgrade -1` drops `yjs_state`, which loses only collaborative snapshots. `quill_content` is untouched.

## Open Questions

- Exact pinned versions of `pycrdt` and `pycrdt-websocket`. Choose these at implementation time (see Decision 1). This does not affect the specs or tasks.
