"""
Prediction Engine - Main orchestration engine of The Oracle 2026
Combines all three pillars with triangulation logic.

Author: Rizki Wahyudi, S.Kom
Version: 2.0.0
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

from .statistical_engine import StatisticalEngine, MatchStats
from .human_context_engine import HumanContextEngine, TeamNews, LineupAnalysis, ManagerMatchup
from .market_intelligence_engine import MarketIntelligenceEngine
from .triangulation_engine import TriangulationEngine, TriangulationResult
from .config import config


@dataclass
class Match:
    """Match data structure"""
    match_id: str
    home_team: str
    away_team: str
    league: str
    kickoff_time: datetime
    venue: str
    referee: str = ""
    home_position: int = 0
    away_position: int = 0
    home_points: int = 0
    away_points: int = 0
    # Additional data from API
    home_goals_season: float = 0.0
    away_goals_season: float = 0.0
    home_conceded_season: float = 0.0
    away_conceded_season: float = 0.0
    home_matches_played: int = 0
    away_matches_played: int = 0
    home_form: str = ""
    away_form: str = ""


@dataclass
class Prediction:
    """Prediction result for a match"""
    match: Match
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    expected_score: str
    recommended_bet: str  # 'home', 'draw', 'away', 'skip'
    confidence_score: float
    confidence_level: str
    triangulation_result: TriangulationResult
    kelly_stake: float = 0.0
    risk_level: str = "medium"
    # New dynamic fields
    home_attack_power: float = 0.0
    away_attack_power: float = 0.0
    home_defense_power: float = 0.0
    away_defense_power: float = 0.0
    value_bet: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DailyPicks:
    """Daily top picks output"""
    date: datetime
    picks: List[Prediction]
    total_confidence: float
    jackpot_picks: List[Prediction] = field(default_factory=list)


class PredictionEngine:
    """
    Main prediction engine that orchestrates all three pillars
    and generates predictions using triangulation logic.
    """
    
    def __init__(self):
        self.stat_engine = StatisticalEngine()
        self.human_engine = HumanContextEngine()
        self.market_engine = MarketIntelligenceEngine()
        self.triangulation = TriangulationEngine()
        self.config = config
        
        # League average goals
        self.league_avg_goals = {
            "Premier League": 2.82,
            "La Liga": 2.69,
            "Serie A": 2.72,
            "Bundesliga": 2.87,
            "Ligue 1": 2.64,
            "Champions League": 2.85,
            "Europa League": 2.65
        }
    
    def _create_match_stats(self, match: Match) -> MatchStats:
        """Create MatchStats from Match data"""
        # Calculate average goals from season data
        home_avg = match.home_goals_season / max(1, match.home_matches_played)
        away_avg = match.away_goals_season / max(1, match.away_matches_played)
        
        # Parse form (e.g., "WWDLW" -> [2,2,1,0,2])
        home_form_list = self._parse_form(match.home_form)
        away_form_list = self._parse_form(match.away_form)
        
        return MatchStats(
            home_team=match.home_team,
            away_team=match.away_team,
            home_avg_goals=home_avg,
            away_avg_goals=away_avg,
            home_goals_scored_last5=home_form_list[:5],
            away_goals_scored_last5=away_form_list[:5],
            home_goals_conceded_last5=[1,1,1,1,1],  # Default
            away_goals_conceded_last5=[1,1,1,1,1],  # Default
            home_position=match.home_position,
            away_position=match.away_position,
            h2h_home_wins=3,
            h2h_away_wins=2,
            h2h_draws=2,
            h2h_matches=7,
            # Season data for attack/defense power calculation
            home_goals_scored_season=match.home_goals_season,
            away_goals_scored_season=match.away_goals_season,
            home_goals_conceded_season=match.home_conceded_season,
            away_goals_conceded_season=match.away_conceded_season,
            home_matches_played=match.home_matches_played,
            away_matches_played=match.away_matches_played,
            home_form_score=match.home_form or "WWWDD",
            away_form_score=match.away_form or "LLDWW"
        )
    
    def _parse_form(self, form: str) -> List[int]:
        """Parse form string to goals scored list"""
        if not form:
            return [2, 2, 1, 1, 2]  # Default
        
        goals = []
        for char in form.upper()[-5:]:
            if char == 'W':
                goals.append(2)
            elif char == 'D':
                goals.append(1)
            else:  # L
                goals.append(0)
        
        # Pad to 5
        while len(goals) < 5:
            goals.append(1)
        
        return goals
    
    def predict_match(
        self,
        match: Match,
        match_stats: MatchStats = None,
        home_news: List[Dict] = None,
        away_news: List[Dict] = None,
        betting_percentages: Dict[str, float] = None
    ) -> Prediction:
        """
        Generate a complete prediction for a match with real triangulation.
        """
        
        # Get league average goals
        league = match.league
        league_avg = self.league_avg_goals.get(league, 2.5)
        
        # Create match stats if not provided
        if match_stats is None:
            match_stats = self._create_match_stats(match)
        
        # Pillar 1: Statistical Analysis with real Poisson
        stat_analysis = self.stat_engine.analyze(match_stats, league_avg)
        
        # Determine statistical favorite
        if stat_analysis.home_win_probability > stat_analysis.away_win_probability:
            stat_favorite = "home"
        elif stat_analysis.away_win_probability > stat_analysis.home_win_probability:
            stat_favorite = "away"
        else:
            stat_favorite = "draw"
        
        # Pillar 2: Human Context Analysis
        home_lineup = LineupAnalysis(
            is_confirmed=True,
            formation="4-3-3",
            key_players_missing=[],
            formation_strength=0.85,
            lineup_quality_score=0.8
        )
        away_lineup = LineupAnalysis(
            is_confirmed=True,
            formation="4-4-2",
            key_players_missing=[],
            formation_strength=0.8,
            lineup_quality_score=0.75
        )
        
        manager_matchup = ManagerMatchup(
            home_manager="Manager A",
            away_manager="Manager B"
        )
        
        human_analysis = self.human_engine.analyze(
            home_news=home_news or [],
            away_news=away_news or [],
            home_lineup=home_lineup,
            away_lineup=away_lineup,
            manager_matchup=manager_matchup,
            home_league_position=match.home_position,
            away_league_position=match.away_position,
            days_since_last_match=3,
            matches_in_last_14_days=2,
            travel_distance_km=500,
            is_home_team=False
        )
        
        # Pillar 3: Market Intelligence
        market_analysis = self.market_engine.analyze(
            match_id=match.match_id,
            home_team=match.home_team,
            away_team=match.away_team,
            city=match.venue.split(",")[0] if "," in match.venue else match.venue,
            referee=match.referee,
            statistical_favorite=stat_favorite,
            betting_percentages=betting_percentages
        )
        
        # Triangulation
        triangulation_result = self.triangulation.analyze(
            statistical=stat_analysis,
            human_context=human_analysis,
            market=market_analysis
        )
        
        # Calculate Kelly Criterion stake
        kelly_stake = self._calculate_kelly_stake(
            triangulation_result.winning_probability,
            1.9  # Default odds
        )
        
        # Determine recommended bet based on real analysis
        recommended_bet = self._determine_recommended_bet(
            triangulation_result,
            stat_analysis
        )
        
        # Get predicted score from Poisson
        expected_score = stat_analysis.predicted_score
        
        # Determine value bet
        value_bet = self._check_value_bet(
            stat_analysis,
            recommended_bet
        )
        
        return Prediction(
            match=match,
            home_win_probability=stat_analysis.home_win_probability,
            draw_probability=stat_analysis.draw_probability,
            away_win_probability=stat_analysis.away_win_probability,
            expected_score=expected_score,
            recommended_bet=recommended_bet,
            confidence_score=triangulation_result.confidence_score,
            confidence_level=triangulation_result.confidence_level.value,
            triangulation_result=triangulation_result,
            kelly_stake=kelly_stake,
            risk_level=triangulation_result.risk_assessment,
            home_attack_power=stat_analysis.home_attack_power,
            away_attack_power=stat_analysis.away_attack_power,
            home_defense_power=stat_analysis.home_defense_power,
            away_defense_power=stat_analysis.away_defense_power,
            value_bet=value_bet
        )
    
    def _check_value_bet(
        self,
        stat_analysis,
        recommended_bet: str
    ) -> str:
        """
        Check if there's a value bet opportunity.
        VALUE BET: When odds are better than they should be based on probability.
        """
        # Get the probability of recommended bet
        if recommended_bet.upper() == "HOME":
            prob = stat_analysis.home_win_probability
        elif recommended_bet.upper() == "AWAY":
            prob = stat_analysis.away_win_probability
        else:
            prob = stat_analysis.draw_probability
        
        # Calculate fair odds (1/probability)
        fair_odds = 1 / prob if prob > 0 else 0
        
        # If fair odds > 2.0 and probability reasonable, it's a value bet
        if fair_odds > 2.2 and prob > 0.35:
            return "💎 VALUE BET"
        
        return ""
    
    def _calculate_kelly_stake(self, win_probability: float, odds: float) -> float:
        """
        Calculate Kelly Criterion stake percentage.
        """
        kelly_fraction = self.config.automation.kelly_fraction
        
        b = odds - 1
        p = win_probability
        q = 1 - p
        
        kelly = (b * p - q) / b if b > 0 else 0
        kelly *= kelly_fraction
        
        return max(0, kelly)
    
    def _determine_recommended_bet(
        self,
        triangulation: TriangulationResult,
        stat_analysis
    ) -> str:
        """
        Determine recommended bet based on triangulation result.
        """
        # Skip if trap detected
        if "🚫" in triangulation.confidence_level.value or "SKIP" in triangulation.confidence_level.value:
            return "skip"
        
        # Low confidence - no bet
        if triangulation.confidence_score < self.config.prediction.min_confidence:
            return "skip"
        
        # Use statistical recommendation
        return stat_analysis.recommendation.split()[0].lower() if stat_analysis.recommendation else "home"
    
    def generate_daily_picks(
        self,
        matches: List[Tuple[Match, MatchStats, List[Dict], List[Dict]]]
    ) -> DailyPicks:
        """
        Generate daily top picks from multiple matches.
        """
        predictions = []
        
        for match, stats, home_news, away_news in matches:
            try:
                pred = self.predict_match(match, stats, home_news, away_news)
                predictions.append(pred)
            except Exception as e:
                print(f"Error predicting {match.home_team} vs {match.away_team}: {e}")
        
        # Filter by threshold
        threshold = self.config.automation.threshold
        filtered_picks = [
            p for p in predictions 
            if p.confidence_score >= threshold and p.recommended_bet != "skip"
        ]
        
        # Sort by confidence
        filtered_picks.sort(key=lambda x: x.confidence_score, reverse=True)
        
        # Get top 10
        top_picks = filtered_picks[:10]
        
        # Get jackpot picks (highest confidence)
        jackpot_picks = [
            p for p in top_picks 
            if "JACKPOT" in p.confidence_level or "HIGH" in p.confidence_level
        ]
        
        # Calculate total confidence
        total_conf = sum(p.confidence_score for p in top_picks) / len(top_picks) if top_picks else 0
        
        return DailyPicks(
            date=datetime.now(),
            picks=top_picks,
            total_confidence=total_conf,
            jackpot_picks=jackpot_picks
        )
    
    def format_prediction_message(self, prediction: Prediction) -> str:
        """
        Format prediction as a Telegram message.
        """
        match = prediction.match
        
        message = f"""
