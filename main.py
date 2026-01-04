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
    level=logging.INFO,
    stream=sys.stdout
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

# Webhook settings for Railway - YOUR URL IS HARDCODED HERE
PORT = int(os.environ.get("PORT", 8080))
WEBHOOK_URL = "https://kawai-bomber-production.up.railway.app"  # Your Railway URL
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_SECRET = "kawai-bomber-secret-2024"

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
    "permissions": "🔐", "limit": "⏳", "broadcast": "📢", "quick": "⚡",
    "attack": "⚔️", "damage": "💢", "victory": "🏁", "defense": "🛡️",
    "magic": "🔮", "ninja": "🥷", "samurai": "🗡️", "katana": "⚔️",
    "cherry": "🌸", "dragon": "🐉", "phoenix": "🔥", "tiger": "🐅",
    "fox": "🦊", "cat": "🐱", "rabbit": "🐰", "bear": "🐻",
    "panda": "🐼", "monkey": "🐵", "bird": "🐦", "fish": "🐠",
    "butterfly": "🦋", "unicorn": "🦄", "rainbow": "🌈", "cloud": "☁️",
    "moon": "🌙", "sun": "☀️", "star2": "🌟", "comet": "☄️",
    "galaxy": "🌌", "planet": "🪐", "alien": "👽", "robot": "🤖",
    "example": "📝", "rate": "📈"
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

# Proxy List
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

