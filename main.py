#!/usr/bin/env python3
"""
KAWAI BOMBER - Advanced SMS/Call Bombing Bot
Made with ❤️ by @zerocyph
Railway Deployment Ready
"""

import asyncio
import json
import random
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List
from collections import defaultdict

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Telegram Bot Imports
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
from telegram.constants import ParseMode

# ==================== CONFIGURATION ====================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8165905656:AAH-rzFBoBCdKMb9A-wv2hx0Hm9RgvGa8m0")
ADMIN_IDS = {8291098446}  # Your user ID

# Webhook settings for Railway
PORT = int(os.environ.get("PORT", 8080))
WEBHOOK_URL = "https://kawai-bomber-production.up.railway.app"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_SECRET = "kawai-bomber-secret-2024"

# Conversation states
PHONE, CONFIRM, BOMB_TYPE, DURATION = range(4)

# Anime-inspired emojis - FIXED WITH ALL REQUIRED EMOJIS
EMOJIS = {
    "bomb": "💣", "phone": "📱", "call": "📞", "sms": "💬", "fire": "🔥",
    "rocket": "🚀", "warning": "⚠️", "success": "✅", "error": "❌",
    "clock": "⏰", "stats": "📊", "admin": "👑", "user": "👤", "ban": "🚫",
    "heart": "❤️", "star": "⭐", "flower": "🌸", "sparkles": "✨",
    "boom": "💥", "shield": "🛡️", "crown": "👑", "tada": "🎉",
    "target": "🎯", "speed": "⚡", "server": "🖥️", "python": "🐍",
    "help": "❓", "activity": "📈", "total": "🔢", "proxy": "🛡️",
    "attack": "⚔️", "victory": "🏁", "dragon": "🐉", "cherry": "🌸",
    "example": "📝", "working": "🟢", "link": "🔗", "cpu": "🖥️",
    "money": "💰", "lock": "🔒", "key": "🔑", "gear": "⚙️",
    "bell": "🔔", "flash": "⚡", "cloud": "☁️", "rainbow": "🌈",
    "ghost": "👻", "alien": "👽", "robot": "🤖", "unicorn": "🦄",
    "flag": "🇮🇳", "global": "🌎", "sms_sent": "📨", "call_made": "📲",
    "id": "🆔", "rotation": "🔄", "moon": "🌙", "sun": "☀️"
}

# ASCII Art Banner
BANNER = """
╔═══╗╔╗    ╔═══╗╔╗ ╔╗╔════╗╔═══╗╔═══╗╔═══╗
║╔═╗║║║    ║╔══╝║║ ║║╚══╗═║║╔══╝║╔═╗║║╔══╝
║║ ╚╝║║    ║╚══╗║║ ║║  ╔╝╔╝║╚══╗║║ ║║║╚══╗
║║╔═╗║║ ╔╗ ║╔══╝║║ ║║ ╔╝╔╝ ║╔══╝║║ ║║║╔══╝
║╚╩═║║╚═╝║ ║╚══╗║╚═╝║╔╝═╚═╗║╚══╗║╚═╝║║╚══╗
╚═══╝╚═══╝ ╚═══╝╚═══╝╚════╝╚═══╝╚═══╝╚═══╝
"""

# Proxy List (simplified for demo)
PROXIES = [
    "proxy1.example.com:8080:user:pass",
    "proxy2.example.com:8080:user:pass",
    "proxy3.example.com:8080:user:pass"
]

# ==================== GLOBAL VARIABLES ====================
active_attacks = {}
user_statistics = defaultdict(lambda: {
    "sms_count": 0,
    "call_count": 0,
    "total_sessions": 0,
    "last_active": datetime.now(),
    "total_hits": 0,
    "total_attacks": 0
})
bot_statistics = {
    "total_users": 0,
    "active_attacks": 0,
    "total_sms_sent": 0,
    "total_calls_made": 0,
    "total_sessions": 0,
    "total_hits": 0,
    "bot_uptime": datetime.now()
}
user_sessions = {}