🏆 *MATCH PREDICTION*

{match.home_team} vs {match.away_team}
📅 {match.kickoff_time.strftime('%d %b %Y, %H:%M')}
🏟️ {match.league}

━━━━━━━━━━━━━━━━━━━━━━━━━

📊 *POISONSON ANALYSIS*
• Home xG: {prediction.home_win_probability:.1%}
• Draw: {prediction.draw_probability:.1%}
• Away xG: {prediction.away_win_probability:.1%}

🎯 *PREDICTED SCORE:* {prediction.expected_score}

{prediction.confidence_level}

💰 *RECOMMENDED:* {prediction.recommended_bet.upper()}
📈 *CONFIDENCE:* {prediction.confidence_score:.0f}%

⚡ *ATTACK POWER*
• Home: {prediction.home_attack_power:.2f}
• Away: {prediction.away_attack_power:.2f}

{prediction.value_bet}

⚠️ *RISK:* {prediction.risk_level}
"""
        
        return message
    
    def format_daily_picks_message(self, picks: DailyPicks) -> str:
        """
        Format daily picks as a Telegram message.
        """
        message = f"""
🌟 *THE ORACLE 2026 - DAILY PICKS* 🌟
📅 {picks.date.strftime('%d %B %Y')}
📊 *Total Picks:* {len(picks.picks)}
🎯 *Avg Confidence:* {picks.total_confidence:.1f}%

