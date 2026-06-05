---
name: ZiZuBot bug tracking log
description: Full dry-run audit log — all bugs found and fixes applied across all sessions
---

# ZiZuBot Bug Tracking Log

## Session 1 — Plugin dry-run (21 bugs fixed, 15 commits)

### Commits (oldest → newest)
8ad361ba, 096a01d5, d988bb5d, 40278c01, 549df7ac, 4bb3e851, 8194baee,
93fa92c7, 76c59db9, 8165c3ba, f79a95f9, d2c4d963

### Documentation commits
ead682f3 — root README.md
23151528 — .env.example (PUBLIC_URL, SESSION, AUTO_APPROVE, WELCOME_DM, etc.)
b2cb9bb3 — ZiZubot/README.md (Koyeb guide, full command list, project map)

---

## Session 2 — Database layer + utils.py dry-run (4 bugs fixed, 4 commits)

### Files analyzed
- database/ia_filterdb.py ✓
- database/users_chats_db.py ✓ (clean — no bugs)
- database/filters_mdb.py ✓
- database/connections_mdb.py ✓ (clean — no bugs)
- database/shortlink_db.py ✓ (clean — no bugs)
- utils.py ✓
- plugins/index.py ✓

### Bugs fixed

#### BUG-22: filters_mdb.py find_filter — UnboundLocalError on no-match (CRITICAL)
- File: database/filters_mdb.py
- Root cause: Variables (reply_text, btn, fileid, alert) assigned inside `async for`
  loop body. If no document matches, loop body never executes → UnboundLocalError on
  `return reply_text, ...`. Caught by bare `except Exception` and returns None — fragile.
  Also iterated ALL matching docs keeping only the last (should use find_one).
- Fix: Replaced find+loop with find_one + explicit None check
- Commit: 278ff9d9

#### BUG-23: utils.py get_poster — blocking IMDB calls freeze event loop (HIGH)
- File: utils.py
- Root cause: imdb.search_movie() and imdb.get_movie() are synchronous blocking calls
  from the cinemagoer library. Running them directly on the asyncio event loop blocks
  ALL bot message handling for 2-5 seconds per IMDB lookup.
- Fix: Wrapped both calls with asyncio.to_thread() to run in a thread pool
- Commit: 1b707634

#### BUG-24: utils.py list_to_str — trailing comma on last element (MEDIUM)
- File: utils.py
- Root cause: ' '.join(f'{elem}, ' for elem in k) — the format string always adds
  ", " after each element including the last, producing "Action, Drama, " not "Action, Drama"
- Fix: Changed to ', '.join(str(elem) for elem in items)
- Commit: 1b707634

#### BUG-25: ia_filterdb.py get_search_results — parameter shadows Python builtin (LOW)
- File: database/ia_filterdb.py
- Root cause: Parameter named `filter` shadows Python's builtin filter() function.
  Not a runtime crash but prevents use of builtin in same scope and confuses linters.
- Fix: Renamed parameter to `db_filter` throughout function
- Commit: 4e8ee1fc

#### BUG-26: plugins/index.py send_for_index — FloodWait falls through to get_messages (MEDIUM)
- File: plugins/index.py
- Root cause: After FloodWait on bot.get_chat(), code slept then fell through to
  bot.get_messages() with an unverified chat_id — could index wrong/inaccessible chat.
- Fix: Return error message to user instead, asking them to retry after rate limit clears
- Commit: 0ca6150c

---

## All files coverage status
| File | Status |
|------|--------|
| bot.py | ✓ Fixed (d2c4d963) |
| info.py | ✓ Clean |
| utils.py | ✓ Fixed (1b707634) |
| Script.py | ✓ Clean |
| database/ia_filterdb.py | ✓ Fixed (4e8ee1fc) |
| database/users_chats_db.py | ✓ Clean |
| database/filters_mdb.py | ✓ Fixed (278ff9d9) |
| database/connections_mdb.py | ✓ Clean |
| database/shortlink_db.py | ✓ Clean |
| plugins/commands.py | ✓ Fixed |
| plugins/pm_filter.py | ✓ Fixed |
| plugins/filters.py | ✓ Fixed |
| plugins/shortlink.py | ✓ Fixed |
| plugins/index.py | ✓ Fixed (0ca6150c) |
| plugins/broadcast.py | ✓ Fixed |
| plugins/etc.py | ✓ Fixed |
| plugins/misc.py | ✓ Fixed |
| plugins/channel.py | ✓ Minor deferred |
| plugins/p_ttishow.py | ✓ Fixed (f79a95f9) |
| plugins/auto_approve.py | ✓ Fixed (76c59db9) |
| plugins/banned.py | ✓ Fixed (8165c3ba) |
| plugins/connection.py | ✓ Fixed |
| plugins/inline.py | ✓ Minor deferred |
| plugins/mov_ser_latest.py | ✓ Fixed |
| plugins/webcode.py | ✓ Clean |

## Deferred / low-risk items
- channel.py: empty list filter passes to Media.find({}) — fetches all docs
- inline.py: no DB error handling on search query
- pm_filter.py: spurious NEXT button when results < max (cosmetic)
- delete tasks lost on restart (architectural limitation)
