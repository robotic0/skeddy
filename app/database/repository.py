"""Data-access helpers for users and reminders."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Reminder, User
from app.nlp.recurrence import Schedule


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_or_create(
        self, user_id: int, default_timezone: str
    ) -> User:
        user = await self._session.get(User, user_id)
        if user is None:
            user = User(id=user_id, timezone=default_timezone)
            self._session.add(user)
            await self._session.flush()
        return user

    async def set_timezone(self, user_id: int, timezone: str) -> None:
        user = await self._session.get(User, user_id)
        if user:
            user.timezone = timezone


class ReminderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: int,
        message: str,
        original_text: str,
        human_readable: str,
        schedule: Schedule,
    ) -> Reminder:
        reminder = Reminder(
            user_id=user_id,
            message=message,
            original_text=original_text,
            human_readable=human_readable,
            schedule_kind=schedule.kind,
            schedule_spec=schedule.to_json(),
        )
        self._session.add(reminder)
        await self._session.flush()
        return reminder

    async def get(self, reminder_id: int) -> Reminder | None:
        return await self._session.get(Reminder, reminder_id)

    async def list_active(self, user_id: int) -> list[Reminder]:
        result = await self._session.scalars(
            select(Reminder)
            .where(Reminder.user_id == user_id, Reminder.active.is_(True))
            .order_by(Reminder.created_at.desc())
        )
        return list(result)

    async def all_active(self) -> list[Reminder]:
        result = await self._session.scalars(
            select(Reminder).where(Reminder.active.is_(True))
        )
        return list(result)

    async def deactivate(self, reminder_id: int) -> None:
        reminder = await self._session.get(Reminder, reminder_id)
        if reminder:
            reminder.active = False
