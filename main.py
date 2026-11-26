#!/usr/bin/env python3
# ================================================================
#   🤖 Telegram Live Auto-Unmute BOT  (24/7)
#   ✨ Premium UI/UX Edition v2.0
#   ─────────────────────────────────────────
#   🟢 লাইভ চালু → অটো জয়েন
#   🔊 মিউটেড মেম্বার → অটো আনমিউট
#   📴 লাইভ বন্ধ → অটো লিভ
#   🛑 STOP বাটন → লিভ + বট বন্ধ
# ================================================================

import asyncio, logging, random, json, os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from telethon import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError, PhoneCodeInvalidError,
    PasswordHashInvalidError, FloodWaitError
)
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.phone import (
    JoinGroupCallRequest, EditGroupCallParticipantRequest,
    GetGroupParticipantsRequest, LeaveGroupCallRequest,
)
from telethon.tl.types import InputGroupCall
from telethon.tl import functions, types

# ──────────────────────────────────────────────
BOT_TOKEN    = os.getenv("BOT_TOKEN",  "")
API_ID       = int(os.getenv("API_ID",  "0"))
API_HASH     = os.getenv("API_HASH",   "")
ADMIN_ID     = int(os.getenv("ADMIN_ID", "0"))
UNMUTE_DELAY = 3
RECHECK_WAIT = 10
VERSION      = "2.0 ✨ Premium"
# ──────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp  = Dispatcher()

state = {
    "client":         None,
    "logged_in":      False,
    "phone":          None,
    "phone_hash":     None,
    "channel_entity": None,
    "channel_link":   None,
    "live_link":      None,
    "is_admin":       True,
    "running":        False,
    "task":           None,
    "step":           None,
    "current_call":   None,
    "in_live":        False,
    "unmute_count":   0,
}


# ══════════════════════════════════════════════
#  🎨 UI HELPER FUNCTIONS
# ══════════════════════════════════════════════

def line(char="━", n=26): return char * n

def box(title, emoji="🤖"):
    w = 22
    top    = "╔" + "═" * w + "╗"
    mid    = f"║  {emoji} <b>{title}</b>  ║"
    bottom = "╚" + "═" * w + "╝"
    return f"{top}\n{mid}\n{bottom}"

def tag_ok(txt):   return f"✅ <b>{txt}</b>"
def tag_err(txt):  return f"❌ <b>{txt}</b>"
def tag_warn(txt): return f"⚠️ <b>{txt}</b>"
def tag_info(txt): return f"ℹ️  {txt}"

def dot_badge(active, on="চালু", off="বন্ধ"):
    return f"🟢 <b>{on}</b>" if active else f"🔴 <b>{off}</b>"

def step_row(icon, label, value):
    return f"{icon} {label:<12}» {value}"


# ══════════════════════════════════════════════
#  ⌨️ KEYBOARDS  — Color-Coded Premium Layout
# ══════════════════════════════════════════════

def kb_main():
    logged  = state["logged_in"]
    running = state["running"]
    return InlineKeyboardMarkup(inline_keyboard=[
        # ── Row 1 : Auth & Info ──
        [
            InlineKeyboardButton(
                text="✅ লগিন হয়েছে" if logged else "🔐 লগিন করুন",
                callback_data="login"
            ),
            InlineKeyboardButton(text="📊 স্ট্যাটাস", callback_data="status"),
        ],
        # ── Row 2 : Setup ──
        [
            InlineKeyboardButton(text="🔗 চ্যানেল সেট করুন", callback_data="ask_channel"),
            InlineKeyboardButton(text="📡 লাইভ লিঙ্ক সেট করুন", callback_data="ask_live"),
        ],
        # ── Row 3 : Admin Mode ──
        [
            InlineKeyboardButton(text="👑 অ্যাডমিন 🟢 ON",  callback_data="admin_on"),
            InlineKeyboardButton(text="🚫 অ্যাডমিন 🔴 OFF", callback_data="admin_off"),
        ],
        # ── Row 4 : Primary Control ──
        [
            InlineKeyboardButton(
                text="🟢 ▶️  START BOT" if not running else "🔄 চলমান...",
                callback_data="run"
            ),
            InlineKeyboardButton(text="🔴 ⏹️  STOP BOT", callback_data="stop"),
        ],
        # ── Row 5 : Footer ──
        [
            InlineKeyboardButton(text="📖 সাহায্য", callback_data="help"),
            InlineKeyboardButton(text="🏠 মেনু",    callback_data="menu"),
        ],
    ])

