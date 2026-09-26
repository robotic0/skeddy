"""Aggregates all feature routers."""
from aiogram import Router

from app.handlers import reminders, start


def get_routers() -> list[Router]:
    return [start.router, reminders.router]


__all__ = ["get_routers"]
