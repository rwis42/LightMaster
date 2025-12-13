from dataclasses import dataclass
from datetime import date, time, datetime, timedelta
from typing import Dict, Optional
from LightPattern import LightPattern


@dataclass
class ScheduledEvent:
    start_date: date
    start_time: time
    end_date: date
    end_time: time
    id: int = 0
    name: str = ""
    priority: int = 0
    pattern: LightPattern

    def __post_init__(self) -> None:
        if self.end_datetime < self.start_datetime:
            raise ValueError("end datetime must be same or after start datetime")

    @property
    def start_datetime(self) -> datetime:
        return datetime.combine(self.start_date, self.start_time)

    @property
    def end_datetime(self) -> datetime:
        return datetime.combine(self.end_date, self.end_time)

    def contains(self, dt: datetime) -> bool:
        return self.start_datetime <= dt <= self.end_datetime

    def to_iso(self) -> Dict[str, str]:
        return {
            "start": self.start_datetime.isoformat(),
            "end": self.end_datetime.isoformat(),
        }

    @classmethod
    def from_datetimes(cls, start: datetime, end: datetime) -> "ScheduledEvent":
        fields = getattr(cls, "__dataclass_fields__", {})
        if "id" in fields and "name" in fields:
            return cls(start.date(), start.time(), end.date(), end.time(), id=None, name="")
        if "id" in fields:
            return cls(start.date(), start.time(), end.date(), end.time(), id=None)
        if "name" in fields:
            return cls(start.date(), start.time(), end.date(), end.time(), name="")
        return cls(start.date(), start.time(), end.date(), end.time(), name="")