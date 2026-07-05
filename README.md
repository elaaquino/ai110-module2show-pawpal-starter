# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

================================================
  Today's Schedule - 2026-06-23
  Owner: Ada Lovelace
================================================
     08:00  Rex    Joint medication (5 min, HIGH)
     09:00  Rex    Morning walk (45 min, HIGH)
     12:00  Mia    Lunch feeding (10 min, MEDIUM)
     15:00  Mia    Feather toy play (15 min, LOW)
------------------------------------------------
  Why this plan:
  Plan for 2026-06-23: 4 task(s), 75 min scheduled. ...
================================================

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Tests cover chronological sorting time, recurrence logic, and conflict detection. Additonally, the AI suggested and explained extra tests. This includes test untimed tasks, touching windows are not a conflict, testing budget/priority based on time for certain tasks, and a tes tthat raises a runtime error on an empty explainPlan().

Sample test output:

```
================================================================================================== test session starts ===================================================================================================
platform win32 -- Python 3.14.6, pytest-9.1.0, pluggy-1.6.0
rootdir: C:\Users\keool\Documents\GitHub\ai110-module2show-pawpal-starter
plugins: anyio-4.14.0
collected 10 items                                                                                                                                                                                                        

tests\test_pawpal.py ..........                                                                                                                                                                                     [100%]

=================================================================================================== 10 passed in 0.04s ===================================================================================================
```
Im at a 45/5 confidence level in the system's reliability!


## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

1. Daily plan generation (priority-weighted, packed greedily within a time budget) → Scheduler.generateSchedule

2. Plan explanation / "why this plan" (human-readable rationale) → Scheduler.explainPlan, with the text assembled by Scheduler._buildRationale

3. Chronological sorting of tasks (untimed tasks fall to the end) → sort_by_time (module-level helper)

4. Task filtering by completion status and/or pet name → Owner.findTasks

5. Recurring-task auto-respawn (completing a daily/weekly task spawns the next occurrence) → Pet.completeTask

