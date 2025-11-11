# Feature Specification: TODO Advanced Field Management

**Feature Branch**: `001-todo-field-management`  
**Created**: 2025-11-11  
**Status**: Draft  
**Input**: User description: "TODO advanced field management: optional due dates, priority (low/medium/high), per-item category, and up to 10 tags with validation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Set deadlines and priority when creating todos (Priority: P1)

When I create or update a TODO item I can optionally assign a due date and select a priority so that I can see what is urgent and when it is due.

**Why this priority**: Deadlines and priority directly drive scheduling decisions; without them advanced fields deliver no value.

**Independent Test**: Create todos via `POST /todos` with different due-date and priority combinations, then verify via `GET /todos/{id}` that the values persist and defaults are applied.

**Acceptance Scenarios**:

1. **Given** a valid TODO payload, **When** I submit `due_date="2025-12-31"` and `priority="high"`, **Then** the API returns 201 and subsequent GET calls surface those exact values.
2. **Given** I omit `priority`, **When** I create the TODO, **Then** the stored item shows `priority="medium"` as the default.
3. **Given** I provide an invalid due date such as `2025-13-01`, **When** I call `POST /todos`, **Then** the API responds 400 with a validation error explaining the ISO `YYYY-MM-DD` requirement.

---

### User Story 2 - Maintain a single category per TODO (Priority: P2)

As a user I want to add, change, or remove a category label (e.g., Work, Personal, Study) from each TODO so that I can group items in filters or reports.

**Why this priority**: Categorization increases information scent for queues and is valuable after core deadline/priority support.

**Independent Test**: Update an existing TODO via `PUT /todos/{id}` setting, changing, and clearing the `category` field while ensuring other fields remain untouched.

**Acceptance Scenarios**:

1. **Given** a TODO without a category, **When** I send `category="Work"` via PUT, **Then** the updated item returns `category="Work"` on all GET endpoints.
2. **Given** a TODO with `category="Study"`, **When** I send `category=null`, **Then** the stored category becomes `null` and responses omit or return `null` without errors.

---

### User Story 3 - Manage a bounded tag list per TODO (Priority: P3)

As a user I can attach up to 10 short tags to a TODO, view them, and ensure duplicates are rejected so that I can later search or filter by those tags.

**Why this priority**: Tags add flexible metadata but are secondary to core fields; bounding and validation prevents bloated payloads.

**Independent Test**: Issue PUT/POST requests that add between 1 and 10 tags, then attempt to add duplicates or an 11th tag to confirm 400 errors and verify GET endpoints return tags in the stored order.

**Acceptance Scenarios**:

1. **Given** a TODO with zero tags, **When** I supply `tags=["frontend","quick-win"]`, **Then** both tags are persisted and returned as a list on GET calls.
2. **Given** a TODO already containing `["backend"]`, **When** I attempt to add another `"backend"` tag, **Then** the API responds 400 with a duplicate-tag error.
3. **Given** a TODO with 10 tags, **When** I attempt to append an 11th, **Then** the API rejects the request citing the maximum tag count.

---

### Edge Cases

- Due date supplied without zero-padded month/day (e.g., `2025-7-1`) must be rejected as non-ISO.
- Past due dates that are otherwise valid (e.g., yesterday) must be accepted to support backlog imports.
- Category strings consisting only of whitespace should be treated as removal rather than stored text.
- Tags must be normalized to lowercase before validation, so inputs like `"Work"` and `"work"` will be treated as duplicates and rejected.
- Bulk GET of legacy TODOs with no advanced fields must still return successfully with `null`/default values without backfilling data.
- Simultaneous updates that reduce and add tags must preserve uniqueness after the full replacement.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `POST /todos` and `PUT /todos/{id}` MUST accept optional fields `due_date`, `priority`, `category`, and `tags` in addition to existing CRUD payload attributes.
- **FR-002**: When provided, `due_date` MUST match ISO 8601 `YYYY-MM-DD`; invalid formats or impossible dates MUST return HTTP 400 with a descriptive validation error.
- **FR-003**: Clients MUST be able to remove an existing due date by sending `due_date=null`, and the API MUST persist `null` in storage.
- **FR-004**: `priority` MUST accept only `low`, `medium`, or `high` (case-insensitive) and default to `medium` whenever omitted.
- **FR-005**: `category` MUST store up to 50 UTF-8 characters after trimming whitespace; inputs exceeding 50 characters MUST trigger HTTP 400.
- **FR-006**: Sending `category=null` or an empty string MUST clear the category without affecting other fields.
- **FR-007**: `tags` MUST be stored as an ordered array with a maximum of 10 entries; each tag MUST be non-empty ASCII/UTF-8 up to 20 characters after trimming and will be normalized to lowercase before persistence.
- **FR-008**: The API MUST reject requests where the provided tag list contains duplicates after lowercase normalization, with an error message explaining the conflict.
- **FR-009**: The API MUST reject requests where more than 10 tags are provided and include the maximum count in the error payload.
- **FR-010**: `GET /todos` and `GET /todos/{id}` MUST always return the new fields (`due_date`, `priority`, `category`, `tags`) for every item, defaulting to `null`, `"medium"`, `null`, and an empty array for legacy records.
- **FR-011**: Data migration MUST add nullable columns (or equivalent fields) for due date, priority (default medium), category, and a tag association table/JSON column without altering existing rows.
- **FR-012**: Swagger/OpenAPI documentation MUST be updated to describe the new fields, their formats, defaults, and validation errors so that API consumers can self-serve.
- **FR-013**: `PUT /todos/{id}` MUST interpret the supplied `tags` array as the complete desired list, replacing any existing tags after normalization rather than performing incremental merges.
- **FR-014**: Validation MUST accept past `due_date` values (including today or earlier) when they satisfy the ISO format, enabling historical backlog imports and late entries.

### Key Entities *(include if feature involves data)*

- **TodoItem**: Represents a single task with attributes `id`, `title`, `description`, `completed`, `due_date (nullable date)`, `priority (enum: low|medium|high)`, `category (nullable varchar(50))`, and `tags (ordered collection)`.
- **TagAssignment**: Represents the association between a `todo_id` and a tag value, enforcing uniqueness per TODO and storing the user-specified ordering for serialization.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of POST/PUT requests with valid due dates, priority, category, and tags persist and are retrievable without data loss across subsequent GET requests.
- **SC-002**: 100% of POST/PUT requests with invalid formats (date, priority enum, category >50 chars, tag >20 chars, duplicate tags after normalization, >10 tags) return HTTP 400 with field-specific error codes.
- **SC-003**: P95 latency for POST/PUT/GET endpoints that include advanced fields remains under 200 ms after validation is added, measured in a staging load test.
- **SC-004**: Legacy TODOs created before this feature remain readable and editable with zero schema- or serialization-related errors in regression suites.
- **SC-005**: Automated test coverage touching advanced field validations and serialization stays at or above 70%, satisfying the stated coverage floor.

## Clarifications
### Session 2025-11-11

- Q: How should tag duplicate detection treat casing when validating tags arrays? ??A: Normalize all tags to lowercase before storage/validation.
- Q: How should the API handle tag updates when clients call PUT /todos/{id}? ??A: Clients send full tag list; server replaces existing tags with normalized input.
- Q: Should the API allow due_date values earlier than today? ??A: Allow any valid ISO date, even if already past.