def kb_back():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 মেনু-তে ফিরুন", callback_data="menu")]
    ])

def kb_refresh():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 রিফ্রেশ করুন",   callback_data="status")],
        [InlineKeyboardButton(text="🏠 মেনু-তে ফিরুন", callback_data="menu")],
    ])

def is_me(uid): return uid == ADMIN_ID


# ══════════════════════════════════════════════
#  📊 STATUS PANEL  — Premium Visual Style
# ══════════════════════════════════════════════

def status_text():
    logged  = state["logged_in"]
    running = state["running"]
    in_live = state["in_live"]
    is_adm  = state["is_admin"]
    channel = state.get("channel_link") or "সেট করা হয়নি"
    live    = state.get("live_link")    or "সেট করা হয়নি"
    total   = state.get("unmute_count", 0)

    # ── Live status bar ──
    if running and in_live:
        bar = "🟢🟢🟢  <b>FULLY ACTIVE</b>"
    elif running:
        bar = "🟡🟡⚪  <b>চলছে — লাইভ খোঁজছে</b>"
    else:
        bar = "🔴⚪⚪  <b>বন্ধ</b>"

    return (
        f"{box('BOT STATUS PANEL', '📊')}\n\n"
        f"{bar}\n\n"
        f"{line()}\n"
        f"{step_row('🔐', 'লগিন', tag_ok('সক্রিয়') if logged else tag_err('করা হয়নি'))}\n"
        f"{step_row('⚡', 'চলমান', '🟢 হ্যাঁ' if running else '🔴 না')}\n"
        f"{step_row('🎙️', 'লাইভ-এ', '🔵 হ্যাঁ' if in_live else '⚪ না')}\n"
        f"{step_row('👑', 'অ্যাডমিন', tag_ok('চালু') if is_adm else '🚫 বন্ধ')}\n"
        f"{line()}\n"
        f"{step_row('🔗', 'চ্যানেল', f'<code>{channel}</code>')}\n"
        f"{step_row('📡', 'লাইভ', f'<code>{live}</code>')}\n"
        f"{line()}\n"
        f"🔊 মোট আনমিউট  »  <b>{total} জন</b>\n"
    )


# ══════════════════════════════════════════════
#  🌟 STATIC TEXT TEMPLATES
# ══════════════════════════════════════════════

WELCOME_TEXT = (
    f"🌟 <b>Live Auto-Unmute Bot</b> 🌟\n"
    f"<i>Premium Edition v{VERSION}</i>\n\n"
    f"{box('কী করে এই বট?', '🎯')}\n\n"
    f"🔸 লাইভ চালু হলে <b>অটো জয়েন</b> করবে\n"
    f"🔸 মিউটেড মেম্বার <b>অটো আনমিউট</b> করবে\n"
    f"🔸 লাইভ বন্ধ হলে <b>অটো লিভ</b> করবে\n"
    f"🔸 <b>২৪/৭</b> একটানা চলবে\n\n"
    f"{line()}\n"
    f"👇 <b>নিচের বাটন দিয়ে নিয়ন্ত্রণ করুন</b>"
)

