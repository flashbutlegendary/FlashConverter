import threading
from typing import Dict, Optional

class ProgressManager:
    """
    A thread-safe, memory-based system state broker.
    Allows concurrent API request tracking without database dependencies.
    """
    def __init__(self):
        self._lock = threading.Lock()
        self._states: Dict[str, Dict] = {}

    def set_progress(self, task_id: str, percentage: int, status_message: str):
        with self._lock:
            self._states[task_id] = {
                "task_id": task_id,
                "percentage": percentage,
                "status": status_message
            }

    def get_progress(self, task_id: str) -> Optional[Dict]:
        with self._lock:
            return self._states.get(task_id)

    def remove_task(self, task_id: str):
        with self._lock:
            if task_id in self._states:
                del self._states[task_id]

# Shared Global Singleton Instance
progress_manager = ProgressManager()