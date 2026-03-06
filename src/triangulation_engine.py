"""
Triangulation Engine - Core of The Oracle 2026
Implements the Triangulasi Data methodology for validation.

Author: Rizki Wahyudi, S.Kom
Version: 2.0.0
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

from .statistical_engine import StatisticalAnalysis
from .human_context_engine import HumanContextAnalysis
from .market_intelligence_engine import MarketIntelligenceAnalysis


class ConfidenceLevel(Enum):
    """Confidence levels for predictions"""
    JACKPOT = "🔥 HIGH CONFIDENCE - JACKPOT POTENTIAL"
    HIGH = "HIGH CONFIDENCE"
    MEDIUM = "⚠️ MEDIUM RISK - CAUTION"
    LOW = "LOW CONFIDENCE"
    SKIP = "🚫 SKIP - POTENTIAL TRAP"


@dataclass
class TriangulationResult:
    """Result of triangulation analysis"""
    confidence_level: ConfidenceLevel
    confidence_score: float
    statistical_support: str  # 'supported', 'neutral', 'contradicted'
    sentiment_support: str  # 'positive', 'neutral', 'negative'
    market_support: str  # 'stable', 'anomaly', 'trap'
    final_recommendation: str
    winning_probability: float
    risk_assessment: str
    key_factors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class TriangulationEngine:
    """
    Triangulation Engine that combines all three pillars:
    1. Statistical Analysis
    2. Human Context
    3. Market Intelligence
    
    Uses the Triangulasi Data methodology to validate predictions.
    """
    
    # Thresholds
    HIGH_CONFIDENCE_THRESHOLD = 85
    MEDIUM_CONFIDENCE_THRESHOLD = 70
    LOW_CONFIDENCE_THRESHOLD = 50
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.triangulation_rules = self.config.get('triangulation_logic', {}).get('rules', [])
    
    def analyze(
        self,
        statistical: StatisticalAnalysis,
        human_context: HumanContextAnalysis,
        market: MarketIntelligenceAnalysis
    ) -> TriangulationResult:
        """
        Perform triangulation analysis combining all three pillars.
        
        Rules:
        - Statistik Mendukung AND Sentimen Positif AND Pasar Stabil = HIGH CONFIDENCE
        - Statistik Mendukung BUT Pasar Anomali = SKIP (TRAP)
        - Statistik Mendukung BUT Sentimen Negatif = MEDIUM RISK
        """
        
        # Determine each pillar's support
        stat_support = self._evaluate_statistical_support(statistical)
        sentiment_support = self._evaluate_sentiment_support(human_context)
        market_support = self._evaluate_market_support(market)
        
        # Calculate overall confidence score
        confidence_score = self._calculate_triangulation_score(
            statistical, human_context, market
        )
        
        # Determine confidence level based on rules
        confidence_level, recommendation = self._apply_triangulation_rules(
            stat_support, sentiment_support, market_support, confidence_score
        )
        
        # Calculate winning probability
        winning_prob = self._calculate_winning_probability(
            statistical, human_context, market
        )
        
        # Identify key factors
        key_factors = self._identify_key_factors(
            statistical, human_context, market
        )
        
        # Generate warnings
        warnings = self._generate_warnings(
            statistical, human_context, market
        )
        
        # Risk assessment
        risk_assessment = self._assess_risk(
            stat_support, sentiment_support, market_support
        )
        
        return TriangulationResult(
            confidence_level=confidence_level,
            confidence_score=confidence_score,
            statistical_support=stat_support,
            sentiment_support=sentiment_support,
            market_support=market_support,
            final_recommendation=recommendation,
            winning_probability=winning_prob,
            risk_assessment=risk_assessment,
            key_factors=key_factors,
            warnings=warnings
        )
    
    def _evaluate_statistical_support(self, stat: StatisticalAnalysis) -> str:
        """
        Evaluate statistical support level.
        """
        # High support: strong probability for one outcome (>50%)
        # Neutral: probabilities are balanced
        # Contradicted: statistical indicators conflict
        
        max_prob = max(stat.home_win_probability, stat.draw_probability, stat.away_win_probability)
        
        if max_prob > 0.55:
            return "supported"
        elif max_prob < 0.40:
            return "contradicted"
        else:
            return "neutral"
    
    def _evaluate_sentiment_support(self, human: HumanContextAnalysis) -> str:
        """
        Evaluate human context/sentiment support level.
        """
        sentiment = human.sentiment_score
        
        if sentiment > 0.6:
            return "positive"
        elif sentiment < 0.4:
            return "negative"
        else:
            return "neutral"
    
    def _evaluate_market_support(self, market: MarketIntelligenceAnalysis) -> str:
        """
        Evaluate market support level.
        """
        if market.trap_indicator:
            return "trap"
        
        if market.odds_movement.suspicious_movement:
            return "anomaly"
        
        if market.market_sentiment == "neutral":
            return "stable"
        
        return "stable"
    
    def _calculate_triangulation_score(
        self,
        stat: StatisticalAnalysis,
        human: HumanContextAnalysis,
        market: MarketIntelligenceAnalysis
    ) -> float:
        """
        Calculate overall triangulation score.
        """
        # Weighted average of all three pillars
        stat_weight = 0.40
        human_weight = 0.30
        market_weight = 0.30
        
        # Normalize individual scores to 0-100
        stat_score = stat.confidence_score
        human_score = human.confidence_score
        market_score = market.confidence_score
        
        # Apply modifiers based on agreement
        stat_support = self._evaluate_statistical_support(stat)
        sentiment = self._evaluate_sentiment_support(human)
        market_supp = self._evaluate_market_support(market)
        
        # Calculate base score
        base_score = (
            stat_score * stat_weight +
            human_score * human_weight +
            market_score * market_weight
        )
        
        # Apply agreement bonus/penalty
        agreement_bonus = 0
        
        # Statistical and sentiment agree
        if stat_support == "supported" and sentiment == "positive":
            agreement_bonus += 10
        
        # Statistical and market agree
        if stat_support == "supported" and market_supp == "stable":
            agreement_bonus += 10
        
        # All three agree
        if stat_support == "supported" and sentiment == "positive" and market_supp == "stable":
            agreement_bonus += 15
        
        # Penalties
        if market_supp == "trap":
            agreement_bonus -= 30
        elif market_supp == "anomaly":
            agreement_bonus -= 15
        
        if sentiment == "negative":
            agreement_bonus -= 10
        
        final_score = base_score + agreement_bonus
        return max(0, min(100, final_score))
    
    def _apply_triangulation_rules(
        self,
        stat_support: str,
        sentiment_support: str,
        market_support: str,
        confidence_score: float
    ) -> Tuple[ConfidenceLevel, str]:
        """
        Apply the triangulation rules to determine confidence level.
        
        Rules from JSON:
        - Statistik Mendukung AND Sentimen Positif AND Pasar Stabil = 🔥 HIGH CONFIDENCE
        - Statistik Mendukung BUT Pasar Anomali = 🚫 SKIP
        - Statistik Mendukung BUT Sentimen Negatif = ⚠️ MEDIUM RISK
        """
        
        # Rule 1: HIGH CONFIDENCE (Jackpot Potential)
        if (stat_support == "supported" and 
            sentiment_support == "positive" and 
            market_support == "stable"):
            return (
                ConfidenceLevel.JACKPOT,
                "🔥 HIGH CONFIDENCE - JACKPOT POTENTIAL - All three pillars align perfectly!"
            )
        
        # Rule 2: SKIP (Potential Trap)
        if stat_support == "supported" and market_support in ["trap", "anomaly"]:
            return (
                ConfidenceLevel.SKIP,
                "🚫 SKIP - POTENTIAL TRAP detected. Statistics support the bet but market shows anomaly."
            )
        
        # Rule 3: MEDIUM RISK (Caution)
        if stat_support == "supported" and sentiment_support == "negative":
            return (
                ConfidenceLevel.MEDIUM,
                "⚠️ MEDIUM RISK - CAUTION. Statistics support but negative sentiment detected."
            )
        
        # Additional rules based on confidence score
        if confidence_score >= self.HIGH_CONFIDENCE_THRESHOLD:
            return (
                ConfidenceLevel.HIGH,
                f"HIGH CONFIDENCE ({confidence_score:.0f}%) - Strong triangulation signal."
            )
        
        if confidence_score >= self.MEDIUM_CONFIDENCE_THRESHOLD:
            return (
                ConfidenceLevel.MEDIUM,
                f"MEDIUM RISK ({confidence_score:.0f}%) - Partial alignment of factors."
            )
        
        return (
            ConfidenceLevel.LOW,
            f"LOW CONFIDENCE ({confidence_score:.0f}%) - Insufficient alignment for recommendation."
        )
    
    def _calculate_winning_probability(
        self,
        stat: StatisticalAnalysis,
        human: HumanContextAnalysis,
        market: MarketIntelligenceAnalysis
    ) -> float:
        """
        Calculate probability of winning based on triangulation.
        """
        # Base probability from statistics
        base_prob = max(stat.home_win_probability, stat.draw_probability, stat.away_win_probability)
        
        # Adjustments
        sentiment = human.sentiment_score
        fatigue = human.fatigue_factor
        market_anomaly = market.trap_indicator
        
        # Positive sentiment boosts probability
        if sentiment > 0.6:
            base_prob *= 1.1
        elif sentiment < 0.4:
            base_prob *= 0.9
        
        # High fatigue reduces probability
        if fatigue > 0.7:
            base_prob *= 0.85
        
        # Market trap significantly reduces probability
        if market_anomaly:
            base_prob *= 0.5
        
        return min(0.95, max(0.05, base_prob))
    
    def _identify_key_factors(
        self,
        stat: StatisticalAnalysis,
        human: HumanContextAnalysis,
        market: MarketIntelligenceAnalysis
    ) -> List[str]:
        """
        Identify key factors driving the prediction.
        """
        factors = []
        
        # Statistical factors
        if stat.h2h_dominance != "balanced":
            factors.append(f"H2H: {stat.h2h_dominance.title()} team has historical dominance")
        
        if stat.form_advantage != "balanced":
            factors.append(f"Form: {stat.form_advantage.title()} team in better form")
        
        if stat.home_advantage_factor > 1.1:
            factors.append("Strong home advantage detected")
        
        # Human context factors
        if human.injury_impact > 0.3:
            factors.append(f"Injury impact: {human.injury_impact:.0%} - {len(human.risk_factors)} risk factors")
        
        if human.motivation_boost > 0.6:
            factors.append("High motivation detected")
        
        if human.fatigue_factor > 0.6:
            factors.append("Fatigue concerns")
        
        # Market factors
        if market.odds_movement.movement_percentage > 10:
            factors.append(f"Significant odds movement: {market.odds_movement.movement_percentage:.1f}%")
        
        if market.smart_money.steam_move_detected:
            factors.append("Sharp money movement detected")
        
        return factors
    
    def _generate_warnings(
        self,
        stat: StatisticalAnalysis,
        human: HumanContextAnalysis,
        market: MarketIntelligenceAnalysis
    ) -> List[str]:
        """
        Generate warnings based on negative factors.
        """
        warnings = []
        
        # Market warnings
        if market.trap_indicator:
            warnings.append(f"🚫 TRAP ALERT: {market.trap_reason}")
        
        if market.odds_movement.suspicious_movement:
            warnings.append(f"⚠️ Suspicious odds movement: {market.odds_movement.movement_direction}")
        
        # Human context warnings
        for risk in human.risk_factors:
            warnings.append(f"⚠️ {risk}")
        
        # Fatigue warnings
        if human.fatigue_factor > 0.7:
            warnings.append("⚠️ High fatigue may impact performance")
        
        # Statistical warnings
        if stat.confidence_score < 60:
            warnings.append("⚠️ Low statistical confidence")
        
        return warnings
    
    def _assess_risk(
        self,
        stat_support: str,
        sentiment_support: str,
        market_support: str
    ) -> str:
        """
        Assess overall risk level.
        """
        risk_score = 0
        
        # Statistical risk
        if stat_support == "contradicted":
            risk_score += 3
        elif stat_support == "neutral":
            risk_score += 1
        
        # Sentiment risk
        if sentiment_support == "negative":
            risk_score += 3
        elif sentiment_support == "neutral":
            risk_score += 1
        
        # Market risk
        if market_support == "trap":
            risk_score += 5
        elif market_support == "anomaly":
            risk_score += 3
        
        # Risk assessment
        if risk_score >= 8:
            return "HIGH RISK - Multiple negative factors"
        elif risk_score >= 5:
            return "MEDIUM RISK - Some concerning factors"
        elif risk_score >= 2:
            return "LOW RISK - Minor concerns"
        else:
            return "MINIMAL RISK - All factors align"


# Example usage
if __name__ == "__main__":
    from .statistical_engine import StatisticalAnalysis, MatchStats
    from .human_context_engine import HumanContextAnalysis, LineupAnalysis, ManagerMatchup
    from .market_intelligence_engine import MarketIntelligenceAnalysis, OddsMovement, SmartMoneyAnalysis, RefereeProfile, WeatherData
    
    # Create sample analyses
    stat_analysis = StatisticalAnalysis(
        home_win_probability=0.55,
        draw_probability=0.25,
        away_win_probability=0.20,
        expected_home_goals=2.1,
        expected_away_goals=1.2,
        score_probabilities={"2-1": 0.15, "2-0": 0.12},
        confidence_score=80,
        home_advantage_factor=1.1,
        h2h_dominance="home",
        form_advantage="home",
        league_position_impact=0.3
    )
    
    human_analysis = HumanContextAnalysis(
        sentiment_score=0.65,
        sentiment_label="positive",
        injury_impact=0.2,
        lineup_analysis=LineupAnalysis(is_confirmed=True),
        manager_matchup=ManagerMatchup(home_manager="Pep Guardiola", away_manager="Jurgen Klopp"),
        motivation_boost=0.7,
        fatigue_factor=0.4,
        confidence_score=75,
        risk_factors=[],
        recommendation="FAVORABLE"
    )
    
    # Create market analysis with proper nested objects
    odds_movement = OddsMovement(
        current_odds=None,
        opening_odds=None,
        movement_percentage=5.0,
        suspicious_movement=False,
        movement_direction="stable"
    )
    smart_money = SmartMoneyAnalysis(
        betting_percentage_home=45,
        betting_percentage_away=30,
        betting_percentage_draw=25,
        sharp_money_direction="home",
        public_money_direction="home",
        steam_move_detected=False,
        reverse_line_movement=False
    )
    referee = RefereeProfile(name="Michael Oliver", matches_officiated=50)
    weather = WeatherData(temperature=18, condition="clear", wind_speed=10, humidity=55, pitch_condition="good")
    
    market_analysis = MarketIntelligenceAnalysis(
        odds_movement=odds_movement,
        smart_money=smart_money,
        referee_profile=referee,
        weather=weather,
        market_sentiment="bullish",
        trap_indicator=False,
        trap_reason="",
        confidence_score=70,
        recommendation="STRONG"
    )
    
    # Run triangulation
    engine = TriangulationEngine()
    result = engine.analyze(stat_analysis, human_analysis, market_analysis)
    
    print(f"Confidence Level: {result.confidence_level.value}")
    print(f"Confidence Score: {result.confidence_score:.1f}%")
    print(f"Recommendation: {result.final_recommendation}")
    print(f"Winning Probability: {result.winning_probability:.1%}")
    print(f"Risk Assessment: {result.risk_assessment}")
    print(f"Key Factors: {result.key_factors}")
    print(f"Warnings: {result.warnings}")
