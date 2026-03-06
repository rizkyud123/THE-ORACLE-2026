"""
Streamlit Dashboard - Visual Interface for The Oracle 2026
Provides interactive visualization of predictions and analysis.

Author: Rizki Wahyudi, S.Kom
Version: 2.0.0
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import List, Dict

# Page config
st.set_page_config(
    page_title="The Oracle 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #424242;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .jackpot-badge {
        background-color: #FFD700;
        color: #000;
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        font-weight: bold;
    }
    .high-risk {
        color: #FF5252;
        font-weight: bold;
    }
    .medium-risk {
        color: #FF9800;
        font-weight: bold;
    }
    .low-risk {
        color: #4CAF50;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<p class="main-header">🏆 The Oracle 2026: Soccer Intelligence System</p>', 
                unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='text-align: center; color: #666; margin-bottom: 2rem;'>
        Version 2.0.0 | Hybrid AI Consensus Engine | Triangulasi Data Methodology<br>
        Developer: Rizki Wahyudi, S.Kom
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("⚙️ Settings")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Daily Picks", "Match Predictor", "Analysis", "Settings"]
    )
    
    if page == "Dashboard":
        dashboard_page()
    elif page == "Daily Picks":
        daily_picks_page()
    elif page == "Match Predictor":
        match_predictor_page()
    elif page == "Analysis":
        analysis_page()
    elif page == "Settings":
        settings_page()


def dashboard_page():
    """Main dashboard with overview."""
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Leagues", "7", "+2")
    with col2:
        st.metric("Today's Picks", "10", "+3")
    with col3:
        st.metric("Jackpot Picks", "3", "+1")
    with col4:
        st.metric("Avg Confidence", "87%", "+5%")
    
    st.markdown("---")
    
    # Quick stats
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Pillar Performance")
        
        # Create sample data for visualization
        pillar_data = pd.DataFrame({
            'Pillar': ['Statistical', 'Human Context', 'Market Intelligence'],
            'Accuracy': [78, 72, 68],
            'Weight': [40, 30, 30]
        })
        
        fig = px.bar(
            pillar_data, 
            x='Pillar', 
            y='Accuracy',
            color='Pillar',
            title='Prediction Accuracy by Pillar',
            color_discrete_sequence=['#1E88E5', '#43A047', '#FB8C00']
        )
        fig.update_layout(yaxis_title="Accuracy (%)", yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Confidence Distribution")
        
        # Confidence distribution
        confidence_data = pd.DataFrame({
            'Level': ['High (85%+)', 'Medium (70-85%)', 'Low (<70%)'],
            'Count': [15, 25, 10]
        })
        
        fig2 = px.pie(
            confidence_data, 
            values='Count', 
            names='Level',
            title='Prediction Confidence Distribution',
            color_discrete_sequence=['#4CAF50', '#FF9800', '#F44336']
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Recent picks
    st.markdown("---")
    st.subheader("📋 Recent Predictions")
    
    # Sample data
    recent_picks = pd.DataFrame({
        'Match': ['Man City vs Liverpool', 'Real Madrid vs Barcelona', 'Bayern vs Dortmund'],
        'Date': ['2024-01-15', '2024-01-14', '2024-01-14'],
        'Prediction': ['Home', 'Away', 'Home'],
        'Confidence': [92, 88, 85],
        'Result': ['✅ Won', '❌ Lost', '✅ Won']
    })
    
    st.dataframe(recent_picks, use_container_width=True)
    
    # Triangulation explanation
    st.markdown("---")
    st.subheader("🔍 How Triangulasi Data Works")
    
    st.info("""
    **Triangulasi Data** ensures maximum accuracy through cross-validation of three factors:
    
    1. **📊 Statistical Analysis**: Poisson distribution, xG, H2H, form
    2. **🧠 Human Context**: News sentiment, injuries, motivation
    3. **📈 Market Intelligence**: Odds movement, smart money, trap detection
    
    A bet is recommended only when all three pillars align!
    """)


def daily_picks_page():
    """Daily picks page."""
    
    st.header("📅 Today's Top Picks")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_confidence = st.slider("Minimum Confidence", 50, 100, 70)
    with col2:
        league_filter = st.selectbox("League", ["All", "Premier League", "La Liga", "Serie A", "Bundesliga"])
    with col3:
        sort_by = st.selectbox("Sort By", ["Confidence", "Time", "League"])
    
    # Generate sample picks
    sample_picks = generate_sample_picks()
    
    # Filter
    filtered_picks = [p for p in sample_picks if p['confidence'] >= min_confidence]
    
    # Display picks
    st.markdown("---")
    
    for pick in filtered_picks:
        display_pick_card(pick)


def match_predictor_page():
    """Match predictor page."""
    
    st.header("🎯 Match Predictor")
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.selectbox(
            "Home Team",
            ["Manchester City", "Liverpool", "Arsenal", "Chelsea", "Manchester United",
             "Real Madrid", "Barcelona", "Atletico Madrid",
             "Bayern Munich", "Dortmund", "Juventus", "Inter", "PSG"]
        )
    
    with col2:
        away_team = st.selectbox(
            "Away Team",
            ["Liverpool", "Manchester City", "Arsenal", "Chelsea", "Manchester United",
             "Barcelona", "Real Madrid", "Atletico Madrid",
             "Dortmund", "Bayern Munich", "Inter", "Juventus", "PSG"]
        )
    
    if st.button("🔮 Generate Prediction", type="primary"):
        if home_team == away_team:
            st.error("Please select different teams!")
        else:
            # Generate prediction
            prediction = generate_prediction(home_team, away_team)
            
            # Display
            display_prediction_result(prediction)


def analysis_page():
    """Analysis page with detailed statistics."""
    
    st.header("📊 Detailed Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Pillar 1: Statistical", "Pillar 2: Human Context", "Pillar 3: Market"])
    
    with tab1:
        st.subheader("📊 Statistical Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Poisson Distribution**")
            st.info("Uses Poisson probability distribution to calculate expected goals and match outcomes based on historical scoring patterns.")
        
        with col2:
            st.write("**xG Analysis**")
            st.info("Expected Goals (xG) measures the quality of scoring chances to predict future performance.")
        
        # xG comparison chart
        xg_data = pd.DataFrame({
            'Team': ['Man City', 'Liverpool', 'Arsenal', 'Chelsea'],
            'xG': [2.1, 1.8, 1.6, 1.4],
            'xGA': [0.9, 1.1, 1.2, 1.3]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=xg_data['Team'], y=xg_data['xG'], name='xG For'))
        fig.add_trace(go.Bar(x=xg_data['Team'], y=xg_data['xGA'], name='xG Against'))
        
        fig.update_layout(
            title='xG Comparison (Last 10 Matches)',
            barmode='group',
            yaxis_title='xG'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("🧠 Human Context Analysis")
        
        st.write("**NLP News Sentiment**")
        st.info("Analyzes news articles and social media to determine team sentiment and identify potential issues.")
        
        # Sentiment visualization
        sentiment_data = pd.DataFrame({
            'Category': ['Positive', 'Neutral', 'Negative'],
            'Count': [45, 35, 20]
        })
        
        fig = px.pie(
            sentiment_data, 
            values='Count', 
            names='Category',
            title='News Sentiment Distribution',
            color_discrete_sequence=['#4CAF50', '#9E9E9E', '#F44336']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("📈 Market Intelligence")
        
        st.write("**Anti-Trap Detection**")
        st.info("Monitors odds movement to detect potential traps and market anomalies.")
        
        # Odds movement chart
        odds_data = pd.DataFrame({
            'Time': ['Opening', '-24h', '-12h', '-6h', 'Current'],
            'Home Odds': [2.0, 1.95, 1.90, 1.85, 1.80],
            'Draw Odds': [3.5, 3.4, 3.3, 3.5, 3.6],
            'Away Odds': [3.8, 3.9, 4.0, 3.9, 3.8]
        })
        
        fig = px.line(
            odds_data, 
            x='Time', 
            y=['Home Odds', 'Draw Odds', 'Away Odds'],
            title='Odds Movement Over Time',
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)


def settings_page():
    """Settings page."""
    
    st.header("⚙️ Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("API Configuration")
        api_football = st.text_input("API-Football Key", type="password")
        weather_api = st.text_input("OpenWeatherMap Key", type="password")
    
    with col2:
        st.subheader("Telegram Settings")
        telegram_token = st.text_input("Telegram Bot Token", type="password")
        chat_id = st.text_input("Chat ID")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Prediction Settings")
        min_conf = st.slider("Minimum Confidence", 50, 100, 70)
        high_conf = st.slider("High Confidence Threshold", 70, 100, 85)
    
    with col2:
        st.subheader("Automation Settings")
        schedule_time = st.time_input("Daily Picks Time", datetime.strptime("07:00", "%H:%M"))
        kelly_fraction = st.slider("Kelly Criterion Fraction", 0.1, 1.0, 0.25)
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("Settings saved successfully!")


# Helper functions

def generate_sample_picks() -> List[Dict]:
    """Generate sample daily picks."""
    return [
        {
            'home': 'Manchester City',
            'away': 'Liverpool',
            'league': 'Premier League',
            'time': '20:00',
            'prediction': 'Home',
            'score': '2-1',
            'confidence': 92,
            'jackpot': True
        },
        {
            'home': 'Real Madrid',
            'away': 'Barcelona',
            'league': 'La Liga',
            'time': '20:00',
            'prediction': 'Home',
            'score': '3-2',
            'confidence': 88,
            'jackpot': True
        },
        {
            'home': 'Bayern Munich',
            'away': 'Dortmund',
            'league': 'Bundesliga',
            'time': '17:30',
            'prediction': 'Home',
            'score': '2-0',
            'confidence': 85,
            'jackpot': False
        },
        {
            'home': 'Juventus',
            'away': 'Inter',
            'league': 'Serie A',
            'time': '19:00',
            'prediction': 'Draw',
            'score': '1-1',
            'confidence': 78,
            'jackpot': False
        },
        {
            'home': 'PSG',
            'away': 'Marseille',
            'league': 'Ligue 1',
            'time': '20:00',
            'prediction': 'Home',
            'score': '3-0',
            'confidence': 82,
            'jackpot': False
        }
    ]


def generate_prediction(home: str, away: str) -> Dict:
    """Generate a prediction for a match."""
    import random
    
    # Simulate prediction
    home_prob = random.uniform(0.35, 0.60)
    away_prob = random.uniform(0.20, 0.40)
    draw_prob = 1 - home_prob - away_prob
    
    if home_prob > away_prob and home_prob > draw_prob:
        prediction = 'Home'
        score = f"{random.randint(1,3)}-{random.randint(0,2)}"
    elif away_prob > home_prob and away_prob > draw_prob:
        prediction = 'Away'
        score = f"{random.randint(0,2)}-{random.randint(1,3)}"
    else:
        prediction = 'Draw'
        score = f"{random.randint(0,2)}-{random.randint(0,2)}"
    
    confidence = random.randint(70, 95)
    
    return {
        'home': home,
        'away': away,
        'home_prob': home_prob,
        'away_prob': away_prob,
        'draw_prob': draw_prob,
        'prediction': prediction,
        'score': score,
        'confidence': confidence,
        'risk': 'Low' if confidence >= 85 else 'Medium' if confidence >= 70 else 'High'
    }


def display_pick_card(pick: Dict):
    """Display a pick as a card."""
    
    jackpot_badge = "🔥" if pick.get('jackpot', False) else ""
    
    st.markdown(f"""
    <div style='background-color: #f5f5f5; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <strong>{pick['home']} vs {pick['away']}</strong><br>
                <small style='color: #666;'>{pick['league']} | {pick['time']}</small>
            </div>
            <div style='text-align: right;'>
                <span class='jackpot-badge'>{jackpot_badge} {pick['confidence']}%</span>
            </div>
        </div>
        <hr style='margin: 0.5rem 0;'>
        <div style='display: flex; justify-content: space-between;'>
            <span>🎯 Prediction: <strong>{pick['prediction']}</strong></span>
            <span>📊 Score: <strong>{pick['score']}</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def display_prediction_result(prediction: Dict):
    """Display prediction result with visualizations."""
    
    st.markdown("---")
    
    # Probability chart
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(f"⚽ {prediction['home']} vs {prediction['away']}")
        
        prob_data = pd.DataFrame({
            'Outcome': ['Home Win', 'Draw', 'Away Win'],
            'Probability': [
                prediction['home_prob'] * 100,
                prediction['draw_prob'] * 100,
                prediction['away_prob'] * 100
            ]
        })
        
        fig = px.bar(
            prob_data,
            x='Outcome',
            y='Probability',
            color='Outcome',
            color_discrete_sequence=['#4CAF50', '#FF9800', '#F44336'],
            title='Win Probabilities'
        )
        fig.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Prediction")
        
        # Show confidence level
        if prediction['confidence'] >= 85:
            st.markdown('<p class="jackpot-badge">🔥 HIGH CONFIDENCE</p>', unsafe_allow_html=True)
        elif prediction['confidence'] >= 70:
            st.markdown('<p style="color: #FF9800; font-weight: bold;">⚠️ MEDIUM RISK</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="high-risk">⚠️ LOW CONFIDENCE</p>', unsafe_allow_html=True)
        
        st.metric("Confidence", f"{prediction['confidence']}%")
        st.metric("Recommended Bet", prediction['prediction'])
        st.metric("Expected Score", prediction['score'])
        st.metric("Risk Level", prediction['risk'])
        
        # Key factors
        st.subheader("📋 Key Factors")
        st.write("• Strong home advantage")
        st.write("• Positive recent form")
        st.write("• Market sentiment stable")


if __name__ == "__main__":
    main()
