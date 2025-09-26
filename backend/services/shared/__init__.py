"""
Shared Services Module
Centralized tier configuration for the VERTICAL-LIGHT-OS parallel architecture.

This module provides the tier configuration system that enables both
enterprise and local business services to coexist in the same platform.
"""

# Core tier configuration - always available
from .tier_config import BusinessTier, TierConfigManager, LOCAL_CONFIG, ENTERPRISE_CONFIG

__all__ = [
 'BusinessTier',
 'TierConfigManager', 
 'LOCAL_CONFIG',
 'ENTERPRISE_CONFIG'
]
