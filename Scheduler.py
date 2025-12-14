
from __future__ import annotations

from typing import List, Tuple, Optional, Callable
from time import sleep
from datetime import datetime

from ScheduledEvent import ScheduledEvent


class EventScheduler:

    def __init__(self) -> None:
        self._events: List[Tuple[int, ScheduledEvent]] = []

    def add_event(self, event: ScheduledEvent, priority: int = 0) -> None:
        self._events.append((priority, event))

    def remove_event(self, event: ScheduledEvent) -> bool:
        for i, (_p, e) in enumerate(self._events):
            if e == event:
                del self._events[i]
                return True
        return False

    def get_matching_events(self, now: Optional[datetime] = None) -> List[Tuple[int, ScheduledEvent]]:
        now = now or datetime.now()
        return [(p, e) for (p, e) in self._events if e.contains(now)]

    def get_highest_priority_event(self, now: Optional[datetime] = None) -> Optional[ScheduledEvent]:
        matches = self.get_matching_events(now)
        if not matches:
            return None
        # sort by priority descending, tie-breaker by earliest start_datetime
        matches.sort(key=lambda pe: (-pe[0], pe[1].start_datetime))
        return matches[0][1]

