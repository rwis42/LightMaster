from dataclasses import dataclass, field
from datetime import date, time, datetime, timedelta
from typing import Dict, Optional, List, Union
from pathlib import Path
import json

from LightPattern import LightPattern


@dataclass
class ScheduledEvent:
    start_date: date
    start_time: time
    end_date: date
    end_time: time
    pattern: LightPattern = field(default_factory=LightPattern)
    id: Optional[int] = None
    name: str = ""
    priority: int = 0

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

    def to_dict(self) -> Dict[str, Union[str, int, List[Dict[str, Union[List[int], int]]]]]:
        return {
            "start": self.start_datetime.isoformat(),
            "end": self.end_datetime.isoformat(),
            "id": self.id,
            "name": self.name,
            "priority": self.priority,
            "pattern": [
                {"color": list(l.color), "count": l.count} for l in self.pattern.as_list()
            ],
        }

    def to_json_file(self, path: Union[str, Path]) -> None:
        p = Path(path)
        with p.open("w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2)

    @classmethod
    def from_dict(cls, data: Dict) -> "ScheduledEvent":
        start = datetime.fromisoformat(data["start"])
        end = datetime.fromisoformat(data["end"])
        pattern = LightPattern()
        for item in data.get("pattern", []):
            color = tuple(item.get("color", (255, 255, 255)))
            count = int(item.get("count", 1))
            pattern.add_light(color, count)
        return cls(start.date(), start.time(), end.date(), end.time(), pattern=pattern, id=data.get("id"), name=data.get("name", ""), priority=int(data.get("priority", 0)))

    @classmethod
    def from_json_file(cls, path: Union[str, Path]) -> "ScheduledEvent":
        p = Path(path)
        with p.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls.from_dict(data)

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