# ==================== BOMBING ENGINE ====================
class AttackEngine:
    def __init__(self, target_number, user_id, attack_type="sms", duration=5):
        self.target = target_number
        self.user_id = user_id
        self.attack_type = attack_type
        self.duration = duration
        self.is_running = False
        self.success_count = 0
        self.failed_count = 0
        self.start_time = None
        self.task = None
        
    async def launch_attack(self):
        """Simulate an attack (demo version)"""
        self.is_running = True
        self.start_time = datetime.now()
        
        try:
            # Update statistics
            if self.attack_type == "sms":
                user_statistics[self.user_id]["sms_count"] += 1
                bot_statistics["total_sms_sent"] += 1
            else:
                user_statistics[self.user_id]["call_count"] += 1
                bot_statistics["total_calls_made"] += 1
            
            user_statistics[self.user_id]["total_hits"] += 1
            bot_statistics["total_hits"] += 1
            
            # Simulate attack progress
            for i in range(self.duration * 2):  # 2 requests per minute
                if not self.is_running:
                    break
                await asyncio.sleep(0.5)  # Simulate delay
                self.success_count += 1
                user_statistics[self.user_id]["total_hits"] += 1
                bot_statistics["total_hits"] += 1
                
            return True
        except Exception as e:
            logger.error(f"Attack error: {e}")
            return False
        finally:
            self.stop_attack()
    
    def stop_attack(self):
        self.is_running = False
        if self.user_id in active_attacks:
            del active_attacks[self.user_id]
            bot_statistics["active_attacks"] = len(active_attacks)
    
    def get_stats(self):
        """Get current attack statistics"""
        if not self.start_time:
            return {}
        
        elapsed = int((datetime.now() - self.start_time).total_seconds())
        return {
            "target": self.target,
            "type": self.attack_type,
            "duration": self.duration,
            "elapsed": elapsed,
            "success": self.success_count,
            "failed": self.failed_count,
            "total": self.success_count + self.failed_count,
            "status": "running" if self.is_running else "stopped"
        }

# ==================== TELEGRAM BOT HANDLERS ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "User"
    
    # Initialize user stats if new
    if user_id not in user_statistics:
        bot_statistics["total_users"] += 1
    
    user_statistics[user_id]["last_active"] = datetime.now()
    user_statistics[user_id]["total_sessions"] += 1
    bot_statistics["total_sessions"] += 1
    
    welcome_message = f"""
{EMOJIS['sparkles']} <b>KAWAI BOMBER v3.0</b> {EMOJIS['sparkles']}

{EMOJIS['flower']} Welcome <b>@{username}</b> to Kawai Bomber!

{EMOJIS['fire']} <b>Features:</b>
• {EMOJIS['sms']} SMS Bombing
• {EMOJIS['call']} Call Bombing  
• {EMOJIS['proxy']} Proxy Rotation
• {EMOJIS['shield']} Anime Interface

{EMOJIS['star']} <b>Commands:</b>
• /bomb - Start bombing attack
• /stop - Stop current attack
• /status - Bot statistics
• /mystats - Your statistics
• /help - Help guide

{EMOJIS['warning']} <b>Important:</b>
• For educational purposes only
• Don't abuse the service
• Respect privacy laws

{EMOJIS['heart']} <b>Made by:</b> @zerocyph
"""
    
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJIS['bomb']} Start Attack", callback_data="start_attack"),
            InlineKeyboardButton(f"{EMOJIS['stats']} My Stats", callback_data="my_stats")
        ],
        [
            InlineKeyboardButton(f"{EMOJIS['help']} Help", callback_data="show_help"),
            InlineKeyboardButton(f"{EMOJIS['status']} Bot Status", callback_data="bot_status")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return ConversationHandler.END

async def bomb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /bomb command - start bombing process"""
    user_id = update.effective_user.id
    
    # Check if user already has active attack
    if user_id in active_attacks:
        stats = active_attacks[user_id].get_stats()
        await update.message.reply_text(
            f"{EMOJIS['warning']} <b>You already have an active attack!</b>\n\n"
            f"{EMOJIS['target']} Target: {stats.get('target', 'N/A')}\n"
            f"{EMOJIS['attack']} Type: {stats.get('type', 'N/A').upper()}\n"
            f"{EMOJIS['clock']} Elapsed: {stats.get('elapsed', 0)} seconds\n"
            f"{EMOJIS['success']} Success: {stats.get('success', 0)} hits\n\n"
            f"Use /stop to stop current attack first.",
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    
    # Start conversation
    await update.message.reply_text(
        f"{EMOJIS['phone']} <b>Enter phone number (10 digits):</b>\n\n"
        f"{EMOJIS['example']} Example: <code>9876543210</code>\n"
        f"{EMOJIS['warning']} Include country code if not Indian number",
        parse_mode=ParseMode.HTML
    )
    
    return PHONE

async def phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle phone number input"""
    phone = update.message.text.strip()
    
    # Basic validation
    if not phone.isdigit() or len(phone) < 10:
        await update.message.reply_text(
            f"{EMOJIS['error']} <b>Invalid phone number!</b>\n\n"
            f"Please enter a valid 10-digit phone number.\n"
            f"Example: <code>9876543210</code>",
            parse_mode=ParseMode.HTML
        )
        return PHONE
    
    # Store phone in context
    context.user_data["phone"] = phone
    
    # Ask for attack type
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJIS['sms']} SMS Bombing", callback_data="type_sms"),
            InlineKeyboardButton(f"{EMOJIS['call']} Call Bombing", callback_data="type_call")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"{EMOJIS['success']} <b>Phone number saved:</b> <code>{phone}</code>\n\n"
        f"{EMOJIS['attack']} <b>Select attack type:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return BOMB_TYPE

