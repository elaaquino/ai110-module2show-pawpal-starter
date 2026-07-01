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

from dataclasses import dataclass, field, replace
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


def sort_by_time(tasks: list[Task]) -> list[Task]:
    """Return tasks sorted by preferred start time; untimed tasks go last."""
    return sorted(tasks, key=lambda t: t.preferredStart or time.max)


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

    def isRecurring(self) -> bool:
        """Return True if this task repeats (daily or weekly)."""
        return self.recurrence in (Recurrence.DAILY, Recurrence.WEEKLY)

    def nextOccurrence(self, newTaskId: str) -> Task:
        """Return a fresh, incomplete copy of this task for its next occurrence.

        All scheduling attributes (type, time, priority, recurrence) are carried
        over; only the id changes and isComplete resets to False.
        """
        return replace(self, taskId=newTaskId, isComplete=False)

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

    def completeTask(self, taskId: str) -> Task | None:
        """Mark a task complete, spawning the next occurrence if it recurs.

        Returns the newly created next-occurrence task (for daily/weekly
        tasks), or None for one-off tasks.
        """
        task = self._find(taskId)
        task.markComplete()
        if task.isRecurring():
            next_task = task.nextOccurrence(self._nextTaskId(task.taskId))
            self.addTask(next_task)
            return next_task
        return None

    def _nextTaskId(self, baseId: str) -> str:
        """Generate a unique next-occurrence id like 't4#2', 't4#3', ..."""
        root = baseId.split("#", 1)[0]
        existing = {t.taskId for t in self.tasks}
        n = 2
        while f"{root}#{n}" in existing:
            n += 1
        return f"{root}#{n}"

    def dueTasks(self, on: date) -> list[Task]:
        """Return this pet's incomplete tasks.

        The `on` date and recurrence are not yet used for filtering: a task
        counts as due whenever it is not complete. Add a recurrence anchor to
        this model to make weekly/daily filtering depend on the date.
        """
        return [t for t in self.tasks if not t.isComplete]

    def _find(self, taskId: str) -> Task:
        """Return the task with the given id, or raise KeyError if absent."""
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
        return [t for pet in self.pets for t in pet.dueTasks(on)]

    def _pet(self, petId: str) -> Pet | None:
        """Return the pet with the given id, or None."""
        return next((p for p in self.pets if p.petId == petId), None)

    def petName(self, petId: str) -> str:
        """Look up a pet's display name by id (used to label plans)."""
        pet = self._pet(petId)
        return pet.name if pet is not None else petId

    def completeTask(self, petId: str, taskId: str) -> Task | None:
        """Complete a task on the given pet, spawning its next occurrence."""
        pet = self._pet(petId)
        if pet is None:
            raise KeyError(f"no pet with id {petId!r}")
        return pet.completeTask(taskId)

    def findTasks(self, completed: bool | None = None,
                  petName: str | None = None) -> list[Task]:
        """Return tasks across all pets, filtered and sorted by time.

        - completed: True -> only done tasks; False -> only pending; None -> all.
        - petName: restrict to the pet with this name (case-insensitive);
          None -> all pets.
        """
        results: list[Task] = []
        for pet in self.pets:
            if petName is not None and pet.name.lower() != petName.lower():
                continue
            for task in pet.tasks:
                if completed is not None and task.isComplete != completed:
                    continue
                results.append(task)
        return sort_by_time(results)


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
        self.conflicts: list[str] = []

    def generateSchedule(self) -> list[Task]:
        """Build an ordered daily plan from self.tasks and self.constraints.

        Strategy:
        1. Fixed-time tasks (meds at 8am, etc.) are always included.
        2. Flexible tasks are sorted by priority (desc), then shorter first,
           and packed greedily until the time budget is exhausted.
        3. The final plan is ordered chronologically by preferred start time;
           untimed tasks fall to the end, with priority breaking ties.

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

        # Lightweight, non-fatal conflict check over the scheduled tasks.
        self.conflicts = self.detectConflicts(plan)
        if self.conflicts:
            self.rationale += " " + " ".join(self.conflicts)

        return self.plan

    def detectConflicts(self, tasks: list[Task] | None = None) -> list[str]:
        """Return warning messages for tasks whose time windows overlap.

        Lightweight strategy: this never raises. It returns an empty list when
        there are no conflicts, or one warning string per overlapping pair.
        Only timed tasks (preferredStart set) are considered; flexible tasks
        have no fixed slot and are skipped.
        """
        if tasks is None:
            tasks = self.plan or self.tasks

        # Pair each timed task with its [start, end) window in minutes.
        windows = [(t, self._window(t)) for t in tasks]
        windows = [(t, w) for t, w in windows if w is not None]
        windows.sort(key=lambda pair: pair[1][0])

        warnings: list[str] = []
        for i, (task_a, (a_start, a_end)) in enumerate(windows):
            for task_b, (b_start, b_end) in windows[i + 1:]:
                if b_start >= a_end:
                    break  # sorted by start: no later task can overlap task_a
                who = ("same pet" if task_a.petId == task_b.petId
                       else "different pets")
                warnings.append(
                    f"WARNING: time conflict ({who}) - "
                    f"'{task_a.description}' ({self._fmt(a_start)}-{self._fmt(a_end)}) "
                    f"overlaps '{task_b.description}' "
                    f"({self._fmt(b_start)}-{self._fmt(b_end)})."
                )
        return warnings

    @staticmethod
    def _window(task: Task) -> tuple[int, int] | None:
        """Return a task's [start, end) window in minutes-since-midnight, or None."""
        if task.preferredStart is None:
            return None
        start = task.preferredStart.hour * 60 + task.preferredStart.minute
        return start, start + task.durationMin

    @staticmethod
    def _fmt(minutes: int) -> str:
        """Format minutes-since-midnight as HH:MM."""
        return f"{minutes // 60:02d}:{minutes % 60:02d}"

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
        """Compose the human-readable explanation of the generated plan."""
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
