from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TaskType(Enum):
    FEEDING = "feeding"
    WALK = "walk"
    MEDICATION = "medication"
    APPOINTMENT = "appointment"
    GROOMING = "grooming"


# ---------------------------------------------------------------------------
# Core data objects (dataclasses)
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    age: int
    health_conditions: list[str] = field(default_factory=list)
    height: float = 0.0
    weight: float = 0.0

    def get_daily_needs(self) -> list[Task]:
        """Return a baseline list of Tasks derived from this pet's species and health data."""
        pass

    def special_care_needed(self) -> bool:
        """Return True if any health conditions require special handling."""
        pass


@dataclass
class Task:
    name: str
    task_type: TaskType
    duration: int                          # minutes
    priority: int                          # 1 (low) – 5 (high)
    frequency: str                         # e.g. "daily", "twice_daily", "weekly"
    pet: Pet = field(repr=False)
    is_flexible: bool = True
    last_completed: Optional[datetime] = None

    def is_due(self, date: datetime) -> bool:
        """Return True if this task is due on the given date."""
        pass

    def get_priority_score(self) -> float:
        """Return a numeric score used for sorting; may factor in health conditions."""
        pass

    def fits_time_slot(self, slot: TimeSlot) -> bool:
        """Return True if this task can fit within the given TimeSlot."""
        pass


@dataclass
class TimeSlot:
    start_time: datetime
    end_time: datetime
    available: bool = True

    def duration(self) -> int:
        """Return slot length in minutes."""
        pass

    def can_fit(self, task: Task) -> bool:
        """Return True if the task duration fits within this slot."""
        pass

    def split(self, task_duration: int) -> list[TimeSlot]:
        """Split this slot around a task block; return the remaining free slots."""
        pass


@dataclass
class Notification:
    task: Task
    trigger_time: datetime
    message: str

    def send(self) -> None:
        """Dispatch the notification (e.g. print, push, or log)."""
        pass


@dataclass
class TaskHistory:
    completed_tasks: list[tuple[Task, datetime]] = field(default_factory=list)

    def log_completion(self, task: Task) -> None:
        """Record that a task was completed right now."""
        pass

    def get_last_completed(self, task: Task) -> Optional[datetime]:
        """Return the most recent completion datetime for the given task."""
        pass

    def get_completion_rate(self, task: Task) -> float:
        """Return the ratio of completed vs expected occurrences (0.0–1.0)."""
        pass

    def streak(self, task: Task) -> int:
        """Return the number of consecutive days the task has been completed."""
        pass


@dataclass
class DailyPlan:
    date: datetime
    scheduled_tasks: list[tuple[Task, TimeSlot]] = field(default_factory=list)
    unscheduled_tasks: list[Task] = field(default_factory=list)
    total_time: int = 0                    # minutes

    def add_task(self, task: Task, slot: TimeSlot) -> None:
        """Add a task/slot pair to the plan and update total_time."""
        pass

    def calculate_total_time(self) -> int:
        """Recompute and store the sum of all scheduled task durations."""
        pass

    def get_summary(self) -> dict:
        """Return a dict summary suitable for display in the Streamlit UI."""
        pass

    def explain_plan(self) -> str:
        """Return a human-readable explanation of the day's schedule."""
        pass


# ---------------------------------------------------------------------------
# Configuration / preferences
# ---------------------------------------------------------------------------

class OwnerPreferences:
    def __init__(
        self,
        max_daily_time: int,
        preferred_times: dict,
        task_priorities_override: dict,
        break_duration: int = 15,
    ):
        self.max_daily_time = max_daily_time            # minutes per day
        self.preferred_times = preferred_times          # e.g. {"morning": (7, 12)}
        self.task_priorities_override = task_priorities_override
        self.break_duration = break_duration            # minutes between tasks

    def adjust_task_priority(self, task: Task) -> int:
        """Return an adjusted priority for the task based on owner overrides."""
        pass

    def is_preferred_time(self, task: Task, slot: TimeSlot) -> bool:
        """Return True if the slot falls within the owner's preferred window for this task."""
        pass

    def get_available_time_slots(self) -> list[TimeSlot]:
        """Return time slots that respect max_daily_time and break rules."""
        pass


# ---------------------------------------------------------------------------
# Constraint checker
# ---------------------------------------------------------------------------

class Constraint:
    def __init__(self, rules: list = None):
        self.rules: list = rules or []

    def check_time_constraint(self, task: Task, slot: TimeSlot) -> bool:
        """Return True if the task fits the slot without violating time rules."""
        pass

    def check_priority_constraint(self, task: Task) -> bool:
        """Return True if the task's priority meets scheduling thresholds."""
        pass

    def check_pet_health_constraints(self, task: Task) -> bool:
        """Return True if no health condition blocks this task from being scheduled."""
        pass

    def validate_schedule(self, plan: DailyPlan) -> bool:
        """Run all constraint checks across the full plan; return True if valid."""
        pass


# ---------------------------------------------------------------------------
# Planner (orchestrator)
# ---------------------------------------------------------------------------

class Planner:
    def __init__(
        self,
        pets: list[Pet],
        tasks: list[Task],
        preferences: OwnerPreferences,
        time_slots: list[TimeSlot],
    ):
        self.pets = pets
        self.tasks = tasks
        self.preferences = preferences
        self.time_slots = time_slots

    def filter_due_tasks(self, date: datetime) -> list[Task]:
        """Return only the tasks that are due on the given date."""
        pass

    def prioritize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority score, applying owner preference overrides."""
        pass

    def allocate_tasks_to_slots(self, tasks: list[Task]) -> DailyPlan:
        """Greedily assign prioritized tasks to available time slots."""
        pass

    def generate_daily_plan(self, date: datetime) -> DailyPlan:
        """End-to-end: filter → prioritize → allocate → return a DailyPlan."""
        pass

    def explain_decisions(self, plan: DailyPlan) -> str:
        """Return a natural-language explanation of scheduling decisions (LLM hook)."""
        pass
