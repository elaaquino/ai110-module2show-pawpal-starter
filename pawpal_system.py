"""PawPal — pet care scheduling system.

Class skeleton generated from diagrams/uml_draft.mmd.
Method bodies are intentionally left as stubs to be implemented.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    """A single pet care task (walk, feeding, meds, enrichment, grooming, etc.)."""

    taskId: str
    type: str
    description: str
    durationMin: int
    priority: int
    preferredWindow: str
    isFixedTime: bool = False
    recurrence: str = ""
    isComplete: bool = False

    def markComplete(self) -> None:
        """Mark this task as done."""
        ...

    def edit(self, changes: dict) -> None:
        """Apply a set of field changes to this task."""
        ...


@dataclass
class Pet:
    """A pet belonging to an owner, along with its care tasks."""

    petId: str
    name: str
    species: str
    breed: str
    ageYears: int
    weightKg: float
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def addTask(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        ...

    def editTask(self, taskId: str, changes: dict) -> None:
        """Edit an existing task identified by taskId."""
        ...

    def removeTask(self, taskId: str) -> None:
        """Remove a task identified by taskId."""
        ...


@dataclass
class Owner:
    """The pet owner and the pets they are responsible for."""

    ownerId: str
    name: str
    email: str
    phone: str
    pets: list[Pet] = field(default_factory=list)

    def addPet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        ...

    def removePet(self, petId: str) -> None:
        """Remove a pet identified by petId."""
        ...

    def updateInfo(self, name: str, email: str, phone: str) -> None:
        """Update this owner's contact information."""
        ...


class Scheduler:
    """Generates a daily care plan from tasks and constraints, and explains it."""

    def __init__(self, date: date, tasks: list[Task] | None = None,
                 constraints: dict | None = None) -> None:
        self.date: date = date
        self.tasks: list[Task] = tasks if tasks is not None else []
        self.constraints: dict = constraints if constraints is not None else {}
        self.plan: list[Task] = []
        self.rationale: str = ""

    def generateSchedule(self, tasks: list[Task], constraints: dict) -> list[Task]:
        """Build an ordered daily plan based on priorities and constraints."""
        ...

    def explainPlan(self) -> str:
        """Return a human-readable explanation of why the plan was chosen."""
        ...

    def setConstraint(self, key: str, value) -> None:
        """Set or update a scheduling constraint."""
        ...
