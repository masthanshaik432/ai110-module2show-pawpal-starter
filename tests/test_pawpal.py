import pytest
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
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def rex():
    return Pet(name="Rex", species="dog", age=4)

@pytest.fixture
def luna():
    return Pet(name="Luna", species="cat", age=2)

@pytest.fixture
def planner(rex, luna):
    tasks = [
        Task(name="Walk Rex",   task_type=TaskType.WALK,     duration=30, priority=3, frequency="daily",   pet=rex),
        Task(name="Feed Rex",   task_type=TaskType.FEEDING,  duration=15, priority=5, frequency="daily",   pet=rex),
        Task(name="Feed Luna",  task_type=TaskType.FEEDING,  duration=15, priority=5, frequency="daily",   pet=luna),
    ]
    preferences = OwnerPreferences(
        max_daily_time=120,
        preferred_times={"morning": (7, 12)},
        task_priorities_override={},
    )
    return Planner(
        pets=[rex, luna],
        tasks=tasks,
        preferences=preferences,
        history=TaskHistory(),
        constraint=Constraint(),
    )


# ---------------------------------------------------------------------------
# Test 1 — mark_complete() changes task status
# ---------------------------------------------------------------------------

def test_mark_complete_sets_completed_flag(rex):
    task = Task(
        name="Rex medication",
        task_type=TaskType.MEDICATION,
        duration=10,
        priority=5,
        frequency="daily",
        pet=rex,
    )

    assert task.completed is False
    assert task.last_completed is None

    task.mark_complete()

    assert task.completed is True
    assert task.last_completed is not None


# ---------------------------------------------------------------------------
# Test 2 — adding a task to a planner increases that pet's task count
# ---------------------------------------------------------------------------

def test_adding_task_increases_pet_task_count(planner, rex):
    rex_tasks_before = [t for t in planner.tasks if t.pet.name == rex.name]
    count_before = len(rex_tasks_before)

    planner.tasks.append(Task(
        name="Rex grooming",
        task_type=TaskType.GROOMING,
        duration=20,
        priority=2,
        frequency="weekly",
        pet=rex,
    ))

    rex_tasks_after = [t for t in planner.tasks if t.pet.name == rex.name]
    assert len(rex_tasks_after) == count_before + 1
