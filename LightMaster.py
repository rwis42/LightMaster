from Scheduler import EventScheduler
from ScheduledEvent import ScheduledEvent
from LightPattern import LightPattern
from datetime import datetime
from time import sleep
from typing import Optional, List
import sys
import json
from pathlib import Path

try:
    from rpi_controller import LEDController
except Exception:
    LEDController = None


def run_processing_loop(scheduler: EventScheduler, controller: Optional[object] = None) -> None:
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
            if controller:
                controller.send_pattern(event.pattern)
            else:
                event.pattern.display()
            sleep(0.01)
        else:
            # no active event
            if controller:
                controller.clear()
            else:
                print("No active event.")
            sleep(5)


if __name__ == "__main__":
    from datetime import timedelta

    def load_events_from_file(path: Path) -> List[ScheduledEvent]:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        events: List[ScheduledEvent] = []
        if isinstance(data, list):
            for item in data:
                # each item should be a dict compatible with ScheduledEvent.from_dict
                try:
                    ev = ScheduledEvent.from_dict(item)
                    events.append(ev)
                except Exception:
                    continue
        elif isinstance(data, dict):
            # single event
            try:
                events.append(ScheduledEvent.from_dict(data))
            except Exception:
                pass
        return events

    sched = EventScheduler()

    # parse CLI args: optional JSON path and flags --leds and --num-pixels=N
    leds_enabled = any(arg == "--leds" for arg in sys.argv[1:])
    num_pixels = 60
    for arg in sys.argv[1:]:
        if arg.startswith("--num-pixels="):
            try:
                num_pixels = int(arg.split("=", 1)[1])
            except Exception:
                pass

    # first non-flag arg is considered the JSON file path
    json_path = None
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            continue
        json_path = arg
        break

    if json_path:
        p = Path(json_path)
        if p.exists():
            for ev in load_events_from_file(p):
                sched.add_event(ev, priority=getattr(ev, "priority", 0))
    # otherwise create a few sample events
    if not any(True for _ in sched._events):
        now = datetime.now()
        e1 = ScheduledEvent.from_datetimes(now + timedelta(seconds=30), now + timedelta(seconds=40))
        e1.pattern.add_light((255, 0, 0), 5)
        e1.pattern.add_light((0, 255, 0), 3)
        e2 = ScheduledEvent.from_datetimes(now + timedelta(seconds=10), now + timedelta(seconds=50))
        e2.pattern.add_light((0, 0, 255), 10)
        e3 = ScheduledEvent.from_datetimes(now + timedelta(seconds=100), now + timedelta(seconds=150))
        e3.pattern.add_light((10, 10, 255), 1)

        sched.add_event(e1, priority=1)
        sched.add_event(e2, priority=2)
        sched.add_event(e3, priority=1)

    controller = None
    if leds_enabled and LEDController is not None:
        controller = LEDController(num_pixels)

    exit_loop = False
    run_processing_loop(sched, controller=controller)
    # To stop the loop, set exit_loop = True from another thread or signal handler.

