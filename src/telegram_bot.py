"""
Telegram Bot - Notification system for The Oracle 2026
Sends daily picks and real-time alerts.

Author: Rizki Wahyudi, S.Kom
Version: 2.0.0
"""

import os
import logging
from datetime import datetime
from typing import List, Optional

# Use the python-telegram-bot v20+ API
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

import threading

from .config import config
from .prediction_engine import PredictionEngine, DailyPicks, Prediction

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram Bot for The Oracle 2026 Soccer Intelligence System."""
    
    def __init__(self, token: str = None, chat_id: str = None):
        self.token = token or config.api_keys.telegram_bot_token
        self.chat_id = chat_id or config.api_keys.telegram_chat_id
        self.application = None
        self.prediction_engine = PredictionEngine()
        
        self.start_message = """
🏆 *Welcome to The Oracle 2026* 🏆

Soccer Intelligence System - Triangulasi Data Methodology

I provide:
• 🎯 Daily Top 10 Picks (Confidence > 85%)
• 🔥 Jackpot Potential Picks
• 📊 Match Predictions
• ⚠️ Real-time Alerts

Use /help to see available commands.
"""
        
        self.help_message = """
📋 *Available Commands:*

/start - Start the bot
/daily - Get today's top picks
/predict <home> vs <away> - Predict a match
/jackpot - Get jackpot potential picks
/status - System status
/help - Show this help message
"""
    
    def start(self):
        """Start the Telegram bot."""
        if not self.token or self.token == "YOUR_TELEGRAM_BOT_TOKEN":
            logger.warning("Telegram bot token not configured. Bot will not start.")
            return False
        
        try:
            self.application = Application.builder().token(self.token).build()
            
            # Add handlers
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("daily", self.daily_command))
            self.application.add_handler(CommandHandler("jackpot", self.jackpot_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("predict", self.predict_command))
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
            
            # Start polling
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)
            
            logger.info("Telegram bot started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error starting Telegram bot: {e}")
            return False
    
    def stop(self):
        """Stop the Telegram bot."""
        if self.application:
            self.application.stop()
            logger.info("Telegram bot stopped")
    
    async def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Send a message to the configured chat."""
        if not self.chat_id or self.chat_id == "YOUR_CHAT_ID":
            logger.warning("Telegram chat ID not configured")
            return False
        
        try:
            if self.application:
                await self.application.bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    parse_mode=parse_mode
                )
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def send_daily_picks(self, picks: DailyPicks) -> bool:
        """Send daily picks to the chat."""
        message = self.prediction_engine.format_daily_picks_message(picks)
        return self.send_message(message)
    
    def send_prediction(self, prediction: Prediction) -> bool:
        """Send a single prediction to the chat."""
        message = self.prediction_engine.format_prediction_message(prediction)
        return self.send_message(message)
    
    # Command handlers
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        await update.message.reply_text(self.start_message, parse_mode="Markdown")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        await update.message.reply_text(self.help_message, parse_mode="Markdown")
    
    async def daily_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /daily command."""
        await update.message.reply_text("📊 Generating daily picks...", parse_mode="Markdown")
        # Would generate picks here
    
    async def jackpot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /jackpot command."""
        await update.message.reply_text("🔥 Loading jackpot picks...", parse_mode="Markdown")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        status = f"""
🔍 *SYSTEM STATUS*

📊 Engine: The Oracle 2026 v{config.version}
👤 Developer: {config.developer}
🏗️ Architecture: Hybrid AI Consensus

✅ System Status: Online
"""
        await update.message.reply_text(status, parse_mode="Markdown")
    
    async def predict_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /predict command."""
        await update.message.reply_text("🎯 Prediction feature coming soon...", parse_mode="Markdown")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages."""
        await update.message.reply_text("Use /help for commands", parse_mode="Markdown")


def run_bot():
    """Run the Telegram bot."""
    bot = TelegramBot()
    bot.start()


if __name__ == "__main__":
    run_bot()
