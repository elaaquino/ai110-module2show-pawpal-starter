from datetime import date, time

import streamlit as st

from pawpal_system import (
    Owner,
    Pet,
    Priority,
    Recurrence,
    Scheduler,
    Task,
    TaskType,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Session "vault": create the Owner once, then reuse it across reruns ---
if "owner" not in st.session_state:
    st.session_state.owner = Owner("o1", "Jordan", "", "")
if "pet_seq" not in st.session_state:
    st.session_state.pet_seq = 0
if "task_seq" not in st.session_state:
    st.session_state.task_seq = 0

owner = st.session_state.owner

# Lookup maps for the enum-backed selectboxes.
PRIORITY_BY_LABEL = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH}
TYPE_BY_LABEL = {t.value: t for t in TaskType}
RECURRENCE_BY_LABEL = {r.value: r for r in Recurrence}


def find_pet(pet_id: str) -> Pet | None:
    """Return the owner's pet with the given id, or None."""
    for pet in owner.pets:
        if pet.petId == pet_id:
            return pet
    return None


st.subheader("Owner")
owner_name = st.text_input("Owner name", value=owner.name)
if owner_name != owner.name:
    owner.updateInfo(owner_name, owner.email, owner.phone)

st.subheader("Add a Pet")
pcol1, pcol2 = st.columns(2)
with pcol1:
    pet_name = st.text_input("Pet name", value="Mochi")
with pcol2:
    species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    st.session_state.pet_seq += 1
    new_pet = Pet(f"p{st.session_state.pet_seq}", pet_name, species, "", 0, 0.0)
    owner.addPet(new_pet)
    st.success(f"Added {pet_name}.")

if owner.pets:
    st.caption("Current pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))
else:
    st.info("No pets yet. Add one above before scheduling tasks.")

st.divider()

st.subheader("Add a Task")
if not owner.pets:
    st.info("Add a pet first.")
else:
    pet_choice = st.selectbox(
        "For pet",
        options=[p.petId for p in owner.pets],
        format_func=lambda pid: find_pet(pid).name,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", list(PRIORITY_BY_LABEL), index=2)

    col4, col5, col6 = st.columns(3)
    with col4:
        task_type = st.selectbox("Type", list(TYPE_BY_LABEL), index=0)
    with col5:
        recurrence = st.selectbox("Recurrence", list(RECURRENCE_BY_LABEL), index=0)
    with col6:
        use_time = st.checkbox("Preferred time")
        preferred = st.time_input("Start", value=time(9, 0)) if use_time else None
    is_fixed = st.checkbox("Fixed time (must occur at the preferred time)")

    if st.button("Add task"):
        if is_fixed and preferred is None:
            st.error("A fixed-time task needs a preferred time. Check 'Preferred time' first.")
        else:
            st.session_state.task_seq += 1
            task = Task(
                f"t{st.session_state.task_seq}",
                pet_choice,
                TYPE_BY_LABEL[task_type],
                task_title,
                int(duration),
                PRIORITY_BY_LABEL[priority],
                preferredStart=preferred,
                isFixedTime=is_fixed,
                recurrence=RECURRENCE_BY_LABEL[recurrence],
            )
            find_pet(pet_choice).addTask(task)
            st.success(f"Added '{task_title}' for {find_pet(pet_choice).name}.")

# Show all current tasks across pets.
all_tasks = owner.allTasks(date.today())
if all_tasks:
    st.write("Current tasks:")
    st.table([
        {
            "pet": owner.petName(t.petId),
            "task": t.description,
            "type": t.type.value,
            "duration_minutes": t.durationMin,
            "priority": t.priority.name,
            "recurrence": t.recurrence.value,
            "time": t.preferredStart.strftime("%H:%M") if t.preferredStart else "flexible",
        }
        for t in all_tasks
    ])

    # Mark a task complete. Recurring tasks automatically spawn the next
    # occurrence via Owner.completeTask -> Pet.completeTask.
    done_choice = st.selectbox(
        "Mark a task complete",
        options=[t.taskId for t in all_tasks],
        format_func=lambda tid: next(
            f"{owner.petName(t.petId)}: {t.description}"
            for t in all_tasks if t.taskId == tid
        ),
    )
    if st.button("Mark complete"):
        task = next(t for t in all_tasks if t.taskId == done_choice)
        spawned = owner.completeTask(task.petId, task.taskId)
        if spawned is not None:
            st.success(
                f"Completed '{task.description}'. Spawned next occurrence "
                f"'{spawned.taskId}' ({spawned.recurrence.value})."
            )
        else:
            st.success(f"Completed '{task.description}' (one-off, no repeat).")
        st.rerun()

st.divider()

st.subheader("Build Schedule")
max_minutes = st.number_input(
    "Daily time budget (minutes)", min_value=0, max_value=1440, value=180
)

if st.button("Generate schedule"):
    constraints = {"max_total_minutes": int(max_minutes)} if max_minutes else {}
    scheduler = Scheduler(date.today(), owner.allTasks(date.today()), constraints)
    plan = scheduler.generateSchedule()

    if not plan:
        st.info("No tasks to schedule yet.")
    else:
        st.write("### Today's Schedule")
        st.table([
            {
                "time": t.preferredStart.strftime("%H:%M") if t.preferredStart else "flexible",
                "pet": owner.petName(t.petId),
                "task": t.description,
                "duration_minutes": t.durationMin,
                "priority": t.priority.name,
            }
            for t in plan
        ])
        if scheduler.conflicts:
            st.write("### Conflicts")
            for warning in scheduler.conflicts:
                st.warning(warning)

        st.write("### Why this plan")
        st.info(scheduler.explainPlan())
