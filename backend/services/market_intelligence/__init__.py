"""
Market Intelligence Service Module
Shared market data and intelligence services for the VERTICAL-LIGHT-OS platform.
"""

from .market_data_engine import MarketDataEngine, get_market_data_engine

__all__ = [
    'MarketDataEngine',
    'get_market_data_engine'
]
