# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Three core actions that a user should be able to perform
1) add a pet, including info such as diet and meds
2) view a daily schedule around the pet
3) obtain a reasoning for the given schedule

Here are objects that I have brainstormed along with their attributes and functions:
Class Pet:
attributes
- name: string
- species: string
- age: int
- health_conditions: list[string]
- height: float
- weight: float
methods
- get_daily_needs()
- special_care_needed()

Class Task:
attributes
- name: string
- task_type: string
- duration: int
- priority: int (1–5)
- frequency: string
- pet: Pet
- is_flexible: bool
- last_completed: datetime
methods
- is_due(date)
- get_priority_score()
- fits_time_slot(slot)

Class TimeSlot:
attributes
- start_time: datetime
- end_time: datetime
- available: bool
methods
- duration()
- can_fit(task)
- split(task_duration)

Class OwnerPreferences
attributes
- max_daily_time: int
- preferred_times: dict
- task_priorities_override: dict
- break_duration: int
methods
- adjust_task_priority(task)
- is_preferred_time(task, slot)
- get_available_time_slots()

Class DailyPlan
attributes
- date: datetime
- scheduled_tasks: list[(Task, TimeSlot)]
- unscheduled_tasks: list[Task]
- total_time: int
methods
- add_task(task, slot)
- calculate_total_time()
- get_summary()
- explain_plan()

Class Planner
attributes
- tasks: list[Task]
- pets: list[Pet]
- preferences: OwnerPreferences
- time_slots: list[TimeSlot]
methods
- filter_due_tasks(date)
- prioritize_tasks(tasks)
- allocate_tasks_to_slots(tasks)
- generate_daily_plan(date)
- explain_decisions(plan)

Class TaskHistory
attributes
- completed_tasks: list[(Task, datetime)]
methods
- log_completion(task)
- get_last_completed(task)
- get_completion_rate(task)

Class Constraint
attributes
- rules: list
methods
- check_time_constraint(task, slot)
- check_priority_constraint(task)
- check_pet_health_constraints(task)
- validate_schedule(plan)


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

After creating the skeleton, I asked AI to review and look for potential setbacks. AI gave quite a few change suggestions (9 in total) and the below are the changes I made

Change 1: Planner now owns TaskHistory and Constraint
Planner.__init__ now takes history and constraint, and time_slots was removed. Slots are pulled from preferences.get_available_time_slots() instead.
Before this, the planner didn’t actually know when tasks were last completed, so “due” logic was guessy. It also wasn’t enforcing any rules when placing tasks, which meant invalid schedules could slip through.

Change 4: Plan is validated before returning
generate_daily_plan() now calls self.constraint.validate_schedule() at the end.
Previously, validation existed but wasn’t part of the normal flow, so bad schedules could make it all the way to the UI without being caught.

Change 7: Two-pass task allocation
Scheduling now happens in two passes:
-Inflexible tasks first (like meds or appointments)
-Flexible tasks after
The old single-pass approach could fill good time slots with low-priority tasks and leave important ones unscheduled.

Change 8: Completion rate now supports time windows
get_completion_rate() now takes a since parameter.
Without it, stats were based on all-time history, which made them misleading—especially for new or recently resumed tasks.

Change 9: total_time is now computed, not stored
Removed the stored total_time field and replaced it with a @property.
Before, it could easily get out of sync depending on how tasks were added. Now it’s always accurate since it’s calculated from the current schedule.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

Pet health constraints block tasks based on the pet’s condition. For example, heart_disease and arthritis prevent walks, and post_surgery prevents walks and grooming. These rules are in _HEALTH_RESTRICTIONS and are the highest priority for safety.
Time constraints ensure a slot is available and has enough minutes for the task.
Owner preferences include max_daily_time as a hard limit, preferred time windows like morning or afternoon, and break durations between tasks.
Priority constraints check that a task’s priority falls in the valid 1–5 range.
Health constraints come first because safety matters most. Time constraints follow to ensure scheduling is possible. Priority and owner preferences then guide the order and placement of tasks within those limits.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff the scheduler makes is guaranteed placement for high priority tasks vs optimal use of time.
Right now, inflexible tasks are scheduled first, in priority order, and each one takes the first time slot that fits. That keeps things simple, but it can waste space. For example, a 60-minute vet appointment might take up a whole morning slot, even if that blocks a quick 10-minute medication that could’ve fit somewhere around it.
So the system is basically favoring predictability making sure important, inflexible tasks get placed over squeezing in as many tasks as possible.
A more efficient approach would look at all inflexible tasks together and figure out the best way to fit them before locking anything in. But that’s a much harder problem to solve, so this version sticks with the simpler tradeoff.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I mainly used inline completions and the chat panel with @workspace.
Inline completions helped with repetitive logic. After writing is_due() for daily tasks, Copilot filled in similar patterns for weekly and biweekly cases, which saved time and kept things consistent.
The chat panel was most useful during design review. Asking focused questions like reviewing the Planner class for responsibility issues helped surface problems, like Planner not owning TaskHistory or Constraint.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One issue came up in complete_task(). Copilot suggested marking the task complete and logging it, but didn’t create the next occurrence. That would break recurring tasks, so I added logic to generate and append the successor.
I also found Copilot works best for small, local logic. For anything involving multiple parts of the system, I double checked it manually.
Using separate chat sessions for design, implementation, and testing helped keep suggestions focused and avoided mixing concerns.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

We ran 24 tests covering three main areas: sorting, recurrence, and conflict detection.
Sorting tests checked that tasks from allocate_tasks_to_slots() are in chronological order, that sequential tasks do not overlap, and that inflexible tasks are placed before flexible ones. This ensures high-priority tasks like medication are never blocked by lower-priority flexible tasks.
Recurrence tests verified that complete_task() generates successors correctly for daily and weekly tasks, preserves last_completed so is_due() works, and does not produce successors for monthly tasks.
Conflict detection tests confirmed that detect_conflicts() flags overlapping tasks, exact duplicates, and fully contained slots while ignoring non-overlapping tasks. We also checked that conflict messages include task names for clear UI warnings.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Confidence is high for these behaviors. Some gaps remain, such as twice-daily tasks, health-based constraints, max daily time enforcement, and TaskHistory streak calculations.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The part I am most satisfied with is how the layers of the project connect from start to finish. I went from a UML diagram on paper to working Python classes, then integrated those classes into a Streamlit UI, and finally wrote tests to verify behavior at each layer. It felt like a real software project, not just a coding exercise.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

The twice_daily logic in is_due() checks if the current hour is past noon, which can break if the owner's schedule does not follow a morning/evening split. I would redesign it to track how many times a task is completed per day instead of relying on the hour. I would also add persistence, since currently all state is in Streamlit session state and resets on page reload, causing users to lose their task history.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The main lesson I learned is that AI handles single-method suggestions well but often misses how methods interact. Each line Copilot suggested made sense on its own, but it did not handle registering a successor or updating history in the same call. The most valuable use of AI was design review. Asking questions like "does this class have too many responsibilities?" or "what could go wrong with this flow?" gave more useful insights than asking it to write code.