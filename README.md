# 🏆 The Oracle 2026: Soccer Intelligence System

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.10+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

A Hybrid AI Consensus prediction system using **Triangulasi Data** methodology for soccer match predictions.

## 📋 Overview

The Oracle 2026 is an advanced soccer intelligence system that combines three pillars of analysis:
- **Statistical Analysis**: Poisson Distribution, xG, H2H, Form
- **Human Context**: NLP Sentiment, Injuries, Motivation
- **Market Intelligence**: Anti-Trap, Smart Money, Odds Analysis

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    THE ORACLE 2026                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  STATISTICAL    │  │  HUMAN CONTEXT  │  │   MARKET    │ │
│  │    PILLAR 1     │  │    PILLAR 2     │  │  PILLAR 3   │ │
│  │                 │  │                 │  │             │ │
│  │ • Poisson       │  │ • NLP Sentiment │  │ • Anti-Trap │ │
│  │ • xG Analysis   │  │ • Line-up       │  │ • Smart $   │ │
│  │ • H2H History   │  │ • Manager       │  │ • Odds      │ │
│  │ • Form Factor   │  │ • Motivation    │  │ • Referee   │ │
│  │ • Home Adv.     │  │ • Fatigue       │  │ • Weather   │ │
│  └────────┬────────┘  └────────┬────────┘  └──────┬──────┘ │
│           │                    │                   │         │
│           └────────────────────┼───────────────────┘         │
│                                ▼                             │
│                 ┌─────────────────────────┐                  │
│                 │   TRIANGULATION ENGINE  │                  │
│                 │                         │                  │
│                 │  Validation Logic:      │                  │
│                 │  Stats + Sentiment +    │                  │
│                 │  Market = CONFIDENCE   │                  │
│                 └────────────┬────────────┘                  │
│                              ▼                               │
│                 ┌─────────────────────────┐                  │
│                 │   PREDICTION ENGINE     │                  │
│                 └────────────┬────────────┘                  │
│                              ▼                               │
│     ┌───────────────────────┼───────────────────────┐       │
│     ▼                       ▼                       ▼       │
│ ┌──────────┐         ┌──────────────┐      ┌──────────┐   │
│ │ Telegram │         │  Streamlit   │      │  Python  │   │
│ │   Bot   │         │  Dashboard   │      │   CLI    │   │
│ └──────────┘         └──────────────┘      └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Triangulasi Data Rules

| Condition | Result |
|-----------|--------|
| Statistik Mendukung AND Sentimen Positif AND Pasar Stabil | 🔥 HIGH CONFIDENCE (JACKPOT) |
| Statistik Mendukung BUT Pasar Anomali | 🚫 SKIP (TRAP) |
| Statistik Mendukung BUT Sentimen Negatif | ⚠️ MEDIUM RISK |

## 📦 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd parlay
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure API keys in `config.json`:
```json
{
  "api_keys": {
    "api_football": "YOUR_API_KEY",
    "openweathermap": "YOUR_WEATHER_KEY",
    "telegram_bot_token": "YOUR_BOT_TOKEN",
    "telegram_chat_id": "YOUR_CHAT_ID"
  }
}
```

## 🚀 Usage

### Streamlit Dashboard
```bash
python main.py dashboard
# or
streamlit run streamlit_app.py
```

### Telegram Bot
```bash
python main.py bot
```

### CLI Prediction
```bash
python main.py predict --home "Manchester City" --away "Liverpool"
```

### Generate Daily Picks
```bash
python main.py daily
```

### Test Telegram
```bash
python main.py test-telegram
```

## 📁 Project Structure

```
parlay/
├── config.json           # Configuration file
├── requirements.txt      # Dependencies
├── main.py              # Main entry point
├── streamlit_app.py     # Streamlit dashboard
├── README.md            # Documentation
├── TODO.md             # Project plan
│
└── src/
    ├── __init__.py
    ├── config.py       # Config loader
    ├── statistical_engine.py    # Pillar 1
    ├── human_context_engine.py  # Pillar 2
    ├── market_intelligence_engine.py  # Pillar 3
    ├── triangulation_engine.py # Core logic
    ├── prediction_engine.py    # Orchestration
    ├── telegram_bot.py         # Notifications
    └── scheduler.py           # Automation
```

## 🔧 Features

### Pillar 1: Statistical Analysis
- [x] Poisson Distribution Score Prediction
- [x] Expected Goals (xG) Analysis
- [x] Head-to-Head (H2H) Historical Dominance
- [x] Macro League Standings & Form Factor
- [x] Home/Away Advantage Analytics

### Pillar 2: Human Context
- [x] NLP News Sentiment Scraper
- [x] Line-up Analysis (60-minute pre-match)
- [x] Tactical Manager Matchup
- [x] Motivation & Stakes Engine
- [x] Fatigue & Travel Distance Index

### Pillar 3: Market Intelligence
- [x] Anti-Trap: Dropping Odds Detector
- [x] Smart Money Flow Analysis
- [x] Market Sentiment Bias vs Statistics
- [x] Referee Disciplinary Profiling
- [x] Weather & Pitch Intelligence

### Automation
- [x] Daily Top 10 Picks (07:00 AM)
- [x] Kelly Criterion Stake Calculator
- [x] Telegram Notifications

## 📊 Requirements

- Python 3.10+
- See `requirements.txt` for dependencies

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - See LICENSE file for details.

## 👤 Developer

**Rizki Wahyudi, S.Kom**
- Version: 2.0.0
- Architecture: Hybrid AI Consensus
- Methodology: Triangulasi Data

---

⚠️ **Disclaimer**: This system is for educational purposes only. Always bet responsibly.