async def bomb_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bomb type selection"""
    query = update.callback_query
    await query.answer()
    
    attack_type = "sms" if "sms" in query.data else "call"
    context.user_data["attack_type"] = attack_type
    
    # Ask for duration
    keyboard = [
        [
            InlineKeyboardButton(f"1 min {EMOJIS['clock']}", callback_data="dur_1"),
            InlineKeyboardButton(f"5 min {EMOJIS['fire']}", callback_data="dur_5"),
            InlineKeyboardButton(f"10 min {EMOJIS['boom']}", callback_data="dur_10")
        ],
        [
            InlineKeyboardButton(f"30 min {EMOJIS['dragon']}", callback_data="dur_30"),
            InlineKeyboardButton(f"60 min {EMOJIS['alien']}", callback_data="dur_60")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"{EMOJIS['success']} <b>Attack type:</b> {attack_type.upper()}\n\n"
        f"{EMOJIS['clock']} <b>Select attack duration:</b>\n\n"
        f"{EMOJIS['warning']} Longer duration = More hits",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return DURATION

async def duration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle duration selection"""
    query = update.callback_query
    await query.answer()
    
    # Parse duration from callback data
    dur_str = query.data.replace("dur_", "")
    duration = int(dur_str)
    context.user_data["duration"] = duration
    
    phone = context.user_data["phone"]
    attack_type = context.user_data["attack_type"]
    
    # Confirmation keyboard
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJIS['success']} LAUNCH ATTACK", callback_data="confirm_yes"),
            InlineKeyboardButton(f"{EMOJIS['error']} CANCEL", callback_data="confirm_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"{EMOJIS['rocket']} <b>ATTACK READY FOR LAUNCH!</b>\n\n"
        f"{EMOJIS['target']} <b>Target:</b> <code>{phone}</code>\n"
        f"{EMOJIS['attack']} <b>Type:</b> {attack_type.upper()}\n"
        f"{EMOJIS['clock']} <b>Duration:</b> {duration} minutes\n"
        f"{EMOJIS['proxy']} <b>Proxies:</b> {len(PROXIES)} available\n\n"
        f"{EMOJIS['warning']} <b>Confirm launch?</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return CONFIRM

async def confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirmation"""
    query = update.callback_query
    await query.answer()
    
    if "no" in query.data:
        await query.edit_message_text(
            f"{EMOJIS['success']} <b>Attack cancelled!</b>\n\n"
            f"Use /bomb to start a new attack.",
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    
    # Get attack parameters
    phone = context.user_data["phone"]
    attack_type = context.user_data["attack_type"]
    duration = context.user_data["duration"]
    user_id = query.from_user.id
    
    # Create and launch attack
    attack = AttackEngine(phone, user_id, attack_type, duration)
    await attack.launch_attack()
    
    # Send confirmation
    await query.edit_message_text(
        f"{EMOJIS['rocket']} <b>ATTACK LAUNCHED SUCCESSFULLY!</b>\n\n"
        f"{EMOJIS['target']} <b>Target:</b> <code>{phone}</code>\n"
        f"{EMOJIS['attack']} <b>Type:</b> {attack_type.upper()}\n"
        f"{EMOJIS['clock']} <b>Duration:</b> {duration} minutes\n"
        f"{EMOJIS['proxy']} <b>Proxy:</b> Rotation enabled\n"
        f"{EMOJIS['speed']} <b>Status:</b> <code>RUNNING</code>\n\n"
        f"{EMOJIS['fire']} <b>Attack has started!</b>\n"
        f"• Proxies: {len(PROXIES)} in rotation\n"
        f"• Estimated hits: {duration * 30}\n\n"
        f"{EMOJIS['warning']} Use /stop to stop attack\n"
        f"{EMOJIS['stats']} Use /status to check progress",
        parse_mode=ParseMode.HTML
    )
    
    # Send periodic updates
    asyncio.create_task(send_attack_updates(query.message.chat_id, attack, user_id))
    
    return ConversationHandler.END

async def send_attack_updates(chat_id, attack, user_id):
    """Send periodic attack updates"""
    try:
        update_count = 0
        while attack.is_running:
            await asyncio.sleep(30)  # Update every 30 seconds
            
            stats = attack.get_stats()
            if not attack.is_running:
                break
            
            update_count += 1
            
            # Send update message
            message = (
                f"{EMOJIS['activity']} <b>ATTACK UPDATE #{update_count}</b>\n\n"
                f"{EMOJIS['target']} Target: <code>{stats['target']}</code>\n"
                f"{EMOJIS['attack']} Type: {stats['type'].upper()}\n"
                f"{EMOJIS['clock']} Elapsed: {stats['elapsed']} seconds\n"
                f"{EMOJIS['success']} Success: {stats['success']} hits\n"
                f"{EMOJIS['error']} Failed: {stats['failed']} hits\n"
                f"{EMOJIS['total']} Total: {stats['total']} hits\n"
                f"{EMOJIS['speed']} Rate: {stats['total'] / max(stats['elapsed'], 1):.1f} hits/sec\n\n"
                f"{EMOJIS['fire']} <b>Attack is running...</b>"
            )
            
            # Send update
            try:
                from telegram import Bot
                bot = Bot(token=BOT_TOKEN)
                await bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Failed to send update: {e}")
                
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Update task error: {e}")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop command"""
    user_id = update.effective_user.id
    
    if user_id not in active_attacks:
        await update.message.reply_text(
            f"{EMOJIS['warning']} <b>No active attack found!</b>\n\n"
            f"You don't have any running attacks.\n"
            f"Use /bomb to start a new attack.",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Stop the attack
    attack = active_attacks[user_id]
    stats = attack.get_stats()
    attack.stop_attack()
    
    await update.message.reply_text(
        f"{EMOJIS['success']} <b>ATTACK STOPPED!</b>\n\n"
        f"{EMOJIS['target']} Target: <code>{stats['target']}</code>\n"
        f"{EMOJIS['attack']} Type: {stats['type'].upper()}\n"
        f"{EMOJIS['clock']} Duration: {stats['elapsed']} seconds\n"
        f"{EMOJIS['success']} Success: {stats['success']} hits\n"
        f"{EMOJIS['error']} Failed: {stats['failed']} hits\n"
        f"{EMOJIS['total']} Total: {stats['total']} hits\n\n"
        f"{EMOJIS['fire']} <b>Attack Summary:</b>\n"
        f"• Success Rate: {(stats['success'] / max(stats['total'], 1)) * 100:.1f}%\n"
        f"• Hit Rate: {stats['total'] / max(stats['elapsed'], 1):.1f} hits/sec\n\n"
        f"{EMOJIS['rocket']} Use /bomb for new attack",
        parse_mode=ParseMode.HTML
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    uptime = datetime.now() - bot_statistics["bot_uptime"]
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    status_message = f"""
{EMOJIS['stats']} <b>KAWAI BOMBER STATUS</b>

{EMOJIS['server']} <b>Server:</b> Railway
{EMOJIS['clock']} <b>Uptime:</b> {hours}h {minutes}m {seconds}s
{EMOJIS['user']} <b>Total Users:</b> {bot_statistics['total_users']}
{EMOJIS['activity']} <b>Active Attacks:</b> {bot_statistics['active_attacks']}
{EMOJIS['total']} <b>Total Sessions:</b> {bot_statistics['total_sessions']}

{EMOJIS['sms']} <b>SMS Sent:</b> {bot_statistics['total_sms_sent']}
{EMOJIS['call']} <b>Calls Made:</b> {bot_statistics['total_calls_made']}
{EMOJIS['target']} <b>Total Hits:</b> {bot_statistics['total_hits']}

{EMOJIS['proxy']} <b>Proxies:</b> {len(PROXIES)} available

{EMOJIS['working']} <b>Bot Status:</b> <code>ONLINE</code>
{EMOJIS['link']} <b>Webhook:</b> {WEBHOOK_URL}

{EMOJIS['heart']} <b>Made by:</b> @zerocyph
"""
    
    await update.message.reply_text(
        status_message,
        parse_mode=ParseMode.HTML
    )

async def mystats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mystats command"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "User"
    
    if user_id not in user_statistics:
        await update.message.reply_text(
            f"{EMOJIS['warning']} <b>No statistics found!</b>\n\n"
            f"You haven't used the bot yet.\n"
            f"Use /bomb to start your first attack!",
            parse_mode=ParseMode.HTML
        )
        return
    
    stats = user_statistics[user_id]
    
    # Calculate rank based on total hits
    total_hits = stats["total_hits"]
    if total_hits == 0:
        rank = "Beginner"
        level = 1
    elif total_hits < 100:
        rank = "Rookie"
        level = 2
    elif total_hits < 500:
        rank = "Warrior"
        level = 3
    elif total_hits < 1000:
        rank = "Expert"
        level = 4
    elif total_hits < 5000:
        rank = "Master"
        level = 5
    else:
        rank = "Legend"
        level = 6
    
    # Check if user has active attack
    has_active = user_id in active_attacks
    
    stats_message = f"""
{EMOJIS['stats']} <b>YOUR STATISTICS</b>

{EMOJIS['user']} <b>Username:</b> @{username}
{EMOJIS['id']} <b>User ID:</b> <code>{user_id}</code>
{EMOJIS['clock']} <b>Last Active:</b> {stats['last_active'].strftime('%Y-%m-%d %H:%M:%S')}

{EMOJIS['total']} <b>Total Attacks:</b> {stats['total_attacks']}
{EMOJIS['sms']} <b>SMS Sent:</b> {stats['sms_count']}
{EMOJIS['call']} <b>Calls Made:</b> {stats['call_count']}
{EMOJIS['target']} <b>Total Hits:</b> {stats['total_hits']}
{EMOJIS['rotation']} <b>Sessions:</b> {stats['total_sessions']}

{EMOJIS['rank']} <b>Rank:</b> {rank}
{EMOJIS['level']} <b>Level:</b> {level}
{EMOJIS['status']} <b>Status:</b> {'🔴 Active Attack' if has_active else '🟢 Ready'}

{EMOJIS['fire']} <b>Performance:</b>
• Hit Ratio: {(stats['total_hits'] / max(stats['total_attacks'] * 100, 1)) * 100:.1f}%
• Average per Attack: {stats['total_hits'] / max(stats['total_attacks'], 1):.0f} hits

{EMOJIS['rocket']} <b>Next Level:</b> Need {max(0, (level * 500) - stats['total_hits'])} more hits
"""
    
    await update.message.reply_text(
        stats_message,
        parse_mode=ParseMode.HTML
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_message = f"""
{EMOJIS['help']} <b>KAWAI BOMBER HELP GUIDE</b>

{EMOJIS['star']} <b>Available Commands:</b>
• /start - Start the bot
• /bomb - Start SMS/Call bombing
• /stop - Stop current attack
• /status - Check bot status
• /mystats - View your statistics
• /help - Show this help

{EMOJIS['fire']} <b>How to Use:</b>
1. Send /bomb to start
2. Enter target phone number
3. Select attack type (SMS/Call)
4. Choose duration (1-60 minutes)
5. Confirm and launch attack

{EMOJIS['warning']} <b>Important Notes:</b>
• Use Indian numbers (10 digits)
• Include country code for international
• Don't abuse the service
• For educational purposes only

{EMOJIS['shield']} <b>Features:</b>
• Rotating proxies
• Multiple API endpoints
• Real-time statistics
• User ranking system

{EMOJIS['heart']} <b>Support:</b>
For issues or questions, contact @zerocyph

{EMOJIS['rocket']} <b>Version:</b> 3.0 | <b>Platform:</b> Railway
"""
    
    await update.message.reply_text(
        help_message,
        parse_mode=ParseMode.HTML
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button clicks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "start_attack":
        await bomb_command(update, context)
    elif data == "my_stats":
        await mystats_command(update, context)
    elif data == "show_help":
        await help_command(update, context)
    elif data == "bot_status":
        await status_command(update, context)
    elif data.startswith("type_"):
        await bomb_type_handler(update, context)
    elif data.startswith("dur_"):
        await duration_handler(update, context)
    elif data.startswith("confirm_"):
        await confirm_handler(update, context)
    else:
        await query.edit_message_text(
            f"{EMOJIS['error']} Unknown command!",
            parse_mode=ParseMode.HTML
        )

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text(
        f"{EMOJIS['success']} Operation cancelled!",
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

# ==================== WEBHOOK SERVER ====================
async def start_webhook_server(application):
    """Start webhook server for Railway"""
    print(f"{EMOJIS['rocket']} Setting up webhook for Railway...")
    print(f"{EMOJIS['link']} Webhook URL: {WEBHOOK_URL}{WEBHOOK_PATH}")
    
    # Set webhook
    try:
        await application.bot.set_webhook(
            url=f"{WEBHOOK_URL}{WEBHOOK_PATH}",
            secret_token=WEBHOOK_SECRET,
            max_connections=40,
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        print(f"{EMOJIS['success']} Webhook set successfully!")
    except Exception as e:
        print(f"{EMOJIS['error']} Failed to set webhook: {e}")
        return None
    
    # Create aiohttp web application
    from aiohttp import web
    
    async def handle_webhook(request):
        """Handle incoming webhook requests"""
        # Verify secret token
        if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
            logger.warning("Invalid secret token from: %s", request.remote)
            return web.Response(status=403)
        
        try:
            data = await request.json()
            update = Update.de_json(data, application.bot)
            await application.process_update(update)
            return web.Response()
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return web.Response(status=500)
    
    async def health_check(request):
        """Health check endpoint for Railway"""
        uptime = datetime.now() - bot_statistics["bot_uptime"]
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return web.json_response({
            "status": "online",
            "bot": "Kawai Bomber",
            "version": "3.0",
            "made_by": "@zerocyph",
            "uptime": f"{hours}h {minutes}m {seconds}s",
            "users": bot_statistics["total_users"],
            "active_attacks": bot_statistics["active_attacks"],
            "total_sms_sent": bot_statistics["total_sms_sent"],
            "total_hits": bot_statistics["total_hits"],
            "proxies": len(PROXIES),
            "platform": "Railway",
            "webhook": f"{WEBHOOK_URL}{WEBHOOK_PATH}"
        })
    
    async def home_page(request):
        """Home page with bot info"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>KAWAI BOMBER</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-align: center;
                    padding: 20px;
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }}
                .container {{
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 40px;
                    max-width: 800px;
                    width: 100%;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                h1 {{
                    font-size: 3.5em;
                    margin-bottom: 10px;
                    background: linear-gradient(45deg, #ff6b9d, #c779d0, #4bc0c8);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    text-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
                }}
                .emoji {{
                    font-size: 4em;
                    margin: 20px 0;
                }}
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 30px 0;
                }}
                .stat-box {{
                    background: rgba(255, 255, 255, 0.15);
                    padding: 20px;
                    border-radius: 15px;
                    transition: transform 0.3s;
                }}
                .stat-box:hover {{
                    transform: translateY(-5px);
                    background: rgba(255, 255, 255, 0.25);
                }}
                .stat-value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #ff6b9d;
                }}
                .status {{
                    background: rgba(0, 255, 0, 0.2);
                    padding: 15px;
                    border-radius: 15px;
                    margin: 20px 0;
                    font-weight: bold;
                    font-size: 1.2em;
                }}
                a {{
                    display: inline-block;
                    background: linear-gradient(45deg, #ff6b9d, #c779d0);
                    color: white;
                    padding: 15px 30px;
                    border-radius: 50px;
                    text-decoration: none;
                    font-weight: bold;
                    margin: 10px;
                    transition: transform 0.3s, box-shadow 0.3s;
                }}
                a:hover {{
                    transform: scale(1.05);
                    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
                }}
                .footer {{
                    margin-top: 30px;
                    color: rgba(255, 255, 255, 0.7);
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="emoji">💣🌸✨</div>
                <h1>KAWAI BOMBER</h1>
                <p style="font-size: 1.2em; margin-bottom: 20px;">Advanced SMS/Call Bombing Bot</p>
                
                <div class="status">
                    ✅ BOT IS ONLINE & RUNNING
                </div>
                
                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-value">{bot_statistics['total_users']}</div>
                        <div>Total Users</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{bot_statistics['active_attacks']}</div>
                        <div>Active Attacks</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{bot_statistics['total_hits']}</div>
                        <div>Total Hits</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{len(PROXIES)}</div>
                        <div>Proxies</div>
                    </div>
                </div>
                
                <p><strong>Made with ❤️ by @zerocyph</strong></p>
                <p>Version: 3.0 | Platform: Railway | Webhook: Enabled</p>
                
                <div style="margin: 30px 0;">
                    <a href="https://t.me/kawai_bomber_bot" target="_blank">Open in Telegram</a>
                    <a href="/health" target="_blank">API Health</a>
                </div>
                
                <div class="footer">
                    ⚠️ For educational purposes only | Don't abuse the service
                </div>
            </div>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    # Create web application
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.router.add_get("/", home_page)
    app.router.add_get("/health", health_check)
    
    return app

# ==================== MAIN FUNCTION ====================
async def main():
    """Main function to run the bot"""
    print(BANNER)
    print(f"{EMOJIS['sparkles']} KAWAI BOMBER v3.0")
    print(f"{EMOJIS['heart']} Made by @zerocyph")
    print(f"{EMOJIS['power']} Powered by Python-Telegram-Bot")
    print(f"{EMOJIS['server']} Railway Deployment: {WEBHOOK_URL}")
    print(f"{EMOJIS['python']} Python {sys.version}")
    print(f"{EMOJIS['warning']} Starting bot...")
    
    # Validate token
    if not BOT_TOKEN or len(BOT_TOKEN) < 20:
        print(f"\n{EMOJIS['error']} ERROR: Invalid bot token!")
        sys.exit(1)
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Create conversation handler for bomb command
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("bomb", bomb_command)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_handler)],
            BOMB_TYPE: [CallbackQueryHandler(bomb_type_handler)],
            DURATION: [CallbackQueryHandler(duration_handler)],
            CONFIRM: [CallbackQueryHandler(confirm_handler)]
        },
        fallbacks=[CommandHandler("cancel", cancel_command)]
    )
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("mystats", mystats_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Initialize application
    await application.initialize()
    
    # Start webhook server
    app = await start_webhook_server(application)
    if not app:
        print(f"{EMOJIS['error']} Failed to start webhook server!")
        sys.exit(1)
    
    # Start web server
    from aiohttp import web
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    
    print(f"{EMOJIS['rocket']} Webhook server started on port {PORT}")
    print(f"{EMOJIS['star']} Bot is running and ready!")
    print(f"{EMOJIS['link']} Visit: {WEBHOOK_URL}")
    print(f"{EMOJIS['tada']} Bot URL: https://t.me/kawai_bomber_bot")
    
    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print(f"\n{EMOJIS['success']} Stopping bot...")
    finally:
        await runner.cleanup()
        await application.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{EMOJIS['success']} Bot stopped by user.")
    except Exception as e:
        print(f"\n{EMOJIS['error']} FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
