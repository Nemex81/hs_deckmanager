# Implementation Notes - Robustness Fixes and Cleanup

## Overview
This document tracks the implementation of robustness fixes and cleanup for the Hearthstone Deck Manager project.

## Completed Tasks

### Commit 1: Fix current_window recursion bug ✅
- **Date**: 2026-01-31
- **Issue**: The `current_window` property in `DefaultController` was calling itself recursively (`return self.current_window()`), causing infinite recursion.
- **Fix**: Changed line 40 in `scr/controller.py` to `return self.win_controller.get_current_window()` to properly delegate to the window controller.
- **Impact**: This critical bug would cause a stack overflow whenever the `current_window` property was accessed. The fix ensures proper retrieval of the current window from the window controller.

## Pending Tasks

### Commit 2: Centralize DB config and remove global session
- Centralize DB path/config in `scr/user_settings.py`
- Update `scr/db.py` to use centralized DB path/URL
- Remove hardcoded `DATABASE_PATH` from `db.py`
- Remove global `session` variable from `db.py`
- Update `scr/models.py` to not import global session
- Update `scr/views/collection_view.py` to use `db_session()` context manager
- Update documentation

### Commit 3: Consolidate logging configuration
- Update `utyls/logger.py` to use `LOGS_DIR` from `user_settings.py`
- Remove multiple `basicConfig` calls
- Ensure single logging initialization
- Update `main.py` to use centralized logging config
- Update documentation

### Commit 4: Update .gitignore and DB documentation
- Add `hearthstone_decks_storage.db` to `.gitignore`
- Add `data/` directory to `.gitignore`
- Update `README.md` with DB location and initialization instructions
- Document where DB will live and how to initialize it

### Commit 5: Add pytest tests
- Create tests for DB operations (CRUD)
- Create tests for parsing logic
- Ensure tests use centralized DB config
- Document how to run tests in `README.md`

## Notes
- All changes are designed to be minimal and surgical
- Each commit is logically independent and includes documentation updates
- Tests will be added to validate core functionality after refactoring
