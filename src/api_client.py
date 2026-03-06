"""
API Client - The Oracle 2026
Fixed: Data Normalization + Odds Integration + Simulated Odds Fallback
"""

import requests
import logging
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pytz import timezone, utc

from .config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WITA = timezone('Asia/Makassar')


def get_current_year_wita() -> int:
    return datetime.now(WITA).year


def get_season_for_date(date_str: str = None) -> int:
    if date_str:
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            year = dt.year
            month = dt.month
        except:
            year = get_current_year_wita()
            month = datetime.now(WITA).month
    else:
        year = get_current_year_wita()
        month = datetime.now(WITA).month
    
    if month in [3, 4, 5, 6]:
        return year - 1
    return year


def get_wita_date() -> str:
    return datetime.now(WITA).strftime('%Y-%m-%d')


def convert_to_wita(utc_time: str) -> datetime:
    try:
        dt = datetime.fromisoformat(utc_time.replace('Z', '+00:00'))
        return dt.astimezone(WITA)
    except:
        return None


def get_prime_time_window(input_date: str = None) -> tuple:
    if input_date:
        try:
            start_dt = datetime.strptime(input_date, '%Y-%m-%d')
            start_dt = WITA.localize(start_dt)
        except:
            start_dt = datetime.now(WITA)
    else:
        start_dt = datetime.now(WITA)
    
    start_window = start_dt.replace(hour=20, minute=0, second=0, microsecond=0)
    end_window = start_dt.replace(hour=5, minute=0, second=0, microsecond=0)
    if start_window.hour >= 20:
        end_window = end_window + timedelta(days=1)
    
    return start_window, end_window


def is_prime_time(kickoff_wita: datetime, start_window: datetime, end_window: datetime) -> bool:
    if start_window <= end_window:
        return start_window <= kickoff_wita <= end_window
    else:
        return kickoff_wita >= start_window or kickoff_wita <= end_window


def rate_limit():
    time.sleep(1)


ALL_COMPETITIONS = [
    {'id': 2021, 'name': 'Premier League', 'country': 'England'},
    {'id': 2016, 'name': 'Championship', 'country': 'England'},
    {'id': 2002, 'name': 'Bundesliga', 'country': 'Germany'},
    {'id': 2014, 'name': 'Serie A', 'country': 'Italy'},
    {'id': 2015, 'name': 'Ligue 1', 'country': 'France'},
    {'id': 2003, 'name': 'Primera Division', 'country': 'Spain'},
    {'id': 2001, 'name': 'Eredivisie', 'country': 'Netherlands'},
    {'id': 2013, 'name': 'Primeira Liga', 'country': 'Portugal'},
    {'id': 2000, 'name': 'FIFA World Cup', 'country': 'World'},
    {'id': 2019, 'name': 'Serie A', 'country': 'Brazil'},
]


# Team aliases for matching
TEAM_ALIASES = {
    'manchester city': ['man city', 'manchester city fc', 'mci'],
    'manchester united': ['manchester utd', 'manchester united fc', 'mun'],
    'liverpool': ['liverpool fc', 'liverpool football club', 'liv'],
    'chelsea': ['chelsea fc', 'chelsea football club', 'che'],
    'arsenal': ['arsenal fc', 'arsenal london', 'ars'],
    'tottenham': ['tottenham hotspur', 'tottenham hotspur fc', 'tot', 'thfc'],
    'newcastle': ['newcastle united', 'newcastle utd', 'newcastle fc', 'new'],
    'aston villa': ['aston villa fc', 'avfc'],
    'west ham': ['west ham united', 'west ham utd', 'west ham fc', 'whu'],
    'milan': ['ac milan', 'ac milan', 'milan'],
    'inter': ['inter milan', 'fc internazionale', 'inter milan'],
    'juventus': ['juventus fc', 'juve'],
    'roma': ['as roma', 'roma fc'],
    'lazio': ['ss lazio', 'lazio roma', 'lazio'],
    'barcelona': ['fc barcelona', 'barca', 'fcb'],
    'real madrid': ['real madrid cf', 'rma'],
    'atletico madrid': ['atletico madrid', 'atm'],
    'sevilla': ['sevilla fc', 'sev'],
    'paris sg': ['paris saint-germain', 'paris sg', 'psg'],
    'marseille': ['olympique marseille', 'om'],
    'lyon': ['olympique lyonnais', 'lyon', 'ol'],
    'monaco': ['as monaco', 'monaco fc'],
    'bayern': ['bayern munich', 'fc bayern', 'bayern munich'],
    'dortmund': ['borussia dortmund', 'bvb'],
    'leipzig': ['rb leipzig'],
    'leverkusen': ['bayer leverkusen'],
    'lille': ['lille osc', 'losc', 'lille'],
    'rennes': ['stade rennais', 'stade rennais fc', 'rennes'],
    'porto': ['fc porto', 'porto'],
    'sporting': ['sporting cp', 'sporting'],
    'benfica': ['sl benfica', 'benfica'],
}


