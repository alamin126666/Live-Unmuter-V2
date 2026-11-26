#!/usr/bin/env python3
# ================================================================
#   Telegram Live Auto-Unmute BOT
#   Premium Edition v3.0
#   ─────────────────────────────────��───────
#   লাইভ চালু → অটো জয়েন
#   মিউটেড মেম্বার → অটো আনমিউট
#   লাইভ বন্ধ → অটো লিভ
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
VERSION      = "3.0 Premium"
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
#  PREMIUM UI HELPER FUNCTIONS
# ══════════════════════════════════════════════

def line(char="─", n=28): 
    return f"<code>{char * n}</code>"

def premium_line():
    return "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

def gradient_line():
    return "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰"

def card_header(title, icon=""):
    """Modern card header design"""
    icon_part = f"{icon} " if icon else ""
    return f"┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n┃ {icon_part}<b>{title}</b>\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"

def tag_success(txt):   
    return f"<b>✓ {txt}</b>"

def tag_error(txt):  
    return f"<b>✗ {txt}</b>"

def tag_warning(txt): 
    return f"<b>⚠ {txt}</b>"

def tag_info(txt): 
    return f"<b>• {txt}</b>"

def status_badge(active, on_text="চালু", off_text="বন্ধ"):
    if active:
        return f"<b>● {on_text}</b>"
    return f"<b>○ {off_text}</b>"

def premium_row(label, value, highlight=False):
    """Premium styled status row"""
    if highlight:
        return f"  <b>{label}</b> → <code>{value}</code>"
    return f"  {label} → {value}"


# ══════════════════════════════════════════════
#  PREMIUM KEYBOARDS WITH BUTTON COLORS
# ══════════════════════════════════════════════

def kb_main():
    """Main menu with colored buttons - Premium Edition"""
    logged  = state["logged_in"]
    running = state["running"]
    
    return InlineKeyboardMarkup(inline_keyboard=[
        # Row 1: Primary Authentication
        [
            InlineKeyboardButton(
                text="✓ লগিন সম্পন্ন" if logged else "লগিন করুন",
                callback_data="login"
            ),
        ],
        # Row 2: Setup Controls
        [
            InlineKeyboardButton(
                text="চ্যানেল সেটআপ", 
                callback_data="ask_channel"
            ),
            InlineKeyboardButton(
                text="লাইভ লিঙ্ক", 
                callback_data="ask_live"
            ),
        ],
        # Row 3: Admin Toggle
        [
            InlineKeyboardButton(
                text="অ্যাডমিন মোড চালু", 
                callback_data="admin_on"
            ),
            InlineKeyboardButton(
                text="অ্যাডমিন মোড বন্ধ", 
                callback_data="admin_off"
            ),
        ],
        # Row 4: Bot Control
        [
            InlineKeyboardButton(
                text="START BOT" if not running else "চলমান...",
                callback_data="run"
            ),
            InlineKeyboardButton(
                text="STOP BOT", 
                callback_data="stop"
            ),
        ],
        # Row 5: Status & Info
        [
            InlineKeyboardButton(
                text="স্ট্যাটাস প্যানেল", 
                callback_data="status"
            ),
            InlineKeyboardButton(
                text="সাহায্য গাইড", 
                callback_data="help"
            ),
        ],
        # Row 6: Refresh
        [
            InlineKeyboardButton(
                text="রিফ্রেশ করুন", 
                callback_data="menu"
            ),
        ],
    ])

def kb_back():
    """Simple back button"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="← মেইন মেনু", 
            callback_data="menu"
        )]
    ])

def kb_refresh():
    """Refresh controls"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="রিফ্রেশ", 
                callback_data="status"
            ),
            InlineKeyboardButton(
                text="ড্যাশবোর্ড", 
                callback_data="menu"
            ),
        ],
        [
            InlineKeyboardButton(
                text="← মেইন মেনু", 
                callback_data="menu"
            )
        ],
    ])

