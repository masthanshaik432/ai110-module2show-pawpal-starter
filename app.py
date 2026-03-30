import streamlit as st

from pawpal_system import (
    Constraint,
    DailyPlan,
    OwnerPreferences,
    Pet,
    Planner,
    Task,
    TaskHistory,
    TaskType,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------------------------------------------------------------------------
# Session state initialisation
#
# st.session_state works like a dictionary that survives reruns.
# The pattern below is the standard guard:
#
#   if "key" not in st.session_state:
#       st.session_state["key"] = <create object once>
#
# Without this guard the object would be recreated (and reset) on every
# button click, because Streamlit reruns the whole script top-to-bottom.
# ---------------------------------------------------------------------------

if "pets" not in st.session_state:
    st.session_state["pets"] = []               # list[Pet]  — grows as user adds pets

if "tasks" not in st.session_state:
    st.session_state["tasks"] = []              # list[Task] — grows as user adds tasks

if "history" not in st.session_state:
    st.session_state["history"] = TaskHistory() # one shared history log for the session

if "constraint" not in st.session_state:
    st.session_state["constraint"] = Constraint()

if "preferences" not in st.session_state:
    # Sensible defaults — owner can adjust these via the UI later
    st.session_state["preferences"] = OwnerPreferences(
        max_daily_time=180,
        preferred_times={
            "morning":   (7,  12),
            "afternoon": (14, 17),
            "evening":   (18, 20),
        },
        task_priorities_override={},
        break_duration=10,
    )

if "planner" not in st.session_state:
    # Planner is rebuilt whenever pets or tasks change (see "Add pet" / "Add task" buttons)
    st.session_state["planner"] = Planner(
        pets=st.session_state["pets"],
        tasks=st.session_state["tasks"],
        preferences=st.session_state["preferences"],
        history=st.session_state["history"],
        constraint=st.session_state["constraint"],
    )

st.title("🐾 PawPal+")
st.caption("Smart pet care scheduling — powered by your backend classes.")

# ---------------------------------------------------------------------------
# Section 1 — Add a Pet  →  calls Pet() and Pet.get_daily_needs()
# ---------------------------------------------------------------------------
st.subheader("Add a Pet")

with st.form("add_pet_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Name", value="Mochi")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)

    health_input = st.text_input(
        "Health conditions (comma-separated, leave blank if none)",
        value="",
        placeholder="e.g. arthritis, diabetes",
    )
    auto_tasks = st.checkbox("Auto-generate baseline tasks from pet profile", value=True)
    submitted_pet = st.form_submit_button("Add Pet")

if submitted_pet:
    conditions = [c.strip() for c in health_input.split(",") if c.strip()]
    new_pet = Pet(name=pet_name, species=species, age=age, health_conditions=conditions)
    st.session_state["pets"].append(new_pet)

    if auto_tasks:
        # get_daily_needs() inspects species + health_conditions and returns Task objects
        baseline_tasks = new_pet.get_daily_needs()
        st.session_state["tasks"].extend(baseline_tasks)
        st.success(
            f"Added **{new_pet.name}** ({species}) with "
            f"{len(baseline_tasks)} auto-generated task(s)."
        )
    else:
        st.success(f"Added **{new_pet.name}** ({species}).")

if st.session_state["pets"]:
    st.write("**Current pets:**")
    st.table([
        {
            "Name": p.name,
            "Species": p.species,
            "Age": p.age,
            "Health conditions": ", ".join(p.health_conditions) or "none",
            "Special care": "yes" if p.special_care_needed() else "no",
        }
        for p in st.session_state["pets"]
    ])

st.divider()

# ---------------------------------------------------------------------------
# Section 2 — Add a Task  →  calls Task() with a real Pet reference
# ---------------------------------------------------------------------------
st.subheader("Add a Task")

if not st.session_state["pets"]:
    st.info("Add a pet first — tasks must be linked to a pet.")
else:
    with st.form("add_task_form"):
        col1, col2 = st.columns(2)
        with col1:
            task_name = st.text_input("Task name", value="Evening walk")
            task_type = st.selectbox("Type", [t.value for t in TaskType])
            frequency = st.selectbox("Frequency", ["daily", "twice_daily", "weekly", "biweekly", "monthly"])
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
            priority = st.slider("Priority", min_value=1, max_value=5, value=3)
            is_flexible = st.checkbox("Flexible (can be skipped if no slot available)", value=True)

        pet_names = [p.name for p in st.session_state["pets"]]
        selected_pet_name = st.selectbox("Assign to pet", pet_names)
        submitted_task = st.form_submit_button("Add Task")

    if submitted_task:
        linked_pet = next(p for p in st.session_state["pets"] if p.name == selected_pet_name)
        new_task = Task(
            name=task_name,
            task_type=TaskType(task_type),
            duration=duration,
            priority=priority,
            frequency=frequency,
            pet=linked_pet,
            is_flexible=is_flexible,
        )
        st.session_state["tasks"].append(new_task)
        st.success(f"Added task **{task_name}** for {selected_pet_name}.")

    if st.session_state["tasks"]:
        st.write("**Current tasks:**")
        st.table([
            {
                "Task": t.name,
                "Pet": t.pet.name,
                "Type": t.task_type.value,
                "Duration (min)": t.duration,
                "Priority": t.priority,
                "Frequency": t.frequency,
                "Flexible": "yes" if t.is_flexible else "no",
            }
            for t in st.session_state["tasks"]
        ])
    else:
        st.info("No tasks yet.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Generate Schedule  →  calls planner.generate_daily_plan()
# ---------------------------------------------------------------------------
st.subheader("Generate Today's Schedule")

if not st.session_state["tasks"]:
    st.info("Add at least one task before generating a schedule.")
else:
    if st.button("Generate schedule"):
        from datetime import datetime
        planner: Planner = st.session_state["planner"]
        plan = planner.generate_daily_plan(datetime.now())
        summary = plan.get_summary()

        st.success(
            f"Scheduled **{summary['scheduled_count']}** task(s) · "
            f"**{summary['total_time_minutes']} min** total"
        )

        if summary["scheduled_tasks"]:
            st.write("**Schedule:**")
            st.table(summary["scheduled_tasks"])

        if summary["unscheduled_tasks"]:
            st.warning("The following tasks could not be scheduled:")
            st.table(summary["unscheduled_tasks"])

        st.write("**Planner decisions:**")
        st.text(planner.explain_decisions(plan))
