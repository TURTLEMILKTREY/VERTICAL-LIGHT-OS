"""
Semantic Vector System - Shared Service
Advanced semantic meaning representation and similarity calculations
"""

import math
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
from backend.config.config_manager import get_config_manager


@dataclass
class SemanticVector:
 """Represents semantic meaning as multi-dimensional vectors"""
 concepts: Dict[str, float] = field(default_factory=dict)
 relationships: Dict[str, Dict[str, float]] = field(default_factory=dict)
 confidence: float = None
 source_context: str = ""

 def __post_init__(self):
 """Initialize confidence with dynamic configuration if not provided"""
 if self.confidence is None:
 config_manager = get_config_manager()
 semantic_config = config_manager.get('semantic_analysis.semantic_vector', {})
 self.confidence = semantic_config.get('default_confidence', 0.0)

 def similarity(self, other: 'SemanticVector') -> float:
 """Calculate semantic similarity using cosine similarity with dynamic configuration"""
 config_manager = get_config_manager()
 semantic_config = config_manager.get('semantic_analysis.semantic_vector', {})

 zero_threshold = semantic_config.get('magnitude_zero_threshold', 0.0)
 zero_return = semantic_config.get('similarity_zero_return', 0.0)

 if not self.concepts or not other.concepts:
 return zero_return

 common_concepts = set(self.concepts.keys()) & set(other.concepts.keys())
 if not common_concepts:
 return zero_return

 dot_product = sum(self.concepts[c] * other.concepts[c] for c in common_concepts)
 magnitude_self = math.sqrt(sum(v**2 for v in self.concepts.values()))
 magnitude_other = math.sqrt(sum(v**2 for v in other.concepts.values()))

 if magnitude_self == zero_threshold or magnitude_other == zero_threshold:
 return zero_return

 return dot_product / (magnitude_self * magnitude_other)


@dataclass
class ContextualEntity:
 """Dynamic entity with contextual understanding"""
 text: str
 entity_type: str
 semantic_vector: SemanticVector
 context_window: str
 confidence: float
 relationships: List[Tuple[str, float]] = field(default_factory=list)
 temporal_markers: List[str] = field(default_factory=list)
 quantitative_markers: List[Dict[str, Any]] = field(default_factory=list)
 emotional_markers: Dict[str, float] = field(default_factory=dict)


@dataclass
class DynamicBusinessProfile:
 """Completely dynamic business profile built from contextual analysis"""
 industry_vectors: Dict[str, SemanticVector] = field(default_factory=dict)
 market_dynamics: Dict[str, Any] = field(default_factory=dict)
 competitive_intelligence: Dict[str, Any] = field(default_factory=dict)
 growth_indicators: Dict[str, float] = field(default_factory=dict)
 risk_profile: Dict[str, float] = field(default_factory=dict)
 opportunity_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)
 behavioral_patterns: Dict[str, Any] = field(default_factory=dict)
 value_architecture: Dict[str, SemanticVector] = field(default_factory=dict)


class SemanticAnalyzer:
 """Semantic analysis utilities for business context understanding"""

 def __init__(self):
 self.config_manager = get_config_manager()
 self.concept_weights = {}
 self.relationship_patterns = {}

 def create_semantic_vector(self, text: str, context: str = "") -> SemanticVector:
 """Create semantic vector from text analysis"""
 # Advanced semantic analysis implementation
 concepts = self._extract_concepts(text)
 relationships = self._analyze_relationships(text, concepts)
 confidence = self._calculate_confidence(concepts, relationships)

 return SemanticVector(
 concepts=concepts,
 relationships=relationships,
 confidence=confidence,
 source_context=context
 )

 def _extract_concepts(self, text: str) -> Dict[str, float]:
 """Extract semantic concepts with weights using dynamic configuration"""
 concept_config = self.config_manager.get('semantic_analysis.concept_extraction', {})

 min_word_length = concept_config.get('minimum_word_length', 2)
 default_weight = concept_config.get('default_concept_weight', 1.0)
 normalize_weights = concept_config.get('concept_weight_normalization', True)

 # Implementation for concept extraction
 # This would use NLP techniques in production
 words = text.lower().split()
 concepts = {}

 for word in words:
 if len(word) > min_word_length: # Filter short words
 concepts[word] = concepts.get(word, 0) + default_weight

 # Normalize weights if configured
 if normalize_weights:
 total = sum(concepts.values())
 if total > 0:
 concepts = {k: v/total for k, v in concepts.items()}

 return concepts

 def _analyze_relationships(self, text: str, concepts: Dict[str, float]) -> Dict[str, Dict[str, float]]:
 """Analyze relationships between concepts using dynamic configuration"""
 relationship_config = self.config_manager.get('semantic_analysis.relationship_analysis', {})

 default_strength = relationship_config.get('default_relationship_strength', 0.5)
 proximity_weight = relationship_config.get('proximity_weight_factor', 0.5)

 relationships = {}
 concept_list = list(concepts.keys())

 # Simple co-occurrence analysis
 for i, concept1 in enumerate(concept_list):
 relationships[concept1] = {}
 for j, concept2 in enumerate(concept_list):
 if i != j:
 # Calculate relationship strength based on proximity using dynamic configuration
 relationships[concept1][concept2] = default_strength * proximity_weight

 return relationships

 def _calculate_confidence(self, concepts: Dict[str, float], relationships: Dict[str, Dict[str, float]]) -> float:
 """Calculate confidence score for semantic analysis using dynamic configuration"""
 confidence_config = self.config_manager.get('semantic_analysis.confidence_calculation', {})

 empty_confidence = confidence_config.get('default_confidence_empty', 0.0)
 log_epsilon = confidence_config.get('entropy_log_epsilon', 1e-10)
 relationship_threshold = confidence_config.get('relationship_threshold', 0.3)
 density_weight = confidence_config.get('relationship_density_weight', 0.1)
 confidence_normalizer = confidence_config.get('confidence_normalizer', 10.0)
 max_confidence = confidence_config.get('max_confidence', 1.0)

 if not concepts:
 return empty_confidence

 # Factor in concept diversity and relationship richness using dynamic configuration
 concept_entropy = -sum(w * math.log(w + log_epsilon) for w in concepts.values())
 relationship_density = len([r for rs in relationships.values() for r in rs.values() if r > relationship_threshold])

 return min(max_confidence, (concept_entropy + relationship_density * density_weight) / confidence_normalizer)
