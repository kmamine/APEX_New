"""In-process async runner: schedules harness runs and fans out SSE progress.

Editing runs are CPU/GPU-bound and long, so each runs in a worker thread
(``asyncio.to_thread``) while progress events are published to per-run
subscriber queues for the SSE endpoint. GPU concurrency is effectively 1 (the
editor pipeline is shared); a queue-backed runner is added in M7 for scale.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from PIL import Image

from ..goalspec import GoalSpec
from ..loop import IterationRecord, RunStatus
from ..service.harness import ApexHarness

TERMINAL = {
    RunStatus.COMPLETED,
    RunStatus.STOPPED_MAX_ITERS,
    RunStatus.STOPPED_IDENTITY,
    RunStatus.FAILED,
    RunStatus.CANCELLED,
}


class InProcessRunner:
    def __init__(self, harness: ApexHarness) -> None:
        self.harness = harness
        self._subscribers: dict[str, list[asyncio.Queue]] = {}
        self._tasks: dict[str, asyncio.Task] = {}

    async def start(
        self,
        goal: GoalSpec,
        input_image: Image.Image,
        reference_images: Sequence[Image.Image] | None = None,
    ) -> str:
        state = self.harness.create_run(goal, input_image, reference_images)
        self._subscribers.setdefault(state.run_id, [])
        self._tasks[state.run_id] = asyncio.create_task(self._run(state.run_id))
        return state.run_id

    async def _run(self, run_id: str) -> None:
        loop = asyncio.get_running_loop()

        def progress(record: IterationRecord, _image_name: str) -> None:
            self._emit(
                run_id,
                {
                    "type": "iteration",
                    "index": record.index,
                    "decision": str(record.decision),
                    "accepted": record.accepted,
                    "overall": record.judge.overall,
                    "identity": (
                        record.metrics.identity.value if record.metrics.identity else None
                    ),
                },
                loop,
            )

        try:
            state = await asyncio.to_thread(self.harness.execute_run, run_id, progress)
            self._emit(
                run_id,
                {"type": "done", "status": str(state.status), "final_index": state.final_index},
                loop,
            )
        except asyncio.CancelledError:
            self._emit(run_id, {"type": "cancelled"}, loop)
        except Exception as exc:
            self._emit(run_id, {"type": "error", "message": str(exc)}, loop)
        finally:
            self._emit(run_id, {"type": "close"}, loop)

    def _emit(self, run_id: str, event: dict, loop: asyncio.AbstractEventLoop) -> None:
        for queue in list(self._subscribers.get(run_id, [])):
            loop.call_soon_threadsafe(queue.put_nowait, event)

    def add_subscriber(self, run_id: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.setdefault(run_id, []).append(queue)
        return queue

    def remove_subscriber(self, run_id: str, queue: asyncio.Queue) -> None:
        subscribers = self._subscribers.get(run_id)
        if subscribers and queue in subscribers:
            subscribers.remove(queue)

    async def cancel(self, run_id: str) -> bool:
        task = self._tasks.get(run_id)
        if task and not task.done():
            task.cancel()
            return True
        return False


__all__ = ["TERMINAL", "InProcessRunner"]
