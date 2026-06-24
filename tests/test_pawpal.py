"""Simple tests for the PawPal system."""

import sys
from datetime import time
from pathlib import Path

# Allow importing pawpal_system.py from the project root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Pet, Priority, Task, TaskType


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


if __name__ == "__main__":
    test_task_completion()
    test_task_addition()
    print("All tests passed.")