# API Endpoints (simplified for now)
API_ENDPOINTS = [
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

# ==================== SIMPLE BOMBING ENGINE ====================
class AttackEngine:
    def __init__(self, target_number, user_id):
        self.target = target_number
        self.user_id = user_id
        self.is_running = False
        self.success_count = 0
        
    async def launch_attack(self, duration_minutes=60):
        self.is_running = True
        self.start_time = datetime.now()
        
        # Simulate attack (in real version, this would use actual APIs)
        while self.is_running:
            self.success_count += 1
            await asyncio.sleep(0.5)
            
            # Check duration
            if duration_minutes > 0:
                elapsed = (datetime.now() - self.start_time).seconds / 60
                if elapsed >= duration_minutes:
                    break
    
    def stop_attack(self):
        self.is_running = False
    
    def get_attack_stats(self):
        return {
            "success": self.success_count,
            "duration": (datetime.now() - self.start_time).total_seconds() if hasattr(self, 'start_time') else 0
        }

# ==================== TELEGRAM BOT HANDLERS ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome command"""
    user_id = update.effective_user.id
    
    if user_id in BANNED_USERS:
        await update.message.reply_text(
            f"{EMOJIS['ban']} <b>ACCESS DENIED!</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Update user statistics
    user_statistics[user_id]["last_active"] = datetime.now()
    if user_id not in USER_DATABASE:
        USER_DATABASE[user_id] = datetime.now()
        bot_statistics["total_users"] += 1
    
    welcome_message = f"""
{EMOJIS['sparkles']} <b>KAWAI BOMBER v3.0</b> {EMOJIS['sparkles']}

{EMOJIS['flower']} Welcome to Kawai Bomber!

{EMOJIS['fire']} Features:
• SMS Bombing
• Call Bombing  
• Proxy Rotation
• Anime Interface

{EMOJIS['star']} Commands:
• /bomb - Start bombing
• /stop - Stop bombing
• /status - Bot statistics
• /mystats - Your profile
• /help - Help guide

{EMOJIS['heart']} Made by @zerocyph
"""
    
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJIS['bomb']} Start Bombing", callback_data="start_bomb"),
            InlineKeyboardButton(f"{EMOJIS['stats']} Stats", callback_data="show_stats")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

async def bomb_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start bombing"""
    user_id = update.effective_user.id
    
    if user_id in BANNED_USERS:
        await update.message.reply_text(
            f"{EMOJIS['ban']} <b>ACCESS DENIED!</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    if user_id in active_attacks:
        await update.message.reply_text(
            f"{EMOJIS['warning']} You already have an active attack!",
            parse_mode=ParseMode.HTML
        )
        return
    
    await update.message.reply_text(
        f"{EMOJIS['phone']} <b>Enter phone number (10 digits):</b>\n\n"
        f"{EMOJIS['example']} Example: 9876543210",
        parse_mode=ParseMode.HTML
    )
    
    # Update statistics
    user_statistics[user_id]["last_active"] = datetime.now()
    user_statistics[user_id]["total_sessions"] += 1
    bot_statistics["total_sessions"] += 1

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop attack"""
    user_id = update.effective_user.id
    
    if user_id not in active_attacks:
        await update.message.reply_text(
            f"{EMOJIS['warning']} No active attack!",
            parse_mode=ParseMode.HTML
        )
        return
    
    active_attacks[user_id].stop_attack()
    del active_attacks[user_id]
    bot_statistics["active_attacks"] = len(active_attacks)
    
    await update.message.reply_text(
        f"{EMOJIS['success']} Attack stopped!",
        parse_mode=ParseMode.HTML
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot status"""
    uptime = datetime.now() - bot_statistics["bot_uptime"]
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    status_message = f"""
{EMOJIS['stats']} <b>KAWAI BOMBER STATUS</b>

{EMOJIS['server']} Server: Railway
{EMOJIS['clock']} Uptime: {hours}h {minutes}m {seconds}s
{EMOJIS['users']} Total Users: {bot_statistics['total_users']}
{EMOJIS['activity']} Active Attacks: {len(active_attacks)}
{EMOJIS['proxy']} Proxies Available: {len(PROXIES)}
{EMOJIS['total']} Total Sessions: {bot_statistics['total_sessions']}
{EMOJIS['speed']} API Endpoints: {len(API_ENDPOINTS)}

{EMOJIS['working']} Bot Status: <b>Online</b>
{EMOJIS['link']} Webhook: {WEBHOOK_URL}

{EMOJIS['heart']} Made by @zerocyph
"""
    
    await update.message.reply_text(
        status_message,
        parse_mode=ParseMode.HTML
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help"""
    help_message = f"""
{EMOJIS['help']} <b>HELP GUIDE - KAWAI BOMBER</b>

{EMOJIS['star']} <b>Commands:</b>
• /start - Start the bot
• /bomb - Start SMS/Call bombing
• /stop - Stop current attack
• /status - Check bot status
• /mystats - View your statistics
• /help - Show this help message

{EMOJIS['warning']} <b>Instructions:</b>
1. Use /bomb to start
2. Enter target phone number
3. Select attack type
4. Choose duration
5. Attack will start automatically

{EMOJIS['shield']} <b>Safety:</b>
• Always verify numbers
• Don't abuse the service
• Respect privacy

{EMOJIS['heart']} <b>Support:</b>
For issues: @zerocyph
Bot Version: 3.0
Platform: Railway
"""
    
    await update.message.reply_text(
        help_message,
        parse_mode=ParseMode.HTML
    )

async def mystats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics"""
    user_id = update.effective_user.id
    
    if user_id not in user_statistics:
        await update.message.reply_text(
            f"{EMOJIS['warning']} You haven't used the bot yet!",
            parse_mode=ParseMode.HTML
        )
        return
    
    stats = user_statistics[user_id]
    
    stats_message = f"""
{EMOJIS['stats']} <b>YOUR STATISTICS</b>

{EMOJIS['user']} User ID: {user_id}
{EMOJIS['clock']} Last Active: {stats['last_active'].strftime('%Y-%m-%d %H:%M:%S')}
{EMOJIS['sms']} SMS Sent: {stats['sms_count']}
{EMOJIS['call']} Calls Made: {stats['call_count']}
{EMOJIS['rotation']} Sessions: {stats['total_sessions']}
{EMOJIS['target']} Total Hits: {stats['total_hits']}

{EMOJIS['rank']} <b>Rank:</b> Beginner
{EMOJIS['level']} <b>Level:</b> 1
{EMOJIS['premium']} <b>Status:</b> Free User

{EMOJIS['heart']} Keep attacking to improve stats!
"""
    
    await update.message.reply_text(
        stats_message,
        parse_mode=ParseMode.HTML
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "start_bomb":
        if user_id in active_attacks:
            await query.edit_message_text(
                f"{EMOJIS['warning']} You already have an active attack!",
                parse_mode=ParseMode.HTML
            )
            return
        
        await query.edit_message_text(
            f"{EMOJIS['phone']} <b>Enter phone number (10 digits):</b>\n\n"
            f"{EMOJIS['example']} Example: 9876543210",
            parse_mode=ParseMode.HTML
        )
    elif query.data == "show_stats":
        uptime = datetime.now() - bot_statistics["bot_uptime"]
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        status_message = f"""
{EMOJIS['stats']} <b>BOT STATISTICS</b>

{EMOJIS['clock']} Uptime: {hours}h {minutes}m {seconds}s
{EMOJIS['users']} Users: {bot_statistics['total_users']}
{EMOJIS['activity']} Active: {len(active_attacks)}
{EMOJIS['total']} Sessions: {bot_statistics['total_sessions']}

{EMOJIS['working']} Status: <b>Operational</b>
"""
        await query.edit_message_text(
            status_message,
            parse_mode=ParseMode.HTML
        )

# ==================== MAIN FUNCTION FOR RAILWAY ====================
async def main():
    """Main async function to run the bot on Railway"""
    print(BANNER)
    print(f"{EMOJIS['sparkles']} Kawai Bomber v3.0")
    print(f"{EMOJIS['heart']} Made by @zerocyph")
    print(f"{EMOJIS['power']} Powered by Python-Telegram-Bot")
    print(f"{EMOJIS['server']} Railway Deployment: {WEBHOOK_URL}")
    print(f"{EMOJIS['warning']} Starting bot...")
    
    # Validate token
    if not BOT_TOKEN or len(BOT_TOKEN) < 20:
        print(f"\n{EMOJIS['error']} ERROR: Invalid bot token!")
        sys.exit(1)
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("bomb", bomb_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("mystats", mystats_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Start the bot in Webhook mode for Railway
    print(f"{EMOJIS['server']} Running in WEBHOOK mode")
    print(f"{EMOJIS['link']} Webhook URL: {WEBHOOK_URL}{WEBHOOK_PATH}")
    print(f"{EMOJIS['cpu']} Port: {PORT}")
    
    # Set webhook for Telegram
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
        sys.exit(1)
    
    # Create HTTP server for webhook (Railway compatible)
    from aiohttp import web
    
    async def handle_webhook(request):
        """Handle incoming webhook requests from Telegram"""
        # Verify secret token
        if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
            logger.warning("Invalid secret token from IP: %s", request.remote)
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
        return web.json_response({
            "status": "online",
            "bot": "Kawai Bomber",
            "version": "3.0",
            "made_by": "@zerocyph",
            "uptime": str(datetime.now() - bot_statistics["bot_uptime"]),
            "users": bot_statistics["total_users"],
            "active_attacks": len(active_attacks),
            "webhook": f"{WEBHOOK_URL}{WEBHOOK_PATH}",
            "platform": "Railway"
        })
    
    async def home_page(request):
        """Home page for web browser"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>KAWAI BOMBER</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-align: center;
                    padding: 50px;
                }}
                .container {{ 
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 40px;
                    max-width: 600px;
                    margin: 0 auto;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                }}
                h1 {{ font-size: 3em; margin-bottom: 10px; }}
                .status {{ 
                    background: rgba(0, 255, 0, 0.2);
                    padding: 10px;
                    border-radius: 10px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .emoji {{ font-size: 2em; }}
                a {{ 
                    color: #ff6b9d; 
                    text-decoration: none;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="emoji">💣🌸✨</div>
                <h1>KAWAI BOMBER</h1>
                <p>Advanced SMS/Call Bombing Bot</p>
                
                <div class="status">
                    ✅ BOT IS RUNNING
                </div>
                
                <p><strong>Made with ❤️ by @zerocyph</strong></p>
                <p>Version: 3.0 | Platform: Railway</p>
                <p>Total Users: {bot_statistics['total_users']}</p>
                <p>Active Attacks: {len(active_attacks)}</p>
                
                <p><a href="/health">Check API Health</a></p>
                <p><a href="https://t.me/kawai_bomber_bot">Open in Telegram</a></p>
            </div>
        </body>
        </html>
        """
        return web.Response(text=html_content, content_type='text/html')
    
    # Create web application
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.router.add_get("/", home_page)
    app.router.add_get("/health", health_check)
    app.router.add_get("/status", health_check)
    
    # Start server on Railway
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    
    print(f"{EMOJIS['rocket']} Webhook server started on port {PORT}")
    print(f"{EMOJIS['star']} Bot is running and ready!")
    print(f"{EMOJIS['link']} Visit: {WEBHOOK_URL} to check status")
    print(f"{EMOJIS['tada']} Bot URL: https://t.me/kawai_bomber_bot")
    
    # Keep running forever
    try:
        await asyncio.Future()  # Run forever
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
