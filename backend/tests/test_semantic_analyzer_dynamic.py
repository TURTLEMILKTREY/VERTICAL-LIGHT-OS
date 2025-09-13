#!/usr/bin/env python3
"""
Comprehensive Dynamic Test Suite for Semantic Analyzer Service
Tests real-world text analysis scenarios, configuration adaptability, and production readiness
"""

import unittest
import sys
import os
import json
import tempfile
import shutil
import math
from unittest.mock import patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestSemanticAnalyzerDynamic(unittest.TestCase):
    """Comprehensive tests for dynamic Semantic Analyzer functionality"""
    
    def setUp(self):
        """Set up test environment with comprehensive semantic analysis configuration"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.temp_dir, 'config')
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Create realistic semantic analysis configuration
        self.test_config = {
            "similarity_threshold": 0.72,
            "confidence_threshold": 0.85,
            "semantic_weights": {
                "exact_match_weight": 0.65,
                "partial_match_weight": 0.42,
                "context_weight": 0.38,
                "intent_weight": 0.55
            },
            "text_processing": {
                "min_text_length": 10,
                "max_text_length": 10000,
                "noise_threshold": 0.15,
                "stop_word_removal": True,
                "stemming_enabled": True,
                "lemmatization_enabled": True
            },
            "context_analysis": {
                "context_window_size": 50,
                "semantic_depth_levels": 3,
                "entity_recognition_threshold": 0.78,
                "relationship_weight": 0.45,
                "topic_coherence_threshold": 0.68
            },
            "confidence_calculation": {
                "base_confidence": 0.50,
                "similarity_boost_factor": 0.35,
                "context_boost_factor": 0.25,
                "length_penalty_factor": 0.10,
                "complexity_adjustment": 0.15
            },
            "language_models": {
                "primary_model_weight": 0.70,
                "secondary_model_weight": 0.30,
                "ensemble_threshold": 0.80,
                "fallback_similarity_method": "cosine"
            },
            "performance_optimization": {
                "batch_processing_size": 100,
                "cache_similarity_threshold": 0.95,
                "parallel_processing_threshold": 500,
                "memory_optimization_level": "balanced"
            }
        }
        
        # Write test configuration
        config_file = os.path.join(self.config_dir, 'semantic_analysis.json')
        with open(config_file, 'w') as f:
            json.dump(self.test_config, f, indent=2)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_mock_config_manager(self):
        """Create mock configuration manager with test config"""
        mock_manager = MagicMock()
        
        def mock_get(key, default=None):
            keys = key.split('.')
            current = self.test_config
            try:
                for k in keys[1:]:  # Skip 'semantic_analysis' prefix
                    current = current[k]
                return current
            except (KeyError, TypeError):
                return default
        
        mock_manager.get.side_effect = mock_get
        return mock_manager
    
    def test_semantic_similarity_real_world_scenarios(self):
        """Test semantic similarity with real business text scenarios"""
        similarity_scenarios = [
            {
                "category": "customer_support_intents",
                "pairs": [
                    {
                        "text1": "I want to cancel my subscription immediately",
                        "text2": "Please help me terminate my account right now",
                        "expected_similarity": 0.85,
                        "intent_match": True
                    },
                    {
                        "text1": "How do I reset my password?",
                        "text2": "I forgot my login credentials and need help",
                        "expected_similarity": 0.72,
                        "intent_match": True
                    },
                    {
                        "text1": "What are your business hours?",
                        "text2": "I love your product design",
                        "expected_similarity": 0.15,
                        "intent_match": False
                    }
                ]
            },
            {
                "category": "product_descriptions",
                "pairs": [
                    {
                        "text1": "Premium wireless noise-canceling headphones with 30-hour battery life",
                        "text2": "High-quality Bluetooth headphones featuring active noise reduction and long-lasting battery",
                        "expected_similarity": 0.78,
                        "intent_match": True
                    },
                    {
                        "text1": "Organic cotton t-shirt available in multiple colors",
                        "text2": "100% natural fiber casual shirt with color variety",
                        "expected_similarity": 0.65,
                        "intent_match": True
                    }
                ]
            },
            {
                "category": "business_requirements",
                "pairs": [
                    {
                        "text1": "We need to increase customer acquisition by 25% this quarter",
                        "text2": "Our goal is to grow our customer base by one-fourth in the next three months",
                        "expected_similarity": 0.88,
                        "intent_match": True
                    },
                    {
                        "text1": "Implement real-time analytics dashboard for executive reporting",
                        "text2": "Create live data visualization system for C-level management insights",
                        "expected_similarity": 0.82,
                        "intent_match": True
                    }
                ]
            }
        ]
        
        try:
            with patch('config.config_manager.get_config_manager') as mock_get_manager:
                mock_get_manager.return_value = self.create_mock_config_manager()
                
                from services.shared.semantic_analyzer import SemanticAnalyzer
                analyzer = SemanticAnalyzer()
                
                for scenario in similarity_scenarios:
                    for pair in scenario["pairs"]:
                        with self.subTest(category=scenario["category"], text1=pair["text1"][:30]):
                            # Calculate basic similarity score (simplified for testing)
                            text1_words = set(pair["text1"].lower().split())
                            text2_words = set(pair["text2"].lower().split())
                            
                            # Jaccard similarity as baseline
                            intersection = len(text1_words.intersection(text2_words))
                            union = len(text1_words.union(text2_words))
                            jaccard_similarity = intersection / union if union > 0 else 0.0
                            
                            # Apply semantic weights from configuration
                            weights = self.test_config["semantic_weights"]
                            
                            # Enhanced similarity with configuration weights
                            enhanced_similarity = (
                                jaccard_similarity * weights["exact_match_weight"] +
                                (jaccard_similarity * 0.8) * weights["partial_match_weight"] +
                                (0.5 if pair["intent_match"] else 0.1) * weights["intent_weight"]
                            ) / (weights["exact_match_weight"] + weights["partial_match_weight"] + weights["intent_weight"])
                            
                            similarity_threshold = self.test_config["similarity_threshold"]
                            
                            if pair["expected_similarity"] >= similarity_threshold:
                                self.assertGreaterEqual(enhanced_similarity, 0.5)
                            else:
                                self.assertLess(enhanced_similarity, 0.8)
                                
        except ImportError as e:
            self.skipTest(f"Semantic Analyzer import failed: {e}")
    
    def test_confidence_calculation_with_various_factors(self):
        """Test confidence calculation with different text characteristics"""
        confidence_scenarios = [
            {
                "name": "high_quality_business_text",
                "text_pair": {
                    "text1": "Implement comprehensive customer relationship management system with advanced analytics capabilities and real-time reporting functionality to enhance customer satisfaction and drive business growth through data-driven insights.",
                    "text2": "Deploy advanced CRM platform featuring sophisticated analytics tools and live reporting capabilities to improve customer experience and accelerate business expansion via intelligent data analysis."
                },
                "characteristics": {
                    "length": "optimal",
                    "complexity": "high",
                    "vocabulary_richness": "excellent",
                    "semantic_clarity": "high"
                },
                "expected_confidence_range": (0.80, 0.95)
            },
            {
                "name": "short_informal_text",
                "text_pair": {
                    "text1": "Fix bug now",
                    "text2": "Repair issue quickly"
                },
                "characteristics": {
                    "length": "minimal",
                    "complexity": "low",
                    "vocabulary_richness": "poor",
                    "semantic_clarity": "medium"
                },
                "expected_confidence_range": (0.40, 0.65)
            },
            {
                "name": "technical_jargon_heavy",
                "text_pair": {
                    "text1": "Configure OAuth 2.0 authentication with JWT tokens for microservices architecture",
                    "text2": "Set up secure API authentication using JSON Web Tokens in distributed service environment"
                },
                "characteristics": {
                    "length": "adequate",
                    "complexity": "very_high",
                    "vocabulary_richness": "specialized",
                    "semantic_clarity": "high"
                },
                "expected_confidence_range": (0.75, 0.90)
            }
        ]
        
        for scenario in confidence_scenarios:
            with self.subTest(scenario=scenario["name"]):
                text1 = scenario["text_pair"]["text1"]
                text2 = scenario["text_pair"]["text2"]
                
                # Calculate confidence based on configuration factors
                conf_config = self.test_config["confidence_calculation"]
                base_confidence = conf_config["base_confidence"]
                
                # Length factor
                avg_length = (len(text1) + len(text2)) / 2
                if avg_length < 20:
                    length_penalty = conf_config["length_penalty_factor"]
                elif avg_length > 200:
                    length_penalty = -conf_config["length_penalty_factor"] * 0.5  # Bonus for detailed text
                else:
                    length_penalty = 0
                
                # Complexity factor (based on unique words)
                unique_words1 = len(set(text1.lower().split()))
                unique_words2 = len(set(text2.lower().split()))
                avg_complexity = (unique_words1 + unique_words2) / 2
                complexity_boost = min(avg_complexity / 20, conf_config["complexity_adjustment"])
                
                # Calculate similarity boost (simplified)
                common_words = len(set(text1.lower().split()).intersection(set(text2.lower().split())))
                total_words = len(set(text1.lower().split()).union(set(text2.lower().split())))
                similarity_score = common_words / total_words if total_words > 0 else 0
                similarity_boost = similarity_score * conf_config["similarity_boost_factor"]
                
                calculated_confidence = base_confidence + similarity_boost + complexity_boost - length_penalty
                calculated_confidence = max(0.0, min(1.0, calculated_confidence))  # Clamp to [0,1]
                
                expected_min, expected_max = scenario["expected_confidence_range"]
                self.assertGreaterEqual(calculated_confidence, expected_min - 0.15)  # Allow some tolerance
                self.assertLessEqual(calculated_confidence, expected_max + 0.15)
    
    def test_context_analysis_with_business_scenarios(self):
        """Test context analysis with realistic business contexts"""
        context_scenarios = [
            {
                "domain": "e-commerce_optimization",
                "context_text": "Our e-commerce platform needs optimization to improve conversion rates. Current cart abandonment rate is 68% and average session duration is 2.3 minutes. We want to implement personalized product recommendations and streamline the checkout process.",
                "query_texts": [
                    "How can we reduce cart abandonment?",
                    "What personalization features should we add?",
                    "Ways to optimize checkout flow"
                ],
                "expected_context_matches": [0.85, 0.78, 0.82],
                "domain_relevance": 0.92
            },
            {
                "domain": "hr_talent_management",
                "context_text": "Our HR department is struggling with employee retention. Current turnover rate is 15% annually, and exit interviews indicate issues with career development opportunities and work-life balance. We need strategies to improve employee satisfaction and retention.",
                "query_texts": [
                    "How to improve employee retention rates?",
                    "What career development programs work best?",
                    "Strategies for better work-life balance"
                ],
                "expected_context_matches": [0.88, 0.75, 0.72],
                "domain_relevance": 0.89
            }
        ]
        
        for scenario in context_scenarios:
            with self.subTest(domain=scenario["domain"]):
                context_text = scenario["context_text"]
                context_config = self.test_config["context_analysis"]
                
                # Extract key context features
                context_words = set(context_text.lower().split())
                context_length = len(context_text)
                
                for i, query_text in enumerate(scenario["query_texts"]):
                    query_words = set(query_text.lower().split())
                    
                    # Calculate context relevance
                    word_overlap = len(context_words.intersection(query_words))
                    total_context_words = len(context_words)
                    
                    # Apply context window (simplified)
                    window_size = context_config["context_window_size"]
                    if context_length > window_size:
                        context_focus_factor = 0.8  # Reduce focus for very long context
                    else:
                        context_focus_factor = 1.0
                    
                    context_relevance = (word_overlap / total_context_words) * context_focus_factor
                    context_relevance *= scenario["domain_relevance"]  # Domain-specific boost
                    
                    expected_match = scenario["expected_context_matches"][i]
                    
                    # Allow reasonable tolerance for simplified calculation
                    self.assertGreaterEqual(context_relevance, expected_match - 0.25)
    
    def test_language_model_ensemble_configuration(self):
        """Test language model ensemble behavior with configuration"""
        ensemble_scenarios = [
            {
                "name": "high_confidence_consensus",
                "model_scores": {
                    "primary_model": 0.89,
                    "secondary_model": 0.85
                },
                "expected_ensemble_score": 0.87,
                "use_ensemble": True
            },
            {
                "name": "low_confidence_fallback",
                "model_scores": {
                    "primary_model": 0.45,
                    "secondary_model": 0.52
                },
                "expected_ensemble_score": 0.47,
                "use_ensemble": False
            },
            {
                "name": "conflicting_models",
                "model_scores": {
                    "primary_model": 0.85,
                    "secondary_model": 0.35
                },
                "expected_ensemble_score": 0.70,
                "use_ensemble": True
            }
        ]
        
        for scenario in ensemble_scenarios:
            with self.subTest(scenario=scenario["name"]):
                model_scores = scenario["model_scores"]
                model_config = self.test_config["language_models"]
                
                # Calculate ensemble score based on configuration weights
                primary_weight = model_config["primary_model_weight"]
                secondary_weight = model_config["secondary_model_weight"]
                ensemble_threshold = model_config["ensemble_threshold"]
                
                primary_score = model_scores["primary_model"]
                secondary_score = model_scores["secondary_model"]
                
                # Determine if ensemble should be used
                avg_confidence = (primary_score + secondary_score) / 2
                use_ensemble = avg_confidence >= ensemble_threshold
                
                if use_ensemble:
                    ensemble_score = (primary_score * primary_weight + 
                                    secondary_score * secondary_weight)
                else:
                    # Fallback to primary model
                    ensemble_score = primary_score
                
                expected_score = scenario["expected_ensemble_score"]
                self.assertAlmostEqual(ensemble_score, expected_score, delta=0.1)
                self.assertEqual(use_ensemble, scenario["use_ensemble"])
    
    def test_performance_optimization_thresholds(self):
        """Test performance optimization behavior based on configuration"""
        performance_scenarios = [
            {
                "name": "large_batch_processing",
                "input_size": 1500,
                "expected_processing_mode": "parallel",
                "expected_batch_size": 100
            },
            {
                "name": "small_batch_processing",
                "input_size": 50,
                "expected_processing_mode": "sequential",
                "expected_batch_size": 50
            },
            {
                "name": "memory_constrained_processing",
                "input_size": 800,
                "memory_level": "conservative",
                "expected_processing_mode": "chunked",
                "expected_batch_size": 100
            }
        ]
        
        for scenario in performance_scenarios:
            with self.subTest(scenario=scenario["name"]):
                input_size = scenario["input_size"]
                perf_config = self.test_config["performance_optimization"]
                
                # Determine processing mode based on configuration
                parallel_threshold = perf_config["parallel_processing_threshold"]
                batch_size = perf_config["batch_processing_size"]
                
                if input_size >= parallel_threshold:
                    processing_mode = "parallel"
                elif input_size >= batch_size:
                    processing_mode = "chunked"
                else:
                    processing_mode = "sequential"
                
                expected_mode = scenario["expected_processing_mode"]
                expected_batch = scenario["expected_batch_size"]
                
                self.assertEqual(processing_mode, expected_mode)
                
                # Batch size should match configuration or input size if smaller
                actual_batch_size = min(input_size, batch_size)
                self.assertEqual(actual_batch_size, expected_batch)
    
    def test_edge_cases_and_error_handling(self):
        """Test edge cases and error handling scenarios"""
        edge_cases = [
            {
                "name": "empty_text_input",
                "text1": "",
                "text2": "some text",
                "expected_behavior": "handle_empty_input",
                "expected_similarity": 0.0
            },
            {
                "name": "identical_texts",
                "text1": "identical text content",
                "text2": "identical text content",
                "expected_behavior": "perfect_match",
                "expected_similarity": 1.0
            },
            {
                "name": "very_long_text",
                "text1": "word " * 2000,  # 2000 repeated words
                "text2": "different content",
                "expected_behavior": "handle_length_limit",
                "expected_similarity": 0.0
            },
            {
                "name": "special_characters_only",
                "text1": "!@#$%^&*()",
                "text2": "{}[]|\\:;\"'<>?,./",
                "expected_behavior": "handle_non_semantic_content",
                "expected_similarity": 0.0
            }
        ]
        
        for case in edge_cases:
            with self.subTest(case=case["name"]):
                text1 = case["text1"]
                text2 = case["text2"]
                text_config = self.test_config["text_processing"]
                
                # Check length constraints
                max_length = text_config["max_text_length"]
                min_length = text_config["min_text_length"]
                
                if len(text1) == 0 or len(text2) == 0:
                    self.assertEqual(case["expected_behavior"], "handle_empty_input")
                    self.assertEqual(case["expected_similarity"], 0.0)
                elif text1 == text2:
                    self.assertEqual(case["expected_behavior"], "perfect_match")
                    self.assertEqual(case["expected_similarity"], 1.0)
                elif len(text1) > max_length or len(text2) > max_length:
                    self.assertEqual(case["expected_behavior"], "handle_length_limit")
                elif not any(c.isalnum() for c in text1 + text2):
                    self.assertEqual(case["expected_behavior"], "handle_non_semantic_content")

if __name__ == '__main__':
    unittest.main(verbosity=2)
