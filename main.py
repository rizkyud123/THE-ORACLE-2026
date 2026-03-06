"""
The Oracle 2026 - Global Neural v2.7.0
Full scan on ALL 15 competitions with Neural v2.6.0 Analysis

Author: Rizki Wahyudi, S.Kom
Version: 2.7.0
"""

import argparse
import logging
from datetime import datetime, timedelta
from pytz import timezone
import random

from src.api_client import api_client, get_prime_time_window, get_wita_date, get_season_for_date
from src.neural_predictor import (
    analyze_triangulation_2_6_0, 
    display_predictions_nusaai,
    NeuralAntiTrapPredictor,
    NeuralPrediction
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WITA = timezone('Asia/Makassar')


def banner():
    print("""
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║  🏆 THE ORACLE 2026 - GLOBAL NEURAL v2.7.0 🏆                        ║
    ║  Version: 2.7.0 | Rizki Wahyudi, S.Kom                               ║
    ║  Mode: GLOBAL COVERAGE (All 15 Competitions)                            ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝
    """)


# ============================================================================
# GLOBAL COMPETITIONS LIST (15 Kompetisi)
# ============================================================================

ALL_COMPETITIONS = [
    {'id': 'PL', 'name': 'Premier League', 'country': 'England'},
    {'id': 'ELC', 'name': 'Championship', 'country': 'England'},
    {'id': 'FL1', 'name': 'Ligue 1', 'country': 'France'},
    {'id': 'FL2', 'name': 'Ligue 2', 'country': 'France'},
    {'id': 'BL1', 'name': 'Bundesliga', 'country': 'Germany'},
    {'id': 'SA', 'name': 'Serie A', 'country': 'Italy'},
    {'id': 'PD', 'name': 'Primera Division', 'country': 'Spain'},
    {'id': 'DED', 'name': 'Eredivisie', 'country': 'Netherlands'},
    {'id': 'PPL', 'name': 'Primeira Liga', 'country': 'Portugal'},
    {'id': 'BEL1', 'name': 'Belgian Pro League', 'country': 'Belgium'},
    {'id': 'SUI', 'name': 'Swiss Super League', 'country': 'Switzerland'},
    {'id': 'AUT', 'name': 'Austrian Bundesliga', 'country': 'Austria'},
    {'id': 'GRE', 'name': 'Super League Greece', 'country': 'Greece'},
    {'id': 'TUR', 'name': 'Super Lig', 'country': 'Turkey'},
    {'id': 'CZE', 'name': 'Czech Liga', 'country': 'Czech Republic'},
]


# ============================================================================
# FETCH ALL GLOBAL MATCHES
# ============================================================================

def fetch_all_global_matches(date: str = None) -> tuple:
    """
    Fetch matches from ALL 15 competitions
    Returns: (matches_list, source)
    """
    now_wita = datetime.now(WITA)
    
    if not date:
        date = now_wita.strftime('%Y-%m-%d')
    
    season = get_season_for_date(date)
    if season < 2025:
        season = 2025
    
    # Get Prime Time window
    start_window, end_window = get_prime_time_window(date)
    
    logger.info(f"📡 Fetching: {date} | Season: {season}")
    logger.info(f"🕐 Prime Time Window: {start_window.strftime('%d %b %H:%M')} - {end_window.strftime('%d %b %H:%M')} WITA")
    logger.info(f"🔍 Scanning ALL {len(ALL_COMPETITIONS)} competitions...")
    
    all_matches = []
    matches_by_competition = {}
    
    # Try RapidAPI first
    logger.info("🔄 Trying RapidAPI...")
    try:
        from src.api_client import RapidAPIClient
        rapid = RapidAPIClient()
        
        for comp in ALL_COMPETITIONS:
            try:
                matches = rapid.get_matches_by_league(comp['id'], date)
                if matches:
                    matches_by_competition[comp['name']] = len(matches)
                    all_matches.extend(matches)
                    logger.info(f"   ✓ {comp['name']}: {len(matches)} matches")
            except Exception as e:
                pass
        
        if all_matches:
            logger.info(f"✅ Found {len(all_matches)} matches from RapidAPI")
            return all_matches, "RAPID-API"
    except:
        pass
    
    # Fallback to Football-Data.org
   logger.info(f"📊 Total raw matches before filtering: {len(all_matches)}")

# Filter Prime Time matches
prime_time_matches = []
for match in all_matches:
    kickoff = match.get('kickoff_wita')
    if kickoff:
        # Jika kickoff adalah string, convert ke datetime dulu (S.Kom Safety)
        if isinstance(kickoff, str):
            kickoff = datetime.fromisoformat(kickoff.replace('Z', '+00:00')).astimezone(WITA)
            
        if start_window <= kickoff <= end_window:
            prime_time_matches.append(match)
        else:
            # Opsional: Log pertandingan yang diluar jam agar Mas tahu datanya ada
            logger.debug(f"⏭️ Skipping {match.get('home_team')} (Kickoff: {kickoff.strftime('%H:%M')} WITA)")
    
    # Filter Prime Time matches
    prime_time_matches = []
    for match in all_matches:
        kickoff = match.get('kickoff_wita')
        if kickoff:
            # Convert to WITA if needed
            if kickoff.tzinfo is None:
                kickoff = WITA.localize(kickoff)
            
            if start_window <= kickoff <= end_window:
                prime_time_matches.append(match)
    
    logger.info(f"🌙 Prime Time matches (20:00-05:00 WITA): {len(prime_time_matches)}")
    
    if prime_time_matches:
        return prime_time_matches, f"GLOBAL-DB ({len(all_matches)} total)"
    
    return all_matches, f"FALLBACK-GLOBAL ({len(all_matches)} total)"


# ============================================================================
# DUAL DATE FETCHING (Auto After 22:00 WITA)
# ============================================================================

def fetch_dual_date_matches() -> tuple:
    """
    If current time > 22:00 WITA, fetch today AND tomorrow
    Combine matches for early morning viewing (01:00 - 05:00 WITA)
    
    Returns: (combined_matches, source_info)
    """
    now_wita = datetime.now(WITA)
    current_hour = now_wita.hour
    
    print(f"\n🕐 Current WITA Time: {now_wita.strftime('%d %b %Y, %H:%M')} WITA")
    
    # Check if past 22:00 WITA
    if current_hour >= 22:
        print(f"⏰ Time is past 22:00 WITA - Fetching TODAY + TOMORROW")
        
        # Get today's date
        today = now_wita.strftime('%Y-%m-%d')
        tomorrow = (now_wita + timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"\n📅 Fetching TODAY: {today}")
        matches_today, source_today = fetch_all_global_matches(today)
        
        print(f"\n📅 Fetching TOMORROW: {tomorrow}")
        matches_tomorrow, source_tomorrow = fetch_all_global_matches(tomorrow)
        
        # Combine matches
        all_matches = matches_today + matches_tomorrow
        
        # Sort by kickoff time
        all_matches.sort(key=lambda x: x.get('kickoff_wita', datetime.min))
        
        source = f"DUAL-DATE ({source_today} + {source_tomorrow})"
        
        print(f"\n✅ Combined: {len(all_matches)} matches ({len(matches_today)} today + {len(matches_tomorrow)} tomorrow)")
        
        return all_matches, source
    else:
        # Normal single date fetch
        date = now_wita.strftime('%Y-%m-%d')
        matches, source = fetch_all_global_matches(date)
        return matches, source


# ============================================================================
# MAIN OUTPUT LOOP - GLOBAL COVERAGE
# ============================================================================

def main_output_loop(date: str = None, force_dual: bool = False):
    """Main output with Global Coverage"""
    
    now_wita = datetime.now(WITA)
    
    print(f"\n📅 Current WITA Time: {now_wita.strftime('%Y-%m-%d %H:%M')}")
    print(f"🔒 Time Lock: 2026")
    
    # Determine fetch strategy
    if force_dual:
        # Force dual date mode
        matches, source = fetch_dual_date_matches()
    elif date:
        # Specific date provided
        matches, source = fetch_all_global_matches(date)
    else:
        # Auto detect - check time
        current_hour = now_wita.hour
        if current_hour >= 22:
            # Auto dual date
            matches, source = fetch_dual_date_matches()
        else:
            # Single date
            date = now_wita.strftime('%Y-%m-%d')
            matches, source = fetch_all_global_matches(date)
    
    if not matches:
        print(f"\n❌ No matches found")
        return
    
    logger.info(f"🔮 Running Neural v2.6.0 Analysis on {len(matches)} matches...")
    
    # Create Neural Predictor
    predictor = NeuralAntiTrapPredictor()
    predictions = []
    
    for i, match in enumerate(matches):
        try:
            logger.info(f"   Analyzing match {i+1}/{len(matches)}: {match.get('home_team')} vs {match.get('away_team')}")
            pred = predictor.analyze_match(match)
            predictions.append(pred)
        except Exception as e:
            logger.error(f"Error analyzing match: {e}")
    
    # Sort by confidence
    predictions.sort(key=lambda x: x.final_confidence, reverse=True)
    
    # Display results
    display_global_predictions(predictions, source, date or now_wita.strftime('%Y-%m-%d'))
    
    # Save to cache for Streamlit/Telegram
    save_predictions_to_cache(predictions, source)


# ============================================================================
# DISPLAY GLOBAL PREDICTIONS
# ============================================================================

def display_global_predictions(predictions: list, source: str, date: str):
    """Display all predictions in organized table"""
    
    print(f"\n{'='*80}")
    print(f"🏆 THE ORACLE 2026 - GLOBAL NEURAL v2.7.0")
    print(f"{'='*80}")
    print(f"📅 Date: {date} | 🏟️ Matches: {len(predictions)}")
    print(f"📡 Source: {source}")
    print(f"🕐 Prime Time: 20:00 - 05:00 WITA")
    print(f"{'='*80}")
    
    # Group by risk level
    high_risk = [p for p in predictions if p.risk_level == "HIGH"]
    medium_risk = [p for p in predictions if p.risk_level == "MEDIUM"]
    low_risk = [p for p in predictions if p.risk_level == "LOW"]
    
    # Display HIGH RISK first (with Smart Traps)
    if high_risk:
        print(f"\n🚨 HIGH RISK MATCHES ({len(high_risk)} matches)")
        print("-"*80)
        for pred in high_risk:
            print_global_prediction(pred)
    
    # Then MEDIUM RISK
    if medium_risk:
        print(f"\n⚠️ MEDIUM RISK MATCHES ({len(medium_risk)} matches)")
        print("-"*80)
        for pred in medium_risk:
            print_global_prediction(pred)
    
    # Then LOW RISK
    if low_risk:
        print(f"\n✅ LOW RISK MATCHES ({len(low_risk)} matches)")
        print("-"*80)
        for pred in low_risk:
            print_global_prediction(pred)
    
    # Summary
    print(f"\n{'='*80}")
    print(f"📊 SUMMARY:")
    print(f"   🚨 HIGH RISK: {len(high_risk)} | ⚠️ MEDIUM: {len(medium_risk)} | ✅ LOW: {len(low_risk)}")
    
    # Count skips
    skips = sum(1 for p in predictions if p.recommended_bet == "SKIP")
    bets = len(predictions) - skips
    print(f"   🎯 Betting Opportunities: {bets} | ⏭️ Skip: {skips}")
    print(f"{'='*80}")
    
    # Best bets
    best = [p for p in predictions if p.recommended_bet != "SKIP" and p.risk_level == "LOW"]
    if best:
        print(f"\n🔥 TOP BETTING OPPORTUNITIES:")
        for i, pred in enumerate(best[:5], 1):
            print(f"   {i}. {pred.home_team} vs {pred.away_team}")
            print(f"      🎯 Bet: {pred.recommended_bet} | O/U: {pred.recommended_market} | Conf: {pred.final_confidence:.0f}%")


def save_predictions_to_cache(predictions, source):
    """Save predictions to cache file for Streamlit/Telegram"""
    import json
    import os
    
    cache_file = "predictions_cache.json"
    
    try:
        # Convert predictions to dict
        pred_dicts = []
        for pred in predictions:
            pred_dict = {
                "match_id": pred.match_id,
                "home_team": pred.home_team,
                "away_team": pred.away_team,
                "league": pred.league,
                "kickoff_wita": str(pred.kickoff_wita) if pred.kickoff_wita else None,
                "final_confidence": pred.final_confidence,
                "risk_level": pred.risk_level,
                "recommended_bet": pred.recommended_bet,
                "recommended_market": pred.recommended_market,
                "h2h_data": {
                    "last_5_results": pred.h2h_data.last_5_results if pred.h2h_data else [],
                    "mental_advantage": pred.h2h_data.mental_advantage if pred.h2h_data else False,
                    "kryptonite_detected": pred.h2h_data.kryptonite_detected if pred.h2h_data else False
                } if pred.h2h_data else None,
                "poisson_data": {
                    "home_expected_goals": pred.poisson_data.home_expected_goals if pred.poisson_data else 0,
                    "away_expected_goals": pred.poisson_data.away_expected_goals if pred.poisson_data else 0,
                    "over_25_probability": pred.poisson_data.over_25_probability if pred.poisson_data else 0
                } if pred.poisson_data else None,
                "weather_data": {
                    "condition": pred.weather_data.condition if pred.weather_data else "clear",
                    "temperature": pred.weather_data.temperature if pred.weather_data else 20,
                    "weather_penalty": pred.weather_data.weather_penalty if pred.weather_data else 0
                } if pred.weather_data else None,
                "news_home": {
                    "sentiment_score": pred.news_home.sentiment_score if pred.news_home else 0.5,
                    "crisis_detected": pred.news_home.crisis_detected if pred.news_home else False,
                    "keywords_found": pred.news_home.keywords_found if pred.news_home else []
                } if pred.news_home else None,
                "market_data": {
                    "home_odds": pred.market_data.home_odds if pred.market_data else 0,
                    "away_odds": pred.market_data.away_odds if pred.market_data else 0,
                    "draw_odds": pred.market_data.draw_odds if pred.market_data else 0,
                    "market_movement": pred.market_data.market_movement if pred.market_data else "stable",
                    "trap_detected": pred.market_data.trap_detected if pred.market_data else False,
                    "trap_reason": pred.market_data.trap_reason if pred.market_data else ""
                } if pred.market_data else None,
                "penalty_reasons": pred.penalty_reasons
            }
            pred_dicts.append(pred_dict)
        
        data = {
            "predictions": pred_dicts,
            "source": source,
            "updated_at": datetime.now(WITA).isoformat()
        }
        
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Saved {len(predictions)} predictions to cache")
        return True
        
    except Exception as e:
        print(f"Error saving cache: {e}")
        return False


def print_global_prediction(pred: NeuralPrediction):
    """Print single prediction in compact format"""
    
    # Risk indicator
    risk_emoji = "🔴" if pred.risk_level == "HIGH" else "🟡" if pred.risk_level == "MEDIUM" else "🟢"
    
    # Market indicator
    market = pred.market_data.market_movement if pred.market_data else "stable"
    market_emoji = "📉" if "dropping" in market else "📈" if "rising" in market else "➡️"
    if pred.market_data.trap_detected if pred.market_data else False:
        market_emoji = "🚨"
    
    # Weather indicator
    weather_emoji = "☀️"
    if pred.weather_data:
        weather_emoji = "🌧️" if pred.weather_data.condition == "rain" else "❄️" if pred.weather_data.condition == "snow" else "⛅" if pred.weather_data.condition == "cloudy" else "☀️"
    
    # News indicator
    news_emoji = "📰✅"
    if pred.news_home:
        news_emoji = "📰⚠️" if pred.news_home.crisis_detected else "📰👎" if pred.news_home.sentiment_score < 0.4 else "📰✅"
    
    # Print match
    print(f"\n{pred.home_team} vs {pred.away_team}")
    print(f"   League: {pred.league}")
    print(f"   🎯 Conf: {pred.final_confidence:.0f}% {risk_emoji} | Risk: {pred.risk_level}")
    print(f"   📊 Analysis: H2H:[{'-'.join(pred.h2h_data.last_5_results) if pred.h2h_data else 'N/A'}] Market:[{market_emoji}] Weather:[{weather_emoji}] News:[{news_emoji}]")
    
    # Print prediction
    if pred.recommended_bet != "SKIP":
        print(f"   🎲 BET: {pred.recommended_bet} | O/U: {pred.recommended_market}")
    else:
        print(f"   ⏭️ SKIP")
    
    # Print penalties if any
    if pred.penalty_reasons:
        for reason in pred.penalty_reasons[:2]:
            print(f"   ⚠️ {reason}")
    
    print("-"*40)


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='The Oracle 2026 - Global Neural v2.7.0')
    parser.add_argument('--date', '-d', type=str, help='Date (YYYY-MM-DD)', default=None)
    parser.add_argument('--dual', action='store_true', help='Force dual date mode (today + tomorrow)')
    parser.add_argument('--test', action='store_true', help='Test Global System')
    
    args = parser.parse_args()
    
    banner()
    
    if args.test:
        # Quick test
        test_matches = [
            {'match_id': '1', 'home_team': 'PSV', 'away_team': 'AZ', 'league': 'Eredivisie', 'venue': 'Eindhoven', 'kickoff_wita': datetime.now()},
            {'match_id': '2', 'home_team': 'Bayern Munich', 'away_team': 'Dortmund', 'league': 'Bundesliga', 'venue': 'Munich', 'kickoff_wita': datetime.now()},
            {'match_id': '3', 'home_team': 'Arsenal', 'away_team': 'Liverpool', 'league': 'Premier League', 'venue': 'London', 'kickoff_wita': datetime.now()},
        ]
        
        predictor = NeuralAntiTrapPredictor()
        predictions = [predictor.analyze_match(m) for m in test_matches]
        predictions.sort(key=lambda x: x.final_confidence, reverse=True)
        display_predictions_nusaai(predictions)
        return
    
    try:
        main_output_loop(args.date, args.dual)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

