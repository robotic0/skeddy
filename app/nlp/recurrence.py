"""The :class:`Schedule` value object — a backend-agnostic description of
when a reminder fires, plus its conversion to an APScheduler trigger.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

ScheduleKind = Literal["once", "cron", "interval"]


@dataclass(slots=True)
class Schedule:
    """Describes a firing rule independently of the scheduler library."""

    kind: ScheduleKind
    run_date: datetime | None = None
    cron: dict[str, Any] = field(default_factory=dict)
    interval: dict[str, int] = field(default_factory=dict)

    # --- persistence ------------------------------------------------------
    def to_json(self) -> str:
        payload: dict[str, Any] = {"kind": self.kind}
        if self.run_date is not None:
            payload["run_date"] = self.run_date.isoformat()
        if self.cron:
            payload["cron"] = self.cron
        if self.interval:
            payload["interval"] = self.interval
        return json.dumps(payload)

    @classmethod
    def from_json(cls, raw: str) -> Schedule:
        data = json.loads(raw)
        run_date = (
            datetime.fromisoformat(data["run_date"])
            if data.get("run_date")
            else None
        )
        return cls(
            kind=data["kind"],
            run_date=run_date,
            cron=data.get("cron", {}),
            interval=data.get("interval", {}),
        )

    # --- scheduler bridge -------------------------------------------------
    def to_trigger(self, timezone: str):
        if self.kind == "once":
            return DateTrigger(run_date=self.run_date, timezone=timezone)
        if self.kind == "cron":
            return CronTrigger(timezone=timezone, **self.cron)
        if self.kind == "interval":
            return IntervalTrigger(timezone=timezone, **self.interval)
        raise ValueError(f"Unknown schedule kind: {self.kind}")

    @property
    def is_recurring(self) -> bool:
        return self.kind in {"cron", "interval"}


def nth_weekday_cron(nth: int, weekday_cron: str, hour: int, minute: int) -> dict:
    """Cron kwargs for "the Nth <weekday> of every month".

    Combining a day-of-month *range* with a day-of-week yields the Nth
    occurrence, because APScheduler ANDs the two fields:

        1st weekday -> day="1-7",   2nd -> day="8-14", ...
        last        -> day="22-31" (approximation of the final week)
    """
    if nth == -1:
        day = "22-31"
    else:
        start = (nth - 1) * 7 + 1
        day = f"{start}-{start + 6}"
    return {
        "day": day,
        "day_of_week": weekday_cron,
        "hour": hour,
        "minute": minute,
    }
