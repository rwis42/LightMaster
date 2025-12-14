from datetime import datetime, timedelta
from ScheduledEvent import ScheduledEvent


def main() -> int:
    now = datetime.now()
    ev = ScheduledEvent.from_datetimes(now, now + timedelta(hours=1))
    ev.id = 123
    ev.name = "Demo Event"
    ev.priority = 5
    ev.pattern.add_light((255, 0, 0), 2)
    ev.pattern.add_light((0, 255, 0), 1)

    path = "demo_event.json"
    ev.to_json_file(path)
    print(f"Wrote event to {path}")

    ev2 = ScheduledEvent.from_json_file(path)
    print("Read back:", ev2.to_dict())

    # simple verification
    ok = ev2.id == ev.id and ev2.name == ev.name and ev2.priority == ev.priority
    print("Verification:", "OK" if ok else "FAILED")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
