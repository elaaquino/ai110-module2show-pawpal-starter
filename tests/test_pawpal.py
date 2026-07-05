"""Simple tests for the PawPal system."""

import sys
from datetime import date, time
from pathlib import Path

# Allow importing pawpal_system.py from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from pawpal_system import (
    Owner,
    Pet,
    Priority,
    Recurrence,
    Scheduler,
    Task,
    TaskType,
    sort_by_time,
)


def make_task(taskId: str = "t1") -> Task:
    """Build a basic task for use in tests."""
    return Task(taskId, "p1", TaskType.WALK, "Evening walk", 30, Priority.MEDIUM,
                preferredStart=time(18, 0))


def test_task_completion():
    """markComplete() changes the task's status to done."""
    task = make_task()
    assert task.isComplete is False
    task.markComplete()
    assert task.isComplete is True


def test_task_addition():
    """Adding a task to a Pet increases that pet's task count."""
    pet = Pet("p1", "Rex", "dog", "Labrador", 4, 28.0)
    assert len(pet.tasks) == 0
    pet.addTask(make_task())
    assert len(pet.tasks) == 1


# --- Required: Sorting Correctness -----------------------------------------

def test_sort_by_time_is_chronological():
    """sort_by_time returns timed tasks in ascending start-time order.

    Tasks are built OUT OF ORDER (15:00, 09:00, 12:00) so a no-op or reversed
    implementation would fail. We assert on the returned start times.
    """
    afternoon = Task("t1", "p1", TaskType.ENRICHMENT, "Play", 15, Priority.LOW,
                     preferredStart=time(15, 0))
    morning = Task("t2", "p1", TaskType.WALK, "Walk", 30, Priority.HIGH,
                   preferredStart=time(9, 0))
    noon = Task("t3", "p1", TaskType.FEEDING, "Lunch", 10, Priority.MEDIUM,
                preferredStart=time(12, 0))

    ordered = sort_by_time([afternoon, morning, noon])

    assert [t.preferredStart for t in ordered] == [time(9, 0), time(12, 0), time(15, 0)]


# --- Required: Recurrence Logic --------------------------------------------

def test_completing_daily_task_spawns_next_occurrence():
    """Completing a DAILY task creates a fresh, incomplete follow-up task.

    NOTE ON WORDING: the assignment says "a new task for the following day."
    The Task model has no date field, so recurrence is modeled as
    spawn-on-completion, not as a dated calendar entry. The "following day's"
    task is the freshly spawned occurrence, which carries the SAME
    preferredStart (so it lands at the same clock time the next time around).
    We assert that observable behavior.
    """
    pet = Pet("p1", "Rex", "dog", "Labrador", 4, 28.0)
    daily = Task("t1", "p1", TaskType.MEDS, "Joint meds", 5, Priority.HIGH,
                 preferredStart=time(8, 0), isFixedTime=True,
                 recurrence=Recurrence.DAILY)
    pet.addTask(daily)

    spawned = pet.completeTask("t1")

    # The original is now done and still present.
    assert daily.isComplete is True
    # A brand-new occurrence exists: distinct id, not complete, same schedule.
    assert spawned is not None
    assert spawned.taskId != daily.taskId
    assert spawned.isComplete is False
    assert spawned.preferredStart == time(8, 0)
    assert spawned.recurrence == Recurrence.DAILY
    # Pet now holds both the completed original and the new occurrence.
    assert len(pet.tasks) == 2


# --- Required: Conflict Detection ------------------------------------------

def test_scheduler_flags_duplicate_times():
    """Two tasks at the exact same start time produce a conflict warning."""
    owner = Owner("o1", "Ada", "ada@example.com", "555-0100")
    rex = Pet("p1", "Rex", "dog", "Labrador", 4, 28.0)
    mia = Pet("p2", "Mia", "cat", "Tabby", 2, 4.5)
    owner.addPet(rex)
    owner.addPet(mia)

    rex.addTask(Task("t1", "p1", TaskType.WALK, "Morning walk", 45, Priority.HIGH,
                     preferredStart=time(9, 0)))
    mia.addTask(Task("t2", "p2", TaskType.FEEDING, "Brunch", 20, Priority.MEDIUM,
                     preferredStart=time(9, 0)))

    scheduler = Scheduler(date(2026, 6, 23), owner.allTasks(date(2026, 6, 23)))
    scheduler.generateSchedule()

    assert len(scheduler.conflicts) == 1
    assert "conflict" in scheduler.conflicts[0].lower()


# --- Extra tests (explained in chat) ---------------------------------------

def test_untimed_tasks_sort_to_the_end():
    """Flexible (untimed) tasks fall after every timed task."""
    timed = Task("t1", "p1", TaskType.WALK, "Walk", 30, Priority.HIGH,
                 preferredStart=time(9, 0))
    untimed = Task("t2", "p1", TaskType.GROOMING, "Brush", 20, Priority.LOW)

    ordered = sort_by_time([untimed, timed])

    assert ordered[0] is timed
    assert ordered[-1] is untimed


def test_touching_windows_are_not_a_conflict():
    """A task ending exactly when the next begins is NOT flagged (boundary)."""
    first = Task("t1", "p1", TaskType.WALK, "Walk", 30, Priority.HIGH,
                 preferredStart=time(9, 0))   # 09:00-09:30
    second = Task("t2", "p1", TaskType.FEEDING, "Feed", 15, Priority.MEDIUM,
                  preferredStart=time(9, 30))  # 09:30-09:45

    scheduler = Scheduler(date(2026, 6, 23), [first, second])
    warnings = scheduler.detectConflicts([first, second])

    assert warnings == []


def test_one_off_task_does_not_spawn():
    """Completing a non-recurring task returns None and spawns nothing."""
    pet = Pet("p1", "Rex", "dog", "Labrador", 4, 28.0)
    pet.addTask(Task("t1", "p1", TaskType.OTHER, "Vet visit", 30, Priority.HIGH,
                     recurrence=Recurrence.NONE))

    spawned = pet.completeTask("t1")

    assert spawned is None
    assert len(pet.tasks) == 1


def test_budget_skips_low_priority_flexible_tasks():
    """A tight time budget drops the lowest-priority flexible task."""
    high = Task("t1", "p1", TaskType.WALK, "Walk", 45, Priority.HIGH)
    low = Task("t2", "p1", TaskType.ENRICHMENT, "Puzzle", 20, Priority.LOW)

    scheduler = Scheduler(date(2026, 6, 23), [high, low],
                          {"max_total_minutes": 45})
    plan = scheduler.generateSchedule()

    assert high in plan
    assert low not in plan


def test_explain_plan_raises_on_empty_plan():
    """explainPlan() raises if there is no plan (e.g. a day with no tasks)."""
    scheduler = Scheduler(date(2026, 6, 23), [])
    scheduler.generateSchedule()

    with pytest.raises(RuntimeError):
        scheduler.explainPlan()


if __name__ == "__main__":
    test_task_completion()
    test_task_addition()
    test_sort_by_time_is_chronological()
    test_completing_daily_task_spawns_next_occurrence()
    test_scheduler_flags_duplicate_times()
    test_untimed_tasks_sort_to_the_end()
    test_touching_windows_are_not_a_conflict()
    test_one_off_task_does_not_spawn()
    test_budget_skips_low_priority_flexible_tasks()
    test_explain_plan_raises_on_empty_plan()
    print("All tests passed.")
