"""PawPal demo — build an owner with pets and tasks, then print today's plan."""

from datetime import date, time

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


def build_owner() -> Owner:
    """Create one owner with two pets and several tasks added OUT OF ORDER.

    Tasks are intentionally inserted in a jumbled time order so the sorting
    and filtering methods have something real to fix.
    """
    owner = Owner("o1", "Ada Lovelace", "ada@example.com", "555-0100")

    rex = Pet("p1", "Rex", "dog", "Labrador", 4, 28.0)
    mia = Pet("p2", "Mia", "cat", "Tabby", 2, 4.5)
    owner.addPet(rex)
    owner.addPet(mia)

    # Added afternoon-first, then morning, then an untimed task — deliberately
    # NOT in chronological order.
    mia.addTask(Task("t1", "p2", TaskType.ENRICHMENT, "Feather toy play", 15,
                     Priority.LOW, preferredStart=time(15, 0),
                     recurrence=Recurrence.DAILY))
    rex.addTask(Task("t2", "p1", TaskType.WALK, "Morning walk", 45,
                     Priority.HIGH, preferredStart=time(9, 0),
                     recurrence=Recurrence.DAILY))
    mia.addTask(Task("t3", "p2", TaskType.FEEDING, "Lunch feeding", 10,
                     Priority.MEDIUM, preferredStart=time(12, 0), isFixedTime=True,
                     recurrence=Recurrence.DAILY))
    rex.addTask(Task("t4", "p1", TaskType.MEDS, "Joint medication", 5,
                     Priority.HIGH, preferredStart=time(8, 0), isFixedTime=True,
                     recurrence=Recurrence.DAILY))
    # An untimed (fully flexible) grooming task — should sort to the end.
    rex.addTask(Task("t5", "p1", TaskType.GROOMING, "Brush coat", 20,
                     Priority.LOW, recurrence=Recurrence.WEEKLY))
    # Deliberately scheduled at the SAME time as Rex's 09:00 walk (different
    # pet) to trigger a conflict warning.
    mia.addTask(Task("t6", "p2", TaskType.FEEDING, "Brunch feeding", 20,
                     Priority.MEDIUM, preferredStart=time(9, 0),
                     recurrence=Recurrence.DAILY))

    return owner


def print_recurrence(owner: Owner) -> None:
    """Show that completing a recurring task spawns its next occurrence."""
    print("=" * 52)
    print("  Recurrence on completion")
    print("=" * 52)

    rex = owner.pets[0]
    before = len(rex.tasks)
    print(f"  Rex has {before} task(s). Completing 't4' (Joint medication, DAILY)...")

    spawned = rex.completeTask("t4")

    after = len(rex.tasks)
    if spawned is not None:
        when = spawned.preferredStart.strftime("%H:%M") if spawned.preferredStart else "flexible"
        print(f"  -> spawned next occurrence '{spawned.taskId}': "
              f"{spawned.description} at {when} (complete={spawned.isComplete}).")
    print(f"  Rex now has {after} task(s): the done original stays, the fresh "
          "occurrence is added.")
    print("=" * 52)


def print_task_list(title: str, tasks: list[Task], owner: Owner) -> None:
    """Print a labeled list of tasks with time, pet, and status."""
    print(f"  {title}")
    if not tasks:
        print("    (none)")
        return
    for t in tasks:
        when = t.preferredStart.strftime("%H:%M") if t.preferredStart else "flexible"
        status = "done" if t.isComplete else "pending"
        print(f"    {when:>8}  {owner.petName(t.petId):<5}  "
              f"{t.description} ({t.priority.name}, {status})")


def print_sort_and_filter(owner: Owner) -> None:
    """Demonstrate sort_by_time and Owner.findTasks in the terminal."""
    print("=" * 52)
    print("  Sorting & Filtering")
    print("=" * 52)

    # Insertion order, to show the tasks really are jumbled.
    raw = [t for pet in owner.pets for t in pet.tasks]
    print_task_list("Insertion order:", raw, owner)
    print("-" * 52)

    # Sorting: chronological, untimed tasks last.
    print_task_list("Sorted by time (sort_by_time):", sort_by_time(raw), owner)
    print("-" * 52)

    # Filtering by completion status.
    print_task_list("Pending only (findTasks completed=False):",
                    owner.findTasks(completed=False), owner)
    print_task_list("Completed only (findTasks completed=True):",
                    owner.findTasks(completed=True), owner)
    print("-" * 52)

    # Filtering by pet name (case-insensitive).
    print_task_list("Rex's tasks (findTasks petName='rex'):",
                    owner.findTasks(petName="rex"), owner)
    print("=" * 52)


def print_schedule(owner: Owner, scheduler: Scheduler) -> None:
    """Print today's ordered schedule and the scheduler's reasoning."""
    plan = scheduler.generateSchedule()

    print("=" * 52)
    print(f"  Today's Schedule - {scheduler.day.isoformat()}")
    print(f"  Owner: {owner.name}")
    print("=" * 52)

    for t in plan:
        when = t.preferredStart.strftime("%H:%M") if t.preferredStart else "flexible"
        print(f"  {when:>8}  {owner.petName(t.petId):<5}  "
              f"{t.description} ({t.durationMin} min, {t.priority.name})")

    print("-" * 52)
    print("  Why this plan:")
    print(f"  {scheduler.explainPlan()}")
    print("=" * 52)


def main() -> None:
    today = date(2026, 6, 23)
    owner = build_owner()

    print_recurrence(owner)
    print()
    print_sort_and_filter(owner)
    print()

    scheduler = Scheduler(today, owner.allTasks(today), {"max_total_minutes": 120})
    print_schedule(owner, scheduler)
    print()

    print("=" * 52)
    print("  Conflict detection (non-fatal)")
    print("=" * 52)
    if scheduler.conflicts:
        for warning in scheduler.conflicts:
            print(f"  {warning}")
    else:
        print("  No time conflicts detected.")
    print("=" * 52)


if __name__ == "__main__":
    main()
