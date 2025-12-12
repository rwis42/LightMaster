import threading
import time
import heapq
import itertools
from typing import Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

# Scheduler.py

@dataclass(order=True)
class _Scheduled:
    when: float
    seq: int
    func: Callable[..., Any] = field(compare=False)
    args: tuple = field(compare=False, default=())
    kwargs: dict = field(compare=False, default_factory=dict)
    interval: Optional[float] = field(compare=False, default=None)
    id: int = field(compare=False, default=0)

class Scheduler:
    """
    A simple thread-backed event scheduler.
    Methods:
      - start()/stop()
      - schedule_after(delay, func, *args, **kwargs)
      - schedule_at(when_wall_time, func, ...)
      - schedule_every(interval, func, ...)
      - cancel(event_id)
    """

    def __init__(self):
        self._lock = threading.Condition()
        self._pq = []  # heap of _Scheduled
        self._counter = itertools.count()
        self._id_counter = itertools.count(1)
        self._canceled = set()
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        with self._lock:
            if self._running:
                return
            self._running = True
            self._thread = threading.Thread(target=self._run, daemon=True, name="SchedulerThread")
            self._thread.start()

    def stop(self, wait=True):
        with self._lock:
            if not self._running:
                return
            self._running = False
            self._lock.notify_all()
        if wait and self._thread is not None:
            self._thread.join()

    def _now(self) -> float:
        return time.monotonic()

    def _wall_to_monotonic(self, wall_ts: float) -> float:
        # convert wall-clock timestamp (time.time() seconds) to monotonic timeline
        return self._now() + (wall_ts - time.time())

    def schedule_at(self, when: Any, func: Callable[..., Any], *args, **kwargs) -> int:
        # when can be a datetime or a float wall timestamp (time.time())
        if isinstance(when, datetime):
            wall = when.timestamp()
        else:
            wall = float(when)
        when_mono = self._wall_to_monotonic(wall)
        return self._schedule_at_monotonic(when_mono, func, args, kwargs, interval=None)

    def _schedule_at_monotonic(self, when: float, func: Callable, args: tuple, kwargs: dict, interval: Optional[float]) -> int:
        with self._lock:
            seq = next(self._counter)
            eid = next(self._id_counter)
            item = _Scheduled(when=when, seq=seq, func=func, args=args, kwargs=kwargs, interval=interval, id=eid)
            heapq.heappush(self._pq, item)
            # wake up run loop if this is the next event
            if self._pq[0] is item:
                self._lock.notify_all()
            return eid

    def cancel(self, event_id: int) -> bool:
        with self._lock:
            if event_id in self._canceled:
                return False
            self._canceled.add(event_id)
            self._lock.notify_all()
            return True

    def _run(self):
        while True:
            with self._lock:
                if not self._running and not self._pq:
                    return
                now = self._now()
                if not self._pq:
                    # wait until something is scheduled or stop
                    self._lock.wait()
                    continue
                next_item = self._pq[0]
                wait_time = next_item.when - now
                if wait_time > 0:
                    # wait until the next item or until new scheduling/cancel/stop
                    self._lock.wait(timeout=wait_time)
                    continue
                # pop due item
                heapq.heappop(self._pq)
            # Execute outside lock
            if next_item.id in self._canceled:
                continue
            try:
                next_item.func(*next_item.args, **next_item.kwargs)
            except Exception:
                # swallow exceptions to keep loop alive
                pass
            # Reschedule if periodic
            if next_item.interval is not None:
                next_when = max(self._now(), next_item.when + next_item.interval)
                with self._lock:
                    seq = next(self._counter)
                    item = _Scheduled(when=next_when, seq=seq, func=next_item.func,
                                      args=next_item.args, kwargs=next_item.kwargs,
                                      interval=next_item.interval, id=next_item.id)
                    heapq.heappush(self._pq, item)
                    # if previously canceled meantime, mark new instance canceled too
                    if next_item.id in self._canceled:
                        # keep canceled id, the run loop will skip it
                        pass