HELP_TEXT = (
    f"📖 <b>ব্যবহার নির্দেশিকা</b>\n\n"
    f"{line()}\n"
    f"<b>ধাপ ১ ›</b> 🔐 <b>লগিন করুন</b>\n"
    f"  └ ফোন নম্বর ও কোড দিয়ে লগিন\n\n"
    f"<b>ধাপ ২ ›</b> 🔗 <b>চ্যানেল সেট করুন</b>\n"
    f"  └ আপনার চ্যানেল লিঙ্ক দিন\n\n"
    f"<b>ধাপ ৩ ›</b> 📡 <b>লাইভ লিঙ্ক সেট করুন</b>\n"
    f"  └ লাইভ লিঙ্ক বা চ্যানেল লিঙ্ক দিন\n\n"
    f"<b>ধাপ ৪ ›</b> 🟢 <b>START BOT চাপুন</b>\n"
    f"  └ বট স্বয়ংক্রিয়ভাবে কাজ শুরু করবে\n\n"
    f"{line()}\n"
    f"💡 <b>টিপস:</b>\n"
    f"• 👑 Admin ON → মিউটেড আনমিউট হবে\n"
    f"• 🚫 Admin OFF → শুধু জয়েন করবে\n"
    f"• 🔄 লাইভ বন্ধ হলে নিজেই লিভ করবে"
)


# ══════════════════════════════════════════════
#  🔧 TELETHON HELPERS  (logic unchanged)
# ══════════════════════════════════════════════

def make_sdp():
    s  = random.randint(100000000, 4294967295)
    s2 = random.randint(100000000, 4294967295)
    fp = ':'.join(f'{random.randint(0,255):02X}' for _ in range(32))
    pw = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=22))
    uf = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
    cn = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=16))
    ms = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=36))
    return json.dumps({
        "fingerprints": [{"hash": "sha-256", "setup": "actpass", "fingerprint": fp}],
        "pwd": pw, "ufrag": uf, "ssrc": s,
        "ssrc-groups": [{"semantics": "FID", "sources": [s, s2]}],
        "sources": {str(s): {"cname": cn, "msid": f"{ms} {ms}a0"}},
    })


async def get_active_call(client, entity):
    try:
        full = await client(functions.channels.GetFullChannelRequest(entity))
        c = full.full_chat.call
        if c:
            return InputGroupCall(id=c.id, access_hash=c.access_hash)
    except Exception:
        pass
    return None


async def do_join_live(client, call, entity):
    me      = await client.get_me()
    join_as = await client.get_input_entity(me)
    for _ in range(5):
        try:
            await client(JoinGroupCallRequest(
                call=call, join_as=join_as,
                muted=True, video_stopped=True,
                params=types.DataJSON(data=make_sdp()),
            ))
            return True
        except Exception as e:
            err = str(e).lower()
            if any(k in err for k in ("ssrc", "retry", "duplicate")):
                await asyncio.sleep(1); continue
            elif "already" in err:
                return True
            elif "flood" in err:
                w = int(''.join(filter(str.isdigit, str(e))) or "10")
                await asyncio.sleep(w + 1)
            else:
                return False
    return False


async def do_leave_live(client, call):
    try:
        await client(LeaveGroupCallRequest(call=call))
    except Exception:
        pass


async def resolve_peer(client, peer, users_map):
    try:
        if hasattr(peer, 'user_id'):
            uid = peer.user_id
            if uid in users_map:
                u = users_map[uid]
                return types.InputPeerUser(user_id=u.id, access_hash=u.access_hash)
            return await client.get_input_entity(uid)
        elif hasattr(peer, 'channel_id'):
            return await client.get_input_entity(types.PeerChannel(channel_id=peer.channel_id))
        elif hasattr(peer, 'chat_id'):
            return types.InputPeerChat(chat_id=peer.chat_id)
    except Exception:
        pass
    return None