def normalize_team_name(team_name: str) -> str:
    """Normalize team name for matching"""
    if not team_name:
        return ""
    
    name = team_name.lower().strip()
    name = name.replace(' fc', '').replace(' football club', '')
    name = name.replace(' cf', '').replace(' ssc', '').replace(' as ', ' ')
    name = name.replace(' ac ', ' ').replace(' us ', ' ').replace(' sc ', ' ')
    name = name.replace(' rc ', ' ').replace(' cd ', ' ').replace(' gd ', ' ')
    name = name.replace(' 1901', '').replace(' 1919', '').replace(' 1903', '')
    
    for canonical, aliases in TEAM_ALIASES.items():
        if name in aliases or name == canonical:
            return canonical
    
    return name


def fuzzy_match(name1: str, name2: str) -> bool:
    """Fuzzy match two team names"""
    n1 = normalize_team_name(name1)
    n2 = normalize_team_name(name2)
    
    if n1 == n2:
        return True
    
    if len(n1) > 3 and len(n2) > 3:
        if n1 in n2 or n2 in n1:
            return True
    
    words1 = set(n1.split())
    words2 = set(n2.split())
    common = words1.intersection(words2)
    
    if len(common) >= 1 and len(common) >= min(len(words1), len(words2)) * 0.5:
        return True
    
    return False


class TheOddsAPI:
    """The Odds API - Market Intelligence"""
    
    def __init__(self):
        self.api_key = "a1cfd1f640a66c683e9df03209a8e286"
        self.base_url = "https://api.the-odds-api.com/v4"
        self.source = "ODDS-API"
    
    def verify_api_status(self) -> bool:
        """Verify The Odds API connection"""
        try:
            response = requests.get(
                f"{self.base_url}/sports",
                params={'api_key': self.api_key},
                timeout=10
            )
            if response.status_code == 200:
                logger.info("✅ The Odds API: Connected")
                return True
            else:
                logger.warning(f"⚠️ The Odds API: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ The Odds API: Connection failed - {e}")
            return False
    
    def get_odds_for_match(self, home_team: str, away_team: str) -> Optional[Dict]:
        """Get odds for specific match with fuzzy matching"""
        try:
            sports = [
                'soccer_epl', 'soccer_eng_championship', 'soccer_germany_bundesliga', 
                'soccer_spain_la_liga', 'soccer_italy_serie_a', 'soccer_france_ligue_1',
                'soccer_portugal_primeira', 'soccer_netherlands_eredivisie'
            ]
            
            for sport in sports:
                try:
                    response = requests.get(
                        f"{self.base_url}/sports/{sport}/odds",
                        params={
                            'api_key': self.api_key,
                            'regions': 'uk',
                            'oddsFormat': 'decimal'
                        },
                        timeout=15
                    )
                    
                    if response.status_code != 200:
                        continue
                    
                    data = response.json()
                    games = data.get('data', [])
                    
                    for game in games:
                        game_home = game.get('home_team', '')
                        game_away = game.get('away_team', '')
                        
                        if fuzzy_match(home_team, game_home) and fuzzy_match(away_team, game_away):
                            bookmakers = game.get('bookmakers', [])
                            if not bookmakers:
                                continue
                            
                            home_odds_list, draw_odds_list, away_odds_list = [], [], []
                            
                            for bm in bookmakers[:5]:
                                markets = bm.get('markets', [])
                                if not markets:
                                    continue
                                outcomes = markets[0].get('outcomes', [])
                                for o in outcomes:
                                    name = o.get('name', '')
                                    odds_val = float(o.get('odds', 0))
                                    if odds_val > 1:
                                        if fuzzy_match(name, game.get('home_team')):
                                            home_odds_list.append(odds_val)
                                        elif fuzzy_match(name, game.get('away_team')):
                                            away_odds_list.append(odds_val)
                                        elif name.lower() in ['draw', 'tie', 'x']:
                                            draw_odds_list.append(odds_val)
                            
                            if home_odds_list or away_odds_list:
                                logger.info(f"   📊 Found odds: {game_home} vs {game_away}")
                                return {
                                    'home_odds': sum(home_odds_list)/len(home_odds_list) if home_odds_list else 2.5,
                                    'draw_odds': sum(draw_odds_list)/len(draw_odds_list) if draw_odds_list else 3.2,
                                    'away_odds': sum(away_odds_list)/len(away_odds_list) if away_odds_list else 2.8,
                                    'bookmakers': len(bookmakers)
                                }
                except:
                    continue
            
            return None
        except:
            return None
    
    def get_simulated_odds(self, home_team: str, away_team: str, league: str) -> Dict:
        """
        Generate simulated odds based on league and team strength
        Used as fallback when real odds aren't available
        """
        # League strength factors
        league_strength = {
            'Premier League': 1.0,
            'Bundesliga': 0.95,
            'Serie A': 0.9,
            'Primera Division': 0.9,
            'Ligue 1': 0.85,
            'Primeira Liga': 0.75,
            'Championship': 0.7,
            'Eredivisie': 0.7,
        }
        
        base_strength = league_strength.get(league, 0.8)
        
        # Generate realistic odds with some variation
        home_base = 2.2 * base_strength
        away_base = 2.8 * base_strength
        
        # Add randomness (simulating market movement)
        home_odds = round(home_base + random.uniform(-0.3, 0.3), 2)
        away_odds = round(away_base + random.uniform(-0.3, 0.3), 2)
        draw_odds = round(3.2 + random.uniform(-0.2, 0.2), 2)
        
        # Ensure minimum odds
        home_odds = max(1.3, min(4.0, home_odds))
        away_odds = max(1.3, min(4.0, away_odds))
        draw_odds = max(2.5, min(4.5, draw_odds))
        
        return {
            'home_odds': home_odds,
            'draw_odds': draw_odds,
            'away_odds': away_odds,
            'bookmakers': 3,
            'simulated': True
        }


