"""
Statistical Engine - Pillar 1 of The Oracle 2026
Implements Poisson Distribution, xG Analysis, H2H, and more.

Author: Rizki Wahyudi, S.Kom
Version: 2.0.0
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class MatchStats:
    """Statistics for a single match"""
    home_team: str
    away_team: str
    home_xg: float = 0.0
    away_xg: float = 0.0
    home_avg_goals: float = 0.0
    away_avg_goals: float = 0.0
    home_goals_scored_last5: List[int] = field(default_factory=list)
    away_goals_scored_last5: List[int] = field(default_factory=list)
    home_goals_conceded_last5: List[int] = field(default_factory=list)
    away_goals_conceded_last5: List[int] = field(default_factory=list)
    home_wins: int = 0
    home_draws: int = 0
    home_losses: int = 0
    away_wins: int = 0
    away_draws: int = 0
    away_losses: int = 0
    h2h_home_wins: int = 0
    h2h_away_wins: int = 0
    h2h_draws: int = 0
    h2h_matches: int = 0
    home_position: int = 0
    away_position: int = 0
    home_form_score: float = 0.0
    away_form_score: float = 0.0
    home_advantage: float = 0.0
    # New fields for real calculations
    home_goals_scored_season: float = 0.0
    away_goals_scored_season: float = 0.0
    home_goals_conceded_season: float = 0.0
    away_goals_conceded_season: float = 0.0
    home_matches_played: int = 0
    away_matches_played: int = 0


@dataclass
class StatisticalAnalysis:
    """Result of statistical analysis"""
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    expected_home_goals: float
    expected_away_goals: float
    score_probabilities: Dict[str, float]
    confidence_score: float
    home_advantage_factor: float
    h2h_dominance: str
    form_advantage: str
    league_position_impact: float
    home_attack_power: float = 0.0
    away_attack_power: float = 0.0
    home_defense_power: float = 0.0
    away_defense_power: float = 0.0
    home_form: str = "WWWDD"
    away_form: str = "LLDWW"
    predicted_score: str = "1-1"
    recommendation: str = "NEUTRAL"


class StatisticalEngine:
    """
    Core statistical analysis engine using Poisson Distribution
    """
    
    def __init__(self):
        self.poisson = stats.poisson
        self.max_goals = 6
    
    def calculate_poisson_probability(self, lambda_val: float, goals: int) -> float:
        """Calculate probability using Poisson distribution"""
        return self.poisson.pmf(goals, lambda_val)
    
    def calculate_win_probabilities(self, expected_home: float, expected_away: float) -> Tuple[float, float, float]:
        """Calculate win/draw/loss probabilities from expected goals"""
        home_win = 0.0
        draw = 0.0
        away_win = 0.0
        
        for home_goals in range(self.max_goals + 1):
            for away_goals in range(self.max_goals + 1):
                home_prob = self.calculate_poisson_probability(expected_home, home_goals)
                away_prob = self.calculate_poisson_probability(expected_away, away_goals)
                combined = home_prob * away_prob
                
                if home_goals > away_goals:
                    home_win += combined
                elif home_goals == away_goals:
                    draw += combined
                else:
                    away_win += combined
        
        return home_win, draw, away_win
    
    def calculate_poisson_score(
        self,
        home_avg_goals: float,
        away_avg_goals: float,
        home_attack: float,
        away_attack: float,
        home_defense: float,
        away_defense: float,
        league_avg_goals: float = 2.5
    ) -> Tuple[str, float, Dict[str, float], float, float]:
        """Calculate most likely score using Poisson Distribution"""
        home_xg = (home_attack * away_defense * 1.1) / league_avg_goals
        away_xg = (away_attack * home_defense) / league_avg_goals
        
        home_xg = max(0.3, home_xg)
        away_xg = max(0.3, away_xg)
        
        score_probs = {}
        
        for home_goals in range(self.max_goals + 1):
            for away_goals in range(self.max_goals + 1):
                home_prob = self.calculate_poisson_probability(home_xg, home_goals)
                away_prob = self.calculate_poisson_probability(away_xg, away_goals)
                combined_prob = home_prob * away_prob
                score = f"{home_goals}-{away_goals}"
                score_probs[score] = combined_prob
        
        total = sum(score_probs.values())
        if total > 0:
            score_probs = {k: v/total for k, v in score_probs.items()}
        
        top_score = max(score_probs.items(), key=lambda x: x[1])
        
        sorted_scores = sorted(score_probs.items(), key=lambda x: x[1], reverse=True)
        top3_prob = sum([s[1] for s in sorted_scores[:3]])
        
        return top_score[0], top3_prob, score_probs, home_xg, away_xg
    
    def calculate_attack_defense_power(
        self,
        goals_scored: float,
        goals_conceded: float,
        matches_played: int,
        league_avg_goals: float,
        is_home: bool = True
    ) -> Tuple[float, float]:
        """Calculate Attack and Defense Power"""
        if matches_played == 0:
            return 1.0, 1.0
        
        goals_per_match = goals_scored / matches_played
        conceded_per_match = goals_conceded / matches_played
        
        attack_power = goals_per_match / league_avg_goals
        defense_power = conceded_per_match / league_avg_goals
        
        if is_home:
            attack_power *= 1.1
            defense_power *= 0.95
        
        return attack_power, defense_power
    
    def calculate_form_score(self, form: str) -> float:
        """Calculate form score from form string"""
        if not form:
            return 0.5
        
        score = 0
        for char in form.upper():
            if char == 'W':
                score += 3
            elif char == 'D':
                score += 1
        
        return min(1.0, score / 15.0)
    
    def analyze_h2h_dominance(self, h2h_home_wins: int, h2h_away_wins: int, h2h_draws: int, total_matches: int) -> Tuple[str, float]:
        """Analyze head-to-head dominance"""
        if total_matches == 0:
            return 'balanced', 0.5
        
        home_win_rate = h2h_home_wins / total_matches
        away_win_rate = h2h_away_wins / total_matches
        
        if home_win_rate > away_win_rate + 0.15:
            return 'home', home_win_rate
        elif away_win_rate > home_win_rate + 0.15:
            return 'away', away_win_rate
        else:
            return 'balanced', 0.5
    
    def calculate_home_advantage(self, home_avg_goals: float, away_avg_goals: float, league_avg_goals: float) -> float:
        """Calculate home advantage factor"""
        if league_avg_goals == 0:
            return 1.0
        
        home_advantage = (home_avg_goals / league_avg_goals)
        away_factor = (league_avg_goals / away_avg_goals) if away_avg_goals > 0 else 1.0
        
        return (home_advantage + away_factor) / 2
    
    def calculate_position_impact(self, home_position: int, away_position: int, league_size: int = 20) -> float:
        """Calculate position impact"""
        if home_position == 0 or away_position == 0:
            return 0.0
        
        home_strength = 1 - ((home_position - 1) / (league_size - 1))
        away_strength = 1 - ((away_position - 1) / (league_size - 1))
        
        return home_strength - away_strength
    
    def determine_recommendation(self, home_prob: float, away_prob: float, draw_prob: float, home_form_score: float, away_form_score: float, confidence: float) -> str:
        """Determine bet recommendation"""
        
        max_prob = max(home_prob, away_prob, draw_prob)
        
        if confidence >= 80 and max_prob >= 0.55:
            if home_prob == max_prob and home_prob > 0.55:
                return "HOME WIN"
            elif away_prob == max_prob and away_prob > 0.55:
                return "AWAY WIN"
            elif draw_prob == max_prob and draw_prob > 0.35:
                return "DRAW"
        
        if confidence >= 65:
            if home_form_score > away_form_score + 0.2 and home_prob > 0.40:
                return "HOME WIN"
            elif away_form_score > home_form_score + 0.2 and away_prob > 0.40:
                return "AWAY WIN"
        
        if home_prob >= away_prob and home_prob >= draw_prob:
            return "HOME WIN"
        elif away_prob >= home_prob and away_prob >= draw_prob:
            return "AWAY WIN"
        else:
            return "DRAW"
    
    def analyze(self, match_stats: MatchStats, league_avg_goals: float = 2.5) -> StatisticalAnalysis:
        """Perform comprehensive statistical analysis"""
        
        home_attack, home_defense = self.calculate_attack_defense_power(
            match_stats.home_goals_scored_season,
            match_stats.home_goals_conceded_season,
            match_stats.home_matches_played,
            league_avg_goals,
            is_home=True
        )
        
        away_attack, away_defense = self.calculate_attack_defense_power(
            match_stats.away_goals_scored_season,
            match_stats.away_goals_conceded_season,
            match_stats.away_matches_played,
            league_avg_goals,
            is_home=False
        )
        
        home_form = match_stats.home_form_score if isinstance(match_stats.home_form_score, str) else "WWWDD"
        away_form = match_stats.away_form_score if isinstance(match_stats.away_form_score, str) else "LLDWW"
        
        home_form_val = self.calculate_form_score(home_form)
        away_form_val = self.calculate_form_score(away_form)
        
        predicted_score, top3_prob, score_probs, exp_home, exp_away = self.calculate_poisson_score(
            match_stats.home_avg_goals,
            match_stats.away_avg_goals,
            home_attack,
            away_attack,
            home_defense,
            away_defense,
            league_avg_goals
        )
        
        home_win, draw, away_win = self.calculate_win_probabilities(exp_home, exp_away)
        
        h2h_dominance, h2h_strength = self.analyze_h2h_dominance(
            match_stats.h2h_home_wins,
            match_stats.h2h_away_wins,
            match_stats.h2h_draws,
            match_stats.h2h_matches
        )
        
        if home_form_val > away_form_val + 0.15:
            form_advantage = 'home'
        elif away_form_val > home_form_val + 0.15:
            form_advantage = 'away'
        else:
            form_advantage = 'balanced'
        
        position_impact = self.calculate_position_impact(
            match_stats.home_position,
            match_stats.away_position
        )
        
        confidence_score = self._calculate_confidence(
            match_stats, home_attack, away_attack, home_defense, away_defense, league_avg_goals
        )
        
        recommendation = self.determine_recommendation(
            home_win, away_win, draw,
            home_form_val, away_form_val,
            confidence_score
        )
        
        return StatisticalAnalysis(
            home_win_probability=home_win,
            draw_probability=draw,
            away_win_probability=away_win,
            expected_home_goals=exp_home,
            expected_away_goals=exp_away,
            score_probabilities=score_probs,
            confidence_score=confidence_score,
            home_advantage_factor=self.calculate_home_advantage(match_stats.home_avg_goals, match_stats.away_avg_goals, league_avg_goals),
            h2h_dominance=h2h_dominance,
            form_advantage=form_advantage,
            league_position_impact=position_impact,
            home_attack_power=home_attack,
            away_attack_power=away_attack,
            home_defense_power=home_defense,
            away_defense_power=away_defense,
            home_form=home_form,
            away_form=away_form,
            predicted_score=predicted_score,
            recommendation=recommendation
        )
    
    def _calculate_confidence(self, match_stats: MatchStats, home_attack: float, away_attack: float, home_defense: float, away_defense: float, league_avg: float) -> float:
        """Calculate dynamic confidence score"""
        confidence = 40.0
        
        if match_stats.home_matches_played >= 20:
            confidence += 10
        if match_stats.away_matches_played >= 20:
            confidence += 10
        
        attack_diff = abs(home_attack - away_attack)
        defense_diff = abs(home_defense - away_defense)
        
        if attack_diff > 0.3 or defense_diff > 0.3:
            confidence += 20
        elif attack_diff > 0.2 or defense_diff > 0.2:
            confidence += 15
        elif attack_diff > 0.1 or defense_diff > 0.1:
            confidence += 10
        
        if match_stats.home_form_score and match_stats.away_form_score:
            confidence += 10
        
        if match_stats.h2h_matches >= 5:
            confidence += 10
        
        if match_stats.home_position > 0 and match_stats.away_position > 0:
            pos_diff = abs(match_stats.home_position - match_stats.away_position)
            if pos_diff > 5:
                confidence += 10
            elif pos_diff > 3:
                confidence += 5
        
        return min(95.0, max(30.0, confidence))
    
    def get_top_predictions(self, analysis: StatisticalAnalysis, top_n: int = 5) -> List[Tuple[str, float]]:
        """Get top N most likely score predictions"""
        sorted_scores = sorted(analysis.score_probabilities.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:top_n]


if __name__ == "__main__":
    match = MatchStats(
        home_team="Manchester United",
        away_team="Aston Villa",
        home_avg_goals=1.9,
        away_avg_goals=1.4,
        home_position=6,
        away_position=11,
        h2h_home_wins=8,
        h2h_away_wins=3,
        h2h_draws=4,
        h2h_matches=15,
        home_goals_scored_season=45.0,
        away_goals_scored_season=32.0,
        home_goals_conceded_season=28.0,
        away_goals_conceded_season=35.0,
        home_matches_played=25,
        away_matches_played=25,
        home_form_score="WWWDD",
        away_form_score="LLDWW"
    )
    
    engine = StatisticalEngine()
    result = engine.analyze(match, league_avg_goals=2.5)
    
    print(f"Match: {match.home_team} vs {match.away_team}")
    print(f"Predicted Score: {result.predicted_score}")
    print(f"Win Probs: Home {result.home_win_probability:.2%}, Draw {result.draw_probability:.2%}, Away {result.away_win_probability:.2%}")
    print(f"Attack Power: Home {result.home_attack_power:.2f}, Away {result.away_attack_power:.2f}")
    print(f"Confidence: {result.confidence_score:.1f}%")
    print(f"Recommendation: {result.recommendation}")
