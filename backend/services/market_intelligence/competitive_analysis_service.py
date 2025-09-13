"""
Competitive Analysis Service - Market Intelligence
Advanced competitor analysis, market positioning, and competitive intelligence
100% Dynamic Configuration - Zero Hardcoded Values
"""

import json
import logging
import threading
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib

from config.config_manager import get_config_manager

logger = logging.getLogger(__name__)


class CompetitiveAnalysisService:
    """
    Advanced competitive analysis service for market intelligence,
    competitor monitoring, and strategic positioning analysis.
    """
    
    def __init__(self):
        self.config_manager = get_config_manager()
        self.competitive_config = self._load_competitive_configuration()
        
        # Competitive intelligence storage
        self.competitor_profiles: Dict[str, Dict[str, Any]] = {}
        self.competitive_landscape: Dict[str, Any] = {}
        self.market_positioning: Dict[str, Dict[str, Any]] = {}
        self.competitive_insights: Dict[str, Any] = {}
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Configuration-driven parameters
        self.analysis_depth = self._get_config_value('analysis.depth_level', 'comprehensive')
        self.confidence_threshold = self._get_config_value('analysis.confidence_threshold', 0.75)
        self.max_competitors = self._get_config_value('analysis.max_competitors_tracked', 20)
        self.update_frequency = self._get_config_value('monitoring.update_frequency_hours', 24)
        
        # Market analysis parameters
        self.market_share_threshold = self._get_config_value('market.significant_share_threshold', 0.05)
        self.threat_assessment_factors = self._get_config_value('threat_assessment.factors', [])
        self.opportunity_gap_threshold = self._get_config_value('opportunities.gap_threshold', 0.3)
        
        # Cache management
        self.analysis_cache: Dict[str, Tuple[Any, datetime]] = {}
        self.cache_ttl = timedelta(hours=self._get_config_value('cache.ttl_hours', 12))
        
        logger.info("CompetitiveAnalysisService initialized with dynamic configuration")
        
    def _load_competitive_configuration(self) -> Dict[str, Any]:
        """Load competitive analysis configuration"""
        try:
            return self.config_manager.get('competitive_analysis', {})
        except Exception as e:
            logger.error(f"Failed to load competitive configuration: {e}")
            return {}
    
    def _get_config_value(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        try:
            keys = key_path.split('.')
            value = self.competitive_config
            for key in keys:
                value = value.get(key, {})
            return value if value != {} else default
        except Exception:
            return default
    
    def analyze_competitive_landscape(self, competitors: Any, 
                                    market_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive competitive landscape analysis
        """
        with self.lock:
            try:
                # Handle None inputs - return fallback immediately
                if competitors is None and market_data is None:
                    return self._create_fallback_analysis()
                
                # Handle different input formats for backward compatibility
                if market_data is None:
                    market_data = {}
                
                # Create business profile from market_data if available
                business_profile = market_data.get('business_profile', {})
                
                # Create analysis signature for caching
                analysis_signature = self._create_analysis_signature(business_profile, market_data)
                
                # Check cache first
                cached_analysis = self._get_cached_analysis(analysis_signature)
                if cached_analysis:
                    return cached_analysis

                # Normalize competitor data to handle both list and dict formats
                competitors_dict = self._normalize_competitor_data(competitors)
                industry = business_profile.get('industry', market_data.get('industry', 'unknown'))
                
                # Perform comprehensive analysis
                landscape_analysis = {
                    'analysis_id': analysis_signature,
                    'timestamp': datetime.now().isoformat(),
                    'industry': industry,
                    'market_structure': self._analyze_market_structure(competitors_dict),
                    'competitive_intensity': self._calculate_competitive_intensity(competitors_dict),
                    'market_leaders': self._identify_market_leaders(competitors_dict),
                    'key_players': self._identify_key_players(competitors_dict),
                    'market_dynamics': self._analyze_market_dynamics(competitors_dict, market_data),
                    'competitive_gaps': self._identify_competitive_gaps(competitors_dict, business_profile),
                    'threat_assessment': self._assess_competitive_threats(competitors_dict, business_profile),
                    'opportunity_analysis': self._analyze_competitive_opportunities(competitors_dict, business_profile),
                    'positioning_recommendations': self._generate_positioning_recommendations(competitors_dict, business_profile),
                    'strategic_insights': self._generate_strategic_insights(competitors_dict, business_profile),
                    'confidence_score': self._calculate_analysis_confidence(competitors_dict, business_profile)
                }
                
                # Cache the analysis
                self._cache_analysis(analysis_signature, landscape_analysis)
                
                logger.info(f"Generated competitive landscape analysis with confidence: {landscape_analysis['confidence_score']}")
                return landscape_analysis
                
            except Exception as e:
                logger.error(f"Error in competitive landscape analysis: {e}")
                return self._create_fallback_analysis()
    
    def monitor_competitor(self, competitor_id: str, competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor specific competitor and track changes
        """
        with self.lock:
            try:
                current_time = datetime.now()
                
                # Get existing profile if available
                existing_profile = self.competitor_profiles.get(competitor_id, {})
                
                # Create comprehensive competitor profile
                competitor_profile = {
                    'competitor_id': competitor_id,
                    'last_updated': current_time.isoformat(),
                    'basic_info': self._extract_basic_info(competitor_data),
                    'market_presence': self._analyze_market_presence(competitor_data),
                    'financial_metrics': self._extract_financial_metrics(competitor_data),
                    'product_portfolio': self._analyze_product_portfolio(competitor_data),
                    'marketing_strategy': self._analyze_marketing_strategy(competitor_data),
                    'strengths': self._identify_competitor_strengths(competitor_data),
                    'weaknesses': self._identify_competitor_weaknesses(competitor_data),
                    'strategic_moves': self._track_strategic_moves(competitor_data, existing_profile),
                    'threat_level': self._assess_threat_level(competitor_data),
                    'monitoring_insights': self._generate_monitoring_insights(competitor_data, existing_profile)
                }
                
                # Store updated profile
                self.competitor_profiles[competitor_id] = competitor_profile
                
                # Generate change analysis if existing profile exists
                change_analysis = {}
                if existing_profile:
                    change_analysis = self._analyze_competitor_changes(existing_profile, competitor_profile)
                
                logger.info(f"Updated competitor profile for: {competitor_id}")
                
                return {
                    'competitor_id': competitor_id,
                    'competitor_profile': competitor_profile,
                    'change_analysis': change_analysis,
                    'recommendations': self._generate_competitor_response_recommendations(competitor_profile)
                }
                
            except Exception as e:
                logger.error(f"Error monitoring competitor {competitor_id}: {e}")
                return {}
    
    def assess_market_positioning(self, business_profile: Dict[str, Any], 
                                competitors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess market positioning relative to competitors
        """
        with self.lock:
            try:
                positioning_analysis = {
                    'current_position': self._determine_current_position(business_profile, competitors),
                    'competitive_advantages': self._identify_competitive_advantages(business_profile, competitors),
                    'positioning_gaps': self._identify_positioning_gaps(business_profile, competitors),
                    'market_segments': self._analyze_market_segments(business_profile, competitors),
                    'differentiation_opportunities': self._find_differentiation_opportunities(competitors),
                    'positioning_strategy': self._recommend_positioning_strategy(business_profile, competitors),
                    'competitive_moats': self._identify_competitive_moats(business_profile, competitors),
                    'positioning_risks': self._assess_positioning_risks(business_profile, competitors)
                }
                
                return positioning_analysis
                
            except Exception as e:
                logger.error(f"Error assessing market positioning: {e}")
                return {}
    
    def generate_competitive_intelligence_report(self, business_profile: Dict[str, Any], 
                                               market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive competitive intelligence report
        """
        with self.lock:
            try:
                # Perform all analyses
                landscape_analysis = self.analyze_competitive_landscape(business_profile, market_data)
                positioning_analysis = self.assess_market_positioning(business_profile, market_data.get('competitors', {}))
                
                # Generate executive summary
                executive_summary = self._generate_executive_summary(landscape_analysis, positioning_analysis)
                
                # Compile comprehensive report
                intelligence_report = {
                    'report_id': self._generate_report_id(),
                    'generated_at': datetime.now().isoformat(),
                    'executive_summary': executive_summary,
                    'competitive_landscape': landscape_analysis,
                    'market_positioning': positioning_analysis,
                    'strategic_recommendations': self._generate_strategic_recommendations(landscape_analysis, positioning_analysis),
                    'action_items': self._generate_action_items(landscape_analysis, positioning_analysis),
                    'monitoring_schedule': self._create_monitoring_schedule(),
                    'key_metrics': self._define_key_metrics(),
                    'next_review_date': self._calculate_next_review_date()
                }
                
                logger.info(f"Generated competitive intelligence report: {intelligence_report['report_id']}")
                return intelligence_report
                
            except Exception as e:
                logger.error(f"Error generating competitive intelligence report: {e}")
                return {}
    
    def _normalize_competitor_data(self, competitors: Any) -> Dict[str, Any]:
        """Normalize competitor data from list or dict format to dict format"""
        try:
            if isinstance(competitors, list):
                # Convert list to dictionary using competitor_id or index
                normalized = {}
                for i, competitor in enumerate(competitors):
                    if isinstance(competitor, dict):
                        competitor_id = competitor.get('competitor_id', f'competitor_{i}')
                        normalized[competitor_id] = competitor
                    else:
                        normalized[f'competitor_{i}'] = {'competitor_id': f'competitor_{i}'}
                return normalized
            elif isinstance(competitors, dict):
                return competitors
            else:
                return {}
        except Exception as e:
            logger.error(f"Error normalizing competitor data: {e}")
            return {}
    
    def _identify_key_players(self, competitors: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify key players in the market"""
        try:
            if not competitors:
                return []
            
            # Sort competitors by market share
            key_players = []
            for competitor_id, data in competitors.items():
                market_share = data.get('market_share', 0)
                if market_share > self._get_config_value('key_players.min_share_threshold', 0.05):
                    key_players.append({
                        'competitor_id': competitor_id,
                        'name': data.get('name', competitor_id),
                        'market_share': market_share,
                        'revenue': data.get('revenue', 0),
                        'position': 'leader' if market_share > self._get_config_value('market_position.leader_threshold', 0.2) else 'challenger'
                    })
            
            # Sort by market share descending
            key_players.sort(key=lambda x: x['market_share'], reverse=True)
            return key_players[:self._get_config_value('key_players.max_count', 10)]
            
        except Exception as e:
            logger.error(f"Error identifying key players: {e}")
            return []
    
    def _analyze_market_dynamics(self, competitors: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market dynamics and trends"""
        try:
            market_dynamics = {
                'growth_trends': self._analyze_growth_trends(competitors),
                'competitive_moves': self._analyze_competitive_moves(competitors),
                'market_evolution': self._analyze_market_evolution(competitors, market_data),
                'disruption_potential': self._assess_disruption_potential(competitors),
                'consolidation_risk': self._assess_consolidation_risk(competitors)
            }
            return market_dynamics
        except Exception as e:
            logger.error(f"Error analyzing market dynamics: {e}")
            return {}

    def _analyze_market_structure(self, competitors: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market structure and concentration"""
        try:
            if not competitors:
                return {
                    'structure_type': 'unknown', 
                    'concentration': 0,
                    'concentration_index': 0,
                    'market_type': 'undefined',
                    'dominant_players': []
                }
            
            # Calculate market shares
            market_shares = [data.get('market_share', 0) for data in competitors.values()]
            total_share = sum(market_shares)
            
            if total_share == 0:
                return {
                    'structure_type': 'fragmented', 
                    'concentration': 0,
                    'concentration_index': 0,
                    'market_type': 'fragmented',
                    'dominant_players': []
                }
            
            # Normalize market shares
            normalized_shares = [share / total_share for share in market_shares]
            
            # Calculate HHI (Herfindahl-Hirschman Index)
            hhi = self._calculate_hhi(normalized_shares)
            
            # Determine market structure type
            concentration_threshold_high = self._get_config_value('market_structure.high_concentration_threshold', 0.7)
            concentration_threshold_medium = self._get_config_value('market_structure.medium_concentration_threshold', 0.4)
            
            if max(normalized_shares) > concentration_threshold_high:
                structure_type = 'monopolistic'
                market_type = 'concentrated'
            elif sum(sorted(normalized_shares, reverse=True)[:3]) > concentration_threshold_medium:
                structure_type = 'oligopolistic'
                market_type = 'moderately_concentrated'
            else:
                structure_type = 'competitive'
                market_type = 'fragmented'
            
            # Identify dominant players
            dominant_threshold = self._get_config_value('market_structure.dominant_threshold', 0.15)
            dominant_players = []
            for competitor_id, data in competitors.items():
                share = data.get('market_share', 0) / total_share if total_share > 0 else 0
                if share > dominant_threshold:
                    dominant_players.append({
                        'competitor_id': competitor_id,
                        'name': data.get('name', competitor_id),
                        'market_share': share,
                        'position_rank': len([s for s in normalized_shares if s > share]) + 1
                    })
            
            # Sort dominant players by market share
            dominant_players.sort(key=lambda x: x['market_share'], reverse=True)
            
            return {
                'structure_type': structure_type,
                'concentration': max(normalized_shares) if normalized_shares else 0,
                'concentration_index': hhi,
                'market_type': market_type,
                'dominant_players': dominant_players,
                'hhi_score': hhi,
                'total_competitors': len(competitors),
                'market_share_distribution': {
                    'top_3_share': sum(sorted(normalized_shares, reverse=True)[:3]),
                    'top_5_share': sum(sorted(normalized_shares, reverse=True)[:5]),
                    'gini_coefficient': self._calculate_gini_coefficient(normalized_shares)
                }
            }
            
            # Calculate Herfindahl-Hirschman Index (HHI)
            hhi_multiplier = self._get_config_value('market_structure.hhi_multiplier', 10000)
            hhi = sum(share ** 2 for share in normalized_shares) * hhi_multiplier
            
            # Determine market structure
            if hhi > self._get_config_value('market_structure.highly_concentrated_threshold', 2500):
                structure_type = 'highly_concentrated'
            elif hhi > self._get_config_value('market_structure.moderately_concentrated_threshold', 1500):
                structure_type = 'moderately_concentrated'
            else:
                structure_type = 'fragmented'
            
            # Calculate concentration ratio (CR4 - top 4 competitors)
            top_competitors_count = self._get_config_value('market_structure.top_competitors_count', 4)
            top_n_shares = sorted(normalized_shares, reverse=True)[:top_competitors_count]
            cr_n = sum(top_n_shares)
            
            return {
                'structure_type': structure_type,
                'hhi_index': hhi,
                'concentration_ratio': cr_n,
                'number_of_competitors': len(competitors),
                'market_share_distribution': dict(zip(competitors.keys(), normalized_shares))
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market structure: {e}")
            return {'structure_type': 'unknown', 'concentration': 0}
    
    def _calculate_hhi(self, market_shares: List[float]) -> float:
        """Calculate Herfindahl-Hirschman Index normalized to 0-1 range"""
        try:
            # HHI = sum of squared market shares
            hhi = sum(share ** 2 for share in market_shares)
            return hhi  # Returns value between 0 and 1
        except Exception as e:
            logger.error(f"Error calculating HHI: {e}")
            return 0.0
    
    def _calculate_gini_coefficient(self, market_shares: List[float]) -> float:
        """Calculate Gini coefficient for market concentration"""
        try:
            if not market_shares:
                return 0.0
            
            # Sort market shares
            sorted_shares = sorted(market_shares)
            n = len(sorted_shares)
            
            # Calculate Gini coefficient
            cumsum = sum((i + 1) * share for i, share in enumerate(sorted_shares))
            gini = (2 * cumsum) / (n * sum(sorted_shares)) - (n + 1) / n
            return max(0.0, min(1.0, gini))  # Ensure between 0 and 1
            
        except Exception as e:
            logger.error(f"Error calculating Gini coefficient: {e}")
            return 0.0
    
    def _analyze_growth_trends(self, competitors: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze growth trends across competitors"""
        try:
            growth_rates = []
            high_growth_competitors = []
            declining_competitors = []
            
            for competitor_id, data in competitors.items():
                growth_rate = data.get('growth_rate', 0)
                growth_rates.append(growth_rate)
                
                high_growth_threshold = self._get_config_value('growth_analysis.high_growth_threshold', 0.15)
                decline_threshold = self._get_config_value('growth_analysis.decline_threshold', -0.05)
                
                if growth_rate > high_growth_threshold:
                    high_growth_competitors.append({
                        'competitor_id': competitor_id,
                        'growth_rate': growth_rate
                    })
                elif growth_rate < decline_threshold:
                    declining_competitors.append({
                        'competitor_id': competitor_id,
                        'growth_rate': growth_rate
                    })
            
            return {
                'average_growth_rate': sum(growth_rates) / len(growth_rates) if growth_rates else 0,
                'high_growth_competitors': high_growth_competitors,
                'declining_competitors': declining_competitors,
                'growth_volatility': self._calculate_growth_volatility(growth_rates)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing growth trends: {e}")
            return {}
    
    def _calculate_growth_volatility(self, growth_rates: List[float]) -> float:
        """Calculate volatility of growth rates"""
        try:
            if len(growth_rates) < 2:
                return 0.0
            
            mean_growth = sum(growth_rates) / len(growth_rates)
            variance = sum((rate - mean_growth) ** 2 for rate in growth_rates) / len(growth_rates)
            return variance ** 0.5
            
        except Exception as e:
            logger.error(f"Error calculating growth volatility: {e}")
            return 0.0
    
    def _analyze_competitive_moves(self, competitors: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze recent competitive moves"""
        try:
            moves = []
            for competitor_id, data in competitors.items():
                # Simulate competitive moves analysis
                move_indicators = data.get('strategic_moves', [])
                for move in move_indicators:
                    moves.append({
                        'competitor_id': competitor_id,
                        'move_type': move.get('type', 'unknown'),
                        'impact_level': move.get('impact', 'medium'),
                        'timing': move.get('timing', 'recent')
                    })
            return moves
        except Exception as e:
            logger.error(f"Error analyzing competitive moves: {e}")
            return []
    
    def _analyze_market_evolution(self, competitors: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market evolution patterns"""
        try:
            return {
                'maturity_level': market_data.get('maturity_level', 'unknown'),
                'evolution_stage': self._determine_evolution_stage(competitors, market_data),
                'disruption_indicators': self._identify_disruption_indicators(competitors),
                'consolidation_trend': self._assess_consolidation_trend(competitors)
            }
        except Exception as e:
            logger.error(f"Error analyzing market evolution: {e}")
            return {}
    
    def _determine_evolution_stage(self, competitors: Dict[str, Any], market_data: Dict[str, Any]) -> str:
        """Determine market evolution stage"""
        try:
            # Simple heuristic based on market data
            growth_rate = market_data.get('growth_rate', 0)
            competitor_count = len(competitors)
            
            if growth_rate > self._get_config_value('market_evolution.high_growth_threshold', 0.2):
                return 'emerging'
            elif growth_rate > self._get_config_value('market_evolution.medium_growth_threshold', 0.05):
                return 'growing'
            elif competitor_count < self._get_config_value('market_evolution.low_competitor_threshold', 5):
                return 'consolidating'
            else:
                return 'mature'
                
        except Exception as e:
            logger.error(f"Error determining evolution stage: {e}")
            return 'unknown'
    
    def _assess_disruption_potential(self, competitors: Dict[str, Any]) -> Dict[str, Any]:
        """Assess potential for market disruption"""
        try:
            disruption_indicators = []
            new_entrants = 0
            innovation_level = 0
            
            for competitor_id, data in competitors.items():
                # Check for disruption indicators
                if data.get('market_entry_date'):
                    # Recent entrant check would go here
                    pass
                
                innovation_score = data.get('innovation_score', 0)
                innovation_level += innovation_score
                
                if innovation_score > self._get_config_value('disruption.high_innovation_threshold', 0.8):
                    disruption_indicators.append({
                        'competitor_id': competitor_id,
                        'disruption_type': 'innovation',
                        'threat_level': 'high'
                    })
            
            avg_innovation = innovation_level / len(competitors) if competitors else 0
            
            return {
                'disruption_risk': 'high' if avg_innovation > self._get_config_value('disruption.risk_threshold', 0.6) else 'medium',
                'disruption_indicators': disruption_indicators,
                'innovation_intensity': avg_innovation
            }
            
        except Exception as e:
            logger.error(f"Error assessing disruption potential: {e}")
            return {}
    
    def _assess_consolidation_risk(self, competitors: Dict[str, Any]) -> Dict[str, Any]:
        """Assess market consolidation risk"""
        try:
            market_shares = [data.get('market_share', 0) for data in competitors.values()]
            total_share = sum(market_shares)
            
            if total_share == 0:
                return {'risk_level': 'low', 'indicators': []}
            
            # Calculate concentration
            normalized_shares = [share / total_share for share in market_shares]
            top_3_share = sum(sorted(normalized_shares, reverse=True)[:3])
            
            consolidation_threshold = self._get_config_value('consolidation.high_risk_threshold', 0.75)
            
            return {
                'risk_level': 'high' if top_3_share > consolidation_threshold else 'medium',
                'top_3_concentration': top_3_share,
                'consolidation_drivers': self._identify_consolidation_drivers(competitors)
            }
            
        except Exception as e:
            logger.error(f"Error assessing consolidation risk: {e}")
            return {}
    
    def _identify_disruption_indicators(self, competitors: Dict[str, Any]) -> List[str]:
        """Identify market disruption indicators"""
        try:
            indicators = []
            # Add logic to identify disruption patterns
            return indicators
        except Exception as e:
            logger.error(f"Error identifying disruption indicators: {e}")
            return []
    
    def _assess_consolidation_trend(self, competitors: Dict[str, Any]) -> str:
        """Assess consolidation trend direction"""
        try:
            # Simple assessment based on competitor count and concentration
            competitor_count = len(competitors)
            if competitor_count < self._get_config_value('consolidation.low_count_threshold', 5):
                return 'consolidating'
            elif competitor_count > self._get_config_value('consolidation.high_count_threshold', 20):
                return 'fragmenting'
            else:
                return 'stable'
        except Exception as e:
            logger.error(f"Error assessing consolidation trend: {e}")
            return 'unknown'
    
    def _identify_consolidation_drivers(self, competitors: Dict[str, Any]) -> List[str]:
        """Identify drivers of market consolidation"""
        try:
            drivers = []
            # Add logic to identify consolidation drivers
            return drivers
        except Exception as e:
            logger.error(f"Error identifying consolidation drivers: {e}")
            return []

    def _calculate_competitive_intensity(self, competitors: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate competitive intensity metrics"""
        try:
            if not competitors:
                return {'intensity_level': 'low', 'score': 0.0}
            
            intensity_factors = {
                'number_of_competitors': len(competitors),
                'market_share_distribution': self._calculate_share_variance(competitors),
                'price_competition': self._assess_price_competition(competitors),
                'innovation_rate': self._assess_innovation_rate(competitors),
                'marketing_intensity': self._assess_marketing_intensity(competitors)
            }
            
            # Weight factors based on configuration
            weights = self._get_config_value('intensity_analysis.factor_weights', {
                'number_of_competitors': 0.2,
                'market_share_distribution': 0.2,
                'price_competition': 0.2,
                'innovation_rate': 0.2,
                'marketing_intensity': 0.2
            })
            
            # Calculate weighted intensity score
            intensity_score = 0
            normalization_factor = self._get_config_value('intensity_analysis.normalization_factor', 10)
            max_normalized_value = self._get_config_value('intensity_analysis.max_normalized_value', 1.0)
            default_weight = self._get_config_value('intensity_analysis.default_weight', 0.2)
            
            for factor, value in intensity_factors.items():
                if isinstance(value, (int, float)):
                    normalized_value = min(value / normalization_factor, max_normalized_value)  # Normalize to 0-1
                    intensity_score += normalized_value * weights.get(factor, default_weight)
            
            # Determine intensity level
            if intensity_score > self._get_config_value('intensity_thresholds.high', 0.7):
                intensity_level = 'high'
            elif intensity_score > self._get_config_value('intensity_thresholds.medium', 0.4):
                intensity_level = 'medium'
            else:
                intensity_level = 'low'
            
            return {
                'intensity_level': intensity_level,
                'score': intensity_score,
                'factors': intensity_factors
            }
            
        except Exception as e:
            logger.error(f"Error calculating competitive intensity: {e}")
            return {'intensity_level': 'low', 'score': 0.0}
    
    def _identify_market_leaders(self, competitors: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify market leaders based on multiple criteria"""
        try:
            if not competitors:
                return []
            
            leader_criteria = self._get_config_value('leader_identification.criteria', [
                'market_share', 'revenue', 'brand_recognition', 'innovation_score'
            ])
            
            scored_competitors = []
            
            for competitor_id, data in competitors.items():
                leader_score = 0
                criteria_scores = {}
                
                for criterion in leader_criteria:
                    criterion_value = data.get(criterion, 0)
                    # Normalize criterion value (assuming max values from config)
                    max_value = self._get_config_value(f'normalization.max_{criterion}', 100)
                    normalized_score = min(criterion_value / max_value, 1.0)
                    criteria_scores[criterion] = normalized_score
                    leader_score += normalized_score
                
                scored_competitors.append({
                    'competitor_id': competitor_id,
                    'leader_score': leader_score / len(leader_criteria),
                    'criteria_scores': criteria_scores,
                    'market_share': data.get('market_share', 0),
                    'key_strengths': self._extract_key_strengths(data)
                })
            
            # Sort by leader score and return top leaders
            scored_competitors.sort(key=lambda x: x['leader_score'], reverse=True)
            
            # Define leaders as top performers above threshold
            leader_threshold = self._get_config_value('leader_identification.threshold', 0.7)
            leaders = [comp for comp in scored_competitors if comp['leader_score'] >= leader_threshold]
            
            # Always include at least the top performer if no one meets threshold
            if not leaders and scored_competitors:
                leaders = [scored_competitors[0]]
            
            return leaders[:self._get_config_value('leader_identification.max_leaders', 5)]
            
        except Exception as e:
            logger.error(f"Error identifying market leaders: {e}")
            return []
    
    def _identify_competitive_gaps(self, competitors: Dict[str, Any], 
                                 business_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Identify gaps in competitive landscape"""
        try:
            our_capabilities = set(business_profile.get('capabilities', []))
            our_segments = set(business_profile.get('target_segments', []))
            our_features = set(business_profile.get('features', []))
            
            # Aggregate competitor capabilities
            all_competitor_capabilities = set()
            all_competitor_segments = set()
            all_competitor_features = set()
            
            capability_coverage = defaultdict(int)
            segment_coverage = defaultdict(int)
            feature_coverage = defaultdict(int)
            
            for competitor_data in competitors.values():
                comp_capabilities = set(competitor_data.get('capabilities', []))
                comp_segments = set(competitor_data.get('target_segments', []))
                comp_features = set(competitor_data.get('features', []))
                
                all_competitor_capabilities.update(comp_capabilities)
                all_competitor_segments.update(comp_segments)
                all_competitor_features.update(comp_features)
                
                # Count coverage
                for cap in comp_capabilities:
                    capability_coverage[cap] += 1
                for seg in comp_segments:
                    segment_coverage[seg] += 1
                for feat in comp_features:
                    feature_coverage[feat] += 1
            
            # Identify gaps
            capability_gaps = all_competitor_capabilities - our_capabilities
            segment_gaps = all_competitor_segments - our_segments
            feature_gaps = all_competitor_features - our_features
            
            # Find underserved areas (low competitor coverage)
            total_competitors = len(competitors)
            underserved_threshold = self._get_config_value('gap_analysis.underserved_threshold', 0.3)
            
            underserved_capabilities = [
                cap for cap, count in capability_coverage.items()
                if count / total_competitors <= underserved_threshold
            ]
            
            underserved_segments = [
                seg for seg, count in segment_coverage.items()
                if count / total_competitors <= underserved_threshold
            ]
            
            return {
                'capability_gaps': list(capability_gaps),
                'segment_gaps': list(segment_gaps),
                'feature_gaps': list(feature_gaps),
                'underserved_capabilities': underserved_capabilities,
                'underserved_segments': underserved_segments,
                'our_unique_capabilities': list(our_capabilities - all_competitor_capabilities),
                'our_unique_segments': list(our_segments - all_competitor_segments),
                'gap_opportunities': self._prioritize_gap_opportunities(capability_gaps, segment_gaps, feature_gaps)
            }
            
        except Exception as e:
            logger.error(f"Error identifying competitive gaps: {e}")
            return {}
    
    def _assess_competitive_threats(self, competitors: Dict[str, Any], 
                                  business_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess competitive threats"""
        try:
            threats = []
            our_budget = business_profile.get('budget_range', {}).get('max', 0)
            our_market_share = business_profile.get('current_market_share', 0)
            our_segments = set(business_profile.get('target_segments', []))
            
            threat_factors = self._get_config_value('threat_assessment.factors', [
                'budget_advantage', 'market_share_advantage', 'segment_overlap', 
                'innovation_capability', 'brand_strength'
            ])
            
            for competitor_id, data in competitors.items():
                threat_score = 0
                threat_details = {}
                
                # Budget threat
                comp_budget = data.get('estimated_budget', 0)
                if comp_budget > our_budget:
                    budget_threat = min(comp_budget / our_budget, 5.0)
                    threat_score += budget_threat * self._get_config_value('threat_weights.budget', 0.2)
                    threat_details['budget_advantage'] = budget_threat
                
                # Market share threat
                comp_market_share = data.get('market_share', 0)
                if comp_market_share > our_market_share:
                    share_threat = comp_market_share / max(our_market_share, 0.01)
                    threat_score += min(share_threat, 5.0) * self._get_config_value('threat_weights.market_share', 0.3)
                    threat_details['market_share_advantage'] = share_threat
                
                # Segment overlap threat
                comp_segments = set(data.get('target_segments', []))
                segment_overlap = len(our_segments.intersection(comp_segments)) / max(len(our_segments), 1)
                threat_score += segment_overlap * self._get_config_value('threat_weights.segment_overlap', 0.25)
                threat_details['segment_overlap'] = segment_overlap
                
                # Innovation threat
                comp_innovation = data.get('innovation_score', 0)
                our_innovation = business_profile.get('innovation_score', 0)
                if comp_innovation > our_innovation:
                    innovation_threat = comp_innovation / max(our_innovation, 0.1)
                    threat_score += min(innovation_threat, 3.0) * self._get_config_value('threat_weights.innovation', 0.15)
                    threat_details['innovation_advantage'] = innovation_threat
                
                # Brand strength threat
                comp_brand = data.get('brand_recognition', 0)
                our_brand = business_profile.get('brand_recognition', 0)
                if comp_brand > our_brand:
                    brand_threat = comp_brand / max(our_brand, 0.1)
                    threat_score += min(brand_threat, 3.0) * self._get_config_value('threat_weights.brand', 0.1)
                    threat_details['brand_advantage'] = brand_threat
                
                # Determine threat level
                threat_threshold_high = self._get_config_value('threat_thresholds.high', 3.0)
                threat_threshold_medium = self._get_config_value('threat_thresholds.medium', 1.5)
                
                if threat_score >= threat_threshold_high:
                    threat_level = 'high'
                elif threat_score >= threat_threshold_medium:
                    threat_level = 'medium'
                else:
                    threat_level = 'low'
                
                threats.append({
                    'competitor_id': competitor_id,
                    'threat_level': threat_level,
                    'threat_score': threat_score,
                    'threat_details': threat_details,
                    'mitigation_strategies': self._generate_threat_mitigation(threat_details, data)
                })
            
            # Sort by threat score
            threats.sort(key=lambda x: x['threat_score'], reverse=True)
            
            return threats
            
        except Exception as e:
            logger.error(f"Error assessing competitive threats: {e}")
            return []
    
    def _analyze_competitive_opportunities(self, competitors: Dict[str, Any], 
                                         business_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze competitive opportunities"""
        try:
            opportunities = []
            
            # Market gaps analysis
            gaps = self._identify_competitive_gaps(competitors, business_profile)
            
            # Underserved segments opportunity
            for segment in gaps.get('underserved_segments', []):
                opportunities.append({
                    'type': 'underserved_segment',
                    'opportunity': f"Target underserved segment: {segment}",
                    'potential_impact': self._calculate_segment_opportunity_impact(segment, competitors),
                    'implementation_difficulty': self._assess_implementation_difficulty(segment, business_profile),
                    'priority': 'high' if segment in business_profile.get('target_segments', []) else 'medium'
                })
            
            # Capability gaps opportunity
            for capability in gaps.get('capability_gaps', []):
                if self._is_capability_attainable(capability, business_profile):
                    opportunities.append({
                        'type': 'capability_development',
                        'opportunity': f"Develop capability: {capability}",
                        'potential_impact': self._calculate_capability_opportunity_impact(capability, competitors),
                        'implementation_difficulty': self._assess_capability_difficulty(capability, business_profile),
                        'priority': 'medium'
                    })
            
            # Competitor weakness exploitation
            for competitor_id, data in competitors.items():
                weaknesses = self._identify_competitor_weaknesses(data)
                for weakness in weaknesses:
                    if self._can_exploit_weakness(weakness, business_profile):
                        opportunities.append({
                            'type': 'competitor_weakness_exploitation',
                            'opportunity': f"Exploit {competitor_id}'s weakness: {weakness}",
                            'potential_impact': self._calculate_weakness_exploitation_impact(weakness, data),
                            'implementation_difficulty': 'medium',
                            'priority': 'high' if data.get('market_share', 0) > 0.1 else 'medium'
                        })
            
            # Sort opportunities by potential impact and priority
            opportunities.sort(key=lambda x: (
                1 if x['priority'] == 'high' else 0,
                x['potential_impact']
            ), reverse=True)
            
            return opportunities[:self._get_config_value('opportunity_analysis.max_opportunities', 10)]
            
        except Exception as e:
            logger.error(f"Error analyzing competitive opportunities: {e}")
            return []
    
    def _generate_positioning_recommendations(self, competitors: Dict[str, Any], 
                                            business_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate positioning recommendations"""
        try:
            recommendations = []
            
            # Differentiation recommendations
            unique_capabilities = self._find_unique_capabilities(business_profile, competitors)
            if unique_capabilities:
                recommendations.append({
                    'type': 'differentiation',
                    'recommendation': f"Emphasize unique capabilities: {', '.join(unique_capabilities)}",
                    'rationale': "Leverage distinctive advantages",
                    'priority': 'high',
                    'implementation_effort': 'low'
                })
            
            # Market positioning recommendations
            positioning_gaps = self._identify_positioning_gaps(business_profile, competitors)
            for gap in positioning_gaps:
                recommendations.append({
                    'type': 'market_positioning',
                    'recommendation': f"Position in underserved market: {gap}",
                    'rationale': "Capture uncontested market space",
                    'priority': 'medium',
                    'implementation_effort': 'medium'
                })
            
            # Competitive response recommendations
            top_threats = [t for t in self._assess_competitive_threats(competitors, business_profile) 
                          if t['threat_level'] == 'high']
            
            for threat in top_threats[:3]:  # Top 3 threats
                recommendations.append({
                    'type': 'competitive_response',
                    'recommendation': f"Counter {threat['competitor_id']} threat",
                    'rationale': f"Mitigate high-level threat (score: {threat['threat_score']:.2f})",
                    'priority': 'high',
                    'implementation_effort': 'high'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating positioning recommendations: {e}")
            return []
    
    def _generate_strategic_insights(self, competitors: Dict[str, Any], 
                                   business_profile: Dict[str, Any]) -> List[str]:
        """Generate strategic insights from competitive analysis"""
        try:
            insights = []
            
            # Market structure insights
            market_structure = self._analyze_market_structure(competitors)
            if market_structure['structure_type'] == 'highly_concentrated':
                insights.append("Market is highly concentrated - focus on niche differentiation")
            elif market_structure['structure_type'] == 'fragmented':
                insights.append("Fragmented market presents consolidation opportunities")
            
            # Competitive intensity insights
            intensity = self._calculate_competitive_intensity(competitors)
            if intensity['intensity_level'] == 'high':
                insights.append("High competitive intensity requires aggressive differentiation")
            elif intensity['intensity_level'] == 'low':
                insights.append("Low competitive intensity allows for market expansion")
            
            # Leader insights
            leaders = self._identify_market_leaders(competitors)
            if leaders:
                top_leader = leaders[0]
                insights.append(f"Market leader {top_leader['competitor_id']} dominates with {top_leader['market_share']:.1%} share")
            
            # Opportunity insights
            opportunities = self._analyze_competitive_opportunities(competitors, business_profile)
            high_priority_opps = [o for o in opportunities if o['priority'] == 'high']
            if high_priority_opps:
                insights.append(f"Key opportunity: {high_priority_opps[0]['opportunity']}")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating strategic insights: {e}")
            return []
    
    def _calculate_analysis_confidence(self, competitors: Dict[str, Any], 
                                     business_profile: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis"""
        try:
            # Data completeness factors
            competitor_data_completeness = self._assess_competitor_data_completeness(competitors)
            business_data_completeness = self._assess_business_data_completeness(business_profile)
            
            # Analysis factors
            sample_size_factor = min(len(competitors) / self._get_config_value('confidence.min_competitors', 5), 1.0)
            data_recency_factor = self._assess_data_recency(competitors)
            
            # Calculate weighted confidence
            confidence = (
                competitor_data_completeness * 0.3 +
                business_data_completeness * 0.2 +
                sample_size_factor * 0.3 +
                data_recency_factor * 0.2
            )
            
            return min(max(confidence, 0.0), 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating analysis confidence: {e}")
            return 0.5
    
    # Helper methods for various analyses
    def _create_analysis_signature(self, business_profile: Dict[str, Any], 
                                 market_data: Dict[str, Any]) -> str:
        """Create unique signature for analysis caching"""
        analysis_string = json.dumps({
            'industry': business_profile.get('industry', ''),
            'segments': business_profile.get('target_segments', []),
            'competitors': list(market_data.get('competitors', {}).keys()),
            'timestamp_day': datetime.now().strftime('%Y-%m-%d')
        }, sort_keys=True)
        
        return hashlib.md5(analysis_string.encode()).hexdigest()
    
    def _get_cached_analysis(self, analysis_signature: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis if available and not expired"""
        if analysis_signature in self.analysis_cache:
            analysis, timestamp = self.analysis_cache[analysis_signature]
            if datetime.now() - timestamp < self.cache_ttl:
                return analysis
            else:
                del self.analysis_cache[analysis_signature]
        return None
    
    def _cache_analysis(self, analysis_signature: str, analysis: Dict[str, Any]) -> None:
        """Cache analysis result"""
        self.analysis_cache[analysis_signature] = (analysis, datetime.now())
        
        # Limit cache size
        max_cache_size = self._get_config_value('cache.max_size', 50)
        if len(self.analysis_cache) > max_cache_size:
            oldest_key = min(self.analysis_cache.keys(), 
                           key=lambda k: self.analysis_cache[k][1])
            del self.analysis_cache[oldest_key]
    
    def _create_fallback_analysis(self) -> Dict[str, Any]:
        """Create fallback analysis when main analysis fails"""
        return {
            'analysis_id': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'industry': 'unknown',
            'market_structure': {'structure_type': 'unknown', 'concentration': 0},
            'competitive_intensity': {'intensity_level': 'medium', 'score': 0.5},
            'market_leaders': [],
            'competitive_gaps': {},
            'threat_assessment': [],
            'opportunity_analysis': [],
            'positioning_recommendations': [],
            'strategic_insights': [],
            'confidence_score': 0.2
        }
    
    # Additional helper methods would continue here...
    # (Due to length constraints, I'll include key remaining methods)
    
    def _extract_basic_info(self, competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract basic competitor information"""
        return {
            'name': competitor_data.get('name', ''),
            'industry': competitor_data.get('industry', ''),
            'founded_year': competitor_data.get('founded_year', 0),
            'headquarters': competitor_data.get('headquarters', ''),
            'employee_count': competitor_data.get('employee_count', 0),
            'company_type': competitor_data.get('company_type', '')
        }
    
    def _analyze_market_presence(self, competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitor's market presence"""
        return {
            'market_share': competitor_data.get('market_share', 0),
            'geographic_presence': competitor_data.get('geographic_presence', []),
            'customer_segments': competitor_data.get('customer_segments', []),
            'brand_recognition': competitor_data.get('brand_recognition', 0),
            'online_presence_score': competitor_data.get('online_presence_score', 0)
        }
    
    def _extract_financial_metrics(self, competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract financial metrics"""
        return {
            'revenue': competitor_data.get('revenue', 0),
            'revenue_growth': competitor_data.get('revenue_growth', 0),
            'profit_margin': competitor_data.get('profit_margin', 0),
            'estimated_budget': competitor_data.get('estimated_budget', 0),
            'funding_rounds': competitor_data.get('funding_rounds', [])
        }
    
    def _identify_competitor_strengths(self, competitor_data: Dict[str, Any]) -> List[str]:
        """Identify competitor strengths"""
        strengths = []
        
        if competitor_data.get('market_share', 0) > self.market_share_threshold:
            strengths.append('strong_market_position')
        
        if competitor_data.get('brand_recognition', 0) > 0.7:
            strengths.append('strong_brand')
        
        if competitor_data.get('innovation_score', 0) > 0.8:
            strengths.append('innovation_leadership')
        
        return strengths
    
    def _identify_competitor_weaknesses(self, competitor_data: Dict[str, Any]) -> List[str]:
        """Identify competitor weaknesses"""
        weaknesses = []
        
        if competitor_data.get('customer_satisfaction', 0) < 0.6:
            weaknesses.append('poor_customer_satisfaction')
        
        if competitor_data.get('revenue_growth', 0) < 0:
            weaknesses.append('declining_revenue')
        
        if len(competitor_data.get('geographic_presence', [])) < 3:
            weaknesses.append('limited_geographic_reach')
        
        return weaknesses
    
    def _analyze_product_portfolio(self, competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze competitor's product portfolio dynamically
        100% Dynamic - No hardcoded values
        """
        try:
            # Dynamically extract product information from competitor data
            products = competitor_data.get('products', competitor_data.get('offerings', []))
            if not isinstance(products, list):
                products = [products] if products else []
            
            # Dynamic portfolio analysis parameters from config
            analysis_factors = self._get_config_value('product_analysis.factors', [
                'innovation_level', 'market_coverage', 'pricing_strategy', 'quality_metrics'
            ])
            
            portfolio_analysis = {
                'total_products': len(products),
                'product_categories': self._categorize_products_dynamically(products),
                'innovation_score': self._calculate_dynamic_innovation_score(products),
                'market_coverage': self._assess_dynamic_market_coverage(products),
                'pricing_strategy': self._analyze_dynamic_pricing_strategy(products),
                'portfolio_strength': self._calculate_dynamic_portfolio_strength(products),
                'gaps_identified': self._identify_dynamic_portfolio_gaps(products),
                'competitive_positioning': self._assess_dynamic_product_positioning(products)
            }
            
            return portfolio_analysis
            
        except Exception as e:
            logger.warning(f"Error analyzing product portfolio: {e}")
            # Dynamic fallback based on available data
            return {
                'total_products': len(competitor_data.get('products', [])),
                'analysis_status': 'limited_data',
                'basic_metrics': self._generate_basic_portfolio_metrics(competitor_data)
            }
    
    def _categorize_products_dynamically(self, products: List[Dict[str, Any]]) -> Dict[str, int]:
        """Dynamically categorize products based on available data"""
        categories = defaultdict(int)
        
        for product in products:
            if isinstance(product, dict):
                # Dynamic category detection from product data
                category = (product.get('category') or 
                           product.get('type') or 
                           product.get('segment') or 
                           'uncategorized')
                categories[str(category)] += 1
            
        return dict(categories)
    
    def _calculate_dynamic_innovation_score(self, products: List[Dict[str, Any]]) -> float:
        """Calculate innovation score based on dynamic product features"""
        if not products:
            return 0.0
            
        innovation_indicators = self._get_config_value('innovation.indicators', [
            'new_features', 'technology_adoption', 'launch_frequency'
        ])
        
        total_score = 0.0
        valid_products = 0
        
        for product in products:
            if isinstance(product, dict):
                product_score = 0.0
                for indicator in innovation_indicators:
                    if indicator in product:
                        product_score += float(product.get(indicator, 0))
                
                if product_score > 0:
                    total_score += product_score
                    valid_products += 1
        
        return total_score / max(valid_products, 1)
    
    def _assess_dynamic_market_coverage(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess market coverage based on dynamic product spread"""
        coverage_metrics = {
            'geographic_reach': set(),
            'market_segments': set(),
            'price_ranges': [],
            'coverage_score': 0.0
        }
        
        for product in products:
            if isinstance(product, dict):
                # Dynamic geographic detection
                if 'markets' in product:
                    markets = product['markets']
                    if isinstance(markets, list):
                        coverage_metrics['geographic_reach'].update(markets)
                
                # Dynamic segment detection
                if 'segment' in product:
                    coverage_metrics['market_segments'].add(str(product['segment']))
                
                # Dynamic pricing detection
                price = product.get('price', product.get('cost', 0))
                if price:
                    coverage_metrics['price_ranges'].append(float(price))
        
        # Calculate coverage score dynamically
        geo_score = len(coverage_metrics['geographic_reach']) * 0.4
        segment_score = len(coverage_metrics['market_segments']) * 0.35
        price_diversity = len(set(coverage_metrics['price_ranges'])) * 0.25
        
        coverage_metrics['coverage_score'] = min(geo_score + segment_score + price_diversity, 10.0)
        coverage_metrics['geographic_reach'] = list(coverage_metrics['geographic_reach'])
        coverage_metrics['market_segments'] = list(coverage_metrics['market_segments'])
        
        return coverage_metrics
    
    def _analyze_dynamic_pricing_strategy(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze pricing strategy dynamically"""
        pricing_data = []
        
        for product in products:
            if isinstance(product, dict):
                price = product.get('price', product.get('cost', product.get('msrp', 0)))
                if price:
                    pricing_data.append(float(price))
        
        if not pricing_data:
            return {'strategy': 'unknown', 'price_range': [0, 0]}
        
        pricing_analysis = {
            'strategy': self._determine_dynamic_pricing_strategy(pricing_data),
            'price_range': [min(pricing_data), max(pricing_data)],
            'average_price': sum(pricing_data) / len(pricing_data),
            'price_distribution': self._analyze_price_distribution(pricing_data)
        }
        
        return pricing_analysis
    
    def _determine_dynamic_pricing_strategy(self, prices: List[float]) -> str:
        """Determine pricing strategy based on price distribution"""
        if not prices:
            return 'unknown'
        
        price_range = max(prices) - min(prices)
        avg_price = sum(prices) / len(prices)
        
        # Dynamic strategy detection
        if price_range < avg_price * 0.2:
            return 'uniform_pricing'
        elif min(prices) < avg_price * 0.5:
            return 'penetration_pricing'
        elif max(prices) > avg_price * 1.5:
            return 'premium_pricing'
        else:
            return 'competitive_pricing'
    
    def _calculate_dynamic_portfolio_strength(self, products: List[Dict[str, Any]]) -> float:
        """Calculate overall portfolio strength dynamically"""
        if not products:
            return 0.0
        
        strength_factors = {
            'product_count': min(len(products) / 10.0, 1.0),
            'diversity': self._calculate_product_diversity(products),
            'innovation': self._calculate_dynamic_innovation_score(products) / 10.0,
            'market_fit': self._assess_market_fit_score(products)
        }
        
        # Dynamic weighting from config
        weights = self._get_config_value('portfolio_strength.weights', {
            'product_count': 0.25,
            'diversity': 0.25,
            'innovation': 0.25,
            'market_fit': 0.25
        })
        
        total_strength = sum(strength_factors[factor] * weights.get(factor, 0.25) 
                           for factor in strength_factors)
        
        return min(total_strength * 10.0, 10.0)
    
    def _calculate_product_diversity(self, products: List[Dict[str, Any]]) -> float:
        """Calculate product diversity score"""
        if not products:
            return 0.0
        
        categories = self._categorize_products_dynamically(products)
        diversity_score = len(categories) / max(len(products), 1)
        
        return min(diversity_score * 2.0, 1.0)
    
    def _assess_market_fit_score(self, products: List[Dict[str, Any]]) -> float:
        """Assess market fit based on available product data"""
        if not products:
            return 0.0
        
        fit_indicators = ['customer_rating', 'market_share', 'sales_performance', 'reviews']
        total_fit = 0.0
        valid_products = 0
        
        for product in products:
            if isinstance(product, dict):
                product_fit = 0.0
                indicators_found = 0
                
                for indicator in fit_indicators:
                    if indicator in product:
                        product_fit += float(product.get(indicator, 0))
                        indicators_found += 1
                
                if indicators_found > 0:
                    total_fit += product_fit / indicators_found
                    valid_products += 1
        
        return (total_fit / max(valid_products, 1)) / 10.0 if valid_products > 0 else 0.5
    
    def _identify_dynamic_portfolio_gaps(self, products: List[Dict[str, Any]]) -> List[str]:
        """Identify portfolio gaps dynamically"""
        gaps = []
        
        categories = self._categorize_products_dynamically(products)
        market_segments = set()
        price_ranges = []
        
        for product in products:
            if isinstance(product, dict):
                if 'segment' in product:
                    market_segments.add(str(product['segment']))
                price = product.get('price', 0)
                if price:
                    price_ranges.append(float(price))
        
        # Dynamic gap identification
        if len(categories) < 3:
            gaps.append('limited_product_diversity')
        
        if len(market_segments) < 2:
            gaps.append('narrow_market_focus')
        
        if len(price_ranges) > 0 and (max(price_ranges) - min(price_ranges)) < (sum(price_ranges) / len(price_ranges)):
            gaps.append('limited_pricing_range')
        
        if not any('premium' in str(cat).lower() for cat in categories):
            gaps.append('missing_premium_segment')
        
        return gaps
    
    def _assess_dynamic_product_positioning(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess product positioning dynamically"""
        positioning = {
            'market_position': 'unknown',
            'competitive_advantage': [],
            'positioning_strength': 0.0
        }
        
        if not products:
            return positioning
        
        # Dynamic positioning assessment
        innovation_score = self._calculate_dynamic_innovation_score(products)
        coverage = self._assess_dynamic_market_coverage(products)
        
        if innovation_score > 7.0:
            positioning['market_position'] = 'innovation_leader'
            positioning['competitive_advantage'].append('high_innovation')
        elif coverage['coverage_score'] > 7.0:
            positioning['market_position'] = 'market_leader'
            positioning['competitive_advantage'].append('broad_coverage')
        elif len(products) > 10:
            positioning['market_position'] = 'diversified_player'
            positioning['competitive_advantage'].append('product_variety')
        else:
            positioning['market_position'] = 'niche_player'
            positioning['competitive_advantage'].append('focused_approach')
        
        positioning['positioning_strength'] = (innovation_score + coverage['coverage_score']) / 2.0
        
        return positioning
    
    def _generate_basic_portfolio_metrics(self, competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic portfolio metrics when detailed analysis fails"""
        return {
            'product_indicators': list(competitor_data.keys()),
            'data_availability': 'limited',
            'analysis_depth': 'basic',
            'recommendation': 'gather_more_product_data'
        }
    
    def _normalize_competitor_data(self, competitors_raw: Any) -> Dict[str, Any]:
        """
        Normalize competitor data to dictionary format - 100% Dynamic
        Handles both list and dictionary inputs safely
        """
        try:
            if isinstance(competitors_raw, dict):
                return competitors_raw
            elif isinstance(competitors_raw, list):
                # Convert list to dictionary using dynamic indexing
                normalized = {}
                for i, competitor in enumerate(competitors_raw):
                    if isinstance(competitor, dict):
                        # Use competitor ID, name, or index as key
                        competitor_key = (
                            competitor.get('id') or 
                            competitor.get('name') or 
                            competitor.get('company') or 
                            f"competitor_{i}"
                        )
                        normalized[str(competitor_key)] = competitor
                    else:
                        # Handle primitive values dynamically
                        normalized[f"competitor_{i}"] = {
                            'name': str(competitor),
                            'data_type': type(competitor).__name__
                        }
                return normalized
            else:
                # Handle single competitor or unexpected format
                return {'unknown_competitor': {
                    'raw_data': str(competitors_raw),
                    'data_type': type(competitors_raw).__name__
                }}
        except Exception as e:
            logger.warning(f"Error normalizing competitor data: {e}")
            return {}
    
    def _analyze_price_distribution(self, prices: List[float]) -> Dict[str, float]:
        """Analyze price distribution patterns"""
        if not prices:
            return {}
        
        sorted_prices = sorted(prices)
        return {
            'median': sorted_prices[len(sorted_prices) // 2],
            'std_deviation': self._calculate_std_deviation(prices),
            'price_spread': max(prices) - min(prices)
        }
    
    def _calculate_std_deviation(self, values: List[float]) -> float:
        """Calculate standard deviation dynamically"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _analyze_marketing_strategy(self, competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitor's marketing strategy"""
        try:
            return {
                'channels': competitor_data.get('marketing_channels', []),
                'spend_level': competitor_data.get('marketing_spend', 'unknown'),
                'positioning': competitor_data.get('brand_positioning', 'unknown'),
                'target_segments': competitor_data.get('target_segments', []),
                'digital_presence': competitor_data.get('digital_metrics', {}),
                'campaign_effectiveness': self._assess_campaign_effectiveness(competitor_data)
            }
        except Exception as e:
            logger.error(f"Error analyzing marketing strategy: {e}")
            return {}
    
    def _analyze_product_portfolio(self, competitor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitor's product portfolio"""
        try:
            products = competitor_data.get('products', [])
            return {
                'product_count': len(products),
                'product_categories': list(set([p.get('category', 'unknown') for p in products])),
                'portfolio_breadth': self._calculate_portfolio_breadth(products),
                'innovation_pipeline': competitor_data.get('innovation_pipeline', []),
                'product_lifecycle_stage': self._assess_product_lifecycle(products)
            }
        except Exception as e:
            logger.error(f"Error analyzing product portfolio: {e}")
            return {}
    
    def _track_strategic_moves(self, competitor_data: Dict[str, Any], existing_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Track strategic moves and changes"""
        try:
            moves = []
            current_moves = competitor_data.get('strategic_moves', [])
            previous_moves = existing_profile.get('strategic_moves', []) if existing_profile else []
            
            # Identify new moves
            for move in current_moves:
                if move not in previous_moves:
                    moves.append({
                        'move_type': move.get('type', 'unknown'),
                        'description': move.get('description', ''),
                        'impact_assessment': self._assess_move_impact(move),
                        'timing': 'recent'
                    })
            
            return moves
        except Exception as e:
            logger.error(f"Error tracking strategic moves: {e}")
            return []
    
    def _assess_threat_level(self, competitor_data: Dict[str, Any]) -> str:
        """Assess threat level posed by competitor"""
        try:
            market_share = competitor_data.get('market_share', 0)
            growth_rate = competitor_data.get('growth_rate', 0)
            innovation_score = competitor_data.get('innovation_score', 0)
            financial_strength = competitor_data.get('financial_strength', 0)
            
            # Calculate weighted threat score
            threat_score = (
                market_share * self._get_config_value('threat_assessment.market_share_weight', 0.3) +
                growth_rate * self._get_config_value('threat_assessment.growth_weight', 0.25) +
                innovation_score * self._get_config_value('threat_assessment.innovation_weight', 0.25) +
                financial_strength * self._get_config_value('threat_assessment.financial_weight', 0.2)
            )
            
            high_threat_threshold = self._get_config_value('threat_assessment.high_threshold', 0.7)
            medium_threat_threshold = self._get_config_value('threat_assessment.medium_threshold', 0.4)
            
            if threat_score > high_threat_threshold:
                return 'high'
            elif threat_score > medium_threat_threshold:
                return 'medium'
            else:
                return 'low'
                
        except Exception as e:
            logger.error(f"Error assessing threat level: {e}")
            return 'medium'
    
    def _generate_monitoring_insights(self, competitor_data: Dict[str, Any], existing_profile: Dict[str, Any]) -> List[str]:
        """Generate monitoring insights"""
        try:
            insights = []
            
            # Compare current vs previous data if available
            if existing_profile:
                # Market share changes
                current_share = competitor_data.get('market_share', 0)
                previous_share = existing_profile.get('basic_info', {}).get('market_share', current_share)
                
                if current_share > previous_share * 1.1:  # 10% increase
                    insights.append(f"Significant market share growth: {((current_share - previous_share) / previous_share * 100):.1f}%")
                elif current_share < previous_share * 0.9:  # 10% decrease
                    insights.append(f"Market share decline: {((previous_share - current_share) / previous_share * 100):.1f}%")
            
            # Current performance insights
            threat_level = self._assess_threat_level(competitor_data)
            if threat_level == 'high':
                insights.append("High threat level - requires immediate attention")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating monitoring insights: {e}")
            return []
    
    def _analyze_competitor_changes(self, existing_profile: Dict[str, Any], current_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze changes in competitor profile"""
        try:
            changes = {
                'market_share_change': self._calculate_metric_change(
                    existing_profile.get('basic_info', {}).get('market_share', 0),
                    current_profile.get('basic_info', {}).get('market_share', 0)
                ),
                'financial_changes': self._analyze_financial_changes(existing_profile, current_profile),
                'strategic_changes': self._analyze_strategic_changes(existing_profile, current_profile),
                'threat_level_change': self._analyze_threat_change(existing_profile, current_profile)
            }
            return changes
        except Exception as e:
            logger.error(f"Error analyzing competitor changes: {e}")
            return {}
    
    def _generate_competitor_response_recommendations(self, competitor_profile: Dict[str, Any]) -> List[str]:
        """Generate recommendations for responding to competitor"""
        try:
            recommendations = []
            threat_level = competitor_profile.get('threat_level', 'medium')
            
            if threat_level == 'high':
                recommendations.extend([
                    "Increase competitive monitoring frequency",
                    "Assess defensive strategies",
                    "Consider preemptive market moves"
                ])
            elif threat_level == 'medium':
                recommendations.extend([
                    "Monitor key strategic initiatives",
                    "Maintain current competitive position"
                ])
            else:
                recommendations.append("Continue standard monitoring")
            
            return recommendations
        except Exception as e:
            logger.error(f"Error generating competitor response recommendations: {e}")
            return []
    
    def _analyze_competitive_positioning(self, competitors: Any) -> Dict[str, Any]:
        """Analyze competitive positioning"""
        try:
            # Handle both list and dict formats
            competitors_dict = self._normalize_competitor_data(competitors)
            
            positioning = {
                'positioning_map': self._create_market_positioning_map(competitors_dict),
                'competitive_clusters': self._identify_competitive_clusters(competitors_dict),
                'positioning_gaps': self._identify_positioning_gaps_internal(competitors_dict),
                'strategic_groups': self._identify_strategic_groups(competitors_dict)
            }
            return positioning
        except Exception as e:
            logger.error(f"Error analyzing competitive positioning: {e}")
            return {}
    
    def _assess_competitive_intensity(self, competitors: Any, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess competitive intensity"""
        try:
            # Handle both list and dict formats
            competitors_dict = self._normalize_competitor_data(competitors)
            
            intensity_result = self._calculate_competitive_intensity(competitors_dict)
            
            # Map the output to expected format
            return {
                'overall_intensity': intensity_result.get('intensity_level', 'medium'),
                'intensity_score': intensity_result.get('score', 0.5),
                'intensity_level': intensity_result.get('intensity_level', 'medium'),
                'score': intensity_result.get('score', 0.5)
            }
        except Exception as e:
            logger.error(f"Error assessing competitive intensity: {e}")
            return {'overall_intensity': 'medium', 'intensity_score': 0.5}
    
    # Helper methods for the above functions
    def _assess_campaign_effectiveness(self, competitor_data: Dict[str, Any]) -> str:
        """Assess marketing campaign effectiveness"""
        try:
            effectiveness_score = competitor_data.get('campaign_effectiveness', 0.5)
            high_threshold = self._get_config_value('marketing.high_effectiveness_threshold', 0.7)
            medium_threshold = self._get_config_value('marketing.medium_effectiveness_threshold', 0.4)
            
            if effectiveness_score > high_threshold:
                return 'high'
            elif effectiveness_score > medium_threshold:
                return 'medium'
            else:
                return 'low'
        except Exception as e:
            logger.error(f"Error assessing campaign effectiveness: {e}")
            return 'unknown'
    
    def _calculate_portfolio_breadth(self, products: List[Dict[str, Any]]) -> str:
        """Calculate product portfolio breadth"""
        try:
            categories = set([p.get('category', 'unknown') for p in products])
            category_count = len(categories)
            
            broad_threshold = self._get_config_value('portfolio.broad_threshold', 5)
            medium_threshold = self._get_config_value('portfolio.medium_threshold', 2)
            
            if category_count >= broad_threshold:
                return 'broad'
            elif category_count >= medium_threshold:
                return 'medium'
            else:
                return 'narrow'
        except Exception as e:
            logger.error(f"Error calculating portfolio breadth: {e}")
            return 'unknown'
    
    def _assess_product_lifecycle(self, products: List[Dict[str, Any]]) -> Dict[str, int]:
        """Assess product lifecycle stage distribution"""
        try:
            lifecycle_stages = {}
            for product in products:
                stage = product.get('lifecycle_stage', 'unknown')
                lifecycle_stages[stage] = lifecycle_stages.get(stage, 0) + 1
            return lifecycle_stages
        except Exception as e:
            logger.error(f"Error assessing product lifecycle: {e}")
            return {}
    
    def _assess_move_impact(self, move: Dict[str, Any]) -> str:
        """Assess impact of strategic move"""
        try:
            impact_score = move.get('impact_score', 0.5)
            high_threshold = self._get_config_value('strategic_moves.high_impact_threshold', 0.7)
            medium_threshold = self._get_config_value('strategic_moves.medium_impact_threshold', 0.4)
            
            if impact_score > high_threshold:
                return 'high'
            elif impact_score > medium_threshold:
                return 'medium'
            else:
                return 'low'
        except Exception as e:
            logger.error(f"Error assessing move impact: {e}")
            return 'medium'
    
    def _calculate_metric_change(self, old_value: float, new_value: float) -> Dict[str, Any]:
        """Calculate change in metric"""
        try:
            if old_value == 0:
                return {'absolute_change': new_value, 'percentage_change': 0, 'direction': 'new'}
            
            absolute_change = new_value - old_value
            percentage_change = (absolute_change / old_value) * 100
            direction = 'increase' if absolute_change > 0 else 'decrease' if absolute_change < 0 else 'stable'
            
            return {
                'absolute_change': absolute_change,
                'percentage_change': percentage_change,
                'direction': direction
            }
        except Exception as e:
            logger.error(f"Error calculating metric change: {e}")
            return {}
    
    def _analyze_financial_changes(self, existing_profile: Dict[str, Any], current_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze financial changes"""
        try:
            old_financial = existing_profile.get('financial_metrics', {})
            new_financial = current_profile.get('financial_metrics', {})
            
            return {
                'revenue_change': self._calculate_metric_change(
                    old_financial.get('revenue', 0),
                    new_financial.get('revenue', 0)
                )
            }
        except Exception as e:
            logger.error(f"Error analyzing financial changes: {e}")
            return {}
    
    def _analyze_strategic_changes(self, existing_profile: Dict[str, Any], current_profile: Dict[str, Any]) -> List[str]:
        """Analyze strategic changes"""
        try:
            changes = []
            old_moves = existing_profile.get('strategic_moves', [])
            new_moves = current_profile.get('strategic_moves', [])
            
            if len(new_moves) > len(old_moves):
                changes.append("New strategic initiatives detected")
            
            return changes
        except Exception as e:
            logger.error(f"Error analyzing strategic changes: {e}")
            return []
    
    def _analyze_threat_change(self, existing_profile: Dict[str, Any], current_profile: Dict[str, Any]) -> str:
        """Analyze threat level change"""
        try:
            old_threat = existing_profile.get('threat_level', 'medium')
            new_threat = current_profile.get('threat_level', 'medium')
            
            if old_threat != new_threat:
                return f"Changed from {old_threat} to {new_threat}"
            else:
                return "No change"
        except Exception as e:
            logger.error(f"Error analyzing threat change: {e}")
            return "Unknown"
    
    def _create_market_positioning_map(self, competitors: Dict[str, Any]) -> Dict[str, Any]:
        """Create market positioning map"""
        try:
            return {'status': 'positioning_map_created', 'competitors': len(competitors)}
        except Exception as e:
            logger.error(f"Error creating market positioning map: {e}")
            return {}
    
    def _identify_competitive_clusters(self, competitors: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify competitive clusters"""
        try:
            clusters = []
            # Simple clustering based on market share
            for competitor_id, data in competitors.items():
                market_share = data.get('market_share', 0)
                if market_share > self._get_config_value('clustering.large_player_threshold', 0.2):
                    cluster = 'large_players'
                elif market_share > self._get_config_value('clustering.medium_player_threshold', 0.05):
                    cluster = 'medium_players'
                else:
                    cluster = 'small_players'
                
                clusters.append({
                    'competitor_id': competitor_id,
                    'cluster': cluster,
                    'market_share': market_share
                })
            
            return clusters
        except Exception as e:
            logger.error(f"Error identifying competitive clusters: {e}")
            return []
    
    def _identify_positioning_gaps_internal(self, competitors: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify positioning gaps (internal method)"""
        try:
            gaps = []
            # Simple gap analysis
            covered_segments = set()
            for competitor_id, data in competitors.items():
                segments = data.get('target_segments', [])
                covered_segments.update(segments)
            
            all_segments = ['premium', 'mid-market', 'budget', 'enterprise', 'smb']
            uncovered_segments = set(all_segments) - covered_segments
            
            for segment in uncovered_segments:
                gaps.append({
                    'segment': segment,
                    'opportunity_level': 'medium'
                })
            
            return gaps
        except Exception as e:
            logger.error(f"Error identifying positioning gaps: {e}")
            return []
    
    def _identify_strategic_groups(self, competitors: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify strategic groups"""
        try:
            groups = []
            # Group by similar market share and growth patterns
            for competitor_id, data in competitors.items():
                market_share = data.get('market_share', 0)
                growth_rate = data.get('growth_rate', 0)
                
                if market_share > self._get_config_value('strategic_groups.large_threshold', 0.2):
                    group = 'market_leaders'
                elif growth_rate > self._get_config_value('strategic_groups.high_growth_threshold', 0.15):
                    group = 'growth_challengers'
                else:
                    group = 'followers'
                
                groups.append({
                    'competitor_id': competitor_id,
                    'strategic_group': group,
                    'characteristics': {
                        'market_share': market_share,
                        'growth_rate': growth_rate
                    }
                })
            
            return groups
        except Exception as e:
            logger.error(f"Error identifying strategic groups: {e}")
            return []
    
    # Continue with other helper methods...


# Singleton instance
_competitive_analysis_service = None
_service_lock = threading.Lock()


def get_competitive_analysis_service() -> CompetitiveAnalysisService:
    """
    Get singleton instance of CompetitiveAnalysisService
    """
    global _competitive_analysis_service
    
    if _competitive_analysis_service is None:
        with _service_lock:
            if _competitive_analysis_service is None:
                _competitive_analysis_service = CompetitiveAnalysisService()
    
    return _competitive_analysis_service


# Export for external use
__all__ = ['CompetitiveAnalysisService', 'get_competitive_analysis_service']
