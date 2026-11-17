## Purpose

Makes sure that text and markup people put into a document can never run as script in another user's browser when the document is edited, saved or viewed.

## ADDED Requirements

### Requirement: Typed markup stays literal text
Characters a user types into the editor, including `<`, `>` and `&`, SHALL be saved and shown as literal text. They SHALL NOT be turned into HTML elements.

#### Scenario: User types an HTML tag
- **WHEN** a user types `<img src=x onerror=alert(1)>` into a document and saves it
- **THEN** reopening the document in edit mode and in view mode shows that exact text, no image element is created, and no script runs

### Requirement: Displayed document HTML is sanitized
Wherever the frontend displays stored document HTML as markup, it SHALL first remove script elements, event-handler attributes (`on*`), `javascript:` URLs and other active content. Formatting produced by the editor (headings, bold, italic, lists, links, colours, alignment) SHALL be kept.

#### Scenario: Stored HTML contains a script payload
- **WHEN** a document's stored content contains `<p>Hi</p><img src=x onerror=alert(1)><script>alert(2)</script>` and a user opens it in view mode
- **THEN** "Hi" is displayed, the `onerror` attribute and the `<script>` element are removed, and no script runs

#### Scenario: Normal formatting is kept
- **WHEN** a document containing a heading, bold text, a bulleted list and an `https://` link is opened in view mode
- **THEN** the heading, bold text, list and working link are all displayed

#### Scenario: javascript: link is neutralised
- **WHEN** stored content contains `<a href="javascript:alert(1)">click</a>` and is opened in view mode
- **THEN** the link text "click" is displayed, and clicking it does not run script
