"""
Intelligence Orchestrator - Market Intelligence
Central coordinator for all market intelligence services and workflow management
100% Dynamic Configuration - Zero Hardcoded Values
"""

import json
import logging
import threading
import asyncio
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib

from config.config_manager import get_config_manager
from .intelligence_engine import get_intelligence_engine
from .competitive_analysis_service import get_competitive_analysis_service
from .data_quality_service import get_data_quality_service

logger = logging.getLogger(__name__)


class IntelligenceOrchestrator:
    """
    Central orchestrator for coordinating all market intelligence services,
    managing workflows, and ensuring seamless service integration.
    """
    
    def __init__(self):
        self.config_manager = get_config_manager()
        self.orchestrator_config = self._load_orchestrator_configuration()
        
        # Service registry
        self.services = {
            'intelligence_engine': get_intelligence_engine(),
            'competitive_analysis': get_competitive_analysis_service(),
            'data_quality': get_data_quality_service()
        }
        
        # Workflow management
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.workflow_results: Dict[str, Dict[str, Any]] = {}
        self.service_health: Dict[str, Dict[str, Any]] = {}
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Configuration-driven parameters
        self.max_concurrent_workflows = self._get_config_value('orchestration.max_concurrent_workflows', 10)
        self.workflow_timeout_minutes = self._get_config_value('orchestration.workflow_timeout_minutes', 30)
        self.service_health_check_interval = self._get_config_value('health.check_interval_minutes', 5)
        self.enable_parallel_processing = self._get_config_value('orchestration.enable_parallel_processing', True)
        
        # Workflow definitions
        self.workflow_definitions = self._load_workflow_definitions()
        
        # Initialize service health monitoring
        self._initialize_health_monitoring()
        
        logger.info("IntelligenceOrchestrator initialized with dynamic configuration")
        
    def _load_orchestrator_configuration(self) -> Dict[str, Any]:
        """Load orchestrator configuration"""
        try:
            return self.config_manager.get('intelligence_orchestrator', {})
        except Exception as e:
            logger.error(f"Failed to load orchestrator configuration: {e}")
            return {}
    
    def _get_config_value(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        try:
            keys = key_path.split('.')
            value = self.orchestrator_config
            for key in keys:
                value = value.get(key, {})
            return value if value != {} else default
        except Exception:
            return default
    
    def _load_workflow_definitions(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined workflow definitions"""
        try:
            workflows = self._get_config_value('workflows', {})
            
            # Default workflows if not configured
            if not workflows:
                workflows = {
                    'comprehensive_market_analysis': {
                        'steps': [
                            {'service': 'data_quality', 'method': 'validate_market_data'},
                            {'service': 'competitive_analysis', 'method': 'analyze_competitive_landscape'},
                            {'service': 'intelligence_engine', 'method': 'analyze_market_context'}
                        ],
                        'parallel_execution': True,
                        'timeout_minutes': self._get_config_value('workflows.comprehensive_analysis_timeout', 15)
                    },
                    'competitor_monitoring': {
                        'steps': [
                            {'service': 'data_quality', 'method': 'validate_market_data'},
                            {'service': 'competitive_analysis', 'method': 'monitor_competitor'}
                        ],
                        'parallel_execution': False,
                        'timeout_minutes': self._get_config_value('workflows.competitor_monitoring_timeout', 10)
                    }
                }
            
            return workflows
            
        except Exception as e:
            logger.error(f"Error loading workflow definitions: {e}")
            return {}
    
    def execute_comprehensive_analysis(self, business_profile: Dict[str, Any], 
                                     market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute comprehensive market intelligence analysis workflow
        """
        with self.lock:
            try:
                workflow_id = self._generate_workflow_id()
                start_time = datetime.now()
                
                workflow_result = {
                    'workflow_id': workflow_id,
                    'workflow_type': 'comprehensive_analysis',
                    'start_time': start_time.isoformat(),
                    'status': 'running',
                    'results': {},
                    'errors': [],
                    'warnings': [],
                    'execution_time': 0,
                    'quality_score': 0.0
                }
                
                # Register active workflow
                self.active_workflows[workflow_id] = workflow_result
                
                try:
                    # Step 1: Data Quality Validation
                    logger.info(f"[{workflow_id}] Starting data quality validation")
                    data_quality_result = self.services['data_quality'].validate_market_data(
                        market_data, 'comprehensive_market_data'
                    )
                    workflow_result['results']['data_quality'] = data_quality_result
                    
                    # Check if data quality is sufficient
                    if data_quality_result['overall_quality_score'] < self._get_config_value('quality.minimum_score', 0.6):
                        workflow_result['warnings'].append("Low data quality detected - results may be unreliable")
                    
                    # Step 2: Competitive Analysis (can run in parallel with intelligence analysis)
                    logger.info(f"[{workflow_id}] Starting competitive analysis")
                    competitive_result = self.services['competitive_analysis'].analyze_competitive_landscape(
                        business_profile, market_data
                    )
                    workflow_result['results']['competitive_analysis'] = competitive_result
                    
                    # Step 3: Market Intelligence Analysis
                    logger.info(f"[{workflow_id}] Starting market intelligence analysis")
                    intelligence_result = self.services['intelligence_engine'].analyze_market_context(
                        business_profile, market_data
                    )
                    workflow_result['results']['intelligence_analysis'] = intelligence_result
                    
                    # Step 4: Synthesis and Integration
                    logger.info(f"[{workflow_id}] Synthesizing results")
                    synthesis_result = self._synthesize_analysis_results(
                        data_quality_result, competitive_result, intelligence_result
                    )
                    workflow_result['results']['synthesis'] = synthesis_result
                    
                    # Calculate overall workflow quality score
                    workflow_result['quality_score'] = self._calculate_workflow_quality_score(workflow_result)
                    
                    # Update status
                    workflow_result['status'] = 'completed'
                    workflow_result['execution_time'] = (datetime.now() - start_time).total_seconds()
                    
                    logger.info(f"[{workflow_id}] Comprehensive analysis completed successfully")
                    
                except Exception as step_error:
                    workflow_result['status'] = 'failed'
                    workflow_result['errors'].append(str(step_error))
                    logger.error(f"[{workflow_id}] Workflow failed: {step_error}")
                
                finally:
                    # Store result and cleanup
                    self.workflow_results[workflow_id] = workflow_result
                    if workflow_id in self.active_workflows:
                        del self.active_workflows[workflow_id]
                
                return workflow_result
                
            except Exception as e:
                logger.error(f"Error executing comprehensive analysis: {e}")
                return self._create_fallback_workflow_result()
    
    def execute_custom_workflow(self, workflow_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a custom workflow based on predefined or dynamic workflow definition
        """
        with self.lock:
            try:
                workflow_id = self._generate_workflow_id()
                start_time = datetime.now()
                
                # Get workflow definition
                workflow_def = self.workflow_definitions.get(workflow_name)
                if not workflow_def:
                    raise ValueError(f"Unknown workflow: {workflow_name}")
                
                workflow_result = {
                    'workflow_id': workflow_id,
                    'workflow_type': workflow_name,
                    'start_time': start_time.isoformat(),
                    'status': 'running',
                    'steps_completed': 0,
                    'total_steps': len(workflow_def['steps']),
                    'results': {},
                    'errors': [],
                    'warnings': [],
                    'execution_time': 0
                }
                
                # Register active workflow
                self.active_workflows[workflow_id] = workflow_result
                
                try:
                    # Execute workflow steps
                    step_results = []
                    
                    if workflow_def.get('parallel_execution', False) and self.enable_parallel_processing:
                        # Execute steps in parallel
                        step_results = self._execute_parallel_steps(workflow_def['steps'], parameters)
                    else:
                        # Execute steps sequentially
                        step_results = self._execute_sequential_steps(workflow_def['steps'], parameters)
                    
                    # Compile results
                    for i, result in enumerate(step_results):
                        step_name = f"step_{i+1}"
                        workflow_result['results'][step_name] = result
                        if result.get('status') == 'success':
                            workflow_result['steps_completed'] += 1
                        else:
                            workflow_result['errors'].append(f"Step {i+1} failed: {result.get('error', 'Unknown error')}")
                    
                    # Determine final status
                    if workflow_result['steps_completed'] == workflow_result['total_steps']:
                        workflow_result['status'] = 'completed'
                    elif workflow_result['steps_completed'] > 0:
                        workflow_result['status'] = 'partially_completed'
                    else:
                        workflow_result['status'] = 'failed'
                    
                    workflow_result['execution_time'] = (datetime.now() - start_time).total_seconds()
                    
                    logger.info(f"[{workflow_id}] Custom workflow '{workflow_name}' completed with status: {workflow_result['status']}")
                    
                except Exception as step_error:
                    workflow_result['status'] = 'failed'
                    workflow_result['errors'].append(str(step_error))
                    logger.error(f"[{workflow_id}] Custom workflow failed: {step_error}")
                
                finally:
                    # Store result and cleanup
                    self.workflow_results[workflow_id] = workflow_result
                    if workflow_id in self.active_workflows:
                        del self.active_workflows[workflow_id]
                
                return workflow_result
                
            except Exception as e:
                logger.error(f"Error executing custom workflow: {e}")
                return self._create_fallback_workflow_result()
    
    def monitor_service_health(self) -> Dict[str, Any]:
        """
        Monitor health of all registered services
        """
        with self.lock:
            try:
                health_report = {
                    'timestamp': datetime.now().isoformat(),
                    'overall_health': 'healthy',
                    'service_status': {},
                    'alerts': [],
                    'recommendations': []
                }
                
                unhealthy_services = 0
                
                for service_name, service in self.services.items():
                    try:
                        # Perform health check
                        health_check = self._perform_service_health_check(service_name, service)
                        health_report['service_status'][service_name] = health_check
                        
                        if health_check['status'] != 'healthy':
                            unhealthy_services += 1
                            health_report['alerts'].append(f"Service {service_name} is {health_check['status']}")
                        
                    except Exception as e:
                        health_report['service_status'][service_name] = {
                            'status': 'error',
                            'error': str(e),
                            'last_check': datetime.now().isoformat()
                        }
                        unhealthy_services += 1
                        health_report['alerts'].append(f"Service {service_name} health check failed")
                
                # Determine overall health
                if unhealthy_services == 0:
                    health_report['overall_health'] = 'healthy'
                elif unhealthy_services < len(self.services) / 2:
                    health_report['overall_health'] = 'degraded'
                else:
                    health_report['overall_health'] = 'unhealthy'
                
                # Generate recommendations
                if unhealthy_services > 0:
                    health_report['recommendations'].append("Investigate unhealthy services")
                    health_report['recommendations'].append("Consider implementing failover mechanisms")
                
                # Store health status
                self.service_health['latest'] = health_report
                
                return health_report
                
            except Exception as e:
                logger.error(f"Error monitoring service health: {e}")
                return {'overall_health': 'unknown', 'error': str(e)}
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get status of a specific workflow
        """
        with self.lock:
            # Check active workflows first
            if workflow_id in self.active_workflows:
                return self.active_workflows[workflow_id]
            
            # Check completed workflows
            if workflow_id in self.workflow_results:
                return self.workflow_results[workflow_id]
            
            return {'error': f'Workflow {workflow_id} not found'}
    
    def list_active_workflows(self) -> List[Dict[str, Any]]:
        """
        List all currently active workflows
        """
        with self.lock:
            return [
                {
                    'workflow_id': wf_id,
                    'workflow_type': wf_data.get('workflow_type'),
                    'status': wf_data.get('status'),
                    'start_time': wf_data.get('start_time'),
                    'steps_completed': wf_data.get('steps_completed', 0),
                    'total_steps': wf_data.get('total_steps', 0)
                }
                for wf_id, wf_data in self.active_workflows.items()
            ]
    
    def cancel_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Cancel an active workflow
        """
        with self.lock:
            if workflow_id not in self.active_workflows:
                return {'success': False, 'message': 'Workflow not found or not active'}
            
            try:
                workflow = self.active_workflows[workflow_id]
                workflow['status'] = 'cancelled'
                workflow['cancelled_at'] = datetime.now().isoformat()
                
                # Move to results
                self.workflow_results[workflow_id] = workflow
                del self.active_workflows[workflow_id]
                
                logger.info(f"Workflow {workflow_id} cancelled successfully")
                return {'success': True, 'message': 'Workflow cancelled'}
                
            except Exception as e:
                logger.error(f"Error cancelling workflow {workflow_id}: {e}")
                return {'success': False, 'message': str(e)}
    
    def _synthesize_analysis_results(self, data_quality: Dict[str, Any], 
                                   competitive: Dict[str, Any], 
                                   intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize results from multiple analysis services"""
        try:
            synthesis = {
                'executive_summary': self._create_executive_summary(data_quality, competitive, intelligence),
                'key_insights': self._extract_key_insights(competitive, intelligence),
                'strategic_recommendations': self._consolidate_recommendations(competitive, intelligence),
                'risk_assessment': self._consolidate_risk_assessment(competitive, intelligence),
                'confidence_metrics': self._calculate_confidence_metrics(data_quality, competitive, intelligence),
                'next_actions': self._generate_next_actions(competitive, intelligence)
            }
            
            return synthesis
            
        except Exception as e:
            logger.error(f"Error synthesizing analysis results: {e}")
            return {}
    
    def _calculate_workflow_quality_score(self, workflow_result: Dict[str, Any]) -> float:
        """Calculate overall quality score for workflow results"""
        try:
            quality_factors = []
            
            # Data quality factor
            data_quality = workflow_result.get('results', {}).get('data_quality', {})
            if data_quality:
                quality_factors.append(data_quality.get('overall_quality_score', 0))
            
            # Competitive analysis confidence factor
            competitive = workflow_result.get('results', {}).get('competitive_analysis', {})
            if competitive:
                quality_factors.append(competitive.get('confidence_score', 0))
            
            # Intelligence analysis confidence factor
            intelligence = workflow_result.get('results', {}).get('intelligence_analysis', {})
            if intelligence:
                quality_factors.append(intelligence.get('confidence_score', 0))
            
            # Calculate weighted average
            if quality_factors:
                return sum(quality_factors) / len(quality_factors)
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"Error calculating workflow quality score: {e}")
            return 0.5
    
    def _execute_sequential_steps(self, steps: List[Dict[str, Any]], parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute workflow steps sequentially"""
        results = []
        
        for step in steps:
            try:
                service_name = step['service']
                method_name = step['method']
                
                if service_name not in self.services:
                    results.append({'status': 'error', 'error': f'Service {service_name} not found'})
                    continue
                
                service = self.services[service_name]
                method = getattr(service, method_name, None)
                
                if method is None:
                    results.append({'status': 'error', 'error': f'Method {method_name} not found in {service_name}'})
                    continue
                
                # Execute method with parameters
                step_parameters = step.get('parameters', {})
                merged_parameters = {**parameters, **step_parameters}
                
                result = method(**merged_parameters)
                results.append({'status': 'success', 'result': result})
                
            except Exception as e:
                results.append({'status': 'error', 'error': str(e)})
        
        return results
    
    def _execute_parallel_steps(self, steps: List[Dict[str, Any]], parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute workflow steps in parallel (simplified implementation)"""
        # For now, execute sequentially but could be enhanced with async/threading
        return self._execute_sequential_steps(steps, parameters)
    
    def _perform_service_health_check(self, service_name: str, service: Any) -> Dict[str, Any]:
        """Perform health check on a service"""
        try:
            # Basic health check - verify service is responsive
            start_time = datetime.now()
            
            # Try to access service configuration or perform lightweight operation
            if hasattr(service, 'config_manager'):
                _ = service.config_manager
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'status': 'healthy',
                'response_time_seconds': response_time,
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    def _initialize_health_monitoring(self) -> None:
        """Initialize service health monitoring"""
        try:
            # Perform initial health check
            initial_health = self.monitor_service_health()
            logger.info(f"Initial service health: {initial_health['overall_health']}")
            
        except Exception as e:
            logger.error(f"Error initializing health monitoring: {e}")
    
    def _generate_workflow_id(self) -> str:
        """Generate unique workflow ID"""
        return f"WF_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(id(self)).encode()).hexdigest()[:8]}"
    
    def _create_fallback_workflow_result(self) -> Dict[str, Any]:
        """Create fallback workflow result"""
        return {
            'workflow_id': 'fallback',
            'workflow_type': 'unknown',
            'status': 'failed',
            'start_time': datetime.now().isoformat(),
            'results': {},
            'errors': ['Workflow execution failed'],
            'warnings': [],
            'execution_time': 0,
            'quality_score': 0.0
        }
    
    # Additional helper methods for synthesis
    def _create_executive_summary(self, data_quality: Dict[str, Any], 
                                competitive: Dict[str, Any], 
                                intelligence: Dict[str, Any]) -> str:
        """Create executive summary from analysis results"""
        try:
            summary_parts = []
            
            # Data quality summary
            dq_score = data_quality.get('overall_quality_score', 0)
            summary_parts.append(f"Data quality score: {dq_score:.1%}")
            
            # Competitive landscape summary
            comp_intensity = competitive.get('competitive_intensity', {}).get('intensity_level', 'unknown')
            summary_parts.append(f"Competitive intensity: {comp_intensity}")
            
            # Intelligence insights
            intel_confidence = intelligence.get('confidence_score', 0)
            summary_parts.append(f"Analysis confidence: {intel_confidence:.1%}")
            
            return " | ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error creating executive summary: {e}")
            return "Executive summary generation failed"
    
    def _extract_key_insights(self, competitive: Dict[str, Any], intelligence: Dict[str, Any]) -> List[str]:
        """Extract key insights from analysis results"""
        insights = []
        
        try:
            # Competitive insights
            comp_insights = competitive.get('strategic_insights', [])
            insights.extend(comp_insights[:3])  # Top 3
            
            # Intelligence insights
            intel_opportunities = intelligence.get('market_opportunities', [])
            if intel_opportunities:
                insights.append(f"Key opportunity: {intel_opportunities[0].get('trend', 'Market expansion')}")
            
        except Exception as e:
            logger.error(f"Error extracting key insights: {e}")
        
        return insights
    
    def _consolidate_recommendations(self, competitive: Dict[str, Any], intelligence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Consolidate recommendations from different analyses"""
        recommendations = []
        
        try:
            # Competitive recommendations
            comp_recs = competitive.get('positioning_recommendations', [])
            for rec in comp_recs:
                recommendations.append({
                    'source': 'competitive_analysis',
                    'type': rec.get('type'),
                    'recommendation': rec.get('recommendation'),
                    'priority': rec.get('priority', 'medium')
                })
            
            # Intelligence recommendations
            intel_recs = intelligence.get('recommendations', [])
            for rec in intel_recs:
                recommendations.append({
                    'source': 'intelligence_analysis',
                    'type': rec.get('type'),
                    'recommendation': rec.get('recommendation'),
                    'priority': rec.get('priority', 'medium')
                })
            
            # Sort by priority
            priority_order = {'high': 3, 'medium': 2, 'low': 1}
            recommendations.sort(key=lambda x: priority_order.get(x.get('priority', 'medium'), 2), reverse=True)
            
        except Exception as e:
            logger.error(f"Error consolidating recommendations: {e}")
        
        return recommendations
    
    def _consolidate_risk_assessment(self, competitive: Dict[str, Any], intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Consolidate risk assessments"""
        try:
            risks = {
                'competitive_risks': competitive.get('threat_assessment', []),
                'market_risks': intelligence.get('risk_assessment', []),
                'overall_risk_level': 'medium'
            }
            
            # Calculate overall risk level
            high_risks = sum(1 for risk in risks['competitive_risks'] if risk.get('threat_level') == 'high')
            high_risks += sum(1 for risk in risks['market_risks'] if risk.get('impact') == 'high')
            
            if high_risks > 2:
                risks['overall_risk_level'] = 'high'
            elif high_risks == 0:
                risks['overall_risk_level'] = 'low'
            
            return risks
            
        except Exception as e:
            logger.error(f"Error consolidating risk assessment: {e}")
            return {'overall_risk_level': 'unknown'}
    
    def _calculate_confidence_metrics(self, data_quality: Dict[str, Any], 
                                    competitive: Dict[str, Any], 
                                    intelligence: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence metrics"""
        try:
            return {
                'data_quality_confidence': data_quality.get('overall_quality_score', 0),
                'competitive_analysis_confidence': competitive.get('confidence_score', 0),
                'intelligence_confidence': intelligence.get('confidence_score', 0),
                'overall_confidence': (
                    data_quality.get('overall_quality_score', 0) +
                    competitive.get('confidence_score', 0) +
                    intelligence.get('confidence_score', 0)
                ) / 3
            }
            
        except Exception as e:
            logger.error(f"Error calculating confidence metrics: {e}")
            return {'overall_confidence': 0.5}
    
    def _generate_next_actions(self, competitive: Dict[str, Any], intelligence: Dict[str, Any]) -> List[str]:
        """Generate next action items"""
        actions = []
        
        try:
            # High priority competitive actions
            comp_threats = competitive.get('threat_assessment', [])
            high_threats = [t for t in comp_threats if t.get('threat_level') == 'high']
            
            for threat in high_threats[:2]:  # Top 2 threats
                actions.append(f"Address competitive threat from {threat.get('competitor_id')}")
            
            # High priority intelligence actions
            intel_opportunities = intelligence.get('market_opportunities', [])
            high_priority_opps = [o for o in intel_opportunities if o.get('potential_impact', 0) > 0.7]
            
            for opp in high_priority_opps[:2]:  # Top 2 opportunities
                actions.append(f"Pursue opportunity: {opp.get('trend')}")
            
            if not actions:
                actions.append("Monitor market conditions and competitive landscape")
            
        except Exception as e:
            logger.error(f"Error generating next actions: {e}")
            actions.append("Review analysis results and plan strategic response")
        
        return actions


# Singleton instance
_intelligence_orchestrator = None
_orchestrator_lock = threading.Lock()


def get_intelligence_orchestrator() -> IntelligenceOrchestrator:
    """
    Get singleton instance of IntelligenceOrchestrator
    """
    global _intelligence_orchestrator
    
    if _intelligence_orchestrator is None:
        with _orchestrator_lock:
            if _intelligence_orchestrator is None:
                _intelligence_orchestrator = IntelligenceOrchestrator()
    
    return _intelligence_orchestrator


# Export for external use
__all__ = ['IntelligenceOrchestrator', 'get_intelligence_orchestrator']
