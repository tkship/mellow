## Requirement: sqlite-persistence

**ID**: REQ-SP-001
All data (users, profiles, memories, vocabulary, CEFR progress) must be persisted to SQLite via SQLAlchemy async. In-memory storage is only for Session Context (by design, short-lived).

**ID**: REQ-SP-002
Each entity must have an ORM model in `mellow/db/models/`, a Repository (abstract + SQLAlchemy impl) in `mellow/db/repos/`, and converter functions bridging Pydantic ↔ ORM.

**ID**: REQ-SP-003
All ORM models must be imported in `mellow/db/models/__init__.py` for `init_db()` to create tables.

**ID**: REQ-SP-004
DI Container injects repos into managers. Each request gets a fresh session via `Depends(get_db_session)` which auto-commits on success and auto-rolls-back on exception.

## Requirement: session-lifecycle

**ID**: REQ-SL-001
`Container.session()` creates a new `AsyncSession` per call. Routes requiring DB writes must use `Depends(get_db_session)` to get a request-scoped session that is properly committed.

**ID**: REQ-SL-002
`JWTAuthProvider` accepts `session_factory` (not a single session) and creates a new session per auth operation.

**ID**: REQ-SL-003
`LearningProfileManager` and `PersonaMemoryManager` accept `session_factory` for future per-operation session creation.

## Requirement: auth-hardening

**ID**: REQ-AH-001
JWT secret must not have a predictable default. Empty string triggers auto-generation of a random dev-only secret with a warning.

**ID**: REQ-AH-002
Knowledge endpoints (`/api/v1/knowledge/lookup`, `/api/v1/knowledge/search`) must require authentication via `Depends(get_current_user)`.

## Requirement: vocabulary-constraint

**ID**: REQ-VC-001
`vocabulary_entries` table must have `UniqueConstraint('user_id', 'word')` enforced at DB level.

**ID**: REQ-VC-002
`SqlAlchemyVocabularyRepository.add_word()` must handle `IntegrityError` by rolling back and returning the existing word.

## Requirement: sqlite-wal

**ID**: REQ-SW-001
SQLite engine must be configured with `PRAGMA journal_mode=WAL` and `PRAGMA foreign_keys=ON` via SQLAlchemy event listener.

## Requirement: scheduler-fix

**ID**: REQ-SF-001
`ProactiveScheduler` must query DB for all memories via `PersonaMemoryRepository.list_all()` instead of accessing the removed `_memories` dict.

## Requirement: volcano-voice

**ID**: REQ-VV-001
ASR/TTS providers must raise `NotImplementedError` with clear message when API keys are not configured.

**ID**: REQ-VV-002
Voice WebSocket must gracefully inform clients when ASR/TTS is unconfigured.