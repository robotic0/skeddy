"""/start, /help and /timezone."""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.database.repository import UserRepository
from app.services.scheduler import is_valid_timezone

router = Router(name="start")

WELCOME = (
    "👋 Salom! Men <b>Skeddy</b> — tabiiy tilni tushunadigan eslatma botman.\n\n"
    "Menga oddiy gap bilan yozing, men vaqtni o‘zim tushunaman:\n\n"
    "• <i>Ertaga soat 9 da shifokorga qo‘ng‘iroq qilishni eslat</i>\n"
    "• <i>Har kuni 22:00 da suv ichishni eslat</i>\n"
    "• <i>Har dushanba soat 10 da hisobotni yubor</i>\n"
    "• <i>Har oyning birinchi dushanbasida ertalab soat 9 da serverni tekshir</i>\n"
    "• <i>30 daqiqadan keyin choynakni o‘chir</i>\n\n"
    "📋 /list — eslatmalaringiz\n"
    "🌍 /timezone Asia/Tashkent — vaqt mintaqasi\n"
    "❓ /help — batafsil yordam"
)

HELP = (
    "<b>Skeddy qanday ishlaydi</b>\n\n"
    "Shunchaki nima va qachon eslatishimni yozing. Men o‘zbek va ingliz tilidagi "
    "iboralarni tushunaman.\n\n"
    "<b>Bir martalik</b>\n"
    "• <code>ertaga 9:00 da ...</code>\n"
    "• <code>bugun soat 18 da ...</code>\n"
    "• <code>2 soatdan keyin ...</code>\n"
    "• <code>27.09 soat 15:30 da ...</code>\n\n"
    "<b>Takrorlanuvchi</b>\n"
    "• <code>har kuni 08:00 da ...</code>\n"
    "• <code>har dushanba 10:00 da ...</code>\n"
    "• <code>har soatda ...</code>\n"
    "• <code>har 15 daqiqada ...</code>\n"
    "• <code>har oyning birinchi dushanbasida 9:00 da ...</code>\n\n"
    "<b>Kun qismlari</b>: ertalab, tush, kechqurun, kechasi\n"
    "<b>Vaqt mintaqasi</b>: <code>/timezone Asia/Tashkent</code>"
)


@router.message(Command("start"))
async def cmd_start(
    message: Message, users: UserRepository, default_tz: str
) -> None:
    await users.get_or_create(message.chat.id, default_tz)
    await message.answer(WELCOME)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP)


@router.message(Command("timezone"))
async def cmd_timezone(
    message: Message,
    command: CommandObject,
    users: UserRepository,
    default_tz: str,
) -> None:
    tz = (command.args or "").strip()
    if not tz:
        user = await users.get_or_create(message.chat.id, default_tz)
        await message.answer(
            f"Joriy vaqt mintaqangiz: <code>{user.timezone}</code>\n"
            "O‘zgartirish uchun: <code>/timezone Asia/Tashkent</code>"
        )
        return
    if not is_valid_timezone(tz):
        await message.answer(
            "Noto‘g‘ri vaqt mintaqasi. Masalan: <code>Asia/Tashkent</code>."
        )
        return
    await users.get_or_create(message.chat.id, default_tz)
    await users.set_timezone(message.chat.id, tz)
    await message.answer(f"✅ Vaqt mintaqasi <code>{tz}</code> ga o‘rnatildi.")
