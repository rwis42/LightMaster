from __future__ import annotations

from typing import List, Tuple, Optional, Callable
import threading
from time import sleep
from datetime import datetime

from ScheduledEvent import ScheduledEvent


class EventScheduler:
	"""Manages a collection of `ScheduledEvent`s with integer priorities.

	Use `add_event` to register events with a priority (higher value = higher
	priority). `get_highest_priority_event` returns the event active at the
	given time with the highest priority. `run` starts a simple processing
	loop that calls a callback whenever the active event changes.
	"""

	def __init__(self) -> None:
		self._events: List[Tuple[int, ScheduledEvent]] = []
		self._lock = threading.Lock()

	def add_event(self, event: ScheduledEvent, priority: int = 0) -> None:
		with self._lock:
			self._events.append((priority, event))

	def remove_event(self, event: ScheduledEvent) -> bool:
		with self._lock:
			for i, (_p, e) in enumerate(self._events):
				if e == event:
					del self._events[i]
					return True
		return False

	def get_matching_events(self, now: Optional[datetime] = None) -> List[Tuple[int, ScheduledEvent]]:
		now = now or datetime.now()
		with self._lock:
			return [(p, e) for (p, e) in self._events if e.contains(now)]

	def get_highest_priority_event(self, now: Optional[datetime] = None) -> Optional[ScheduledEvent]:
		matches = self.get_matching_events(now)
		if not matches:
			return None
		# sort by priority descending, tie-breaker by earliest start_datetime
		matches.sort(key=lambda pe: (-pe[0], pe[1].start_datetime))
		return matches[0][1]

	def run(self, callback: Callable[[Optional[ScheduledEvent]], None], interval: float = 1.0, stop_event: Optional[threading.Event] = None) -> None:
		"""Start a loop that checks active event every `interval` seconds.

		`callback` will be called with the current highest-priority
		`ScheduledEvent` (or `None` if none match). Callback is called only
		when the active event changes.
		"""
		if stop_event is None:
			stop_event = threading.Event()

		last_event: Optional[ScheduledEvent] = None
		while not stop_event.is_set():
			evt = self.get_highest_priority_event()
			if evt != last_event:
				try:
					callback(evt)
				except Exception:
					pass
				last_event = evt
			sleep(interval)

