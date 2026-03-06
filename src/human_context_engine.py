"""
Human Context Engine - Pillar 2 of The Oracle 2026
Implements NLP Sentiment, Line-up Analysis, Manager Matchup, and more.

Author: Rizki Wahyudi, S.Kom
Version: 2.0.0
"""

import re
import json
import requests
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import quote


@dataclass
class TeamNews:
    """News and sentiment data for a team"""
    team_name: str
    recent_news: List[Dict] = field(default_factory=list)
    sentiment_score: float = 0.5  # 0-1 scale, 0.5 = neutral
    injury_count: int = 0
    key_players_out: List[str] = field(default_factory=list)
    crisis_level: str = "none"  # none, low, medium, high
    motivation_factors: List[str] = field(default_factory=list)
    fatigue_index: float = 0.5  # 0-1 scale, higher = more fatigued


@dataclass
class LineupAnalysis:
    """Line-up analysis result"""
    is_confirmed: bool = False
    formation: str = "unknown"
    key_players_missing: List[str] = field(default_factory=list)
    formation_strength: float = 0.5  # 0-1 scale
    lineup_quality_score: float = 0.5  # 0-1 scale
    expected_changes: int = 0


@dataclass
class ManagerMatchup:
    """Manager vs Manager historical data"""
    home_manager: str
    away_manager: str
    home_manager_wins: int = 0
    away_manager_wins: int = 0
    draws: int = 0
    total_matches: int = 0
    home_manager_form: float = 0.5
    away_manager_form: float = 0.5


@dataclass
class HumanContextAnalysis:
    """Result of human context analysis"""
    sentiment_score: float  # 0-1 scale
    sentiment_label: str  # positive, neutral, negative
    injury_impact: float  # 0-1 scale (higher = more impact)
    lineup_analysis: LineupAnalysis
    manager_matchup: ManagerMatchup
    motivation_boost: float  # 0-1 scale
    fatigue_factor: float  # 0-1 scale (higher = more fatigued)
    confidence_score: float
    risk_factors: List[str] = field(default_factory=list)
    recommendation: str = ""