class RapidAPIClient:
    """Primary API - RapidAPI"""
    
    def __init__(self):
        self.api_key = "4666a7fa0cmsh945954136dfc854p137b5djsn5927d5725e3f"
        self.host = "api-football-v1.p.rapidapi.com"
        self.base_url = "https://api-football-v1.p.rapidapi.com/v3"
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': self.host
        }
        self.source = "PREMIUM-DB"
    
    def get_fixtures(self, date: str, season: int) -> List[Dict]:
        try:
            response = requests.get(
                f"{self.base_url}/fixtures",
                headers=self.headers,
                params={'date': date, 'season': season},
                timeout=15
            )
            
            if response.status_code in [403, 429]:
                raise Exception(f"API Error: {response.status_code}")
            
            response.raise_for_status()
            data = response.json()
            return data.get('response', [])
            
        except Exception as e:
            logger.error(f"RapidAPI error: {e}")
            raise


class FootballAPIClient:
    """Fallback API - Football-Data.org"""
    
    def __init__(self):
        self.api_key = config.api_keys.api_football
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {'X-Auth-Token': self.api_key}
        self.source = "FALLBACK-DB"
    
    def check_all_leagues(self, date: str) -> List[Dict]:
        all_matches = []
        logger.info(f"🔍 Checking all {len(ALL_COMPETITIONS)} competitions...")
        
        for comp in ALL_COMPETITIONS:
            try:
                matches = self._fetch_competition(comp['id'], date)
                if matches:
                    all_matches.extend(matches)
                    logger.info(f"   ✓ {comp['name']}: {len(matches)} matches")
            except Exception as e:
                logger.debug(f"   ✗ {comp['name']}: {e}")
        
        return all_matches
    
  def _fetch_competition(self, comp_id: int, date: str) -> List[Dict]:
    try:
        # S.Kom Fix: Tambahkan rentang agar Matchday Weekend tertangkap
        current_dt = datetime.strptime(date, '%Y-%m-%d')
        # Tarik data dari H-1 sampai H+2 (Total 3 hari)
        d_from = (current_dt).strftime('%Y-%m-%d')
        d_to = (current_dt + timedelta(days=2)).strftime('%Y-%m-%d')
        
        response = requests.get(
            f"{self.base_url}/competitions/{comp_id}/matches",
            headers=self.headers,
            params={'dateFrom': d_from, 'dateTo': d_to}, # PAKAI RANGE!
            timeout=10
        )
        
        if response.status_code == 403:
            return [] # Liga tidak didukung tier gratis
            
        response.raise_for_status()
        data = response.json()
        return data.get('matches', [])
    except Exception as e:
        logger.debug(f"Fetch error {comp_id}: {e}")
        return []
    
    def get_matches(self, date: str) -> List[Dict]:
        return self.check_all_leagues(date)


