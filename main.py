from datetime import datetime

from pawpal_system import (
    Constraint,
    OwnerPreferences,
    Pet,
    Planner,
    Task,
    TaskHistory,
    TaskType,
)

# ---------------------------------------------------------------------------
# Owner preferences
# ---------------------------------------------------------------------------
preferences = OwnerPreferences(
    max_daily_time=180,                 # 3 hours total per day
    preferred_times={
        "morning":   (7,  12),
        "afternoon": (14, 17),
        "evening":   (18, 20),
    },
    task_priorities_override={
        "medication": 5,                # always max priority regardless of task setting
    },
    break_duration=10,                  # 10-minute buffer between tasks
)

# ---------------------------------------------------------------------------
# Pets
# ---------------------------------------------------------------------------
rex = Pet(
    name="Rex",
    species="dog",
    age=4,
    health_conditions=["arthritis"],    # restricts strenuous walks
    weight=28.5,
    height=0.6,
)

luna = Pet(
    name="Luna",
    species="cat",
    age=2,
    health_conditions=[],
    weight=4.2,
    height=0.25,
)

# ---------------------------------------------------------------------------
# Tasks  (three tasks with meaningfully different durations and priorities)
# ---------------------------------------------------------------------------
tasks = [
    Task(
        name="Morning walk with Rex",
        task_type=TaskType.WALK,
        duration=20,                    # shorter due to arthritis
        priority=3,
        frequency="daily",
        pet=rex,
        is_flexible=True,
    ),
    Task(
        name="Rex arthritis medication",
        task_type=TaskType.MEDICATION,
        duration=10,
        priority=5,
        frequency="daily",
        pet=rex,
        is_flexible=False,             # must be scheduled, no skipping
    ),
    Task(
        name="Feed Luna",
        task_type=TaskType.FEEDING,
        duration=15,
        priority=5,
        frequency="twice_daily",
        pet=luna,
        is_flexible=False,
    ),
    Task(
        name="Groom Luna",
        task_type=TaskType.GROOMING,
        duration=30,
        priority=2,
        frequency="weekly",
        pet=luna,
        is_flexible=True,
    ),
    Task(
        name="Vet appointment for Rex",
        task_type=TaskType.APPOINTMENT,
        duration=60,
        priority=4,
        frequency="monthly",
        pet=rex,
        is_flexible=False,
    ),
]

# ---------------------------------------------------------------------------
# Planner setup
# ---------------------------------------------------------------------------
history    = TaskHistory()
constraint = Constraint()

planner = Planner(
    pets=[rex, luna],
    tasks=tasks,
    preferences=preferences,
    history=history,
    constraint=constraint,
)

# ---------------------------------------------------------------------------
# Generate and print today's schedule
# ---------------------------------------------------------------------------
today = datetime.now()
plan  = planner.generate_daily_plan(today)

print("=" * 56)
print("          PAWPAL+  —  TODAY'S SCHEDULE")
print("=" * 56)
print(plan.explain_plan())
print()
print("-" * 56)
print(planner.explain_decisions(plan))
print("=" * 56)