class HumanContextEngine:
    """
    Human context analysis engine using NLP and contextual data.
    Analyzes news sentiment, line-ups, manager matchups, and motivation factors.
    """
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.news_sources = [
            "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en",
        ]
        # Keywords for sentiment analysis
        self.positive_keywords = [
            "win", "victory", "success", "impressive", "dominant", "strong",
            "return", "recovered", "fit", "ready", "motivated", "confident",
            "upgrade", "boost", "positive", "good", "great", "excellent"
        ]
        self.negative_keywords = [
            "injury", "lose", "loss", "defeat", "crisis", "problem",
            "suspended", "doubtful", "out", "sick", "fatigue", "tired",
            "controversy", "conflict", "bench", "missing", "bad", "poor"
        ]
        self.crisis_keywords = [
            "crisis", "scandal", "fired", "resign", "emergency", "major injury",
            "death", "tragedy", "lawsuit", "investigation"
        ]
    
    def fetch_news(self, team_name: str, days: int = 7) -> List[Dict]:
        """
        Fetch recent news for a team using Google News RSS.
        """
        news_items = []
        
        for source in self.news_sources:
            try:
                url = source.format(query=quote(team_name + " football"))
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'xml')
                    items = soup.find_all('item')[:10]  # Get top 10 news
                    
                    for item in items:
                        title = item.find('title').get_text() if item.find('title') else ""
                        description = item.find('description').get_text() if item.find('description') else ""
                        pub_date = item.find('pubDate').get_text() if item.find('pubDate') else ""
                        
                        news_items.append({
                            'title': title,
                            'description': description,
                            'date': pub_date,
                            'source': 'Google News'
                        })
            except Exception as e:
                print(f"Error fetching news for {team_name}: {e}")
        
        return news_items
    
    def analyze_sentiment(self, news_items: List[Dict]) -> Tuple[float, str]:
        """
        Analyze sentiment from news items.
        Returns sentiment score (0-1) and label (positive/neutral/negative).
        """
        if not news_items:
            return 0.5, "neutral"
        
        positive_count = 0
        negative_count = 0
        total = 0
        
        for item in news_items:
            text = (item.get('title', '') + ' ' + item.get('description', '')).lower()
            
            for keyword in self.positive_keywords:
                if keyword in text:
                    positive_count += 1
                    total += 1
            
            for keyword in self.negative_keywords:
                if keyword in text:
                    negative_count += 1
                    total += 1
        
        if total == 0:
            return 0.5, "neutral"
        
        # Calculate sentiment score
        sentiment_score = positive_count / (positive_count + negative_count + 1)
        
        # Determine label
        if sentiment_score > 0.6:
            label = "positive"
        elif sentiment_score < 0.4:
            label = "negative"
        else:
            label = "neutral"
        
        return sentiment_score, label
    
    def detect_crisis(self, news_items: List[Dict]) -> str:
        """
        Detect crisis level based on news content.
        Returns: none, low, medium, high
        """
        crisis_count = 0
        
        for item in news_items:
            text = (item.get('title', '') + ' ' + item.get('description', '')).lower()
            
            for keyword in self.crisis_keywords:
                if keyword in text:
                    crisis_count += 1
                    break
        
        if crisis_count >= 3:
            return "high"
        elif crisis_count >= 2:
            return "medium"
        elif crisis_count >= 1:
            return "low"
        else:
            return "none"
    
    def extract_injury_info(self, news_items: List[Dict]) -> Tuple[int, List[str]]:
        """
        Extract injury information from news.
        Returns injury count and list of key players out.
        """
        injury_patterns = [
            r'(\w+\s+\w+)\s+out\s+for',
            r'(\w+\s+\w+)\s+injured',
            r'(\w+\s+\w+)\s+sidelined',
            r'(\w+\s+\w+)\s+missing',
            r'(\w+\s+\w+)\s+doubtful'
        ]
        
        key_players_out = []
        
        for item in news_items:
            text = (item.get('title', '') + ' ' + item.get('description', '')).lower()
            
            if 'injury' in text or 'injured' in text:
                for pattern in injury_patterns:
                    matches = re.findall(pattern, text)
                    key_players_out.extend(matches)
        
        # Deduplicate
        key_players_out = list(set(key_players_out))[:5]  # Max 5 players
        
        return len(key_players_out), key_players_out
    
    def analyze_lineup(
        self,
        confirmed_lineup: List[str],
        expected_lineup: List[str],
        key_players_missing: List[str]
    ) -> LineupAnalysis:
        """
        Analyze line-up data and compare with expectations.
        """
        is_confirmed = len(confirmed_lineup) >= 11
        
        # Calculate formation (simplified - would need actual formation data)
        formation = "4-3-3"  # Default formation
        
        # Calculate formation strength based on missing key players
        missing_impact = len(key_players_missing) * 0.1
        formation_strength = max(0.3, 1.0 - missing_impact)
        
        # Calculate lineup quality score
        lineup_quality = 1.0 - (len(key_players_missing) * 0.15)
        lineup_quality = max(0.3, min(1.0, lineup_quality))
        
        # Count expected changes
        changes = abs(len(confirmed_lineup) - len(expected_lineup))
        
        return LineupAnalysis(
            is_confirmed=is_confirmed,
            formation=formation,
            key_players_missing=key_players_missing,
            formation_strength=formation_strength,
            lineup_quality_score=lineup_quality,
            expected_changes=changes
        )
    
    def analyze_manager_matchup(
        self,
        home_manager: str,
        away_manager: str,
        h2h_results: List[Dict] = None
    ) -> ManagerMatchup:
        """
        Analyze manager vs manager historical data.
        """
        matchup = ManagerMatchup(
            home_manager=home_manager,
            away_manager=away_manager
        )
        
        if h2h_results:
            for result in h2h_results:
                # Parse result - simplified
                if result.get('home_manager') == home_manager:
                    if result.get('result') == 'win':
                        matchup.home_manager_wins += 1
                    elif result.get('result') == 'loss':
                        matchup.away_manager_wins += 1
                    else:
                        matchup.draws += 1
                    matchup.total_matches += 1
        
        # Calculate form (simplified - would need actual form data)
        if matchup.total_matches > 0:
            matchup.home_manager_form = matchup.home_manager_wins / matchup.total_matches
            matchup.away_manager_form = matchup.away_manager_wins / matchup.total_matches
        else:
            # Default form based on recent performance
            matchup.home_manager_form = 0.5
            matchup.away_manager_form = 0.5
        
        return matchup
    
    def calculate_motivation(
        self,
        league_position: int,
        league_size: int,
        points: int,
        matches_remaining: int,
        title_contender: bool = False,
        relegation_threat: bool = False,
        promotion_contender: bool = False
    ) -> Tuple[float, List[str]]:
        """
        Calculate motivation level based on league context.
        Returns motivation score and list of factors.
        """
        motivation = 0.5
        factors = []
        
        # Title challenge
        if title_contender:
            motivation += 0.2
            factors.append("Title Challenge")
        
        # Relegation battle
        if relegation_threat:
            position_from_bottom = league_size - league_position
            if position_from_bottom <= 3:
                motivation += 0.25
                factors.append("Relegation Battle - Must Win")
            elif position_from_bottom <= 5:
                motivation += 0.15
                factors.append("Relegation Danger")
        
        # Promotion push
        if promotion_contender:
            if league_position <= 2:
                motivation += 0.2
                factors.append("Automatic Promotion Push")
            elif league_position <= 6:
                motivation += 0.1
                factors.append("Playoff Contention")
        
        # End of season stakes
        if matches_remaining <= 5:
            motivation += 0.1
            factors.append("End of Season")
        
        # Points gap analysis
        points_per_match = points / max(1, 30 - matches_remaining)  # Assume 30 match season
        if points_per_match > 2.0:
            motivation += 0.1
            factors.append("High Points Per Game")
        
        return min(1.0, motivation), factors
    
    def calculate_fatigue(
        self,
        days_since_last_match: int,
        matches_in_last_14_days: int,
        travel_distance_km: float,
        is_home_team: bool
    ) -> float:
        """
        Calculate fatigue index based on fixture congestion and travel.
        """
        fatigue = 0.5
        
        # Fixture congestion impact
        if matches_in_last_14_days >= 4:
            fatigue += 0.25
        elif matches_in_last_14_days >= 3:
            fatigue += 0.15
        elif matches_in_last_14_days >= 2:
            fatigue += 0.05
        
        # Short rest impact
        if days_since_last_match < 3:
            fatigue += 0.2
        elif days_since_last_match < 5:
            fatigue += 0.1
        
        # Travel impact (for away team)
        if not is_home_team and travel_distance_km > 1000:
            fatigue += 0.15
        elif not is_home_team and travel_distance_km > 500:
            fatigue += 0.1
        elif not is_home_team and travel_distance_km > 200:
            fatigue += 0.05
        
        return min(1.0, fatigue)
    
    def analyze(
        self,
        home_news: List[Dict],
        away_news: List[Dict],
        home_lineup: LineupAnalysis,
        away_lineup: LineupAnalysis,
        manager_matchup: ManagerMatchup,
        home_league_position: int,
        away_league_position: int,
        days_since_last_match: int = 3,
        matches_in_last_14_days: int = 2,
        travel_distance_km: float = 0,
        is_home_team: bool = True
    ) -> HumanContextAnalysis:
        """
        Perform comprehensive human context analysis.
        """
        # Analyze sentiment
        home_sentiment, home_label = self.analyze_sentiment(home_news)
        away_sentiment, away_label = self.analyze_sentiment(away_news)
        
        # Calculate average sentiment
        avg_sentiment = (home_sentiment + away_sentiment) / 2
        overall_label = "positive" if avg_sentiment > 0.6 else "negative" if avg_sentiment < 0.4 else "neutral"
        
        # Extract injury info
        home_injuries, home_players_out = self.extract_injury_info(home_news)
        away_injuries, away_players_out = self.extract_injury_info(away_news)
        
        # Calculate injury impact
        injury_impact = (home_injuries + away_injuries) * 0.15
        injury_impact = min(1.0, injury_impact)
        
        # Detect crisis
        home_crisis = self.detect_crisis(home_news)
        away_crisis = self.detect_crisis(away_news)
        
        # Calculate motivation
        home_motivation, home_factors = self.calculate_motivation(
            home_league_position, 20, 50, 10
        )
        away_motivation, away_factors = self.calculate_motivation(
            away_league_position, 20, 45, 10
        )
        avg_motivation = (home_motivation + away_motivation) / 2
        
        # Calculate fatigue
        home_fatigue = self.calculate_fatigue(
            days_since_last_match, matches_in_last_14_days, 0, True
        )
        away_fatigue = self.calculate_fatigue(
            days_since_last_match, matches_in_last_14_days, travel_distance_km, False
        )
        avg_fatigue = (home_fatigue + away_fatigue) / 2
        
        # Calculate confidence score
        confidence = 50.0
        if home_news:
            confidence += 15
        if away_news:
            confidence += 15
        if home_lineup.is_confirmed:
            confidence += 10
        if manager_matchup.total_matches > 0:
            confidence += 10
        
        # Identify risk factors
        risk_factors = []
        
        if home_crisis in ["medium", "high"]:
            risk_factors.append(f"Home team in {home_crisis} crisis")
        if away_crisis in ["medium", "high"]:
            risk_factors.append(f"Away team in {away_crisis} crisis")
        if home_injuries > 2:
            risk_factors.append(f"Home team has {home_injuries} key injuries")
        if away_injuries > 2:
            risk_factors.append(f"Away team has {away_injuries} key injuries")
        if avg_fatigue > 0.7:
            risk_factors.append("High fatigue factor")
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            avg_sentiment, injury_impact, avg_motivation, avg_fatigue
        )
        
        return HumanContextAnalysis(
            sentiment_score=avg_sentiment,
            sentiment_label=overall_label,
            injury_impact=injury_impact,
            lineup_analysis=home_lineup,  # Simplified
            manager_matchup=manager_matchup,
            motivation_boost=avg_motivation,
            fatigue_factor=avg_fatigue,
            confidence_score=min(100.0, confidence),
            risk_factors=risk_factors,
            recommendation=recommendation
        )
    
    def _generate_recommendation(
        self,
        sentiment: float,
        injury_impact: float,
        motivation: float,
        fatigue: float
    ) -> str:
        """
        Generate recommendation based on human context factors.
        """
        if sentiment > 0.6 and injury_impact < 0.3 and fatigue < 0.6:
            return "FAVORABLE - Positive sentiment, low injuries, reasonable fatigue"
        elif sentiment < 0.4 or injury_impact > 0.6:
            return "CAUTION - Negative sentiment or high injury impact"
        elif fatigue > 0.7:
            return "CAUTION - High fatigue may affect performance"
        else:
            return "NEUTRAL - No significant human factors detected"


# Example usage
if __name__ == "__main__":
    engine = HumanContextEngine()
    
    # Sample news
    home_news = [
        {'title': 'Team wins big match', 'description': 'Impressive victory for home team'},
        {'title': 'Key player returns', 'description': 'Star player recovered from injury'}
    ]
    away_news = [
        {'title': 'Team loses key player', 'description': 'Star player injured and out'},
        {'title': 'Poor performance', 'description': 'Team struggling in recent matches'}
    ]
    
    # Analyze
    sentiment, label = engine.analyze_sentiment(home_news)
    print(f"Home sentiment: {sentiment:.2f} ({label})")
    
    crisis = engine.detect_crisis(home_news)
    print(f"Crisis level: {crisis}")
    
    injuries, players = engine.extract_injury_info(home_news)
    print(f"Injuries: {injuries}, Players out: {players}")
