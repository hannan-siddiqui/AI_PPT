"""
Asynchronous Orchestration & In-Memory Job Queue
Enables non-blocking presentation generation with real-time polling.
"""
import uuid
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional

MAX_WORKERS = 4
_executor = ThreadPoolExecutor(max_workers=MAX_WORKERS, thread_name_prefix="PPTGenWorker")
_lock = threading.Lock()
_jobs: Dict[str, Dict[str, Any]] = {}


def create_job(metadata: Optional[Dict[str, Any]] = None) -> str:
    """Create a new job and register it with 'queued' status."""
    job_id = str(uuid.uuid4())
    now = time.time()
    with _lock:
        _jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "step": "Stage 1/5: Request ingested and queued",
            "progress": 5,
            "created_at": now,
            "updated_at": now,
            "metadata": metadata or {},
            "logs": [],
            "result": None,
            "error": None
        }
    return job_id


def update_job(
    job_id: str,
    status: Optional[str] = None,
    step: Optional[str] = None,
    progress: Optional[int] = None,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    log_msg: Optional[str] = None,
    logs: Optional[list] = None
) -> None:
    """Update progress, status, logs, or result for an active job."""
    with _lock:
        if job_id not in _jobs:
            return
        job = _jobs[job_id]
        if status is not None:
            job["status"] = status
        if step is not None:
            job["step"] = step
        if progress is not None:
            job["progress"] = progress
        if result is not None:
            job["result"] = result
        if error is not None:
            job["error"] = error
            job["status"] = "failed"
        if logs is not None:
            job["logs"] = list(logs)
        if log_msg:
            job.setdefault("logs", []).append(log_msg)
        job["updated_at"] = time.time()


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve current state of a job."""
    with _lock:
        job = _jobs.get(job_id)
        if job:
            return dict(job)
        return None


def submit_task(job_id: str, fn, *args, **kwargs):
    """Execute a long-running generation pipeline in background thread."""
    def _runner():
        try:
            fn(job_id, *args, **kwargs)
        except Exception as e:
            import traceback
            traceback.print_exc()
            update_job(
                job_id,
                status="failed",
                step=f"Error encountered: {str(e)}",
                error=str(e)
            )

    _executor.submit(_runner)