━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        if picks.jackpot_picks:
            message += "\n🔥 *JACKPOT PICKS*\n"
            for i, pick in enumerate(picks.jackpot_picks, 1):
                message += f"{i}. {pick.match.home_team} vs {pick.match.away_team}\n"
                message += f"   🎯 Bet: {pick.recommended_bet.upper()} | 📈 {pick.confidence_score:.0f}%\n\n"
        
        message += "\n📋 *ALL PICKS*\n"
        for i, pick in enumerate(picks.picks, 1):
            emoji = "✅" if pick.confidence_score >= 85 else "⚠️"
            message += f"{emoji} {i}. {pick.match.home_team} vs {pick.match.away_team}\n"
            message += f"   🎯 {pick.recommended_bet.upper()} ({pick.expected_score}) | 📈 {pick.confidence_score:.0f}%\n"
        
        message += """
━━━━━━━━━━━━━━━━━━━━━━━━━

💎 *Kelly Criterion advised for stake sizing*
⚠️ *Bet responsibly - no guarantee of wins*
"""
        
        return message


# Example usage
if __name__ == "__main__":
    engine = PredictionEngine()
    
    # Create sample match with real data
    match = Match(
        match_id="12345",
        home_team="Manchester United",
        away_team="Aston Villa",
        league="Premier League",
        kickoff_time=datetime.now() + timedelta(days=1),
        venue="Old Trafford, Manchester",
        referee="Michael Oliver",
        home_position=6,
        away_position=11,
        # Season stats for attack/defense power
        home_goals_season=45.0,
        away_goals_season=32.0,
        home_conceded_season=28.0,
        away_conceded_season=35.0,
        home_matches_played=25,
        away_matches_played=25,
        home_form="WWWDD",
        away_form="LLDWW"
    )
    
    # Generate prediction
    prediction = engine.predict_match(match)
    
    print(f"Match: {match.home_team} vs {match.away_team}")
    print(f"Predicted Score: {prediction.expected_score}")
    print(f"Confidence: {prediction.confidence_score:.1f}%")
    print(f"Level: {prediction.confidence_level}")
    print(f"Recommended Bet: {prediction.recommended_bet}")
    print(f"Attack Power - Home: {prediction.home_attack_power:.2f}, Away: {prediction.away_attack_power:.2f}")
    print(f"Defense Power - Home: {prediction.home_defense_power:.2f}, Away: {prediction.away_defense_power:.2f}")
    print(f"Value Bet: {prediction.value_bet}")
    print(f"Risk: {prediction.risk_level}")
