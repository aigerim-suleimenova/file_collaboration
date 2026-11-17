## Purpose

Lets authorized people edit the same document at the same time and see each other's changes and cursors live. Edits are saved by the backend and survive reloads and restarts.

## ADDED Requirements

### Requirement: Collaboration endpoint served by the backend
The system SHALL provide real-time document sync over a WebSocket at `/api/v1/collab/{file_id}` on the same backend service that serves the REST API. Collaborative editing SHALL NOT depend on any separately run sync server.

#### Scenario: Editing works with only the standard services running
- **WHEN** only the backend, database and frontend are running and a user opens a document they own in edit mode
- **THEN** the editor connects to `/api/v1/collab/{file_id}` and reports a connected collaboration status

### Requirement: Collaboration connections are authenticated
The collaboration endpoint SHALL accept a connection only if the request includes one of the following:
- a `token` query parameter with a valid, unexpired user access token for an active user who owns the file; or
- a `share_token` query parameter with a valid, unexpired share token whose `file_id` claim equals the requested `file_id`.

Any other connection SHALL be closed before any document data is sent, using these close codes:
- `4001`: no credentials, or credentials that are invalid or expired;
- `4003`: valid credentials that do not grant access to this file;
- `4004`: the file does not exist.

#### Scenario: Owner connects with access token
- **WHEN** the file's owner connects with `?token=<valid access token>`
- **THEN** the connection is accepted and the current document state is synced to the client

#### Scenario: No credentials
- **WHEN** a client connects to `/api/v1/collab/{file_id}` with no `token` and no `share_token`
- **THEN** the server closes the connection with code `4001` and sends no document data

#### Scenario: Expired or tampered token
- **WHEN** a client connects with an access token or share token that is expired or has an invalid signature
- **THEN** the server closes the connection with code `4001`

#### Scenario: Authenticated user who is not the owner
- **WHEN** user B connects with a valid access token to a file owned by user A, with no share token
- **THEN** the server closes the connection with code `4003` and sends no document data

#### Scenario: Share token for a different file
- **WHEN** a client connects to file X with a valid share token whose `file_id` claim is file Y
- **THEN** the server closes the connection with code `4003`

#### Scenario: Share token for this file
- **WHEN** a client connects to file X with a valid, unexpired share token whose `file_id` claim is file X
- **THEN** the connection is accepted and the client can read and edit the document

#### Scenario: Unknown file
- **WHEN** a client with otherwise valid credentials connects to a `file_id` that does not exist
- **THEN** the server closes the connection with code `4004`

### Requirement: Concurrent edits converge
All clients connected to the same document SHALL receive each other's edits live. After all edits have propagated, every client SHALL show the same content, including formatting.

#### Scenario: Two editors type at the same time
- **WHEN** two authorized clients are connected to the same document and both type at different positions at the same time
- **THEN** both clients show both insertions, in the same order and with the same formatting

### Requirement: Collaborative document state is saved
The system SHALL save each document's collaborative state in the database while it is being edited. A client that connects to a document SHALL receive the latest saved state, even after every client has disconnected and the backend has restarted.

#### Scenario: Reload keeps edits
- **WHEN** a user edits a document, closes the editor, and reopens it
- **THEN** the editor shows the edited content with its formatting

#### Scenario: Backend restart keeps edits
- **WHEN** a user edits a document, waits for the save interval to pass, and the backend process restarts
- **THEN** a client that reconnects receives the edited content

### Requirement: Initial content is loaded once without destroying shared state
When a document has no saved collaborative state, its existing stored content SHALL be loaded into the shared document once, keeping its formatting. Opening the editor SHALL NOT clear or overwrite shared content that already exists.

#### Scenario: First open of an existing document
- **WHEN** the owner opens a document that has stored HTML content (with headings and bold text) but no collaborative state
- **THEN** the editor shows that content with its headings and bold formatting

#### Scenario: Second client joins a document with content
- **WHEN** a second client opens a document whose shared state already contains text
- **THEN** the content is not duplicated, cleared or converted to plain text for any connected client

### Requirement: Presence shows who is editing
Each connected client SHALL share presence information, and other clients SHALL see a cursor labelled with that user's display name (full name, or email if no name is set; or "Guest" for share-token connections). Each user SHALL have a stable colour across reconnects.

#### Scenario: Collaborator cursor is labelled
- **WHEN** user "Aigerim" and a second client are editing the same document
- **THEN** the second client sees a cursor labelled "Aigerim"

#### Scenario: Colour stays the same after a reconnect
- **WHEN** a user disconnects and reconnects to the same document
- **THEN** their cursor colour is the same as before

### Requirement: Unauthenticated legacy collaboration endpoints are not exposed
The system SHALL NOT expose any HTTP or WebSocket endpoint that lists a document's active users, broadcasts messages to a document's collaborators, or accepts collaboration traffic without the authentication defined above. The endpoints `WS /api/v1/ws/{file_id}`, `GET /api/v1/file/{file_id}/users` and `POST /api/v1/file/{file_id}/broadcast` SHALL return 404 (or close the WebSocket without accepting it).

#### Scenario: Broadcast endpoint removed
- **WHEN** a client sends `POST /api/v1/file/{file_id}/broadcast` with any body, authenticated or not
- **THEN** the response status is 404

#### Scenario: Users endpoint removed
- **WHEN** a client sends `GET /api/v1/file/{file_id}/users`
- **THEN** the response status is 404
