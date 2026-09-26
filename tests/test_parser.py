"""Unit tests for the natural-language reminder parser."""
from __future__ import annotations

from datetime import datetime

import pytest

from app.nlp import parse

NOW = datetime(2026, 9, 26, 12, 0)  # a Saturday, noon


def test_returns_none_for_non_temporal_text():
    assert parse("salom qalaysan", now=NOW) is None


def test_relative_minutes():
    result = parse("30 daqiqadan keyin choynakni o'chir", now=NOW)
    assert result is not None
    assert result.schedule.kind == "once"
    assert result.schedule.run_date == datetime(2026, 9, 26, 12, 30)
    assert "choynak" in result.message.lower()


def test_relative_english():
    result = parse("in 2 hours call mom", now=NOW)
    assert result.schedule.kind == "once"
    assert result.schedule.run_date == datetime(2026, 9, 26, 14, 0)


def test_tomorrow_with_time():
    result = parse("ertaga soat 9 da shifokorga qo'ng'iroq qil", now=NOW)
    assert result.schedule.kind == "once"
    assert result.schedule.run_date == datetime(2026, 9, 27, 9, 0)


def test_daily():
    result = parse("har kuni 22:00 da suv ich", now=NOW)
    assert result.schedule.kind == "cron"
    assert result.schedule.cron == {"hour": 22, "minute": 0}


def test_weekly_specific_day():
    result = parse("har dushanba soat 10 da hisobotni yubor", now=NOW)
    assert result.schedule.kind == "cron"
    assert result.schedule.cron["day_of_week"] == "mon"
    assert result.schedule.cron["hour"] == 10


def test_every_monday_english():
    result = parse("every monday at 18:30 water the plants", now=NOW)
    assert result.schedule.cron["day_of_week"] == "mon"
    assert result.schedule.cron["hour"] == 18
    assert result.schedule.cron["minute"] == 30


def test_interval_minutes():
    result = parse("har 15 daqiqada holatni tekshir", now=NOW)
    assert result.schedule.kind == "interval"
    assert result.schedule.interval == {"minutes": 15}


def test_hourly():
    result = parse("har soatda ko'zni dam oldir", now=NOW)
    assert result.schedule.kind == "cron"
    assert result.schedule.cron == {"minute": 0}


def test_first_monday_of_month_the_headline_example():
    result = parse(
        "har oyning birinchi dushanbasida ertalab soat 9 da "
        "server jurnallarini tekshir",
        now=NOW,
    )
    assert result.schedule.kind == "cron"
    cron = result.schedule.cron
    assert cron["day"] == "1-7"
    assert cron["day_of_week"] == "mon"
    assert cron["hour"] == 9
    assert cron["minute"] == 0


def test_last_friday_of_month():
    result = parse("har oyning oxirgi juma 17:00 da hisobotni yop", now=NOW)
    assert result.schedule.cron["day"] == "22-31"
    assert result.schedule.cron["day_of_week"] == "fri"


def test_day_period_default_evening():
    result = parse("ertaga kechqurun mashina yuvishni eslat", now=NOW)
    # kechqurun -> 19:00
    assert result.schedule.run_date == datetime(2026, 9, 27, 19, 0)


def test_explicit_date():
    result = parse("27.09 soat 15:30 da to'lovni amalga oshir", now=NOW)
    assert result.schedule.kind == "once"
    assert result.schedule.run_date == datetime(2026, 9, 27, 15, 30)


def test_bare_time_today_rolls_to_tomorrow_if_past():
    # 09:00 is before NOW (12:00) -> should roll to next day
    result = parse("soat 9 da yugur", now=NOW)
    assert result.schedule.run_date == datetime(2026, 9, 27, 9, 0)


@pytest.mark.parametrize(
    "text",
    [
        "har kuni 08:00 da mashq qil",
        "every day at 8 do exercise",
    ],
)
def test_schedule_roundtrips_through_json(text):
    from app.nlp.recurrence import Schedule

    parsed = parse(text, now=NOW)
    restored = Schedule.from_json(parsed.schedule.to_json())
    assert restored.kind == parsed.schedule.kind
    assert restored.cron == parsed.schedule.cron
