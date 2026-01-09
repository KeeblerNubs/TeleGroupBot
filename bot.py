import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import *
from storage import dj_booth
from roles import has_access
from state import get_role, set_role

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------------- START ----------------

@dp.message(F.text == "/start")
async def start(msg: Message):
    if msg.from_user.id not in dj_booth:
        set_role(msg.from_user.id, ROLE_MEMBER)

    await msg.answer("🎛 Welcome to the Community Bot!\nUse /panel")

# ---------------- PANEL ----------------

@dp.message(F.text == "/panel")
async def panel(msg: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎧 DJ Dashboard", callback_data="panel_dj"),
            InlineKeyboardButton(text="💎 Donate", callback_data="panel_donate")
        ],
        [
            InlineKeyboardButton(text="👤 My Role", callback_data="panel_role")
        ]
    ])

    await msg.answer(
        f"""🎛 COMMUNITY CONTROL PANEL

🎧 LIVE DJ BOOTH
On Decks: {dj_booth['current_dj'] or 'Vacant'}
Queue: {len(dj_booth['queue'])}
Applications: {len(dj_booth['applications'])}
""",
        reply_markup=keyboard
    )

# ---------------- MY ROLE ----------------

@dp.callback_query(F.data == "panel_role")
async def my_role(call: CallbackQuery):
    role = get_role(call.from_user.id)
    await call.answer()
    await call.message.answer(f"👤 Your role: {role}")

# ---------------- DJ DASHBOARD ----------------

@dp.callback_query(F.data == "panel_dj")
async def dj_panel(call: CallbackQuery):
    role = get_role(call.from_user.id)
    if not has_access(role, ROLE_DJ):
        await call.answer("⛔ DJ access only", show_alert=True)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Join Queue", callback_data="dj_join"),
            InlineKeyboardButton(text="➖ Leave Queue", callback_data="dj_leave")
        ]
    ])

    await call.answer()
    await call.message.answer("🎧 DJ DASHBOARD", reply_markup=keyboard)

# ---------------- DJ QUEUE ----------------

@dp.callback_query(F.data == "dj_join")
async def join_queue(call: CallbackQuery):
    user_id = call.from_user.id

    if dj_booth["status"] != "OPEN":
        await call.answer("Booth is closed", show_alert=True)
        return

    if user_id in dj_booth["queue"]:
        await call.answer("Already in queue", show_alert=True)
        return

    dj_booth["queue"].append(user_id)
    await call.answer("✅ Joined DJ queue")

@dp.callback_query(F.data == "dj_leave")
async def leave_queue(call: CallbackQuery):
    user_id = call.from_user.id

    if user_id in dj_booth["queue"]:
        dj_booth["queue"].remove(user_id)
        await call.answer("➖ Left queue")
    else:
        await call.answer("Not in queue", show_alert=True)

# ---------------- HOST COMMAND ----------------

@dp.message(F.text == "?host")
async def host_panel(msg: Message):
    role = get_role(msg.from_user.id)
    if not has_access(role, ROLE_HOST):
        await msg.answer("⛔ Host only")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔓 Open Booth", callback_data="host_open")],
        [InlineKeyboardButton(text="🔒 Close Booth", callback_data="host_close")],
        [InlineKeyboardButton(text="🧹 Clear Queue", callback_data="host_clear")]
    ])

    await msg.answer("👑 HOST CONTROL PANEL", reply_markup=keyboard)

# ---------------- HOST ACTIONS ----------------

@dp.callback_query(F.data == "host_open")
async def host_open(call: CallbackQuery):
    dj_booth["status"] = "OPEN"
    await call.answer("Booth opened")

@dp.callback_query(F.data == "host_close")
async def host_close(call: CallbackQuery):
    dj_booth["status"] = "CLOSED"
    await call.answer("Booth closed")

@dp.callback_query(F.data == "host_clear")
async def host_clear(call: CallbackQuery):
    dj_booth["queue"].clear()
    dj_booth["current_dj"] = None
    await call.answer("Queue cleared")

# ---------------- RUN ----------------

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
