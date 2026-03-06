"""
The Oracle 2026: Soccer Intelligence System
A Hybrid AI Consensus prediction system using Triangulasi Data methodology.

Author: Rizki Wahyudi, S.Kom
Version: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "Rizki Wahyudi, S.Kom"

from .statistical_engine import StatisticalEngine
from .human_context_engine import HumanContextEngine
from .market_intelligence_engine import MarketIntelligenceEngine
from .triangulation_engine import TriangulationEngine
from .prediction_engine import PredictionEngine

__all__ = [
    "StatisticalEngine",
    "HumanContextEngine",
    "MarketIntelligenceEngine",
    "TriangulationEngine",
    "PredictionEngine",
]