async def unmute_new_members(client, call, done_set: set):
    offset = ""
    count  = 0
    while True:
        try:
            result = await client(GetGroupParticipantsRequest(
                call=call, ids=[], sources=[], offset=offset, limit=100,
            ))
        except Exception:
            break
        if not result.participants:
            break

        users_map = {u.id: u for u in getattr(result, 'users', [])}

        for p in result.participants:
            src      = getattr(p, 'source', None)
            is_muted = getattr(p, 'muted', False) or getattr(p, 'muted_by_you', False)

            if src in done_set:
                continue
            if not is_muted:
                done_set.add(src)
                continue

            ip = await resolve_peer(client, p.peer, users_map)
            if ip is None:
                continue

            try:
                await client(EditGroupCallParticipantRequest(
                    call=call, participant=ip, muted=False,
                ))
                done_set.add(src)
                count += 1
                state["unmute_count"] += 1
                await asyncio.sleep(UNMUTE_DELAY)
            except FloodWaitError as e:
                await asyncio.sleep(e.seconds + 2)
            except Exception:
                pass

        offset = getattr(result, 'next_offset', "")
        if not offset:
            break
    return count


# ══════════════════════════════════════════════
#  🔄 24/7 LIVE LOOP
# ══════════════════════════════════════════════

async def live_loop():
    client   = state["client"]
    entity   = state["channel_entity"]
    done_set = set()
    cur_id   = None

    await bot.send_message(ADMIN_ID,
        f"{box('BOT লুপ শুরু হয়েছে', '🚀')}\n\n"
        f"🟢 লাইভ চালু হলে → <b>জয়েন করবো</b>\n"
        f"⏳ লাইভ বন্ধ থাকলে → <b>অপেক্ষা করবো</b>\n"
        f"🛑 STOP চাপলে → <b>লিভ করবো</b>\n\n"
        f"<i>মনিটরিং চলছে... ⚡</i>",
        reply_markup=kb_back()
    )

    while state["running"]:
        try:
            call = await get_active_call(client, entity)

            # ── লাইভ নেই ──
            if call is None:
                if state["in_live"]:
                    if state["current_call"]:
                        await do_leave_live(client, state["current_call"])
                    state["in_live"]      = False
                    state["current_call"] = None
                    cur_id                = None
                    done_set.clear()
                    await bot.send_message(ADMIN_ID,
                        f"📴 <b>লাইভ বন্ধ হয়ে গেছে</b>\n\n"
                        f"└ অটো লিভ করা হয়েছে ✅\n"
                        f"└ নতুন লাইভের অপেক্ষায়... ⏳",
                        reply_markup=kb_back()
                    )
                await asyncio.sleep(RECHECK_WAIT)
                continue

            # ── নতুন লাইভ শুরু হয়েছে ──
            if call.id != cur_id:
                done_set.clear()
                cur_id                = call.id
                state["current_call"] = call

                await bot.send_message(ADMIN_ID,
                    f"🟢 <b>লাইভ পাওয়া গেছে!</b>\n\n"
                    f"└ জয়েন করছি... ⏳",
                    reply_markup=kb_back()
                )

                ok = await do_join_live(client, call, entity)
                if ok:
                    state["in_live"] = True
                    await bot.send_message(ADMIN_ID,
                        f"{box('লাইভ-এ যোগ হয়েছে!', '🎙️')}\n\n"
                        f"🔊 মিউটেড মেম্বার আনমিউট হবে\n"
                        f"🔵 লাইভ বন্ধ না হওয়া পর্যন্ত থাকবো\n"
                        f"⚡ সব কিছু চলছে...",
                        reply_markup=kb_back()
                    )
                else:
                    state["in_live"] = False
                    await bot.send_message(ADMIN_ID,
                        f"{tag_err('জয়েন করা সম্ভব হয়নি')}\n\n"
                        f"└ আবার চেষ্টা করছি...",
                        reply_markup=kb_back()
                    )
                    await asyncio.sleep(10)
                    continue

                await asyncio.sleep(2)

            # ── Admin mode: নতুন মিউটেড মেম্বার চেক ও আনমিউট ──
            if state["is_admin"] and state["in_live"]:
                new = await unmute_new_members(client, call, done_set)
                if new > 0:
                    total = state.get("unmute_count", 0)
                    await bot.send_message(ADMIN_ID,
                        f"🔊 <b>{new} জন নতুন আনমিউট হয়েছে!</b>\n"
                        f"└ মোট: <b>{total}</b> জন 📊",
                        reply_markup=kb_back()
                    )
                await asyncio.sleep(UNMUTE_DELAY)
            else:
                await asyncio.sleep(UNMUTE_DELAY)

        except asyncio.CancelledError:
            break
        except FloodWaitError as e:
            await bot.send_message(ADMIN_ID,
                f"⏳ <b>Flood Wait</b>: {e.seconds} সেকেন্ড অপেক্ষা...",
                reply_markup=kb_back()
            )
            await asyncio.sleep(e.seconds + 5)
        except Exception as e:
            await bot.send_message(ADMIN_ID,
                f"{tag_warn('লুপ এরর')}\n\n"
                f"<code>{e}</code>\n\n"
                f"<i>১০ সেকেন্ড পর আবার চেষ্টা...</i>",
                reply_markup=kb_back()
            )
            await asyncio.sleep(10)

    # ── লুপ শেষ (STOP বাটন থেকে) ──
    total = state.get("unmute_count", 0)
    if state["in_live"] and state["current_call"]:
        await do_leave_live(client, state["current_call"])
        state["in_live"]      = False
        state["current_call"] = None
        await bot.send_message(ADMIN_ID,
            f"{box('বট বন্ধ হয়েছে', '👋')}\n\n"
            f"└ লাইভ থেকে লিভ করা হয়েছে ✅\n"
            f"└ মোট আনমিউট: <b>{total}</b> জন 🔊\n"
            f"└ বট সম্পূর্ণ বন্ধ 🔴",
            reply_markup=kb_main()
        )
    else:
        await bot.send_message(ADMIN_ID,
            f"🛑 <b>বট বন্ধ হয়েছে</b>\n\n"
            f"└ মোট আনমিউট: <b>{total}</b> জন 🔊\n\n"
            f"<i>আবার শুরু করতে ▶️ START চাপুন</i>",
            reply_markup=kb_main()
        )


