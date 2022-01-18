from typing import Dict, List

from taskee import events, states


class Task:
    """Wrapper class around a persistent Earth Engine task."""

    def __init__(self, obj: Dict):
        self.status = obj
        self.id = obj["id"]
        self.description = obj["description"]
        self.event = events.New(self)

    def __str__(self) -> str:
        return f"<{self.id}>: {self.description} [{self.state}]"

    @property
    def state(self) -> str:
        """Get the last state of the task."""
        return self.status["state"]

    def update(self, new_status: Dict) -> None:
        """Update the status of the task and record any changed attributes as events."""

        last_state = self.status["state"]
        new_state = new_status["state"]
        # Only track attempts for running tasks
        last_attempt = self.status["attempt"] if last_state == states.RUNNING else None
        new_attempt = self.status["attempt"] if last_state == states.RUNNING else None

        self.event = events.parse_event(
            self, last_state, new_state, last_attempt, new_attempt
        )

        self.status = new_status


class TaskManager:
    """Manager class for handling all Earth Engine tasks."""

    def __init__(self, tasks: Dict):
        self.tasks = {}
        self.update(tasks)

    def update(self, task_list: List[Dict]) -> None:
        """Update all tasks. Existing tasks will be updated and new tasks will be added to the manager."""
        current_tasks = self.tasks.keys()

        for task in task_list:
            task_id = task["id"]

            # Store new tasks
            if task_id not in current_tasks:
                new_task = Task(task)
                self.tasks[task_id] = new_task

            # Update existing tasks
            else:
                self.tasks[task_id].update(task)
