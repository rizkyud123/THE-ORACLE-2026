"""
Configuration module for The Oracle 2026
Loads and manages configuration from config.json
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class APIKeys:
    """API Keys configuration"""
    api_football: str = ""
    openweathermap: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    newsapi: str = ""
    the_odds_api: str = ""
    rapidapi_key: str = ""
    rapidapi_host_livescore: str = ""
    rapidapi_host_sport: str = ""


@dataclass
class AutomationSettings:
    """Automation settings"""
    daily_output: str = "Daily Top 10 Picks"
    threshold: int = 85
    schedule: str = "07:00"
    kelly_fraction: float = 0.25


@dataclass
class PredictionSettings:
    """Prediction settings"""
    min_confidence: int = 70
    high_confidence: int = 85
    leagues: list = field(default_factory=lambda: [])


class Config:
    """Main configuration class"""
    
    _instance: Optional['Config'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from config.json"""
        config_path = Path(__file__).parent.parent / "config.json"
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        else:
            # Default configuration if config.json doesn't exist
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "project_name": "The Oracle 2026: Soccer Intelligence System",
            "developer": "Rizki Wahyudi, S.Kom",
            "version": "2.0.0",
            "api_keys": {},
            "automation_features": {
                "daily_operation": {
                    "threshold": 85,
                    "schedule": "07:00"
                },
                "execution_strategy": {
                    "kelly_criterion_fraction": 0.25
                }
            },
            "prediction_settings": {
                "min_confidence_threshold": 70,
                "high_confidence_threshold": 85,
                "leagues": []
            }
        }
    
    @property
    def project_name(self) -> str:
        return self._config.get("project_name", "The Oracle 2026")
    
    @property
    def developer(self) -> str:
        return self._config.get("developer", "Rizki Wahyudi, S.Kom")
    
    @property
    def version(self) -> str:
        return self._config.get("version", "2.0.0")
    
    @property
    def architecture(self) -> Dict:
        return self._config.get("architecture", {})
    
    @property
    def api_keys(self) -> APIKeys:
        keys = self._config.get("api_keys", {})
        return APIKeys(
            api_football=keys.get("api_football", ""),
            openweathermap=keys.get("openweathermap", ""),
            telegram_bot_token=keys.get("telegram_bot_token", ""),
            telegram_chat_id=keys.get("telegram_chat_id", ""),
            newsapi=keys.get("newsapi", ""),
            the_odds_api=keys.get("the_odds_api", ""),
            rapidapi_key=keys.get("rapidapi_key", ""),
            rapidapi_host_livescore=keys.get("rapidapi_host_livescore", ""),
            rapidapi_host_sport=keys.get("rapidapi_host_sport", "")
        )
    
    @property
    def automation(self) -> AutomationSettings:
        auto = self._config.get("automation_features", {}).get("daily_operation", {})
        exec_strategy = self._config.get("automation_features", {}).get("execution_strategy", {})
        return AutomationSettings(
            threshold=auto.get("threshold", 85),
            schedule=auto.get("schedule", "07:00"),
            kelly_fraction=exec_strategy.get("kelly_criterion_fraction", 0.25)
        )
    
    @property
    def prediction(self) -> PredictionSettings:
        pred = self._config.get("prediction_settings", {})
        return PredictionSettings(
            min_confidence=pred.get("min_confidence_threshold", 70),
            high_confidence=pred.get("high_confidence_threshold", 85),
            leagues=pred.get("leagues", [])
        )
    
    @property
    def triangulation_rules(self) -> list:
        return self._config.get("triangulation_logic", {}).get("rules", [])
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self._config.get(key, default)


# Global config instance
config = Config()
