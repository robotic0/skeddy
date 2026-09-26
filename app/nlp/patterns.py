"""Bilingual (Uzbek + English) lexicon and regexes for the reminder parser.

Everything the parser needs to recognise time, weekdays, ordinals and
recurrence keywords lives here so the grammar is easy to extend.
"""
from __future__ import annotations

import re

# --- Weekdays -> Python weekday number (Mon=0 .. Sun=6) --------------------
WEEKDAYS: dict[str, int] = {
    # Uzbek
    "dushanba": 0,
    "seshanba": 1,
    "chorshanba": 2,
    "payshanba": 3,
    "juma": 4,
    "shanba": 5,
    "yakshanba": 6,
    # English
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6,
}

# APScheduler cron uses three-letter lowercase day names.
CRON_DOW = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

# --- Ordinals (nth weekday of month) ---------------------------------------
ORDINALS: dict[str, int] = {
    # Uzbek
    "birinchi": 1,
    "ikkinchi": 2,
    "uchinchi": 3,
    "to'rtinchi": 4,
    "toʻrtinchi": 4,
    "turtinchi": 4,
    "oxirgi": -1,
    "songgi": -1,
    "so'nggi": -1,
    # English
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "last": -1,
}

# --- Time-unit words -> canonical unit -------------------------------------
UNITS: dict[str, str] = {
    "daqiqa": "minutes",
    "minut": "minutes",
    "minute": "minutes",
    "minutes": "minutes",
    "min": "minutes",
    "soat": "hours",
    "hour": "hours",
    "hours": "hours",
    "kun": "days",
    "day": "days",
    "days": "days",
    "hafta": "weeks",
    "week": "weeks",
    "weeks": "weeks",
}

# --- Day-period words -> default hour ---------------------------------------
DAY_PERIODS: dict[str, int] = {
    "ertalab": 9,
    "tong": 7,
    "tush": 12,
    "tushda": 12,
    "peshin": 12,
    "kunduzi": 14,
    "kechqurun": 19,
    "kechasi": 22,
    "kech": 21,
    "morning": 9,
    "noon": 12,
    "afternoon": 14,
    "evening": 19,
    "night": 22,
}

# Words that mark a PM interpretation for a bare hour.
PM_HINTS = {"kechqurun", "kechasi", "kech", "evening", "night", "pm", "afternoon"}
AM_HINTS = {"ertalab", "tong", "morning", "am"}

# --- Recurrence keyword groups ---------------------------------------------
EVERY_WORDS = ("har", "every", "each")
DAILY_WORDS = ("har kuni", "kunlik", "every day", "daily", "everyday")
WEEKLY_WORDS = ("har hafta", "haftalik", "every week", "weekly")
MONTHLY_WORDS = ("har oy", "oylik", "every month", "monthly")
HOURLY_WORDS = ("har soat", "soatlik", "every hour", "hourly")

# Filler words stripped from the extracted reminder message.
FILLER_WORDS = (
    "menga",
    "eslat",
    "eslatib",
    "eslatma",
    "eslatishni",
    "qil",
    "qilishni",
    "remind",
    "me",
    "to",
    "that",
    "please",
    "kerak",
)

# --- Compiled regexes -------------------------------------------------------

# "soat 9:30 da", "soat 9 da", "at 9:30", "9am", "9 pm", "9:00"
TIME_RE = re.compile(
    r"""
    (?:\bsoat\s+|\bat\s+)?          # optional "soat"/"at"
    (?P<hour>2[0-3]|[01]?\d)         # hour 0-23 (two-digit forms tried first)
    (?::(?P<minute>[0-5]\d))?        # optional :minutes
    \s*(?P<ampm>am|pm)?              # optional am/pm
    (?:\s*da\b)?                     # optional Uzbek locative "da"
    """,
    re.VERBOSE | re.IGNORECASE,
)

# "in 30 minutes", "30 daqiqadan keyin", "2 soatdan song"
RELATIVE_RE = re.compile(
    r"""
    (?:\bin\s+)?
    (?P<amount>\d+)\s*
    (?P<unit>daqiqa|minut|minute|minutes|min|soat|hour|hours|kun|day|days|hafta|week|weeks)
    (?:dan)?\s*(?:keyin|song|so'ng|soʻng|later)?
    """,
    re.VERBOSE | re.IGNORECASE,
)

# "every 15 minutes", "har 2 soat"
INTERVAL_RE = re.compile(
    r"""
    \b(?:har|every|each)\s+
    (?P<amount>\d+)\s*
    (?P<unit>daqiqa|minut|minute|minutes|min|soat|hour|hours|kun|day|days|hafta|week|weeks)
    """,
    re.VERBOSE | re.IGNORECASE,
)

# ISO or dotted dates: 2026-09-27 or 27.09.2026 or 27.09
DATE_RE = re.compile(
    r"\b(?P<y>\d{4})-(?P<m>\d{1,2})-(?P<d>\d{1,2})\b"
    r"|\b(?P<d2>\d{1,2})\.(?P<m2>\d{1,2})(?:\.(?P<y2>\d{4}))?\b"
)


def weekday_alternation() -> str:
    return "|".join(sorted(WEEKDAYS, key=len, reverse=True))


def ordinal_alternation() -> str:
    return "|".join(re.escape(o) for o in sorted(ORDINALS, key=len, reverse=True))


# "birinchi dushanba", "first monday", "oxirgi juma"
NTH_WEEKDAY_RE = re.compile(
    rf"\b(?P<ord>{ordinal_alternation()})\s+(?P<wd>{weekday_alternation()})",
    re.IGNORECASE,
)

# a bare weekday mention, e.g. "dushanba" / "monday"
WEEKDAY_RE = re.compile(rf"\b(?P<wd>{weekday_alternation()})\b", re.IGNORECASE)

TOMORROW_WORDS = ("ertaga", "tomorrow")
TODAY_WORDS = ("bugun", "today")
