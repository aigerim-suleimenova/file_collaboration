## 1. Backend dependencies and data model

- [x] 1.1 Add `pycrdt` and `pycrdt-websocket` to `backend/requirements.txt` at exact pinned versions that support Python 3.11. Verify that `pip install -r requirements.txt` succeeds in the `python:3.11-slim` image (`docker build ./backend`).
- [x] 1.2 Add `yjs_state: bytes | None` (LargeBinary, nullable) to `File` in `app/models.py`. Create an Alembic revision in `app/alembic/versions/` chained after the current head. Verify that `alembic upgrade head` then `alembic downgrade -1` then `alembic upgrade head` all succeed against the dev Postgres.
- [x] 1.3 Add `full_name: str | None` to `UserPublic`. Verify that `GET /api/v1/users/me` returns `full_name`.

## 2. Backend test harness (written first, failing)

- [x] 2.1 Create `backend/tests/conftest.py` with an in-memory SQLite engine (`StaticPool`), a `get_db` override, `TestClient`, and fixtures `user_a`, `user_b`, `file_of_a`, `access_token(user)` and `share_token(file, expires)`. Verify that `pytest backend/tests -q` collects the tests without errors.
- [x] 2.2 Write `tests/test_collab_auth.py`, one test per scenario in `specs/realtime-collaboration` "Collaboration connections are authenticated": 4001 for no credentials, expired token and bad signature; 4003 for a non-owner and for a share token on the wrong file; 4004 for an unknown file; accept for the owner and for a matching share token (the first received frame is a y-sync message, byte `0`). Verify that the tests fail before the implementation.
- [x] 2.3 Write `tests/test_legacy_endpoints_removed.py`: `POST /api/v1/file/{id}/broadcast` and `GET /api/v1/file/{id}/users` return 404, and `WS /api/v1/ws/{id}` is not accepted. Verify that they fail before the removal in 4.1.

## 3. Backend collaboration service

- [x] 3.1 Create `app/services/collab.py` with one module-level pycrdt `WebsocketServer` (`auto_clean_rooms=False`) and a Starlette-WebSocket adapter (`path`, `send`, `recv`, `__aiter__`). Start and stop it in a FastAPI lifespan in `app/main.py`. Verify that the app starts with `uvicorn app.main:app` without errors.
- [x] 3.2 Add the route `@router.websocket("/collab/{file_id}")` in a new `app/api/routes/collab.py` and register it in `app/api/main.py`. It must apply the auth rules (design Decision 2: accept, then close with 4001/4003/4004) before calling `server.serve(adapter)`. Verify that all tests in 2.2 pass.
- [x] 3.3 Implement room loading and saving (design Decision 4): load `yjs_state` when a room is created, save at most every 2 s while there are changes (throttled), save and remove the room when the last client leaves, and save all rooms on shutdown. Run the database work via `anyio.to_thread.run_sync`. Verify with `tests/test_collab_persistence.py`: client 1 writes text through a pycrdt doc, disconnects, then a new client receives the same text, and `File.yjs_state` is not null.
- [x] 3.4 Add a comment next to `CMD` in `backend/Dockerfile` and `backend/Dockerfile.prod` explaining that a single worker is required because collaboration rooms live in process memory. Check whether uvicorn logs WebSocket query strings, and if it does, turn that off or document it. Verify by reviewing the Dockerfile diff and a sample log line.

## 4. Remove the legacy channel (backend)

- [x] 4.1 Delete `app/services/websocket_manager.py`, remove the routes in `app/api/routes/websocket.py` (delete the file and its `include_router`), and remove `get_file_manager` and `FileManagerDep` from `app/api/deps.py`. Verify that the tests in 2.3 pass and `grep -r "FileConnectionManager\|FileManagerDep" backend/app` finds nothing.

## 5. Frontend collaboration client

- [x] 5.1 In `QuillEditor.vue`, change the provider to `new WebsocketProvider(collabUrl, documentId, ydoc, { params })`. `collabUrl` comes from `VITE_COLLAB_WS` or, by default, `ws(s)://${location.host}/api/v1/collab`. `params` is `{ token }` or `{ share_token }` (new prop `shareToken`). Remove the `password` option and the `roomName` prefix. Verify in the browser devtools Network → WS that the request goes to `/api/v1/collab/<id>?token=...` and gets status 101.
- [x] 5.2 Remove the `ytext.delete/insert(plainText)` block and the 5 s connection race. Create the `QuillBinding` immediately, and load the initial content once on the first `sync` event when `ytext.length === 0` (design Decision 5). Verify that opening a formatted document shows headings and bold, and that a second tab opening it shows no duplication.
- [x] 5.3 Handle `connection-close` codes 4001/4003/4004 by calling `provider.disconnect()` and showing a clear status message instead of reconnecting. Verify that opening the editor with a tampered `share_token` shows the message and the Network tab shows no repeated reconnect attempts.
- [x] 5.4 Add a `user` prop and set awareness `{ name, color }` before connecting. The colour comes from a hash of the user id. Guests are "Guest" with an id kept in `sessionStorage`. Pass `{ id, name: full_name || email }` from `FileEditor.vue` using `authStore.user`. Verify that two browsers show a cursor labelled with the other user's name, and that the colour stays the same after a reload.
- [x] 5.5 In `FileEditor.vue`, remove `connectWebSocket`, `disconnectWebSocket`, `wsRef` and the `content_update` sender, and pass `shareToken` through to `QuillEditor`. Verify that `grep -n "wsRef\|connectWebSocket" src/views/FileEditor.vue` finds nothing and `npm run build` succeeds.