class APIClient:
    """Main API Client with All Fallbacks"""
    
    def __init__(self):
        self.rapid = RapidAPIClient()
        self.football = FootballAPIClient()
        self.odds_api = TheOddsAPI()
        self.last_source = "UNKNOWN"
        self.odds_cache = {}
        
        # Verify The Odds API on init
        self.odds_available = self.odds_api.verify_api_status()
    
    def enrich_with_odds(self, matches: List[Dict]) -> List[Dict]:
        """Enrich match data with odds from The Odds API with simulated fallback"""
        
        enriched = []
        for match in matches:
            home = match.get('home_team', '')
            away = match.get('away_team', '')
            league = match.get('league', '')
            
            # Check cache first
            cache_key = f"{home}|{away}"
            if cache_key in self.odds_cache:
                odds_data = self.odds_cache[cache_key]
            elif self.odds_available:
                # Try real API first
                odds_data = self.odds_api.get_odds_for_match(home, away)
                if odds_data:
                    logger.info(f"   📊 Real odds: {home} vs {away}")
                self.odds_cache[cache_key] = odds_data
            else:
                odds_data = None
            
            # Fallback to simulated odds
            if not odds_data:
                odds_data = self.odds_api.get_simulated_odds(home, away, league)
                logger.info(f"   📊 Simulated odds: {home} vs {away}")
            
            if odds_data:
                match['odds'] = odds_data
                home_odds = odds_data.get('home_odds', 2.5)
                away_odds = odds_data.get('away_odds', 2.5)
                
                # Detect market movement
                if home_odds < 1.8:
                    match['market_movement'] = 'dropping_home'  # Strong home favorite
                elif home_odds > 3.2:
                    match['market_movement'] = 'rising_home'  # Home underdog
                elif away_odds < 1.8:
                    match['market_movement'] = 'dropping_away'  # Strong away favorite
                else:
                    match['market_movement'] = 'stable'
            else:
                match['odds'] = {'home_odds': 0, 'draw_odds': 0, 'away_odds': 0}
                match['market_movement'] = 'no_data'
            
            enriched.append(match)
        
        return enriched
    
    def get_prime_time_matches(self, input_date: str = None) -> tuple:
        """Get matches within Prime Time window with 3-day Smart Lookahead"""
        if not input_date:
            input_date = get_wita_date()
        
        season = get_season_for_date(input_date)
        start_window, end_window = get_prime_time_window(input_date)
        
        # S.Kom Optimization: Tarik data 3 hari sekaligus untuk cover Weekend WITA
        current_dt = datetime.strptime(input_date, '%Y-%m-%d')
        dates_to_fetch = [
            (current_dt).strftime('%Y-%m-%d'),
            (current_dt + timedelta(days=1)).strftime('%Y-%m-%d'),
            (current_dt + timedelta(days=2)).strftime('%Y-%m-%d')
        ]
        
        logger.info(f"📡 Scanning Range: {dates_to_fetch[0]} to {dates_to_fetch[-1]}")
        
        all_matches = []
        source_used = None

        # 1. RapidAPI Loop
        try:
            for date in dates_to_fetch:
                fixtures = self.rapid.get_fixtures(date, season)
                if fixtures:
                    parsed = [self._parse_rapidapi(f) for f in fixtures]
                    all_matches.extend([m for m in parsed if m])
            
            if all_matches:
                source_used = "PREMIUM-DB"
        except Exception as e:
            logger.warning(f"⚠️ RapidAPI failed (403/Limit): {e}")

        # 2. Football-Data.org Fallback Loop
        if not all_matches:
            logger.info("🔄 Falling back to Football-Data.org (Multi-Date Scan)...")
            for date in dates_to_fetch:
                matches = self.football.get_matches(date)
                if matches:
                    parsed = [self._parse_footballdata(m) for m in matches]
                    all_matches.extend([m for m in parsed if m])
            
            if all_matches:
                source_used = "FALLBACK-DB"

        self.last_source = source_used or "NO-DATA"
        
        # 3. Odds Enrichment & Prime Time Filter
        if all_matches:
            logger.info(f"📊 Total raw matches found: {len(all_matches)}")
            all_matches = self.enrich_with_odds(all_matches)
            self.last_source += "+ODDS"
        
        prime_time_matches = []
        for match in all_matches:
            kickoff = match.get('kickoff_wita')
            # Pastikan pengecekan Prime Time mencakup rentang 3 hari tersebut
            if kickoff and is_prime_time(kickoff, start_window, end_window + timedelta(days=1)):
                prime_time_matches.append(match)
        
        prime_time_matches.sort(key=lambda x: x.get('kickoff_wita', datetime.min))
        return prime_time_matches, self.last_source
    
    def _parse_rapidapi(self, f: Dict) -> Optional[Dict]:
        """Parse RapidAPI response to STANDARD format"""
        try:
            fix = f.get('fixture', {})
            league = f.get('league', {})
            teams = f.get('teams', {})
            goals = f.get('goals', {})
            
            utc_time = fix.get('date', '')
            kickoff_wita = convert_to_wita(utc_time)
            
            return {
                'match_id': str(fix.get('id', '')),
                'home_team': teams.get('home', {}).get('name', 'TBD'),
                'away_team': teams.get('away', {}).get('name', 'TBD'),
                'league': league.get('name', 'Unknown'),
                'kickoff_time': kickoff_wita,
                'kickoff_utc': utc_time,
                'kickoff_wita': kickoff_wita,
                'venue': fix.get('venue', {}).get('name', 'Stadium'),
                'city': fix.get('venue', {}).get('city', ''),
                'status': fix.get('status', {}).get('short', 'NS'),
                'status_long': fix.get('status', {}).get('long', 'Not Started'),
                'home_score': goals.get('home', 0),
                'away_score': goals.get('away', 0),
            }
        except:
            return None
    
    def _parse_footballdata(self, m: Dict) -> Optional[Dict]:
        """Parse Football-Data.org response to STANDARD format"""
        try:
            comp = m.get('competition', {})
            home = m.get('homeTeam', {})
            away = m.get('awayTeam', {})
            score = m.get('score', {})
            
            utc_time = m.get('utcDate', '')
            kickoff_wita = convert_to_wita(utc_time)
            
            return {
                'match_id': str(m.get('id', '')),
                'home_team': home.get('name', 'TBD'),
                'away_team': away.get('name', 'TBD'),
                'league': comp.get('name', 'Unknown'),
                'kickoff_time': kickoff_wita,
                'kickoff_utc': utc_time,
                'kickoff_wita': kickoff_wita,
                'venue': home.get('venue', 'Stadium'),
                'city': '',
                'status': m.get('status', 'SCHEDULED'),
                'status_long': m.get('status', 'Not Started'),
                'home_score': score.get('fullTime', {}).get('home', 0) or score.get('halfTime', {}).get('home', 0) or 0,
                'away_score': score.get('fullTime', {}).get('away', 0) or score.get('halfTime', {}).get('away', 0) or 0,
            }
        except Exception as e:
            logger.debug(f"Parse error: {e}")
            return None


api_client = APIClient()


def test_all_leagues():
    print("\n🧪 Testing All Leagues Fallback...")
    
    date = "2025-03-15"
    matches, source = api_client.get_prime_time_matches(date)
    
    print(f"\n✅ Results:")
    print(f"   Source: {source}")
    print(f"   Matches: {len(matches)}")
    
    leagues = {}
    for m in matches:
        league = m.get('league', 'Unknown')
        leagues[league] = leagues.get(league, 0) + 1
    
    print(f"\n📊 Leagues found:")
    for league, count in sorted(leagues.items(), key=lambda x: x[1], reverse=True):
        print(f"   {league}: {count}")


if __name__ == "__main__":
    test_all_leagues()