# ══════════════════════════════════════════════
#  /start COMMAND
# ══════════════════════════════════════════════

@dp.message(Command("start"))
async def cmd_start(msg: Message):
    if not is_me(msg.from_user.id): return
    await msg.answer(WELCOME_TEXT, reply_markup=kb_main())


# ══════════════════════════════════════════════
#  📲 CALLBACKS
# ══════════════════════════════════════════════

@dp.callback_query(F.data == "menu")
async def cb_menu(cq: CallbackQuery):
    if not is_me(cq.from_user.id): return
    await cq.message.edit_text(WELCOME_TEXT, reply_markup=kb_main())
    await cq.answer()

@dp.callback_query(F.data == "help")
async def cb_help(cq: CallbackQuery):
    if not is_me(cq.from_user.id): return
    await cq.message.edit_text(HELP_TEXT, reply_markup=kb_back())
    await cq.answer("📖 নির্দেশিকা")

@dp.callback_query(F.data == "status")
async def cb_status(cq: CallbackQuery):
    if not is_me(cq.from_user.id): return
    await cq.message.edit_text(status_text(), reply_markup=kb_refresh())
    await cq.answer("🔄 আপডেট হয়েছে!")

@dp.callback_query(F.data == "login")
async def cb_login(cq: CallbackQuery):
    if not is_me(cq.from_user.id): return
    if state["logged_in"]:
        await cq.answer("✅ আপনি ইতিমধ্যে লগিন করা আছেন!", show_alert=True); return

    if state["client"] is None:
        client = TelegramClient("bot_user_session", API_ID, API_HASH)
        await client.connect()
        state["client"] = client

    client = state["client"]
    if await client.is_user_authorized():
        state["logged_in"] = True
        me = await client.get_me()
        await cq.message.edit_text(
            f"{tag_ok('আপনি ইতিমধ্যে লগিন করা আছেন!')}\n\n"
            f"👤 নাম:    <b>{me.first_name}</b>\n"
            f"📱 ইউজার: @{getattr(me, 'username', 'N/A')}",
            reply_markup=kb_main()
        )
        await cq.answer(); return

    state["step"] = "phone"
    await cq.message.edit_text(
        f"🔐 <b>লগিন প্রক্রিয়া</b>\n"
        f"{line()}\n\n"
        f"📱 আপনার <b>ফোন নম্বর</b> পাঠান\n\n"
        f"<i>ফরম্যাট:</i>  <code>+8801XXXXXXXXX</code>\n\n"
        f"💡 <i>আন্তর্জাতিক ফরম্যাটে (+দিয়ে) দিন</i>",
        reply_markup=kb_back()
    )
    await cq.answer()

