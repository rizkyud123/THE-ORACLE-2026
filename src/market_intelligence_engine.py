"""
Market Intelligence Engine - Pillar 3 of The Oracle 2026
"""

import requests
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class OddsData:
    home_win: float = 0.0
    draw: float = 0.0
    away_win: float = 0.0
    over_25: float = 0.0
    under_25: float = 0.0
    both_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class OddsMovement:
    current_odds: OddsData = field(default_factory=OddsData)
    opening_odds: OddsData = field(default_factory=OddsData)
    movement_percentage: float = 0.0
    suspicious_movement: bool = False
    movement_direction: str = "stable"


@dataclass
class SmartMoneyAnalysis:
    betting_percentage_home: float = 0.0
    betting_percentage_away: float = 0.0
    betting_percentage_draw: float = 0.0
    sharp_money_direction: str = "unknown"
    public_money_direction: str = "unknown"
    steam_move_detected: bool = False
    reverse_line_movement: bool = False


@dataclass
class RefereeProfile:
    name: str = ""
    matches_officiated: int = 0
    avg_yellow_cards: float = 0.0
    avg_red_cards: float = 0.0
    avg_penalties: float = 0.0
    home_team_favor: float = 0.0
    card_trend: str = "normal"


@dataclass
class WeatherData:
    temperature: float = 20.0
    condition: str = "clear"
    wind_speed: float = 0.0
    humidity: float = 50.0
    pitch_condition: str = "good"


@dataclass
class MarketIntelligenceAnalysis:
    odds_movement: OddsMovement = field(default_factory=OddsMovement)
    smart_money: SmartMoneyAnalysis = field(default_factory=SmartMoneyAnalysis)
    referee_profile: RefereeProfile = field(default_factory=RefereeProfile)
    weather: WeatherData = field(default_factory=WeatherData)
    market_sentiment: str = "neutral"
    trap_indicator: bool = False
    trap_reason: str = ""
    confidence_score: float = 50.0
    recommendation: str = ""


