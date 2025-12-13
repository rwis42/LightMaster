from Scheduler import EventScheduler
from ScheduledEvent import ScheduledEvent
from LightPattern import LightPattern
from datetime import datetime
import threading
from time import sleep
from typing import Optional


if __name__ == "__main__":
	# Simple demo when running the module directly.
	from datetime import timedelta

	now = datetime.now()
	e1 = ScheduledEvent.from_datetimes(now - timedelta(seconds=30), now + timedelta(seconds=30))
	e1.pattern._lights.append(LightPattern.Light(color=(255, 0, 0), count=5)).append(LightPattern.Light(color=(0, 255, 0), count=3))    
	e2 = ScheduledEvent.from_datetimes(now - timedelta(seconds=10), now + timedelta(seconds=50))
	e2.pattern._lights.append(LightPattern.Light(color=(0, 0, 255), count=10))

	sched = EventScheduler()
	sched.add_event(e1, priority=1)
	sched.add_event(e2, priority=2)

	stop = threading.Event()

	def cb(ev: Optional[ScheduledEvent]) -> None:
		if ev is None:
			print("No active event")
		else:
			print(f"Active: {ev.name!r} id={ev.id} start={ev.start_datetime}")
			ev.pattern.display()

	try:
		# run for a short demo period
		t = threading.Thread(target=sched.run, args=(cb, 0.5, stop), daemon=True)
		t.start()
		sleep(5)
	finally:
		stop.set()