@dp.callback_query(F.data == "ask_channel")
async def cb_ask_channel(cq: CallbackQuery):
    if not is_me(cq.from_user.id): return
    if not state["logged_in"]:
        await cq.answer("❌ আগে লগিন করুন!", show_alert=True); return
    state["step"] = "channel"
    await cq.message.edit_text(
        f"🔗 <b>চ্যানেল সেট করুন</b>\n"
        f"{line()}\n\n"
        f"আপনার চ্যানেলের <b>লিঙ্ক</b> পাঠান:\n\n"
        f"<i>উদাহরণ:</i>\n"
        f"<code>https://t.me/yourchannel</code>\n"
        f"<code>@yourchannel</code>",
        reply_markup=kb_back()
    )
    await cq.answer()

@dp.callback_query(F.data == "ask_live")
async def cb_ask_live(cq: CallbackQuery):
    if not is_me(cq.from_user.id): return
    if not state["logged_in"]:
        await cq.answer("❌ আগে লগিন করুন!", show_alert=True); return
    state["step"] = "live"
    await cq.message.edit_text(
        f"📡 <b>লাইভ লিঙ্ক সেট করুন</b>\n"
        f"{line()}\n\n"
        f"লাইভ স্ট্রিমের <b>লিঙ্ক</b> পাঠান:\n\n"
        f"<i>উদাহরণ:</i>\n"
        f"<code>https://t.me/channel?livestream=xxx</code>\n\n"
        f"💡 <i>একই চ্যানেল হলে চ্যানেল লিঙ্কও চলবে</i>",
        reply_markup=kb_back()
    )
    await cq.answer()

@dp.callback_query(F.data == "admin_on")
async def cb_admin_on(cq: CallbackQuery):
    if not is_me(cq.from_user.id): return
    state["is_admin"] = True
    await cq.answer("👑 অ্যাডমিন মোড চালু!", show_alert=True)
    await cq.message.edit_text(
        f"👑 <b>অ্যাডমিন মোড চালু হয়েছে</b>\n\n"
        f"└ 🔊 মিউটেড মেম্বার স্বয়ংক্রিয় আনমিউট হবে",
        reply_markup=kb_refresh()
    )

@dp.callback_query(F.data == "admin_off")
async def cb_admin_off(cq: CallbackQuery):
    if not is_me(cq.from_user.id): return
    state["is_admin"] = False
    await cq.answer("🚫 অ্যাডমিন মোড বন্ধ!", show_alert=True)
    await cq.message.edit_text(
        f"🚫 <b>অ্যাডমিন মোড বন্ধ হয়েছে</b>\n\n"
        f"└ 👤 শুধু লাইভ-এ জয়েন করবে",
        reply_markup=kb_refresh()
    )

@dp.callback_query(F.data == "run")
async def cb_run(cq: CallbackQuery):
    if not is_me(cq.from_user.id): return
    if not state["logged_in"]:
        await cq.answer("❌ আগে লগিন করুন!", show_alert=True); return
    if state["channel_entity"] is None:
        await cq.answer("❌ আগে চ্যানেল সেট করুন!", show_alert=True); return
    if state["running"]:
        await cq.answer("⚠️ ইতিমধ্যে চলছে!", show_alert=True); return

    state["running"]     = True
    state["unmute_count"] = 0
    state["task"]        = asyncio.create_task(live_loop())
    await cq.message.edit_text(
        f"{box('BOT শুরু হয়েছে!', '🚀')}\n\n"
        f"✅ লাইভ চালু হলে → জয়েন করবো\n"
        f"✅ মিউটেড মেম্বার → আনমিউট করবো\n"
        f"✅ লাইভ বন্ধ হলে → লিভ করবো\n"
        f"✅ STOP দিলে → সব বন্ধ হবে\n\n"
        f"<i>বট এখন সক্রিয় ⚡</i>",
        reply_markup=kb_back()
    )
    await cq.answer("🚀 শুরু!")