def kb_quick_actions():
    """Quick action panel"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="কুইক স্টার্ট", callback_data="run"),
            InlineKeyboardButton(text="জরুরি স্টপ", callback_data="stop"),
        ],
        [
            InlineKeyboardButton(text="স্ট্যাটাস চেক", callback_data="status"),
        ],
        [
            InlineKeyboardButton(text="← মেইন মেনু", callback_data="menu"),
        ],
    ])

def is_me(uid): 
    return uid == ADMIN_ID


# ══════════════════════════════════════════════
#  PREMIUM STATUS PANEL
# ══════════════════════════════════════════════

def status_text():
    """Ultra premium status display"""
    logged  = state["logged_in"]
    running = state["running"]
    in_live = state["in_live"]
    is_adm  = state["is_admin"]
    channel = state.get("channel_link") or "সেট করা হয়নি"
    live    = state.get("live_link")    or "সেট করা হয়নি"
    total   = state.get("unmute_count", 0)

    # Dynamic Status Indicator
    if running and in_live:
        status_bar = "●●●●●  <b>FULLY OPERATIONAL</b>  ●●●●●"
        status_desc = "সব সিস্টেম সচল - লাইভে আছেন"
    elif running:
        status_bar = "●●●○○  <b>SEARCHING FOR LIVE</b>  ○○●●●"
        status_desc = "লাইভ খোঁজা হচ্ছে..."
    else:
        status_bar = "●●○○○  <b>SYSTEM OFFLINE</b>  ○○○●●"
        status_desc = "বট বন্ধ আছে"

    # Build Premium Status Panel
    output = f"{card_header('বট স্ট্যাটাস প্যানেল')}\n\n"
    output += f"{status_bar}\n"
    output += f"<i>{status_desc}</i>\n\n"
    output += f"{gradient_line()}\n\n"
    
    # Authentication Status
    output += f"<b>অথেন্টিকেশন স্ট্যাটাস</b>\n"
    output += f"{premium_row('লগিন', tag_success('সফল') if logged else tag_error('প্রয়োজন'), True)}\n\n"
    
    # System Status
    output += f"<b>সিস্টেম স্ট্যাটাস</b>\n"
    output += f"{premium_row('বট চলমান', status_badge(running, 'হ্যাঁ', 'না'))}\n"
    output += f"{premium_row('লাইভে আছে', status_badge(in_live, 'হ্যাঁ', 'না'))}\n"
    output += f"{premium_row('অ্যাডমিন মোড', status_badge(is_adm, 'চালু', 'বন্ধ'))}\n\n"
    
    output += f"{premium_line()}\n\n"
    
    # Configuration
    output += f"<b>কনফিগারেশন</b>\n"
    output += f"{premium_row('চ্যানেল', channel, True)}\n"
    output += f"{premium_row('লাইভ লিঙ্ক', live, True)}\n\n"
    
    output += f"{premium_line()}\n\n"
    
    # Statistics
    output += f"<b>পারফরম্যান্স</b>\n"
    output += f"  মোট আনমিউট » <b><code>{total}</code> জন</b>\n"
    output += f"  ভার্সন » <code>{VERSION}</code>\n\n"
    
    output += f"{gradient_line()}\n"
    output += f"<i>রিফ্রেশ বাটন চাপুন লাইভ আপডেটের জন্য</i>"
    
    return output


# ══════════════════════════════════════════════
#  PREMIUM WELCOME & HELP SCREENS
# ══════════════════════════════════════════════

WELCOME_TEXT = f"""
╔═══════════════════════════════╗
║   <b>Live Auto-Unmute Bot</b>   ║
║   <i>Premium Edition {VERSION}</i>   ║
╚═══════════════════════════════╝

{gradient_line()}

<b>বটের ফিচারসমূহ:</b>

• <b>স্মার্ট অটো জয়েন</b>
  লাইভ চালু হলে অটোমেটিক জয়েন

• <b>ইন্সট্যান্ট আনমিউট</b>
  মিউটেড মেম্বারদের অটো আনমিউট

• <b>অটো লিভ সিস্টেম</b>
  লাইভ বন্ধ হলে অটো লিভ করবে

• <b>24/7 নন-স্টপ</b>
  সবসময় সক্রিয় থাকবে

• <b>প্রিমিয়াম UI/UX</b>
  আধুনিক ডিজাইন ও স্মুথ অভিজ্ঞতা

{premium_line()}

