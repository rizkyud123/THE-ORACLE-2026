"""
The Oracle 2026 - Telegram Notifier
Scheduled alerts for next-day predictions

Author: Rizki Wahyudi, S.Kom
Version: 2.7.0
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pytz import timezone
import requests
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WITA = timezone('Asia/Makassar')


class TelegramNotifier:
    """Telegram Bot for The Oracle 2026 notifications"""
    
    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Send message to Telegram"""
        
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram credentials not configured")
            return False
        
        try:
            url = f"{self.api_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                logger.info("Message sent successfully")
                return True
            else:
                logger.error(f"Failed to send message: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def format_html_message(self, predictions: List[Dict], date_str: str) -> str:
        """Format predictions as HTML message"""
        
        # Header
        message = f"""
🏆 <b>The Oracle 2026 - Next Day Briefing</b>

📅 <b>Date:</b> {date_str}
⏰ <b>Time Zone:</b> WITA (Asia/Makassar)
🕐 <b>Prime Time:</b> 20:00 - 05:00

━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        # Filter high confidence predictions
        high_conf = [p for p in predictions if p.get("final_confidence", 0) >= 70]
        
        if high_conf:
            message += f"🎯 <b>HIGH CONFIDENCE PICKS</b> ({len(high_conf)} matches)\n"
            
            for i, pred in enumerate(high_conf[:5], 1):
                conf = pred.get("final_confidence", 0)
                home = pred.get("home_team", "?")
                away = pred.get("away_team", "?")
                league = pred.get("league", "?")
                risk = pred.get("risk_level", "MEDIUM")
                
                # Risk emoji
                risk_emoji = "🔴" if risk == "HIGH" else "🟡" if risk == "MEDIUM" else "🟢"
                
                # Bet
                bet = pred.get("recommended_bet", "SKIP")
                bet_emoji = "⏭️" if bet == "SKIP" else "🎯"
                
                message += f"""
{i}. {home} vs {away}
   📊 {league} | {conf:.0f}% {risk_emoji}
   {bet_emoji} Bet: <b>{bet}</b>

"""
        
        # Anti-Trap warnings
        traps = [p for p in predictions if p.get("market_data", {}).get("trap_detected")]
        
        if traps:
            message += f"\n🚨 <b>ANTI-TRAP ALERTS</b> ({len(traps)} matches)\n"
            
            for pred in traps[:3]:
                home = pred.get("home_team", "?")
                away = pred.get("away_team", "?")
                reason = pred.get("market_data", {}).get("trap_reason", "Unknown")
                
                message += f"""
• {home} vs {away}
   ⚠️ {reason}

"""
        
        # Summary
        total = len(predictions)
        skips = sum(1 for p in predictions if p.get("recommended_bet") == "SKIP")
        
        message += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━

📊 <b>SUMMARY:</b>
   Total Matches: {total}
   🎯 Opportunities: {total - skips}
   ⏭️ Skip: {skips}

🔗 <b>Dashboard:</b> Streamlit URL
"""
        
        return message


def load_predictions_from_cache() -> List[Dict]:
    """Load predictions from cache file"""
    
    cache_file = "predictions_cache.json"
    
    try:
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                data = json.load(f)
                return data.get("predictions", [])
    except Exception as e:
        logger.error(f"Error loading cache: {e}")
    
    return []


def send_daily_briefing(bot_token: str = None, chat_id: str = None):
    """Main function to send daily briefing"""
    
    notifier = TelegramNotifier(bot_token, chat_id)
    
    # Get predictions from cache
    predictions = load_predictions_from_cache()
    
    if not predictions:
        logger.warning("No predictions found in cache")
        return False
    
    # Get tomorrow's date
    tomorrow = (datetime.now(WITA) + timedelta(days=1)).strftime("%d %B %Y")
    
    # Format and send
    message = notifier.format_html_message(predictions, tomorrow)
    
    return notifier.send_message(message)


def send_next_day_report():
    """Send report for next day matches"""
    
    logger.info("📨 Preparing next day report...")
    
    # Get predictions
    predictions = load_predictions_from_cache()
    
    if not predictions:
        logger.warning("No predictions to send")
        return
    
    # Filter for tomorrow
    tomorrow_date = (datetime.now(WITA) + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Format message
    date_str = (datetime.now(WITA) + timedelta(days=1)).strftime("%d %B %Y")
    
    notifier = TelegramNotifier()
    message = notifier.format_html_message(predictions, date_str)
    
    # Send
    notifier.send_message(message)
    
    logger.info("✅ Next day report sent")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="The Oracle 2026 - Telegram Notifier")
    parser.add_argument("--test", action="store_true", help="Send test message")
    parser.add_argument("--daily", action="store_true", help="Send daily briefing")
    args = parser.parse_args()
    
    if args.test:
        # Test message
        notifier = TelegramNotifier()
        test_msg = """
🏆 <b>The Oracle 2026 - Test</b>

✅ Bot is working correctly!

Time: """ + datetime.now(WITA).strftime("%d %b %Y, %H:%M WITA")
        
        notifier.send_message(test_msg)
    
    elif args.daily:
        send_next_day_report()
    
    else:
        print("Usage:")
        print("  python telegram_notifier.py --test    # Send test message")
        print("  python telegram_notifier.py --daily   # Send daily briefing")
