import tempfile
import shutil
from pathlib import Path

# Use the operating system's default fast temp directories
BASE_TEMP_DIR = Path(tempfile.gettempdir()) / "flash_converter"

def create_task_workspace(task_id: str) -> Path:
    """
    Creates isolated scratch workspaces for every individual conversion job.
    Ensures absolute data partitioning.
    """
    workspace = BASE_TEMP_DIR / task_id
    workspace.mkdir(parents=True, exist_ok=True)
    return workspace

def remove_task_workspace(workspace_path: Path):
    """
    Secure directory deletion garbage collector.
    Fires in a BackgroundTask thread after file transmission succeeds.
    """
    try:
        if workspace_path.exists() and workspace_path.is_dir():
            shutil.rmtree(workspace_path)
            print(f"[CLEANUP SYSTEM] Destroyed temp path workspace: {workspace_path.name}")
    except OSError as e:
        print(f"[CLEANUP ERROR] Failed to clean temp workspace directory {workspace_path}: {e}")