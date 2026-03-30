from datetime import datetime

from pawpal_system import (
    Constraint,
    DailyPlan,
    OwnerPreferences,
    Pet,
    Planner,
    Task,
    TaskHistory,
    TaskType,
    TimeSlot,
)

# ---------------------------------------------------------------------------
# Owner preferences
# ---------------------------------------------------------------------------
preferences = OwnerPreferences(
    max_daily_time=180,
    preferred_times={
        "morning":   (7,  12),
        "afternoon": (14, 17),
        "evening":   (18, 20),
    },
    task_priorities_override={
        "medication": 5,
    },
    break_duration=10,
)

# ---------------------------------------------------------------------------
# Pets
# ---------------------------------------------------------------------------
rex = Pet(
    name="Rex",
    species="dog",
    age=4,
    health_conditions=["arthritis"],
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
# Tasks added intentionally out of order (low priority → high priority)
# ---------------------------------------------------------------------------
tasks = [
    Task(
        name="Groom Luna",
        task_type=TaskType.GROOMING,
        duration=30,
        priority=2,                         # lowest priority — added first
        frequency="weekly",
        pet=luna,
        is_flexible=True,
    ),
    Task(
        name="Morning walk with Rex",
        task_type=TaskType.WALK,
        duration=20,
        priority=3,
        frequency="daily",
        pet=rex,
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
        name="Rex arthritis medication",
        task_type=TaskType.MEDICATION,
        duration=10,
        priority=5,                         # highest priority — added last
        frequency="daily",
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
# Simulate some completions so filtering has something to show
# ---------------------------------------------------------------------------
tasks[0].mark_complete()   # Groom Luna  — mark complete
tasks[1].mark_complete()   # Morning walk with Rex — mark complete
# Feed Luna, Vet appointment, Rex medication remain incomplete

# ---------------------------------------------------------------------------
# Demo 1 — raw task order (as added)
# ---------------------------------------------------------------------------
print("=" * 56)
print("  TASK ORDER AS ADDED (low → high priority)")
print("=" * 56)
for t in tasks:
    status = "DONE" if t.completed else "pending"
    print(f"  [{status}]  priority {t.priority}  {t.name} ({t.pet.name})")

# ---------------------------------------------------------------------------
# Demo 2 — sorted by priority score descending
# ---------------------------------------------------------------------------
print()
print("=" * 56)
print("  SORTED BY PRIORITY SCORE (high → low)")
print("=" * 56)
by_priority = sorted(tasks, key=lambda t: t.get_priority_score(), reverse=True)
for t in by_priority:
    print(f"  score {t.get_priority_score():.1f}  {t.name} ({t.pet.name})")

# ---------------------------------------------------------------------------
# Demo 3 — sorted by last_completed (most recent first; None → end)
# ---------------------------------------------------------------------------
print()
print("=" * 56)
print("  SORTED BY LAST COMPLETED (most recent → oldest)")
print("=" * 56)
by_time = sorted(tasks, key=lambda t: t.last_completed or datetime.min, reverse=True)
for t in by_time:
    ts = t.last_completed.strftime("%H:%M:%S") if t.last_completed else "never"
    print(f"  {ts:>12}  {t.name} ({t.pet.name})")

# ---------------------------------------------------------------------------
# Demo 4 — filter: completed tasks only
# ---------------------------------------------------------------------------
print()
print("=" * 56)
print("  FILTER: completed tasks")
print("=" * 56)
for t in planner.filter_tasks(completed=True):
    print(f"  {t.name} ({t.pet.name})")

# ---------------------------------------------------------------------------
# Demo 5 — filter: incomplete tasks only
# ---------------------------------------------------------------------------
print()
print("=" * 56)
print("  FILTER: incomplete tasks")
print("=" * 56)
for t in planner.filter_tasks(completed=False):
    print(f"  {t.name} ({t.pet.name})")

# ---------------------------------------------------------------------------
# Demo 6 — filter: all tasks for Rex
# ---------------------------------------------------------------------------
print()
print("=" * 56)
print("  FILTER: tasks for Rex")
print("=" * 56)
for t in planner.filter_tasks(pet_name="Rex"):
    status = "DONE" if t.completed else "pending"
    print(f"  [{status}]  {t.name}")

# ---------------------------------------------------------------------------
# Demo 7 — filter: incomplete tasks for Luna
# ---------------------------------------------------------------------------
print()
print("=" * 56)
print("  FILTER: incomplete tasks for Luna")
print("=" * 56)
for t in planner.filter_tasks(completed=False, pet_name="Luna"):
    print(f"  {t.name}")

# ---------------------------------------------------------------------------
# Generate and print today's schedule
# ---------------------------------------------------------------------------
today = datetime.now()
plan  = planner.generate_daily_plan(today)

print()
print("=" * 56)
print("          PAWPAL+  —  TODAY'S SCHEDULE")
print("=" * 56)
print(plan.explain_plan())
print()
print("-" * 56)
print(planner.explain_decisions(plan))
print("=" * 56)

# ---------------------------------------------------------------------------
# Conflict detection demo
# Force two tasks into the same time slot by constructing a DailyPlan
# manually — the normal allocator prevents this, so we bypass it here
# to verify detect_conflicts() catches it.
# ---------------------------------------------------------------------------
print()
print("=" * 56)
print("  CONFLICT DETECTION DEMO")
print("=" * 56)

clash_start = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
clash_end   = clash_start.replace(hour=9)

slot_a = TimeSlot(start_time=clash_start, end_time=clash_end)
slot_b = TimeSlot(start_time=clash_start.replace(minute=30),
                  end_time=clash_end.replace(minute=30))  # starts 30 min in — fully overlapping

conflict_plan = DailyPlan(date=today)
conflict_plan.scheduled_tasks.append((tasks[1], slot_a))   # Morning walk with Rex  08:00–09:00
conflict_plan.scheduled_tasks.append((tasks[4], slot_b))   # Rex medication         08:30–09:30

conflicts = conflict_plan.detect_conflicts()

if conflicts:
    for warning in conflicts:
        print(f"  ⚠  {warning}")
else:
    print("  No conflicts detected.")
