"""PawPal — pet care scheduling system.

Core implementation of the four domain classes:
- Task     : a single pet care activity.
- Pet      : pet details plus its list of tasks.
- Owner    : manages multiple pets and aggregates their tasks.
- Scheduler: the "brain" that organizes tasks into an ordered daily plan
             and explains why it chose that plan.

Design note: the Scheduler does NOT hold an Owner. The Owner aggregates its
pets' tasks via allTasks(day); the caller passes that list to the Scheduler.
This keeps the Scheduler a pure function of (tasks, constraints) and matches
the dependency arrows in diagrams/uml_draft.mmd.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum


class TaskType(Enum):
    """Categories of pet care tasks."""

    WALK = "walk"
    FEEDING = "feeding"
    MEDS = "meds"
    ENRICHMENT = "enrichment"
    GROOMING = "grooming"
    OTHER = "other"


class Priority(Enum):
    """Task priority levels (higher value = more urgent)."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Recurrence(Enum):
    """How often a task repeats."""

    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Task:
    """A single pet care task (walk, feeding, meds, enrichment, grooming, etc.)."""

    taskId: str
    petId: str
    type: TaskType
    description: str
    durationMin: int
    priority: Priority
    preferredStart: time | None = None
    preferredEnd: time | None = None
    isFixedTime: bool = False
    recurrence: Recurrence = Recurrence.NONE
    isComplete: bool = False

    def __post_init__(self) -> None:
        """Validate field values on construction."""
        if self.durationMin <= 0:
            raise ValueError("durationMin must be positive")
        if self.isFixedTime and self.preferredStart is None:
            raise ValueError("a fixed-time task requires a preferredStart")

    def markComplete(self) -> None:
        """Mark this task as done."""
        self.isComplete = True

    def edit(self, changes: dict) -> None:
        """Apply a set of field changes to this task.

        Only existing attributes are updated; unknown keys raise KeyError so
        typos surface instead of silently creating junk attributes.
        """
        for key, value in changes.items():
            if not hasattr(self, key):
                raise KeyError(f"Task has no field {key!r}")
            setattr(self, key, value)


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
        """Add a task to this pet's task list, keeping petId consistent."""
        if task.petId != self.petId:
            raise ValueError(
                f"task.petId {task.petId!r} does not match pet {self.petId!r}"
            )
        self.tasks.append(task)

    def editTask(self, taskId: str, changes: dict) -> None:
        """Edit an existing task identified by taskId."""
        self._find(taskId).edit(changes)

    def removeTask(self, taskId: str) -> None:
        """Remove a task identified by taskId."""
        self.tasks = [t for t in self.tasks if t.taskId != taskId]

    def dueTasks(self, on: date) -> list[Task]:
        """Return this pet's tasks that still need doing on the given date.

        A task is due if it is not yet complete and its recurrence applies:
        - DAILY / NONE: always a candidate while incomplete.
        - WEEKLY: due on the same weekday it was created/anchored. With no
          stored anchor in this skeleton we treat weekly as due any day; refine
          once a recurrence anchor is added.
        """
        due = []
        for t in self.tasks:
            if t.isComplete:
                continue
            if t.recurrence in (Recurrence.NONE, Recurrence.DAILY, Recurrence.WEEKLY):
                due.append(t)
        return due

    def _find(self, taskId: str) -> Task:
        for t in self.tasks:
            if t.taskId == taskId:
                return t
        raise KeyError(f"no task with id {taskId!r}")


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
        self.pets.append(pet)

    def removePet(self, petId: str) -> None:
        """Remove a pet identified by petId."""
        self.pets = [p for p in self.pets if p.petId != petId]

    def updateInfo(self, name: str, email: str, phone: str) -> None:
        """Update this owner's contact information."""
        self.name = name
        self.email = email
        self.phone = phone

    def allTasks(self, on: date) -> list[Task]:
        """Aggregate due tasks across all pets into one list for the Scheduler."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.dueTasks(on))
        return tasks

    def petName(self, petId: str) -> str:
        """Look up a pet's display name by id (used to label plans)."""
        for pet in self.pets:
            if pet.petId == petId:
                return pet.name
        return petId


