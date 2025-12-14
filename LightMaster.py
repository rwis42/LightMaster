from Scheduler import EventScheduler
from ScheduledEvent import ScheduledEvent
from LightPattern import LightPattern
from datetime import datetime
from time import sleep
from typing import Optional


def run_processing_loop(scheduler: EventScheduler) -> None:
    """
    Run a processing loop that checks for the highest priority scheduled event
    at regular intervals and invokes the callback with the event or None.
    The loop continues until exit_loop is set.
    """
    current_event: Optional[ScheduledEvent] = None
    while not exit_loop:
        event: Optional[ScheduledEvent] = scheduler.get_highest_priority_event()
        if event != current_event and event is not None:
            print(f"Active Event: {event.name} (Priority: {event.priority})")
            current_event = event
            event.pattern.display()
        else:
            print("No active event.")
            sleep(5)


if __name__ == "__main__":
    from datetime import timedelta

    now = datetime.now()
    e1 = ScheduledEvent.from_datetimes(now + timedelta(seconds=30), now + timedelta(seconds=40))
    e1.pattern._lights.append(LightPattern.Light(color=(255, 0, 0), count=5))
    e1.pattern._lights.append(LightPattern.Light(color=(0, 255, 0), count=3))    
    e2 = ScheduledEvent.from_datetimes(now + timedelta(seconds=10), now + timedelta(seconds=50))
    e2.pattern._lights.append(LightPattern.Light(color=(0, 0, 255), count=10))
    e3 = ScheduledEvent.from_datetimes(now + timedelta(seconds=100), now + timedelta(seconds=150))
    e3.pattern._lights.append(LightPattern.Light(color=(10, 10, 255), count=1))

    sched = EventScheduler()
    sched.add_event(e1, priority=1)
    sched.add_event(e2, priority=2)
    sched.add_event(e3, priority=1)

    exit_loop = False
    run_processing_loop(sched)
    # To stop the loop, set exit_loop = True from another thread or signal handler.

