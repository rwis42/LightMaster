import threading
import time
from datetime import datetime, timedelta

from Scheduler import EventScheduler
from ScheduledEvent import ScheduledEvent
from LightPattern import LightPattern
from LightMaster import run_processing_loop

try:
    from rpi_controller import LEDController
except Exception:
    LEDController = None


def main() -> None:
    now = datetime.now()
    # event active now
    ev = ScheduledEvent.from_datetimes(now - timedelta(seconds=5), now + timedelta(seconds=5))
    ev.pattern.add_light((255, 0, 0), 2)

    sched = EventScheduler()
    sched.add_event(ev, priority=1)

    # ensure module-level exit flag is available
    import LightMaster as LM
    LM.exit_loop = False

    controller = None
    if LEDController is not None:
        controller = LEDController(num_pixels=8)

    t = threading.Thread(target=run_processing_loop, args=(sched, controller), daemon=True)
    t.start()

    # run for a short time
    time.sleep(3)
    LM.exit_loop = True
    t.join(timeout=2)
    print("smoke test finished")


if __name__ == "__main__":
    main()