@dp.callback_query(F.data == "stop")
async def cb_stop(cq: CallbackQuery):
    if not is_me(cq.from_user.id): return
    if not state["running"]:
        await cq.answer("⚠️ ইতিমধ্যে বন্ধ আছে!", show_alert=True); return

    state["running"] = False
    if state["task"]:
        state["task"].cancel()
        state["task"] = None

    client = state["client"]
    total  = state.get("unmute_count", 0)
    if state["in_live"] and state["current_call"] and client:
        await do_leave_live(client, state["current_call"])
        state["in_live"]      = False
        state["current_call"] = None
        await cq.message.edit_text(
            f"{box('BOT বন্ধ হয়েছে', '🛑')}\n\n"
            f"└ লাইভ থেকে লিভ করা হয়েছে ✅\n"
            f"└ মোট আনমিউট: <b>{total}</b> জন 🔊\n\n"
            f"<i>আবার শুরু করতে ▶️ START চাপুন</i>",
            reply_markup=kb_main()
        )
    else:
        await cq.message.edit_text(
            f"🛑 <b>BOT বন্ধ হয়েছে</b>\n\n"
            f"└ মোট আনমিউট: <b>{total}</b> জন 🔊\n\n"
            f"<i>আবার শুরু করতে ▶️ START চাপুন</i>",
            reply_markup=kb_main()
        )
    await cq.answer("⏹ বন্ধ!")