<b>নিচের বাটন দিয়ে শুরু করুন</b>
<i>সম্পূর্ণ প্রিমিয়াম অভিজ্ঞতা উপভোগ করুন</i>
"""

HELP_TEXT = f"""
{card_header('ব্যবহার নির্দেশিকা')}

{gradient_line()}

<b>কুইক স্টার্ট গাইড:</b>

<b>পর্ব ১ › লগিন করুন</b>
  ├ "লগিন করুন" বাটন চাপুন
  ├ ফোন নম্বর পাঠান
  ├ OTP কোড পাঠান
  └ লগিন সম্পন্ন

<b>পর্ব ২ › চ্যানেল সেটআপ</b>
  ├ "চ্যানেল সেটআপ" চাপুন
  ├ আপনার চ্যানেল লিঙ্ক পাঠান
  └ চ্যানেল সেভ হয়েছে

<b>পর্ব ৩ › লাইভ লিঙ্ক</b>
  ├ "লাইভ লিঙ্ক" বাটন চাপুন
  ├ লাইভ লিঙ্ক পাঠান
  └ লিঙ্ক সেভ হয়েছে

<b>পর্ব ৪ › START BOT</b>
  ├ "START BOT" চাপুন
  └ বট চালু হয়ে গেছে

{premium_line()}

<b>প্রো টিপস:</b>

• <b>অ্যাডমিন মোড চালু</b> → মিউটেড আনমিউট হবে
• <b>অ্যাডমিন মোড বন্ধ</b> → শুধু জয়েন করবে
• <b>স্ট্যাটাস প্যানেল</b> → সব তথ্য দেখুন
• <b>রিফ্রেশ</b> → লাইভ আপডেট পান

{gradient_line()}

<b>অ্যাডভান্সড ফিচার:</b>

▪ স্মার্ট লাইভ ডিটেকশন
▪ অটোমেটিক রি-কানেক্ট
▪ ফ্লাড প্রটেকশন
▪ স্মুথ বোর্ড হ্যান্ডলিং
▪ প্রিমিয়াম অ্যানিমেশন

