"""
The Oracle 2026 - Streamlit Dashboard
Professional Visual Interface with Neural Predictions

Author: Rizki Wahyudi, S.Kom
Version: 2.7.0
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from pytz import timezone
import plotly.graph_objects as go
import plotly.express as px

WITA = timezone('Asia/Makassar')

# Page Config
st.set_page_config(
    page_title="The Oracle 2026",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Bloomberg-style dark mode
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .metric-card {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #333;
    }
    .match-card {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid;
        margin-bottom: 10px;
    }
    .high-risk { border-left-color: #ff4b4b; }
    .medium-risk { border-left-color: #ffa500; }
    .low-risk { border-left-color: #00cc96; }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# CACHE & DATA LOADING
# ============================================================================

def load_predictions_cache():
    """Load predictions from cache file"""
    cache_file = "predictions_cache.json"
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except:
            pass
    
    return None


def save_predictions_cache(predictions):
    """Save predictions to cache file"""
    cache_file = "predictions_cache.json"
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(predictions, f, indent=2, default=str)
        return True
    except Exception as e:
        st.error(f"Error saving cache: {e}")
        return False


# ============================================================================
# SIDEBAR - API KEYS & SETTINGS
# ============================================================================

def sidebar_settings():
    """Sidebar configuration"""
    with st.sidebar:
        st.title("🏆 The Oracle 2026")
        st.markdown("---")
        
        # API Keys (secure input)
        st.subheader("🔑 API Configuration")
        api_football = st.text_input("API-Football Key", type="password")
        openweather = st.text_input("OpenWeatherMap Key", type="password")
        newsapi = st.text_input("NewsAPI Key", type="password")
        
        st.markdown("---")
        
        # Bankroll & Stats
        st.subheader("💰 Bankroll Settings")
        bankroll = st.number_input("Initial Bankroll ($)", value=1000.0, step=100.0)
        success_rate = st.slider("Success Rate (%)", 0, 100, 65)
        
        st.markdown("---")
        
        # Filters
        st.subheader("🔍 Filters")
        selected_leagues = st.multiselect(
            "Leagues",
            ["Premier League", "Bundesliga", "Serie A", "La Liga", "Ligue 1", 
             "Eredivisie", "Primeira Liga", "Championship"],
            default=["Premier League", "Bundesliga", "Serie A"]
        )
        
        risk_filter = st.multiselect(
            "Risk Level",
            ["LOW", "MEDIUM", "HIGH"],
            default=["LOW", "MEDIUM", "HIGH"]
        )
        
        min_confidence = st.slider("Min Confidence (%)", 0, 100, 50)
        
        st.markdown("---")
        
        # Refresh button
        if st.button("🔄 Refresh Predictions"):
            st.rerun()
        
        st.markdown(f"""
        <div style='text-align: center; color: #666; font-size: 12px;'>
        Version 2.7.0 | Time Lock: 2026 | WITA
        </div>
        """, unsafe_allow_html=True)
        
        return {
            "api_keys": {"api_football": api_football, "openweathermap": openweather, "newsapi": newsapi},
            "bankroll": bankroll,
            "success_rate": success_rate,
            "leagues": selected_leagues,
            "risk_filter": risk_filter,
            "min_confidence": min_confidence
        }


# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main_dashboard(settings):
    """Main dashboard layout"""
    
    # Header
    st.title("🏆 The Oracle 2026")
    st.markdown("### Global Neural Prediction System v2.7.0")
    
    # Load cached predictions or generate demo data
    cached = load_predictions_cache()
    
    if cached and "predictions" in cached:
        predictions = cached["predictions"]
        st.info(f"📊 Loaded {len(predictions)} predictions from cache")
    else:
        # Generate demo predictions for display
        predictions = generate_demo_predictions()
    
    # Filter predictions
    filtered = filter_predictions(predictions, settings)
    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Matches", len(filtered))
    with col2:
        low_risk = len([p for p in filtered if p.get("risk_level") == "LOW"])
        st.metric("✅ Low Risk", low_risk)
    with col3:
        avg_conf = sum(p.get("final_confidence", 0) for p in filtered) / max(1, len(filtered))
        st.metric("📈 Avg Confidence", f"{avg_conf:.0f}%")
    with col4:
        opportunities = len([p for p in filtered if p.get("recommended_bet") != "SKIP"])
        st.metric("🎯 Opportunities", opportunities)
    
    st.markdown("---")
    
    # League Filter
    if settings["leagues"]:
        filtered = [p for p in filtered if p.get("league") in settings["leagues"]]
    
    # Risk Filter
    if settings["risk_filter"]:
        filtered = [p for p in filtered if p.get("risk_level") in settings["risk_filter"]]
    
    # Confidence Filter
    filtered = [p for p in filtered if p.get("final_confidence", 0) >= settings["min_confidence"]]
    
    # Display Matches
    if filtered:
        for pred in filtered:
            display_match_card(pred)
    else:
        st.warning("No matches match your filters")


# ============================================================================
# MATCH CARD DISPLAY
# ============================================================================

def display_match_card(pred):
    """Display a single match card with expanders"""
    
    risk_class = pred.get("risk_level", "MEDIUM").lower()
    
    # Color coding
    risk_colors = {"HIGH": "#ff4b4b", "MEDIUM": "#ffa500", "LOW": "#00cc96"}
    risk_color = risk_colors.get(risk_class, "#ffa500")
    
    # Confidence color
    conf = pred.get("final_confidence", 0)
    conf_color = "#ff4b4b" if conf < 50 else "#ffa500" if conf < 70 else "#00cc96"
    
    with st.expander(f"⚽ {pred.get('home_team')} vs {pred.get('away_team')}", expanded=False):
        # Header
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{pred.get('league', 'Unknown')}")
            st.caption(f"🕐 {pred.get('kickoff_wita', 'N/A')}")
        
        with col2:
            st.markdown(f"<span style='color:{conf_color}; font-size:24px; font-weight:bold;'>{conf:.0f}%</span>", unsafe_allow_html=True)
            st.caption("Confidence")
        
        with col3:
            risk_emoji = "🔴" if risk_class == "HIGH" else "🟡" if risk_class == "MEDIUM" else "🟢"
            st.markdown(f"{risk_emoji} **{risk_class}**")
            st.caption("Risk Level")
        
        with col4:
            bet = pred.get("recommended_bet", "SKIP")
            st.markdown(f"**{'⏭️ SKIP' if bet == 'SKIP' else f'🎯 {bet}'}**")
            st.caption("Recommended")
        
        # Pillar Analysis
        st.markdown("### 📊 Pillar Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            display_statistical_pillar(pred)
        
        with col2:
            display_sensor_pillar(pred)
        
        # Market Analysis
        display_market_pillar(pred)
        
        # Penalties
        if pred.get("penalty_reasons"):
            st.markdown("### ⚠️ Penalties Applied")
            for reason in pred["penalty_reasons"]:
                st.markdown(f"- {reason}")


def display_statistical_pillar(pred):
    """Display Statistical pillar with Poisson chart"""
    
    st.markdown("#### 📈 Statistical Pillar")
    
    # H2H Results
    h2h = pred.get("h2h_data", {})
    last5 = h2h.get("last_5_results", [])
    h2h_str = "-".join(last5) if last5 else "N/A"
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**H2H (Last 5):** `{h2h_str}`")
    with col2:
        if h2h.get("mental_advantage"):
            st.success("🧠 Mental Advantage (+15%)")
        if h2h.get("kryptonite_detected"):
            st.error("⚠️ KRYPTONITE DETECTED")
    
    # Poisson chart
    poisson = pred.get("poisson_data", {})
    if poisson:
        home_xg = poisson.get("home_expected_goals", 1.5)
        away_xg = poisson.get("away_expected_goals", 1.2)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Home xG', 'Away xG'],
            y=[home_xg, away_xg],
            marker_color=['#00cc96', '#ff4b4b'],
            text=[f"{home_xg:.1f}", f"{away_xg:.1f}"],
            textposition='auto'
        ))
        fig.update_layout(
            title="Expected Goals (xG)",
            template="plotly_dark",
            height=250
        )
        st.plotly_chart(fig, use_container_width=True)


def display_sensor_pillar(pred):
    """Display Weather & News sensors"""
    
    st.markdown("#### 🌤️ Sensor Pillar")
    
    # Weather
    weather = pred.get("weather_data", {})
    if weather:
        weather_emoji = "☀️" if weather.get("condition") == "clear" else "🌧️" if weather.get("condition") == "rain" else "❄️"
        st.markdown(f"**Weather:** {weather_emoji} {weather.get('condition', 'N/A')} ({weather.get('temperature', 'N/A')}°C)")
        
        if weather.get("weather_penalty", 0) < 0:
            st.warning(f"⚠️ Weather Penalty: {weather.get('weather_penalty')*100:.0f}%")
    
    # News
    news = pred.get("news_home", {})
    if news:
        if news.get("crisis_detected"):
            st.error(f"🚨 CRISIS: {news.get('keywords_found', [])}")
        else:
            st.success(f"✅ News: {news.get('sentiment_score', 0.5):.2f}")


def display_market_pillar(pred):
    """Display Market pillar with odds"""
    
    st.markdown("#### 💰 Market Pillar")
    
    market = pred.get("market_data", {})
    if market:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Home Odds", f"{market.get('home_odds', 'N/A')}")
        with col2:
            st.metric("Draw Odds", f"{market.get('draw_odds', 'N/A')}")
        with col3:
            st.metric("Away Odds", f"{market.get('away_odds', 'N/A')}")
        
        # Trap indicator
        if market.get("trap_detected"):
            st.error(f"🚨 SMART TRAP: {market.get('trap_reason', 'Unknown')}")
        else:
            st.success(f"Market Movement: {market.get('market_movement', 'stable')}")


# ============================================================================
# FILTERS & HELPERS
# ============================================================================

def filter_predictions(predictions, settings):
    """Filter predictions based on settings"""
    
    filtered = []
    
    for pred in predictions:
        # Risk filter
        if settings["risk_filter"] and pred.get("risk_level") not in settings["risk_filter"]:
            continue
        
        # Confidence filter
        if pred.get("final_confidence", 0) < settings["min_confidence"]:
            continue
        
        filtered.append(pred)
    
    return filtered


def generate_demo_predictions():
    """Generate demo predictions for display"""
    
    demo_matches = [
        {"home_team": "Manchester City", "away_team": "Liverpool", "league": "Premier League"},
        {"home_team": "Bayern Munich", "away_team": "Dortmund", "league": "Bundesliga"},
        {"home_team": "PSV", "away_team": "AZ", "league": "Eredivisie"},
        {"home_team": "Real Madrid", "away_team": "Barcelona", "league": "La Liga"},
    ]
    
    predictions = []
    
    for i, match in enumerate(demo_matches):
        import random
        
        conf = random.randint(40, 85)
        risk = "LOW" if conf >= 70 else "MEDIUM" if conf >= 50 else "HIGH"
        
        pred = {
            "match_id": str(i),
            **match,
            "league": match["league"],
            "kickoff_wita": "2026-03-07 03:00 WITA",
            "final_confidence": conf,
            "risk_level": risk,
            "recommended_bet": "SKIP" if conf < 60 else random.choice(["HOME", "AWAY", "DRAW"]),
            "h2h_data": {
                "last_5_results": random.choice(["H-D-A-H-W", "W-W-H-D-A", "A-A-H-D-W"]),
                "mental_advantage": conf > 70,
                "kryptonite_detected": conf < 50
            },
            "poisson_data": {
                "home_expected_goals": round(random.uniform(1.0, 2.5), 1),
                "away_expected_goals": round(random.uniform(0.8, 2.0), 1),
                "over_25_probability": random.uniform(0.4, 0.7)
            },
            "weather_data": {
                "condition": random.choice(["clear", "rain", "cloudy"]),
                "temperature": random.randint(10, 25),
                "weather_penalty": random.choice([0, -0.10, -0.15])
            },
            "news_home": {
                "sentiment_score": random.uniform(0.3, 0.8),
                "crisis_detected": random.random() > 0.7,
                "keywords_found": random.choice([[], ["Injury"], ["Crisis", "Bad Form"]])
            },
            "market_data": {
                "home_odds": round(random.uniform(1.5, 3.0), 2),
                "draw_odds": round(random.uniform(2.8, 3.5), 2),
                "away_odds": round(random.uniform(1.5, 3.0), 2),
                "market_movement": random.choice(["stable", "dropping_home", "rising_away"]),
                "trap_detected": random.random() > 0.8,
                "trap_reason": "Smart Trap" if random.random() > 0.8 else ""
            },
            "penalty_reasons": random.choice([[], ["Weather: rain (-10%)"], ["Crisis: Injury"]]) if random.random() > 0.5 else []
        }
        
        predictions.append(pred)
    
    return predictions


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    settings = sidebar_settings()
    main_dashboard(settings)
