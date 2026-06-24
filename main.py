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
)


def build_owner() -> Owner:
    """Create one owner with two pets and several tasks at different times."""
    owner = Owner("o1", "Ada Lovelace", "ada@example.com", "555-0100")

    rex = Pet("p1", "Rex", "dog", "Labrador", 4, 28.0)
    mia = Pet("p2", "Mia", "cat", "Tabby", 2, 4.5)
    owner.addPet(rex)
    owner.addPet(mia)

    # Fixed-time task: medication must happen at 08:00.
    rex.addTask(Task("t1", "p1", TaskType.MEDS, "Joint medication", 5,
                     Priority.HIGH, preferredStart=time(8, 0), isFixedTime=True,
                     recurrence=Recurrence.DAILY))
    # Flexible high-priority morning walk.
    rex.addTask(Task("t2", "p1", TaskType.WALK, "Morning walk", 45,
                     Priority.HIGH, preferredStart=time(9, 0),
                     recurrence=Recurrence.DAILY))
    # Fixed-time feeding at noon.
    mia.addTask(Task("t3", "p2", TaskType.FEEDING, "Lunch feeding", 10,
                     Priority.MEDIUM, preferredStart=time(12, 0), isFixedTime=True,
                     recurrence=Recurrence.DAILY))
    # Flexible low-priority enrichment in the afternoon.
    mia.addTask(Task("t4", "p2", TaskType.ENRICHMENT, "Feather toy play", 15,
                     Priority.LOW, preferredStart=time(15, 0),
                     recurrence=Recurrence.DAILY))

    return owner


def print_schedule(owner: Owner, scheduler: Scheduler) -> None:
    """Print today's ordered schedule and the scheduler's reasoning."""
    plan = scheduler.generateSchedule()

    print("=" * 48)
    print(f"  Today's Schedule - {scheduler.day.isoformat()}")
    print(f"  Owner: {owner.name}")
    print("=" * 48)

    for t in plan:
        when = t.preferredStart.strftime("%H:%M") if t.preferredStart else "flexible"
        print(f"  {when:>8}  {owner.petName(t.petId):<5}  "
              f"{t.description} ({t.durationMin} min, {t.priority.name})")

    print("-" * 48)
    print("  Why this plan:")
    print(f"  {scheduler.explainPlan()}")
    print("=" * 48)


def main() -> None:
    today = date(2026, 6, 23)
    owner = build_owner()
    scheduler = Scheduler(today, owner.allTasks(today), {"max_total_minutes": 120})
    print_schedule(owner, scheduler)


if __name__ == "__main__":
    main()