## 6. Frontend content safety

- [x] 6.1 Remove all `&lt;`/`&gt;`/`&amp;` un-escaping in `QuillEditor.vue` (`setQuillContent` and the `text-change` handler), and emit `quill.root.innerHTML` without un-escaping (see design Decision 8). Verify that typing `<img src=x onerror=alert(1)>`, saving and reopening shows the literal text with no alert.
- [x] 6.2 Add `dompurify` and render `file.content` in `FileEditor.vue` through a computed `DOMPurify.sanitize(html, { USE_PROFILES: { html: true } })`. Apply the same to any other `v-html` (check with `grep -rn "v-html" src`). Verify by setting `quill_content` in the database to the payloads from `specs/document-content-safety`: view mode shows "Hi" and "click" without running script, and a heading, list and https link still display.

## 7. Configuration, scripts and docs

- [x] 7.1 Remove the `collab:server*` scripts from `frontend/package.json`, delete `frontend/start-collab.sh` and `frontend/start-collab-simple.sh`, and delete `frontend/collab.config.js` if nothing imports it (check with `grep`). Verify that `npm run build` succeeds.
- [x] 7.2 Update `env.production.example` and `docker-compose.prod.yml`: `VITE_COLLAB_WS=wss://<backend-host>/api/v1/collab`, and remove `COLLAB_WS_HOST/PORT`. Update the README's collaboration flow and add a "Known limitations" section (single worker, two-first-openers race, HTML snapshot lag, share links grant edit access). Verify that `grep -rnE "(:|port |--port )1234\b|COLLAB_WS_(HOST|PORT)"` (excluding node_modules) finds nothing except docs marked "Outdated". Those are merged or removed in the repo cleanup change. The plain `1234` pattern also matched the dev database password `12345678`.

## 8. End-to-end verification

- [x] 8.1 Run `cd backend && pytest -q`. All tests must pass.
- [x] 8.2 Manual two-browser check with `docker compose up` (no Node server running):
  - the owner and a share-link guest edit at the same time and both see each other's text and labelled cursors;
  - after `docker compose restart backend` the content is still there;
  - a user B access token to A's file is refused (4003).

  Record the result in the change notes.

## Implementation notes

- **Existing bugs fixed along the way** (needed for the specified behaviour):
  - `get_current_user` passed the JWT `sub` to `session.get` as a string (`deps.py`).
  - A `FileEditor` watcher called `syncContent()` after every keystroke, which re-inserted the whole document once the Yjs binding existed.
  - The editor's `:key` changed when content went from empty to non-empty, which remounted the editor mid-typing.
  - Empty documents never mounted the editor (content was `undefined`).
  - The current user was loaded only at login, so after a reload the owner's cursor showed as "Guest".
  - The URL query string (and so the tokens) was logged by uvicorn. Fixed with a redaction filter (`app/core/log_redaction.py`).
- **Found while implementing and left for later changes:**
  - A fresh `alembic upgrade head` fails at `update_file_schema_001`, because `5566abc09711` creates `item`, not `file`.
  - `SECRET_KEY` defaults to a new random value per process, so deployments must set it.
  - The Dockerfile health check calls `/health`, which doesn't exist.
  - There is no ESLint config, so CI's lint step does nothing.
  - The owner's view mode previously read `file.content`, which `GET /files/{id}` never returns. It now reads `quill_content`.
- **Verification run on 2026-11-17** (local backend + Vite against a throwaway Postgres 17 database; Docker was not running):
  - pytest: 21 passed.
  - The real `y-websocket` 1.5.4 client syncs with the server. Owner and share-link guest edits converge. A non-owner gets one `4003` close and does not reconnect; no credentials gives `4001`.
  - Chrome, owner and guest tabs:
    - the stored HTML loaded once with its heading and bold, and was not duplicated when a second tab joined or a tab reloaded;
    - the guest's text appeared live in the owner's tab;
    - the guest's cursor was labelled "Guest" with the same colour after a reload;
    - when a reconnect had an invalid token, the banner showed, editing was disabled and there was exactly one reconnect attempt;
    - in view mode, DOMPurify removed `onerror`, `<script>` and the `javascript:` href, kept the heading, list, bold and https link, and none of the XSS markers ran;
    - typed `<img …>` is saved escaped.
  - Backend restart: the saved Yjs state (198 bytes) brought back the guest's text with formatting.
- **1.1 verified:** `docker build ./backend` succeeds on Python 3.11.18 with `pycrdt` 0.14.13 and `pycrdt-websocket` 0.16.9. The app imports, and all 21 tests pass inside the image.
- **8.2 verified with containers instead of `docker compose`** (agreed with the user, because the compose file has existing bugs: the backend uses `POSTGRES_PORT=5433`, but Postgres listens on 5432 inside the network, and the frontend container's Vite proxy targets its own `localhost:8000`). Both are left for the CI/cleanup change.
  - Setup: the built backend image ran with a throwaway `postgres:15-alpine` container on a private network.
  - The real `y-websocket` client test passed: owner and guest converge, a non-owner gets `4003`, no credentials gives `4001`.
  - After `docker restart` of the backend, the state was saved on shutdown and a fresh client read `"hello from A + B"`.
  - The two-browser UI part was verified earlier against the local backend (see above).