class MarketIntelligenceEngine:
    def __init__(self, api_key: str = "", weather_api_key: str = ""):
        self.api_key = api_key
        self.weather_api_key = weather_api_key
        self.odds_history: Dict[str, List[OddsData]] = {}
    
    def fetch_odds(self, match_id: str) -> OddsData:
        return OddsData(home_win=2.0, draw=3.5, away_win=3.8, over_25=1.9, under_25=1.9, both_score=1.8)
    
    def track_odds_movement(self, match_id: str, current_odds: OddsData, historical_odds: List[OddsData] = None) -> OddsMovement:
        opening_odds = historical_odds[0] if historical_odds and len(historical_odds) > 0 else current_odds
        
        home_movement = (current_odds.home_win - opening_odds.home_win) / opening_odds.home_win if opening_odds.home_win > 0 else 0
        away_movement = (current_odds.away_win - opening_odds.away_win) / opening_odds.away_win if opening_odds.away_win > 0 else 0
        
        if abs(home_movement) > 0.1 and home_movement < 0:
            direction = "towards_home"
        elif abs(away_movement) > 0.1 and away_movement < 0:
            direction = "towards_away"
        elif abs(home_movement) > 0.1 and home_movement > 0:
            direction = "away_improving"
        else:
            direction = "stable"
        
        movement_pct = abs(home_movement) + abs(away_movement)
        suspicious = movement_pct > 0.2
        
        return OddsMovement(current_odds=current_odds, opening_odds=opening_odds, movement_percentage=movement_pct * 100, suspicious_movement=suspicious, movement_direction=direction)
    
    def detect_trap(self, odds_movement: OddsMovement, statistical_favorite: str) -> Tuple[bool, str]:
        if statistical_favorite == 'home' and odds_movement.movement_direction == "away_improving":
            return True, "Odds moving towards away despite home being favored"
        if odds_movement.suspicious_movement:
            return True, f"Suspicious odds movement: {odds_movement.movement_percentage:.1f}%"
        return False, ""
    
    def analyze_smart_money(self, betting_percentages: Dict[str, float] = None, line_movement: str = "stable") -> SmartMoneyAnalysis:
        if betting_percentages is None:
            betting_percentages = {'home': 40, 'draw': 25, 'away': 35}
        
        public_dir = max(betting_percentages, key=betting_percentages.get)
        sharp_dir = public_dir
        if line_movement == "towards_home":
            sharp_dir = "home"
        elif line_movement == "towards_away":
            sharp_dir = "away"
        
        steam_move = line_movement != "stable" and public_dir != sharp_dir
        reverse_line = (public_dir == "home" and line_movement == "away_improving") or (public_dir == "away" and line_movement == "towards_home")
        
        return SmartMoneyAnalysis(betting_percentage_home=betting_percentages.get('home', 40), betting_percentage_away=betting_percentages.get('away', 35), betting_percentage_draw=betting_percentages.get('draw', 25), sharp_money_direction=sharp_dir, public_money_direction=public_dir, steam_move_detected=steam_move, reverse_line_movement=reverse_line)
    
    def get_referee_profile(self, referee_name: str) -> RefereeProfile:
        return RefereeProfile(name=referee_name, matches_officiated=50, avg_yellow_cards=3.5, avg_red_cards=0.2, avg_penalties=0.4, home_team_favor=0.05, card_trend="normal")
    
    def fetch_weather(self, city: str) -> WeatherData:
        return WeatherData(temperature=18.0, condition="clear", wind_speed=10.0, humidity=55.0, pitch_condition="good")
    
    def calculate_market_sentiment(self, odds_movement: OddsMovement, smart_money: SmartMoneyAnalysis) -> str:
        bullish = 0
        bearish = 0
        if odds_movement.movement_direction in ["towards_home", "away_improving"]:
            bullish += 1
        if smart_money.steam_move_detected:
            bullish += 1
        if smart_money.reverse_line_movement:
            bearish += 1
        
        if bullish > bearish + 1:
            return "bullish"
        elif bearish > bullish + 1:
            return "bearish"
        return "neutral"
    
    def analyze(self, match_id: str, home_team: str, away_team: str, city: str = "", referee: str = "", statistical_favorite: str = "home", betting_percentages: Dict[str, float] = None) -> MarketIntelligenceAnalysis:
        current_odds = self.fetch_odds(match_id)
        odds_movement = self.track_odds_movement(match_id, current_odds, [])
        
        is_trap, trap_reason = self.detect_trap(odds_movement, statistical_favorite)
        smart_money = self.analyze_smart_money(betting_percentages, odds_movement.movement_direction)
        
        referee_profile = self.get_referee_profile(referee)
        weather = self.fetch_weather(city)
        market_sentiment = self.calculate_market_sentiment(odds_movement, smart_money)
        
        confidence = 50.0
        if odds_movement.movement_percentage > 0:
            confidence += 15
        if smart_money.steam_move_detected:
            confidence += 15
        
        recommendation = "NEUTRAL"
        if is_trap:
            recommendation = "AVOID - Potential trap"
        elif market_sentiment == "bullish" and smart_money.steam_move_detected:
            recommendation = "STRONG"
        
        return MarketIntelligenceAnalysis(odds_movement=odds_movement, smart_money=smart_money, referee_profile=referee_profile, weather=weather, market_sentiment=market_sentiment, trap_indicator=is_trap, trap_reason=trap_reason, confidence_score=min(100.0, confidence), recommendation=recommendation)


if __name__ == "__main__":
    engine = MarketIntelligenceEngine()
    result = engine.analyze("12345", "Man City", "Liverpool", "Manchester", "Oliver", "home")
    print(f"Sentiment: {result.market_sentiment}, Trap: {result.trap_indicator}, Conf: {result.confidence_score:.0f}%")