6. supporting pieces: Task.nextOccurrence (clones a fresh incomplete copy), Task.isRecurring (gate), Pet._nextTaskId (unique id like t4#2), Owner.completeTask (UI-facing delegator)
Time-conflict detection (overlap-based, non-fatal warnings) → Scheduler.detectConflicts

7. supporting pieces: Scheduler._window (task → [start, end) in minutes), Scheduler._fmt (minutes → HH:MM)
Task field validation on construction (duration > 0, fixed-time needs a start) → Task.__post_init__

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. Set owner info — edit the owner's name (persists across reruns via st.session_state).
2. Add a pet — name + species; the app shows the running list of current pets.
3. Add a task — pick the pet, then set title, duration, priority, type, recurrence, and an optional preferred/fixed time. Invalid combos (fixed-time without a time) are blocked with an error.
4. Browse tasks — a sorted table with filter-by-pet and filter-by-status (All/Pending/Completed) dropdowns.
5. Live conflict banner — as tasks are added, overlaps are surfaced immediately (st.warning), or a green "no conflicts" confirmation.
6. Mark a task complete — completing a recurring task shows the spawned next occurrence.
7. Build schedule — set a daily time budget, generate the ordered plan (table), see conflicts, and read the "Why this plan" explanation.

Example workflow

1. Enter the owner's name.
2. Add a pet → "Rex" (dog).
3. Add a task → "Morning walk," 45 min, HIGH, daily, preferred 09:00.
4. Add a few more tasks (feeding, meds, grooming) for one or more pets.
5. Watch the Tasks table re-sort by time and the live conflict banner update.
6. Set a daily time budget and click Generate schedule.
7. View Today's Schedule, any conflict warnings, and the explanation of why tasks were ordered/skipped.
8. Click Mark complete on the walk → its next daily occurrence is spawned automatically.

Key Scheduler behaviors shown

Recurrence: completing t4 (daily meds) spawns t4#2 at the same 08:00, incomplete — original stays as "done."
Sorting: the jumbled insertion order (09:00, 08:00, flexible, 08:00, 15:00, 12:00, 09:00) is reordered chronologically, flexible last.
Filtering: pending-only, completed-only, and by-pet ("rex") views.
Priority + budget packing: 115/120 min used; fixed-time tasks placed first, flexible tasks ordered HIGH→LOW.
Conflict warning (non-fatal): Rex's 09:00 walk vs. Mia's 09:00 feeding flagged as "different pets" — the plan still generates.

Sample CLI output

====================================================
  Recurrence on completion
====================================================
  Rex has 3 task(s). Completing 't4' (Joint medication, DAILY)...
  -> spawned next occurrence 't4#2': Joint medication at 08:00 (complete=False).
  Rex now has 4 task(s): the done original stays, the fresh occurrence is added.
====================================================

====================================================
  Sorting & Filtering
====================================================
  Insertion order:
       09:00  Rex    Morning walk (HIGH, pending)
       08:00  Rex    Joint medication (HIGH, done)
    flexible  Rex    Brush coat (LOW, pending)
       08:00  Rex    Joint medication (HIGH, pending)
       15:00  Mia    Feather toy play (LOW, pending)
       12:00  Mia    Lunch feeding (MEDIUM, pending)
       09:00  Mia    Brunch feeding (MEDIUM, pending)
----------------------------------------------------
  Sorted by time (sort_by_time):
       08:00  Rex    Joint medication (HIGH, done)
       08:00  Rex    Joint medication (HIGH, pending)
       09:00  Rex    Morning walk (HIGH, pending)
       09:00  Mia    Brunch feeding (MEDIUM, pending)
       12:00  Mia    Lunch feeding (MEDIUM, pending)
       15:00  Mia    Feather toy play (LOW, pending)
    flexible  Rex    Brush coat (LOW, pending)
----------------------------------------------------
  Pending only (findTasks completed=False):
       08:00  Rex    Joint medication (HIGH, pending)
       09:00  Rex    Morning walk (HIGH, pending)
       09:00  Mia    Brunch feeding (MEDIUM, pending)
       12:00  Mia    Lunch feeding (MEDIUM, pending)
       15:00  Mia    Feather toy play (LOW, pending)
    flexible  Rex    Brush coat (LOW, pending)
  Completed only (findTasks completed=True):
       08:00  Rex    Joint medication (HIGH, done)
----------------------------------------------------
  Rex's tasks (findTasks petName='rex'):
       08:00  Rex    Joint medication (HIGH, done)
       08:00  Rex    Joint medication (HIGH, pending)
       09:00  Rex    Morning walk (HIGH, pending)
    flexible  Rex    Brush coat (LOW, pending)
====================================================

====================================================
  Today's Schedule - 2026-06-23
  Owner: Ada Lovelace
====================================================
     08:00  Rex    Joint medication (5 min, HIGH)
     09:00  Rex    Morning walk (45 min, HIGH)
     09:00  Mia    Brunch feeding (20 min, MEDIUM)
     12:00  Mia    Lunch feeding (10 min, MEDIUM)
     15:00  Mia    Feather toy play (15 min, LOW)
  flexible  Rex    Brush coat (20 min, LOW)
----------------------------------------------------
  Why this plan:
  Plan for 2026-06-23: 6 task(s), 115 min scheduled. Time budget: 115/120 min used. Fixed-time tasks were placed first because they must occur at a set time: Joint medication (08:00), Lunch feeding (12:00). Flexible tasks were ordered by priority (then shortest first): Morning walk [HIGH], Brunch feeding [MEDIUM], Feather toy play [LOW], Brush coat [LOW]. WARNING: time conflict (different pets) - 'Morning walk' (09:00-09:45) overlaps 'Brunch feeding' (09:00-09:20).
====================================================

====================================================
  Conflict detection (non-fatal)
====================================================
  WARNING: time conflict (different pets) - 'Morning walk' (09:00-09:45) overlaps 'Brunch feeding' (09:00-09:20).
====================================================

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