# ══════════════════════════════════════════════
#  ✍️ TEXT INPUT HANDLER
# ══════════════════════════════════════════════

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_text(msg: Message):
    if not is_me(msg.from_user.id): return
    step   = state.get("step")
    client = state["client"]

    if step == "phone":
        phone = msg.text.strip()
        try:
            result              = await client.send_code_request(phone)
            state["phone"]      = phone
            state["phone_hash"] = result.phone_code_hash
            state["step"]       = "code"
            await msg.answer(
                f"🔢 <b>ভেরিফিকেশন কোড</b>\n"
                f"{line()}\n\n"
                f"📱 আপনার ফোনে একটি কোড পাঠানো হয়েছে\n\n"
                f"⬇️ <b>কোডটি এখানে পাঠান:</b>",
                reply_markup=kb_back()
            )
        except FloodWaitError as e:
            state["step"] = None
            await msg.answer(
                f"⏳ <b>অনেক চেষ্টা করা হয়েছে</b>\n\n"
                f"└ {e.seconds} সেকেন্ড পর আবার চেষ্টা করুন",
                reply_markup=kb_main()
            )
        except Exception as e:
            state["step"] = None
            await msg.answer(
                f"{tag_err('এরর হয়েছে:')}\n<code>{e}</code>",
                reply_markup=kb_main()
            )

    elif step == "code":
        try:
            await client.sign_in(state["phone"], msg.text.strip(), phone_code_hash=state["phone_hash"])
            me = await client.get_me()
            state["logged_in"] = True
            state["step"]      = None
            await msg.answer(
                f"🎉 <b>লগিন সফল হয়েছে!</b>\n"
                f"{line()}\n\n"
                f"👤 নাম:    <b>{me.first_name}</b>\n"
                f"📱 ইউজার: @{getattr(me, 'username', 'N/A')}\n\n"
                f"<i>এখন 🔗 চ্যানেল সেট করুন 👇</i>",
                reply_markup=kb_main()
            )
        except SessionPasswordNeededError:
            state["step"] = "2fa"
            await msg.answer(
                f"🔐 <b>দুই-স্তর যাচাই (2FA)</b>\n"
                f"{line()}\n\n"
                f"আপনার <b>2FA পাসওয়ার্ড</b> পাঠান:",
                reply_markup=kb_back()
            )
        except PhoneCodeInvalidError:
            state["step"] = None
            await msg.answer(
                f"{tag_err('ভুল কোড দেওয়া হয়েছে!')}\n\n"
                f"<i>আবার লগিন বাটন চাপুন</i>",
                reply_markup=kb_main()
            )
        except Exception as e:
            state["step"] = None
            await msg.answer(
                f"{tag_err('এরর:')}\n<code>{e}</code>",
                reply_markup=kb_main()
            )

    elif step == "2fa":
        try:
            await client.sign_in(password=msg.text.strip())
            me = await client.get_me()
            state["logged_in"] = True
            state["step"]      = None
            await msg.answer(
                f"🎉 <b>লগিন সফল হয়েছে!</b>\n"
                f"{line()}\n\n"
                f"👤 নাম:    <b>{me.first_name}</b>\n"
                f"📱 ইউজার: @{getattr(me, 'username', 'N/A')}\n\n"
                f"<i>এখন 🔗 চ্যানেল সেট করুন 👇</i>",
                reply_markup=kb_main()
            )
        except PasswordHashInvalidError:
            state["step"] = None
            await msg.answer(
                f"{tag_err('ভুল 2FA পাসওয়ার্ড!')}\n\n"
                f"<i>আবার লগিন বাটন চাপুন</i>",
                reply_markup=kb_main()
            )
        except Exception as e:
            state["step"] = None
            await msg.answer(
                f"{tag_err('এরর:')}\n<code>{e}</code>",
                reply_markup=kb_main()
            )

    elif step == "channel":
        link = msg.text.strip()
        try:
            try: await client(JoinChannelRequest(link))
            except Exception: pass
            entity = await client.get_entity(link)
            state["channel_entity"] = entity
            state["channel_link"]   = link
            state["step"]           = None
            title = getattr(entity, 'title', link)
            await msg.answer(
                f"✅ <b>চ্যানেল সেট হয়েছে!</b>\n"
                f"{line()}\n\n"
                f"📢 চ্যানেল: <b>{title}</b>\n\n"
                f"<i>এখন 📡 লাইভ লিঙ্ক সেট করুন 👇</i>",
                reply_markup=kb_main()
            )
        except Exception as e:
            state["step"] = None
            await msg.answer(
                f"{tag_err('এরর:')}\n<code>{e}</code>",
                reply_markup=kb_main()
            )

    elif step == "live":
        link = msg.text.strip()
        try:
            try: await client(JoinChannelRequest(link))
            except Exception: pass
            entity = await client.get_entity(link)
            state["channel_entity"] = entity
            state["live_link"]      = link
            state["step"]           = None
            title = getattr(entity, 'title', link)
            await msg.answer(
                f"✅ <b>লাইভ লিঙ্ক সেট হয়েছে!</b>\n"
                f"{line()}\n\n"
                f"📡 লাইভ: <b>{title}</b>\n\n"
                f"<i>এখন 🟢 START BOT চাপুন 👇</i>",
                reply_markup=kb_main()
            )
        except Exception:
            state["live_link"] = link
            state["step"]      = None
            await msg.answer(
                f"✅ <b>লাইভ লিঙ্ক সেট হয়েছে!</b>\n"
                f"{line()}\n\n"
                f"📡 লিঙ্ক: <code>{link}</code>\n"
                f"<i>(চ্যানেল entity ব্যবহার করা হবে)</i>\n\n"
                f"<i>এখন 🟢 START BOT চাপুন 👇</i>",
                reply_markup=kb_main()
            )


# ══════════════════════════════════════════════
#  🚀 MAIN
# ══════════════════════════════════════════════

async def main():
    if not BOT_TOKEN or API_ID == 0 or not API_HASH:
        print("❗ BOT_TOKEN, API_ID, API_HASH সেট করুন!")
        return
    print(f"🤖 Live Auto-Unmute Bot {VERSION} শুরু হচ্ছে...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