<i>উপভোগ করুন প্রিমিয়াম অভিজ্ঞতা</i>
"""


# ══════════════════════════════════════════════
#  TELETHON HELPERS (Smooth & Optimized)
# ══════════════════════════════════════════════

def make_sdp():
    """Generate SDP for voice call"""
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
    """Get active group call with smooth handling"""
    try:
        full = await client(functions.channels.GetFullChannelRequest(entity))
        c = full.full_chat.call
        if c:
            return InputGroupCall(id=c.id, access_hash=c.access_hash)
    except Exception as e:
        logging.debug(f"No active call: {e}")
    return None


async def do_join_live(client, call, entity):
    """Join live call with retry logic and smooth error handling"""
    me      = await client.get_me()
    join_as = await client.get_input_entity(me)
    
    for attempt in range(5):
        try:
            await client(JoinGroupCallRequest(
                call=call, join_as=join_as,
                muted=True, video_stopped=True,
                params=types.DataJSON(data=make_sdp()),
            ))
            return True
            
        except Exception as e:
            err = str(e).lower()
            
            # Handle SSRC conflicts
            if any(k in err for k in ("ssrc", "retry", "duplicate")):
                await asyncio.sleep(1 + attempt * 0.5)
                continue
                
            # Already joined
            elif "already" in err:
                return True
                
            # Flood wait handling
            elif "flood" in err:
                wait_time = int(''.join(filter(str.isdigit, str(e))) or "10")
                logging.info(f"Flood wait: {wait_time}s")
                await asyncio.sleep(wait_time + 2)
                continue
                
            else:
                logging.error(f"Join error: {e}")
                return False
                
    return False


async def do_leave_live(client, call):
    """Leave live call smoothly"""
    try:
        await client(LeaveGroupCallRequest(call=call))
        logging.info("Left live call")
    except Exception as e:
        logging.debug(f"Leave error: {e}")


async def resolve_peer(client, peer, users_map):
    """Resolve peer entity with caching"""
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
            
    except Exception as e:
        logging.debug(f"Peer resolve error: {e}")
        
    return None


async def unmute_new_members(client, call, done_set: set):
    """Unmute muted participants with smooth processing"""
    offset = ""
    count  = 0
    
    while True:
        try:
            result = await client(GetGroupParticipantsRequest(
                call=call, ids=[], sources=[], offset=offset, limit=100,
            ))
        except Exception as e:
            logging.error(f"Failed to get participants: {e}")
            break
            
        if not result.participants:
            break

        users_map = {u.id: u for u in getattr(result, 'users', [])}

        for p in result.participants:
            src      = getattr(p, 'source', None)
            is_muted = getattr(p, 'muted', False) or getattr(p, 'muted_by_you', False)

            # Skip if already processed
            if src in done_set:
                continue
                
            # Skip if not muted
            if not is_muted:
                done_set.add(src)
                continue

            # Resolve peer
            ip = await resolve_peer(client, p.peer, users_map)
            if ip is None:
                continue

            # Unmute participant
            try:
                await client(EditGroupCallParticipantRequest(
                    call=call, participant=ip, muted=False,
                ))
                done_set.add(src)
                count += 1
                state["unmute_count"] = state.get("unmute_count", 0) + 1
                logging.info(f"Unmuted participant #{count}")
                await asyncio.sleep(UNMUTE_DELAY)
                
            except Exception as e:
                err_str = str(e).lower()
                if "flood" in err_str:
                    wait_time = int(''.join(filter(str.isdigit, str(e))) or "10")
                    logging.warning(f"Flood wait: {wait_time}s")
                    await asyncio.sleep(wait_time + 2)
                else:
                    logging.debug(f"Unmute error: {e}")

        offset = result.next_offset
        if not offset:
            break

    return count


# ══════════════════════════════════════════════
#  MAIN BOT LOOP - Smooth & Optimized
# ══════════════════════════════════════════════

async def bot_loop():
    """Main bot loop with smooth state handling"""
    client = state["client"]
    entity = state["channel_entity"]
    done_set = set()
    
    while state["running"]:
        try:
            # Check for active call
            call = await get_active_call(client, entity)
            
            if call is None:
                # No active live
                if state["in_live"]:
                    state["in_live"] = False
                    state["current_call"] = None
                    done_set.clear()
                    logging.info("Live ended - waiting for next...")
                    
                await asyncio.sleep(RECHECK_WAIT)
                continue

            # Live is active
            if not state["in_live"]:
                # Try to join
                joined = await do_join_live(client, call, entity)
                if joined:
                    state["in_live"] = True
                    state["current_call"] = call
                    done_set.clear()
                    logging.info("Joined live successfully!")
                    
                    # Notify admin
                    try:
                        await bot.send_message(
                            ADMIN_ID,
                            f"<b>● লাইভে জয়েন সফল</b>\n\n"
                            f"বট এখন লাইভে আছে\n"
                            f"আনমিউট প্রসেস চলছে..."
                        )
                    except:
                        pass
                else:
                    logging.warning("Failed to join live, retrying...")
                    await asyncio.sleep(5)
                    continue

            # Unmute members if admin mode is on
            if state["is_admin"]:
                unmuted = await unmute_new_members(client, call, done_set)
                if unmuted > 0:
                    logging.info(f"Unmuted {unmuted} members in this cycle")

            # Wait before next check
            await asyncio.sleep(RECHECK_WAIT)

        except asyncio.CancelledError:
            logging.info("Bot loop cancelled")
            break
            
        except Exception as e:
            logging.error(f"Loop error: {e}")
            await asyncio.sleep(10)

    # Cleanup on exit
    if state["in_live"] and state["current_call"]:
        try:
            await do_leave_live(client, state["current_call"])
            state["in_live"] = False
            logging.info("Left live before stopping")
        except:
            pass


# ══════════════════════════════════════════════
#  BOT COMMAND HANDLERS - Premium Edition
# ══════════════════════════════════════════════

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Start command with premium welcome screen"""
    if not is_me(message.from_user.id):
        await message.answer("<b>Unauthorized Access</b>")
        return
        
    await message.answer(
        WELCOME_TEXT,
        reply_markup=kb_main(),
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("menu"))
async def cmd_menu(message: Message):
    """Show main menu"""
    if not is_me(message.from_user.id):
        return
        
    await message.answer(
        f"{card_header('মেইন কন্ট্রোল প্যানেল')}\n\n"
        f"<b>বট নিয়ন্ত্রণ করতে নিচের বাটন ব্যবহার করুন</b>\n\n"
        f"{status_badge(state['running'], 'বট চালু আছে', 'বট বন্ধ আছে')}\n"
        f"{status_badge(state['logged_in'], 'লগিন করা আছে', 'লগিন করা নেই')}",
        reply_markup=kb_main()
    )


