## Architecture

### Persistence Layer
- **ORM Models**: `UserRow`, `LearningProfileRow`, `PersonaMemoryRow`, `VocabularyEntryRow`, `CefrProgressRow` in `mellow/db/models/`
- **Repository Pattern**: Abstract base class (ABC) + `SqlAlchemy*Repository` implementation in `mellow/db/repos/`
- **Converters**: `profile_to_row`/`row_to_profile`, `mem_to_row`/`row_to_mem`, `row_to_dict` bridge Pydantic ↔ ORM
- **Session Management**: Request-scoped `get_db_session` dependency in `api/deps.py` with auto commit/rollback/close

### Key Decisions
- **D1**: Session lifecycle — each request gets a fresh `AsyncSession` via FastAPI `Depends(get_db_session)`, auto-committed on success, auto-rolled-back on exception
- **D2**: Auth Provider uses `session_factory` — each auth operation creates a new session, avoiding stale session issues
- **D3**: Scheduler uses DB query — `PersonaMemoryRepository.list_all()` instead of in-memory `_memories` dict
- **D4**: JWT secret — empty default triggers auto-generation of dev-only random secret + warning
- **D5**: SQLite WAL mode — enabled via SQLAlchemy event listener on `connect`
- **D6**: Vocabulary unique constraint — `UniqueConstraint('user_id', 'word')` + `IntegrityError` handling
- **D7**: LLM phrases — try LLM generation first, fallback to hard-coded phrase map on any failure
- **D8**: ASR/TTS — Volcano Engine HTTP API with `NotImplementedError` when unconfigured

### Component Diagram
```
FastAPI Route
    ↓ Depends(get_db_session) → AsyncSession
    ↓ Depends(get_container) → Container
Container
    → session_factory (async_sessionmaker)
    → auth(session_factory) → JWTAuthProvider
    → profile_manager(repo) → LearningProfileManager
    → memory_manager(repo) → PersonaMemoryManager
```