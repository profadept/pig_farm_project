# Backlog

Branches deferred to be picked up later.

## Bug Fixes
- fix/container-graceful-shutdown — uvicorn ignores SIGTERM on shutdown,
  forces SIGKILL after 10s. Caused by --reload spawning a child process
  plus how uv run wraps the command. Investigate Dockerfile CMD vs
  docker-compose command: field.

## Phase 3 (in progress)
- feat/add-pydantic-schemas — separate request/response models from
  SQLModel table classes. Prevents hashed_password leaking through
  JSON API (audit gap #4).
- feat/add-services — extract business logic from routes into service
  functions. Both API and web routers call the same service.
- refactor/add-routers — split main.py into src/routers/api/ and
  src/routers/web/ per domain.
- feat/add-exception-handling — custom exceptions + FastAPI handlers.
- feat/add-dependencies — extract get_current_user, get_db_session;
  remove unused session params from show_register_page, login_route,
  show_settings_page; consider def over async def where no await exists.

## Cleanup
- chore/add-makefile-fix-target — add `fix` target running
  `uv run ruff check --fix .` for auto-fixing lint issues like
  import sorting without typing the full command.
- chore/standardize-enum-naming — TransactionTypeEnum uses lowercase
  member names (income, expense) while UserRole uses ALL_CAPS (ADMIN,
  STAFF). Check all .income/.expense usages before renaming.
- docs/standardize-docstrings — proper Google-style docstrings across
  all route handlers in main.py.
- chore/add-claude-md — commit CLAUDE.md and docs/ into the repo.

## Phase 4
- chore/test-infrastructure — conftest.py, test DB fixtures, async
  test session setup.
- Tests per service, then per API route, then per web route.

## Phase 5 — New Features
- Redesign transaction tracking to account for weaners separately,
  enabling per-batch income and profit reporting.
- Post-transaction UX: after saving, show option to add another
  transaction without returning to home.
- Split Job/Item unit of measure into separate enum values.
- Extend login session duration (currently 20 min / 1200s); investigate
  why session expires faster than expected.
- feat/add-user-schemas — build UserBase/UserCreate/UserRead when a real
  consumer exists: either a JSON user API endpoint, or when
  feat/add-services extracts registration logic and needs a clean
  input/output contract. Build and test them together with that
  consumer, not speculatively ahead of it.
- All templates.TemplateResponse(name, {"request": ...}) calls in main.py
  use deprecated argument order. Update to TemplateResponse(request, name)
  across every route. Mechanical, touches ~15 call sites.