@dp.message(Command("status"))
async def cmd_status(message: Message):
    """Show status panel"""
    if not is_me(message.from_user.id):
        return
        
    await message.answer(
        status_text(),
        reply_markup=kb_refresh()
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Show help guide"""
    if not is_me(message.from_user.id):
        return
        
    await message.answer(
        HELP_TEXT,
        reply_markup=kb_back()
    )


# ══════════════════════════════════════════════
#  CALLBACK HANDLERS - Smooth Navigation
# ══════════════════════════════════════════════

@dp.callback_query(F.data == "menu")
async def cb_menu(callback: CallbackQuery):
    """Return to main menu with smooth transition"""
    if not is_me(callback.from_user.id):
        await callback.answer("Unauthorized", show_alert=True)
        return
        
    await callback.message.edit_text(
        f"{card_header('মেইন কন্ট্রোল প্যানেল')}\n\n"
        f"<b>বট নিয়ন্ত্রণ করতে নিচের বাটন ব্যবহার করুন</b>\n\n"
        f"{status_badge(state['running'], 'বট চালু আছে', 'বট বন্ধ আছে')}\n"
        f"{status_badge(state['logged_in'], 'লগিন করা আছে', 'লগিন করা নেই')}",
        reply_markup=kb_main()
    )
    await callback.answer("মেইন মেনু")


@dp.callback_query(F.data == "status")
async def cb_status(callback: CallbackQuery):
    """Show status panel"""
    if not is_me(callback.from_user.id):
        await callback.answer("Unauthorized", show_alert=True)
        return
        
    await callback.message.edit_text(
        status_text(),
        reply_markup=kb_refresh()
    )
    await callback.answer("স্ট্যাটাস আপডেট করা হয়েছে")


@dp.callback_query(F.data == "help")
async def cb_help(callback: CallbackQuery):
    """Show help screen"""
    if not is_me(callback.from_user.id):
        await callback.answer("Unauthorized", show_alert=True)
        return
        
    await callback.message.edit_text(
        HELP_TEXT,
        reply_markup=kb_back()
    )
    await callback.answer("সাহায্য গাইড")


@dp.callback_query(F.data == "login")
async def cb_login(callback: CallbackQuery):
    """Start login process"""
    if not is_me(callback.from_user.id):
        await callback.answer("Unauthorized", show_alert=True)
        return

    if state["logged_in"]:
        await callback.answer("আপনি ইতিমধ্যে লগিন করা আছেন", show_alert=True)
        return

    state["step"] = "await_phone"
    await callback.message.edit_text(
        f"{card_header('লগিন প্রসেস')}\n\n"
        f"<b>ধাপ ১/৩: ফোন নম্বর</b>\n\n"
        f"আপনার Telegram ফোন নম্বর পাঠান\n"
        f"<i>উদাহরণ: +8801XXXXXXXXX</i>\n\n"
        f"{premium_line()}\n"
        f"<i>আন্তর্জাতিক ফরম্যাটে (+88) সহ পাঠান</i>",
        reply_markup=kb_back()
    )
    await callback.answer("ফোন নম্বর পাঠান")


@dp.callback_query(F.data == "ask_channel")
async def cb_ask_channel(callback: CallbackQuery):
    """Ask for channel link"""
    if not is_me(callback.from_user.id):
        await callback.answer("Unauthorized", show_alert=True)
        return

    if not state["logged_in"]:
        await callback.answer("প্রথমে লগিন করুন", show_alert=True)
        return

    state["step"] = "await_channel"
    await callback.message.edit_text(
        f"{card_header('চ্যানেল সেটআপ')}\n\n"
        f"<b>আপনার চ্যানেল লিঙ্ক পাঠান</b>\n\n"
        f"উদাহরণ:\n"
        f"<code>https://t.me/your_channel</code>\n"
        f"অথবা\n"
        f"<code>@your_channel</code>\n\n"
        f"{premium_line()}\n"
        f"<i>যে চ্যানেলে লাইভ হয়, সেটির লিঙ্ক দিন</i>",
        reply_markup=kb_back()
    )
    await callback.answer("চ্যানেল লিঙ্ক পাঠান")


@dp.callback_query(F.data == "ask_live")
async def cb_ask_live(callback: CallbackQuery):
    """Ask for live link"""
    if not is_me(callback.from_user.id):
        await callback.answer("Unauthorized", show_alert=True)
        return

    if not state["logged_in"]:
        await callback.answer("প্রথমে লগিন করুন", show_alert=True)
        return

    state["step"] = "await_live"
    await callback.message.edit_text(
        f"{card_header('লাইভ লিঙ্ক সেটআপ')}\n\n"
        f"<b>লাইভ লিঙ্ক পাঠান</b>\n\n"
        f"উদাহরণ:\n"
        f"<code>https://t.me/channel_name</code>\n"
        f"অথবা\n"
        f"<code>@channel_name</code>\n\n"
        f"{premium_line()}\n"
        f"<i>চ্যানেল লিঙ্ক দিলেও কাজ করবে</i>",
        reply_markup=kb_back()
    )
    await callback.answer("লাইভ লিঙ্ক পাঠান")


@dp.callback_query(F.data == "admin_on")
async def cb_admin_on(callback: CallbackQuery):
    """Enable admin mode"""
    if not is_me(callback.from_user.id):
        await callback.answer("Unauthorized", show_alert=True)
        return

    state["is_admin"] = True
    await callback.answer("অ্যাডমিন মোড চালু হয়েছে", show_alert=True)
    
    await callback.message.edit_text(
        f"{card_header('অ্যাডমিন মোড')}\n\n"
        f"<b>● অ্যাডমিন মোড সফলভাবে চালু হয়েছে</b>\n\n"
        f"এখন মিউটেড মেম্বারদের আনমিউট করা হবে\n"
        f"স্বয়ংক্রিয় আনমিউট সিস্টেম সক্রিয়\n\n"
        f"{premium_line()}\n"
        f"<i>বন্ধ করতে \"অ্যাডমিন মোড বন্ধ\" চাপুন</i>",
        reply_markup=kb_main()
    )


@dp.callback_query(F.data == "admin_off")
async def cb_admin_off(callback: CallbackQuery):
    """Disable admin mode"""
    if not is_me(callback.from_user.id):
        await callback.answer("Unauthorized", show_alert=True)
        return

    state["is_admin"] = False
    await callback.answer("অ্যাডমিন মোড বন্ধ হয়েছে", show_alert=True)
    
    await callback.message.edit_text(
        f"{card_header('অ্যাডমিন মোড')}\n\n"
        f"<b>○ অ্যাডমিন মোড বন্ধ করা হয়েছে</b>\n\n"
        f"মিউটেড মেম্বার আনমিউট হবে না\n"
        f"শুধুমাত্র লাইভে জয়েন করবে\n\n"
        f"{premium_line()}\n"
        f"<i>চালু করতে \"অ্যাডমিন মোড চালু\" চাপুন</i>",
        reply_markup=kb_main()
    )


@dp.callback_query(F.data == "run")
async def cb_run(callback: CallbackQuery):
    """Start the bot"""
    if not is_me(callback.from_user.id):
        await callback.answer("Unauthorized", show_alert=True)
        return

    if not state["logged_in"]:
        await callback.answer("প্রথমে লগিন করুন", show_alert=True)
        return

    if not state["channel_entity"]:
        await callback.answer("প্রথমে চ্যানেল সেট করুন", show_alert=True)
        return

    if state["running"]:
        await callback.answer("বট ইতিমধ্যে চলছে", show_alert=True)
        return

    state["running"] = True
    state["task"] = asyncio.create_task(bot_loop())
    
    await callback.message.edit_text(
        f"{card_header('বট স্টার্ট')}\n\n"
        f"<b>● বট সফলভাবে চালু হয়েছে</b>\n\n"
        f"সিস্টেম স্ট্যাটাস: <b>ACTIVE</b>\n"
        f"লাইভ খোঁজা হচ্ছে...\n"
        f"স্বয়ংক্রিয় প্রসেস চলছে\n\n"
        f"{gradient_line()}\n\n"
        f"<i>স্ট্যাটাস দেখতে \"স্ট্যাটাস প্যানেল\" চাপুন</i>",
        reply_markup=kb_quick_actions()
    )
    await callback.answer("বট চালু হয়েছে")


@dp.callback_query(F.data == "stop")
async def cb_stop(callback: CallbackQuery):
    """Stop the bot"""
    if not is_me(callback.from_user.id):
        await callback.answer("Unauthorized", show_alert=True)
        return

    if not state["running"]:
        await callback.answer("বট ইতিমধ্যে বন্ধ আছে", show_alert=True)
        return

    state["running"] = False
    
    if state["task"]:
        state["task"].cancel()
        try:
            await state["task"]
        except asyncio.CancelledError:
            pass
        state["task"] = None

    await callback.message.edit_text(
        f"{card_header('বট স্টপ')}\n\n"
        f"<b>○ বট সফলভাবে বন্ধ হয়েছে</b>\n\n"
        f"সিস্টেম স্ট্যাটাস: <b>OFFLINE</b>\n"
        f"সব প্রসেস বন্ধ করা হয়েছে\n"
        f"ডেটা সেভ করা হয়েছে\n\n"
        f"{gradient_line()}\n\n"
        f"<i>পুনরায় চালু করতে \"START BOT\" চাপুন</i>",
        reply_markup=kb_main()
    )
    await callback.answer("বট বন্ধ হয়েছে")


# ══════════════════════════════════════════════
#  MESSAGE HANDLERS - Input Processing
# ══════════════════════════════════════════════

@dp.message()
async def handle_message(message: Message):
    """Handle user input based on current step"""
    if not is_me(message.from_user.id):
        return

    step = state.get("step")
    if not step:
        return

    # Phone Number Input
    if step == "await_phone":
        phone = message.text.strip()
        state["phone"] = phone
        state["step"] = None

        if state["client"] is None:
            state["client"] = TelegramClient("bot_session", API_ID, API_HASH)
            await state["client"].connect()

        try:
            result = await state["client"].send_code_request(phone)
            state["phone_hash"] = result.phone_code_hash
            state["step"] = "await_code"
            
            await message.answer(
                f"{card_header('লগিন প্রসেস')}\n\n"
                f"<b>ধাপ ২/৩: OTP কোড</b>\n\n"
                f"আপনার Telegram-এ কোড পাঠানো হয়েছে\n"
                f"কোডটি এখানে পাঠান\n\n"
                f"{premium_line()}\n"
                f"<i>৫ ডিজিটের কোড টাইপ করুন</i>",
                reply_markup=kb_back()
            )
        except FloodWaitError as e:
            await message.answer(
                f"{tag_error('Flood Wait')}\n\n"
                f"<b>{e.seconds} সেকেন্ড</b> অপেক্ষা করুন",
                reply_markup=kb_back()
            )
            state["step"] = None
        except Exception as e:
            await message.answer(
                f"{tag_error('ত্রুটি')}\n\n{str(e)}",
                reply_markup=kb_back()
            )
            state["step"] = None

    # OTP Code Input
    elif step == "await_code":
        code = message.text.strip()
        state["step"] = None

        try:
            await state["client"].sign_in(state["phone"], code, phone_code_hash=state["phone_hash"])
            state["logged_in"] = True
            
            await message.answer(
                f"{card_header('লগিন সফল')}\n\n"
                f"<b>● আপনি সফলভাবে লগিন করেছেন</b>\n\n"
                f"অথেন্টিকেশন সম্পন্ন\n"
                f"সেশন সেভ করা হয়েছে\n"
                f"সিস্টেম রেডি\n\n"
                f"{gradient_line()}\n\n"
                f"<b>পরবর্তী ধাপ:</b>\n"
                f"চ্যানেল সেটআপ করুন\n"
                f"লাইভ লিঙ্ক সেট করুন",
                reply_markup=kb_main()
            )
            
        except SessionPasswordNeededError:
            state["step"] = "await_2fa"
            await message.answer(
                f"{card_header('২-ফ্যাক্টর অথেন্টিকেশন')}\n\n"
                f"<b>ধাপ ৩/৩: পাসওয়ার্ড</b>\n\n"
                f"আপনার ২FA পাসওয়ার্ড পাঠান\n\n"
                f"{premium_line()}\n"
                f"<i>Cloud Password লিখুন</i>",
                reply_markup=kb_back()
            )
            
        except PhoneCodeInvalidError:
            await message.answer(
                f"{tag_error('ভুল কোড')}\n\n"
                f"OTP কোড সঠিক নয়\n"
                f"পুনরায় চেষ্টা করুন",
                reply_markup=kb_back()
            )
            
        except Exception as e:
            await message.answer(
                f"{tag_error('ত্রুটি')}\n\n{str(e)}",
                reply_markup=kb_back()
            )

    # 2FA Password Input
    elif step == "await_2fa":
        password = message.text.strip()
        state["step"] = None

        try:
            await state["client"].sign_in(password=password)
            state["logged_in"] = True
            
            await message.answer(
                f"{card_header('লগিন সফল')}\n\n"
                f"<b>● আপনি সফলভাবে লগিন করেছেন</b>\n\n"
                f"২FA যাচাই সম্পন্ন\n"
                f"সেশন সেভ করা হয়েছে\n"
                f"সিস্টেম রেডি\n\n"
                f"{gradient_line()}\n\n"
                f"<b>পরবর্তী ধাপ:</b>\n"
                f"চ্যানেল সেটআপ করুন\n"
                f"লাইভ লিঙ্ক সেট করুন",
                reply_markup=kb_main()
            )
            
        except PasswordHashInvalidError:
            await message.answer(
                f"{tag_error('ভুল পাসওয়ার্ড')}\n\n"
                f"পাসওয়ার্ড সঠিক নয়\n"
                f"পুনরায় চেষ্টা করুন",
                reply_markup=kb_back()
            )
            
        except Exception as e:
            await message.answer(
                f"{tag_error('ত্রুটি')}\n\n{str(e)}",
                reply_markup=kb_back()
            )

    # Channel Link Input
    elif step == "await_channel":
        link = message.text.strip()
        state["step"] = None

        try:
            entity = await state["client"].get_entity(link)
            await state["client"](JoinChannelRequest(entity))
            
            state["channel_entity"] = entity
            state["channel_link"] = link
            
            await message.answer(
                f"{card_header('চ্যানেল সেটআপ সফল')}\n\n"
                f"<b>● চ্যানেল সফলভাবে সেট করা হয়েছে</b>\n\n"
                f"চ্যানেল: <code>{link}</code>\n"
                f"সংযুক্ত হয়েছে\n"
                f"সেভ করা হয়েছে\n\n"
                f"{gradient_line()}\n\n"
                f"<b>পরবর্তী ধাপ:</b>\n"
                f"লাইভ লিঙ্ক সেট করুন",
                reply_markup=kb_main()
            )
            
        except Exception as e:
            await message.answer(
                f"{tag_error('ত্রুটি')}\n\n"
                f"চ্যানেল খুঁজে পাওয়া যায়নি\n"
                f"সঠিক লিঙ্ক দিন\n\n"
                f"<code>{str(e)}</code>",
                reply_markup=kb_back()
            )

    # Live Link Input
    elif step == "await_live":
        link = message.text.strip()
        state["step"] = None
        state["live_link"] = link
        
        await message.answer(
            f"{card_header('লাইভ লিঙ্ক সেটআপ সফল')}\n\n"
            f"<b>● লাইভ লিঙ্ক সফলভাবে সেট করা হয়েছে</b>\n\n"
            f"লিঙ্ক: <code>{link}</code>\n"
            f"সেভ করা হয়েছে\n\n"
            f"{gradient_line()}\n\n"
            f"<b>সব সেটআপ সম্পন্ন</b>\n"
            f"এখন \"START BOT\" চাপুন",
            reply_markup=kb_main()
        )


# ══════════════════════════════════════════════
#  MAIN ENTRY POINT
# ══════════════════════════════════════════════

async def main():
    """Start the bot with premium experience"""
    logging.info("Starting Premium Live Auto-Unmute Bot...")
    logging.info(f"Version: {VERSION}")
    
    try:
        await dp.start_polling(bot)
    finally:
        if state["client"]:
            await state["client"].disconnect()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
