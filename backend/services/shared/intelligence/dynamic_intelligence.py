"""
Dynamic Intelligence Engine - Shared Service
Advanced intelligence engine for real-time pattern recognition and adaptive learning
"""

import json
import hashlib
import logging
import threading
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict

from backend.services.shared.semantic import SemanticVector
from backend.config.config_manager import get_config_manager

logger = logging.getLogger(__name__)


class DynamicIntelligenceEngine:
 """Advanced intelligence engine for real-time pattern recognition"""

 def __init__(self):
 self.config_manager = get_config_manager()
 self.pattern_memory: Dict[str, Dict[str, Any]] = defaultdict(dict)
 self.learning_cache: Dict[str, Any] = {}
 self.semantic_networks: Dict[str, Dict[str, SemanticVector]] = defaultdict(dict)
 self.context_correlations: Dict[str, Dict[str, float]] = defaultdict(dict)
 self.success_patterns: Dict[str, Dict[str, Any]] = {}

 # Get default adaptation weight from configuration
 pattern_config = self.config_manager.get('intelligence_engine.pattern_recognition', {})
 default_weight = pattern_config.get('min_adaptation_weight', 1.0)
 self.adaptation_weights: Dict[str, float] = defaultdict(lambda: default_weight)
 self.lock = threading.RLock()

 def learn_pattern(self, context: str, pattern: Dict[str, Any], outcome_score: float = None):
 """Learn and store patterns for future analysis improvement using dynamic configuration"""
 pattern_config = self.config_manager.get('intelligence_engine.pattern_recognition', {})

 # Use dynamic default outcome score
 if outcome_score is None:
 outcome_score = pattern_config.get('default_outcome_score', 0.5)

 with self.lock:
 pattern_hash = self._generate_pattern_hash(context, pattern)

 if pattern_hash not in self.pattern_memory[context]:
 self.pattern_memory[context][pattern_hash] = {
 'pattern': pattern,
 'frequency': 0,
 'success_rate': [],
 'adaptations': [],
 'first_seen': datetime.now().isoformat(),
 'last_updated': datetime.now().isoformat()
 }

 pattern_data = self.pattern_memory[context][pattern_hash]
 pattern_data['frequency'] += 1
 pattern_data['success_rate'].append(outcome_score)
 pattern_data['last_updated'] = datetime.now().isoformat()

 # Update adaptation weights based on success using dynamic configuration
 avg_success = sum(pattern_data['success_rate']) / len(pattern_data['success_rate'])
 min_weight = pattern_config.get('min_adaptation_weight', 0.1)
 max_weight = pattern_config.get('max_adaptation_weight', 2.0)
 weight_multiplier = pattern_config.get('adaptation_multiplier', 2.0)

 self.adaptation_weights[pattern_hash] = max(min_weight, min(max_weight, avg_success * weight_multiplier))

 def retrieve_similar_patterns(self, context: str, current_pattern: Dict[str, Any], 
 similarity_threshold: float = None) -> List[Dict[str, Any]]:
 """Retrieve similar patterns from memory for adaptive learning using dynamic configuration"""
 pattern_config = self.config_manager.get('intelligence_engine.pattern_recognition', {})

 # Use dynamic similarity threshold
 if similarity_threshold is None:
 similarity_threshold = pattern_config.get('similarity_threshold_default', 0.7)

 default_success_rate = pattern_config.get('default_outcome_score', 0.5)

 similar_patterns = []
 current_vector = self._pattern_to_vector(current_pattern)

 with self.lock:
 for pattern_hash, pattern_data in self.pattern_memory[context].items():
 stored_vector = self._pattern_to_vector(pattern_data['pattern'])
 similarity = current_vector.similarity(stored_vector)

 if similarity >= similarity_threshold:
 similar_patterns.append({
 'pattern': pattern_data['pattern'],
 'similarity': similarity,
 'success_rate': sum(pattern_data['success_rate']) / len(pattern_data['success_rate']) if pattern_data['success_rate'] else default_success_rate,
 'frequency': pattern_data['frequency'],
 'weight': self.adaptation_weights[pattern_hash]
 })

 return sorted(similar_patterns, key=lambda x: x['similarity'] * x['weight'], reverse=True)

 def analyze_context_intelligence(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
 """Analyze context for intelligence insights"""
 intelligence_insights = {
 'complexity_score': self._calculate_complexity(context_data),
 'pattern_matches': self._find_pattern_matches(context_data),
 'adaptation_recommendations': self._generate_adaptations(context_data),
 'confidence_levels': self._assess_confidence(context_data)
 }

 return intelligence_insights

 def update_semantic_network(self, domain: str, concept: str, vector: SemanticVector):
 """Update semantic network with new concept vectors"""
 with self.lock:
 self.semantic_networks[domain][concept] = vector

 def get_semantic_relationships(self, domain: str, concept: str, threshold: float = None) -> List[Dict[str, Any]]:
 """Get semantically related concepts using dynamic configuration"""
 semantic_config = self.config_manager.get('intelligence_engine.semantic_analysis', {})

 # Use dynamic relationship threshold
 if threshold is None:
 threshold = semantic_config.get('relationship_threshold', 0.6)

 if domain not in self.semantic_networks or concept not in self.semantic_networks[domain]:
 return []

 target_vector = self.semantic_networks[domain][concept]
 relationships = []

 for other_concept, other_vector in self.semantic_networks[domain].items():
 if other_concept != concept:
 similarity = target_vector.similarity(other_vector)
 if similarity >= threshold:
 relationships.append({
 'concept': other_concept,
 'similarity': similarity,
 'vector': other_vector
 })

 return sorted(relationships, key=lambda x: x['similarity'], reverse=True)

 def _generate_pattern_hash(self, context: str, pattern: Dict[str, Any]) -> str:
 """Generate unique hash for pattern identification"""
 pattern_str = json.dumps(pattern, sort_keys=True)
 return hashlib.md5(f"{context}:{pattern_str}".encode()).hexdigest()

 def _pattern_to_vector(self, pattern: Dict[str, Any]) -> SemanticVector:
 """Convert pattern to semantic vector for comparison"""
 concepts = {}
 for key, value in pattern.items():
 if isinstance(value, (str, int, float)):
 concepts[f"{key}:{str(value)[:50]}"] = 1.0
 elif isinstance(value, (list, dict)):
 concepts[f"{key}:complex"] = 0.5

 semantic_config = self.config_manager.get('intelligence_engine.semantic_analysis', {})
 default_confidence = semantic_config.get('default_semantic_confidence', 0.8)

 return SemanticVector(concepts=concepts, confidence=default_confidence)

 def _calculate_complexity(self, context_data: Dict[str, Any]) -> float:
 """Calculate complexity score for context data using dynamic configuration"""
 complexity_config = self.config_manager.get('intelligence_engine.complexity_assessment', {})

 volume_normalizer = complexity_config.get('data_volume_normalizer', 1000.0)
 diversity_normalizer = complexity_config.get('key_diversity_normalizer', 20.0)
 depth_normalizer = complexity_config.get('nesting_depth_normalizer', 10.0)
 max_complexity = complexity_config.get('max_complexity_score', 1.0)

 complexity_factors = [
 len(str(context_data)) / volume_normalizer, # Data volume
 len(context_data.keys()) / diversity_normalizer, # Key diversity
 self._count_nested_structures(context_data) / depth_normalizer # Nesting depth
 ]

 return min(max_complexity, sum(complexity_factors) / len(complexity_factors))

 def _count_nested_structures(self, data: Any, depth: int = 0) -> int:
 """Count nested data structures using dynamic configuration"""
 complexity_config = self.config_manager.get('intelligence_engine.complexity_assessment', {})
 max_recursion = complexity_config.get('max_recursion_depth', 5)

 if depth > max_recursion: # Prevent infinite recursion
 return depth

 if isinstance(data, dict):
 return max([self._count_nested_structures(v, depth + 1) for v in data.values()] or [depth])
 elif isinstance(data, list) and data:
 return max([self._count_nested_structures(item, depth + 1) for item in data[:3]] or [depth])

 return depth

 def _find_pattern_matches(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
 """Find matching patterns from memory"""
 matches = []
 complexity_config = self.config_manager.get('intelligence_engine.complexity_assessment', {})
 truncate_length = complexity_config.get('context_truncate_length', 100)

 context_str = json.dumps(context_data, sort_keys=True)[:truncate_length] # Truncate for performance

 with self.lock:
 for context, patterns in self.pattern_memory.items():
 for pattern_hash, pattern_data in patterns.items():
 pattern_config = self.config_manager.get('intelligence_engine.pattern_matching', {})
 pattern_truncate = pattern_config.get('pattern_truncate_length', 100)
 similarity_threshold = pattern_config.get('simple_similarity_threshold', 0.3)
 default_success_rate = pattern_config.get('default_success_rate', 0.5)
 max_matches = pattern_config.get('max_pattern_matches', 10)

 # Simple similarity check
 pattern_str = json.dumps(pattern_data['pattern'], sort_keys=True)[:pattern_truncate]
 if self._simple_similarity(context_str, pattern_str) > similarity_threshold:
 matches.append({
 'context': context,
 'pattern': pattern_data['pattern'],
 'success_rate': sum(pattern_data['success_rate']) / len(pattern_data['success_rate']) if pattern_data['success_rate'] else default_success_rate,
 'frequency': pattern_data['frequency']
 })

 return matches[:max_matches]

 def _simple_similarity(self, str1: str, str2: str) -> float:
 """Simple string similarity calculation"""
 words1 = set(str1.lower().split())
 words2 = set(str2.lower().split())

 if not words1 or not words2:
 return 0.0

 intersection = len(words1 & words2)
 union = len(words1 | words2)

 return intersection / union if union > 0 else 0.0

 def _generate_adaptations(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
 """Generate adaptation recommendations based on patterns using dynamic configuration"""
 adaptation_config = self.config_manager.get('intelligence_engine.adaptation_recommendations', {})

 high_complexity_threshold = adaptation_config.get('high_complexity_threshold', 0.7)
 low_complexity_threshold = adaptation_config.get('low_complexity_threshold', 0.3)
 complexity_reduction_confidence = adaptation_config.get('complexity_reduction_confidence', 0.8)
 detail_enhancement_confidence = adaptation_config.get('detail_enhancement_confidence', 0.7)

 adaptations = []

 # Example adaptations based on context complexity
 complexity = self._calculate_complexity(context_data)

 if complexity > high_complexity_threshold:
 adaptations.append({
 'type': 'complexity_reduction',
 'recommendation': 'Consider breaking down complex elements',
 'confidence': complexity_reduction_confidence
 })

 if complexity < low_complexity_threshold:
 adaptations.append({
 'type': 'detail_enhancement',
 'recommendation': 'Consider adding more specific details',
 'confidence': detail_enhancement_confidence
 })

 return adaptations

 def _assess_confidence(self, context_data: Dict[str, Any]) -> Dict[str, float]:
 """Assess confidence levels for different aspects using dynamic configuration"""
 confidence_config = self.config_manager.get('intelligence_engine.confidence_assessment', {})

 completeness_normalizer = confidence_config.get('data_completeness_normalizer', 10.0)
 pattern_normalizer = confidence_config.get('pattern_recognition_normalizer', 10.0)
 max_confidence = confidence_config.get('max_confidence', 1.0)

 return {
 'data_completeness': min(max_confidence, len(context_data.keys()) / completeness_normalizer),
 'pattern_recognition': len(self._find_pattern_matches(context_data)) / pattern_normalizer,
 'semantic_clarity': self._assess_semantic_clarity(context_data)
 }

 def _assess_semantic_clarity(self, context_data: Dict[str, Any]) -> float:
 """Assess semantic clarity of context data using dynamic configuration"""
 confidence_config = self.config_manager.get('intelligence_engine.confidence_assessment', {})

 default_clarity = confidence_config.get('default_semantic_clarity', 0.5)
 max_confidence = confidence_config.get('max_confidence', 1.0)
 word_length_normalizer = confidence_config.get('word_length_normalizer', 10.0)

 text_content = ' '.join([str(v) for v in context_data.values() if isinstance(v, str)])

 if not text_content:
 return default_clarity

 # Simple clarity assessment based on text characteristics
 words = text_content.split()
 avg_word_length = sum(len(word) for word in words) / len(words) if words else 0

 return min(max_confidence, avg_word_length / word_length_normalizer)


# Singleton instance for easy import
_intelligence_engine = None

def get_intelligence_engine() -> DynamicIntelligenceEngine:
 """Get shared DynamicIntelligenceEngine instance"""
 global _intelligence_engine
 if _intelligence_engine is None:
 _intelligence_engine = DynamicIntelligenceEngine()
 return _intelligence_engine