class Scheduler:
    """Generates a daily care plan from tasks and constraints, and explains it.

    Supported constraint keys (all optional):
    - "max_total_minutes": int — daily time budget for flexible tasks.
    """

    def __init__(self, day: date, tasks: list[Task] | None = None,
                 constraints: dict | None = None) -> None:
        self.day: date = day
        self.tasks: list[Task] = tasks if tasks is not None else []
        self.constraints: dict = constraints if constraints is not None else {}
        self.plan: list[Task] = []
        self.rationale: str = ""

    def generateSchedule(self) -> list[Task]:
        """Build an ordered daily plan from self.tasks and self.constraints.

        Strategy:
        1. Fixed-time tasks (meds at 8am, etc.) are always included.
        2. Flexible tasks are sorted by priority (desc), then shorter first,
           and packed greedily until the time budget is exhausted.
        3. The final plan is ordered by clock time for fixed tasks, with the
           remaining flexible tasks following in priority order.

        Populates self.plan and self.rationale, then returns the plan.
        """
        budget = self.constraints.get("max_total_minutes")

        fixed = [t for t in self.tasks if t.isFixedTime]
        flexible = [t for t in self.tasks if not t.isFixedTime]
        flexible.sort(key=lambda t: (-t.priority.value, t.durationMin))

        plan: list[Task] = list(fixed)
        used = sum(t.durationMin for t in fixed)
        skipped: list[Task] = []

        for t in flexible:
            if budget is None or used + t.durationMin <= budget:
                plan.append(t)
                used += t.durationMin
            else:
                skipped.append(t)

        # Order the final plan chronologically; tasks without a preferred time
        # fall to the end, with priority breaking ties.
        plan.sort(key=lambda t: (
            t.preferredStart or time.max,
            -t.priority.value,
        ))

        self.plan = plan
        self.rationale = self._buildRationale(plan, skipped, used, budget)
        return self.plan

    def explainPlan(self) -> str:
        """Return a human-readable explanation of why the plan was chosen.

        Raises if called before generateSchedule has produced a plan.
        """
        if not self.plan:
            raise RuntimeError("call generateSchedule() before explainPlan()")
        return self.rationale

    def setConstraint(self, key: str, value) -> None:
        """Set or update a scheduling constraint."""
        self.constraints[key] = value

    def _buildRationale(self, plan: list[Task], skipped: list[Task],
                        used: int, budget: int | None) -> str:
        lines = [f"Plan for {self.day.isoformat()}: {len(plan)} task(s), "
                 f"{used} min scheduled."]
        if budget is not None:
            lines.append(f"Time budget: {used}/{budget} min used.")

        fixed = [t for t in plan if t.isFixedTime]
        if fixed:
            lines.append(
                "Fixed-time tasks were placed first because they must occur at a "
                "set time: " + ", ".join(
                    f"{t.description} ({t.preferredStart.strftime('%H:%M')})"
                    for t in fixed
                ) + "."
            )

        flexible = [t for t in plan if not t.isFixedTime]
        if flexible:
            lines.append(
                "Flexible tasks were ordered by priority (then shortest first): "
                + ", ".join(f"{t.description} [{t.priority.name}]" for t in flexible)
                + "."
            )

        if skipped:
            lines.append(
                "Skipped (over time budget) - defer or extend the day: "
                + ", ".join(
                    f"{t.description} [{t.priority.name}, {t.durationMin} min]"
                    for t in skipped
                ) + "."
            )
        return " ".join(lines)


if __name__ == "__main__":
    # Minimal smoke test / usage demo.
    today = date(2026, 6, 23)

    owner = Owner("o1", "Ada", "ada@example.com", "555-0100")
    rex = Pet("p1", "Rex", "dog", "Lab", 4, 28.0)
    mia = Pet("p2", "Mia", "cat", "Tabby", 2, 4.5)
    owner.addPet(rex)
    owner.addPet(mia)

    rex.addTask(Task("t1", "p1", TaskType.MEDS, "Joint meds", 5, Priority.HIGH,
                     preferredStart=time(8, 0), isFixedTime=True,
                     recurrence=Recurrence.DAILY))
    rex.addTask(Task("t2", "p1", TaskType.WALK, "Morning walk", 45, Priority.HIGH,
                     recurrence=Recurrence.DAILY))
    rex.addTask(Task("t3", "p1", TaskType.ENRICHMENT, "Puzzle feeder", 20,
                     Priority.LOW, recurrence=Recurrence.DAILY))
    mia.addTask(Task("t4", "p2", TaskType.FEEDING, "Wet food", 10, Priority.MEDIUM,
                     recurrence=Recurrence.DAILY))
    mia.addTask(Task("t5", "p2", TaskType.GROOMING, "Brush coat", 15, Priority.LOW,
                     recurrence=Recurrence.WEEKLY))

    scheduler = Scheduler(today, owner.allTasks(today), {"max_total_minutes": 75})
    plan = scheduler.generateSchedule()

    print("Daily plan:")
    for t in plan:
        when = t.preferredStart.strftime("%H:%M") if t.preferredStart else "flexible"
        print(f"  - [{when}] {owner.petName(t.petId)}: {t.description} "
              f"({t.durationMin} min, {t.priority.name})")
    print("\nWhy:")
    print(" ", scheduler.explainPlan())
