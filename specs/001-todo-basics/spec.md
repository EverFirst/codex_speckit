# Feature Specification: TODO 기본 관리

**Feature Branch**: `001-todo-basics`  
**Created**: 2025-11-11  
**Status**: Draft  
**Input**: User description: "싱글 유저 TODO API에서 CRUD와 완료 토글을 제공한다."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - TODO 작성 및 목록 조회 (Priority: P1)

싱글 유저로서 해야 할 일을 빠르게 기록하고 최신 순으로 목록을 확인하고 싶다.

**Why this priority**: 모든 후속 기능의 기반이 되는 기본 사용 흐름이다.

**Independent Test**: FastAPI TestClient로 POST /todos 후 GET /todos 호출 시 새 항목이 상단에 포함되는지 검증.

**Acceptance Scenarios**:

1. **Given** 제목과 선택적 설명을 포함한 유효한 페이로드, **When** POST /todos 호출, **Then** 201 응답과 고유 ID·기본 completed=false가 반환.
2. **Given** 기존 항목이 다수 존재, **When** GET /todos 호출, **Then** 생성일 역순 정렬과 전체 개수 반환.

---

### User Story 2 - TODO 상세 조회 및 수정 (Priority: P2)

사용자는 특정 TODO의 상세 정보를 보고 제목·설명·마감 여부를 수정할 수 있어야 한다.

**Why this priority**: 기록한 항목을 유지보수할 수 있어야 목록이 유용하다.

**Independent Test**: 기존 항목에 대해 GET /todos/{id}, PUT /todos/{id} 순서로 호출해 변경된 데이터와 updated_at 타임스탬프 갱신을 확인.

**Acceptance Scenarios**:

1. **Given** 존재하는 ID, **When** GET /todos/{id}, **Then** 200 응답과 전체 속성이 반환.
2. **Given** 제목 10자, 설명 100자, **When** PUT /todos/{id} 요청, **Then** 200 응답과 동일 데이터·updated_at 갱신.
3. **Given** 존재하지 않는 ID, **When** GET 또는 PUT 호출, **Then** 404 응답과 에러 메시지.

---

### User Story 3 - 완료 토글 및 삭제 (Priority: P3)

사용자는 작업 완료 여부를 빠르게 전환하고 더 이상 필요 없는 항목을 삭제할 수 있어야 한다.

**Why this priority**: 완료 관리와 정리는 생산성 도구의 핵심 반복 동작이다.

**Independent Test**: PATCH /todos/{id}/status 로 완료 토글 후 DELETE /todos/{id} 요청이 204를 반환하고 목록에서 제거되었는지 확인.

**Acceptance Scenarios**:

1. **Given** 완료되지 않은 항목, **When** PATCH /todos/{id}/status 로 completed=true 전환, **Then** completed_at 기록과 200 응답.
2. **Given** 완료된 항목, **When** 동일 엔드포인트 호출, **Then** completed=false, completed_at=null.
3. **Given** 고유 ID, **When** DELETE /todos/{id}, **Then** 204 응답과 이후 조회 시 404.

---

### Edge Cases

- 제목이 비어 있거나 공백뿐일 때 400과 구체적 메시지 반환.
- 제목 200자 초과 또는 설명 2000자 초과 시 422 Validation error 처리.
- 중복 ID 삭제·갱신 요청은 모두 404 및 에러 바디 `{ "detail": "TODO not found" }`.
- 완료 토글은 멱등하지 않으므로 상태 전환 후 최신 상태가 응답 본문에 항상 포함되어야 한다.
- DB 오류 등 서버 예외는 500과 추적 ID를 포함한 에러 응답을 남기고 로그에 기록.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 시스템은 `POST /todos` 엔드포인트를 제공하고 제목(title), 선택 설명(description)을 수신하여 TODO 항목을 생성해야 한다.
- **FR-002**: 제목은 1~200자의 UTF-8 문자열이어야 하며 필수 항목이다; 위반 시 422 Validation Error를 반환해야 한다.
- **FR-003**: 설명은 0~2000자 제한의 선택 필드이며 없을 경우 빈 문자열로 저장하지 않고 `null`로 유지해야 한다.
- **FR-004**: 생성 시 `completed`는 기본 false, `created_at`과 `updated_at`은 ISO-8601 UTC로 기록되고 고유 ID(UUID v4)로 응답해야 한다.
- **FR-005**: `GET /todos`는 전체 항목을 `created_at` 내림차순으로 반환하고 페이지 제한이 없음을 명시하는 `total_count`를 포함해야 한다.
- **FR-006**: `GET /todos/{id}`는 존재하지 않을 경우 404를, 성공 시 해당 항목 전체 속성을 반환해야 한다.
- **FR-007**: `PUT /todos/{id}` 또는 `PATCH /todos/{id}`는 제목·설명·completed를 수정하며 동일한 유효성 규칙을 적용하고 `updated_at`을 갱신해야 한다.
- **FR-008**: `PATCH /todos/{id}/status`는 완료 전환 전용 API로 completed와 completed_at를 토글하며 변경 후 상태를 응답에 포함해야 한다.
- **FR-009**: `DELETE /todos/{id}`는 항목을 영구 제거하고 204 No Content를 반환해야 하며 복구 기능은 제공하지 않는다.
- **FR-010**: 모든 엔드포인트는 JSON 응답을 사용하고 성공/실패 시 적절한 HTTP 상태 코드(200/201/204/400/404/422/500)를 준수해야 한다.
- **FR-011**: 오류 응답에는 `detail` 메시지와 가능한 경우 `error_code`를 포함해 클라이언트가 원인을 파악할 수 있게 해야 한다.
- **FR-012**: Swagger UI(OpenAPI 3.0)는 모든 엔드포인트와 스키마를 최신 상태로 노출해야 한다.

### Key Entities *(include if feature involves data)*

- **TodoItem**
  - `id` (UUID v4): 고유 식별자, 서버에서 생성.
  - `title` (string, 1-200): 필수 제목.
  - `description` (string|null, <=2000): 선택 설명.
  - `completed` (bool): 완료 여부.
  - `created_at` (datetime UTC): 생성 시각.
  - `updated_at` (datetime UTC): 마지막 수정 시각.
  - `completed_at` (datetime|null): 완료된 경우 타임스탬프.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 정상 입력으로 POST /todos 호출 시 100%가 201 응답을 받고 새 항목이 즉시 GET /todos 결과에 반영된다.
- **SC-002**: p95 응답 시간이 GET /todos 및 POST /todos 모두 200ms 이내(로컬 SQLite, 50개 항목 기준)여야 한다.
- **SC-003**: 유효하지 않은 제목/설명으로 요청 시 100%가 422와 명확한 detail 메시지를 반환한다.
- **SC-004**: CRUD 및 상태 토글에 대한 pytest 통합 테스트 커버리지가 최소 70% 라인을 유지한다.
- **SC-005**: Swagger UI에서 모든 엔드포인트가 호출 가능하고 example payload가 최신 스키마와 일치한다.

## Assumptions

- 단일 사용자 환경으로 인증/권한은 v1 범위에 포함되지 않는다.
- 동시 수정 충돌은 고려하지 않으며 최신 요청이 항상 승리한다.
- SQLite를 기본 DB로 사용하며 로컬 개발/테스트는 인메모리 모드로 수행한다.
