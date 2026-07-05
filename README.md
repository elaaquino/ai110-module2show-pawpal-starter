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

Sample test output:

```
# Paste your pytest output here
```

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

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
