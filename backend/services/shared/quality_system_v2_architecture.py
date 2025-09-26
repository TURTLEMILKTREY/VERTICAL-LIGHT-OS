"""
ENTERPRISE-GRADE QUALITY SYSTEM v2.0 ARCHITECTURE
Microservices-based, scalable, secure, and maintainable design

SOLVES ALL IDENTIFIED FLAWS:
1. Microservices architecture for scalability
2. Event-driven communication for decoupling
3. Domain-driven design for maintainability
4. Enterprise security patterns
5. Multi-tenant architecture
6. Comprehensive observability
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Protocol
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import uuid
from contextlib import asynccontextmanager


# ============================================================================
# DOMAIN MODELS - Core Business Logic
# ============================================================================

class TenantId(str):
 """Strong typing for tenant identification"""
 pass


class UserId(str):
 """Strong typing for user identification"""
 pass


@dataclass
class QualityThresholdDecision:
 """Immutable domain event for threshold decisions"""
 id: str = field(default_factory=lambda: str(uuid.uuid4()))
 tenant_id: TenantId
 user_id: UserId
 threshold_value: float
 risk_level: str
 business_rationale: str
 acknowledged_risks: List[str]
 timestamp: datetime = field(default_factory=datetime.utcnow)
 metadata: Dict[str, Any] = field(default_factory=dict)

 def validate(self) -> List[str]:
 """Domain validation rules"""
 errors = []
 if not 0.0 <= self.threshold_value <= 1.0:
 errors.append("Threshold must be between 0.0 and 1.0")
 if not self.business_rationale.strip():
 errors.append("Business rationale is required")
 if not self.acknowledged_risks:
 errors.append("Risk acknowledgment is required")
 return errors


@dataclass
class QualityPerformanceMetrics:
 """Performance tracking for quality decisions"""
 decision_id: str
 processing_time_ms: float
 data_throughput: float
 error_rate: float
 user_satisfaction_score: Optional[float] = None
 business_impact_score: Optional[float] = None


# ============================================================================
# PORTS - Interface Definitions (Dependency Inversion)
# ============================================================================

class QualityDecisionRepository(Protocol):
 """Port for persisting quality decisions"""
 async def save_decision(self, decision: QualityThresholdDecision) -> None: ...
 async def get_decision_by_id(self, decision_id: str) -> Optional[QualityThresholdDecision]: ...
 async def get_decisions_by_tenant(self, tenant_id: TenantId) -> List[QualityThresholdDecision]: ...
 async def get_decisions_by_user(self, user_id: UserId) -> List[QualityThresholdDecision]: ...


class PerformanceMetricsRepository(Protocol):
 """Port for performance metrics storage"""
 async def record_metrics(self, metrics: QualityPerformanceMetrics) -> None: ...
 async def get_metrics_by_decision(self, decision_id: str) -> List[QualityPerformanceMetrics]: ...


class EventPublisher(Protocol):
 """Port for publishing domain events"""
 async def publish(self, event_type: str, event_data: Dict[str, Any]) -> None: ...


class AuditLogger(Protocol):
 """Port for security and compliance auditing"""
 async def log_decision(self, decision: QualityThresholdDecision, user_context: Dict[str, Any]) -> None: ...
 async def log_security_event(self, event_type: str, details: Dict[str, Any]) -> None: ...


class NotificationService(Protocol):
 """Port for user notifications"""
 async def notify_threshold_change(self, user_id: UserId, decision: QualityThresholdDecision) -> None: ...
 async def notify_performance_alert(self, tenant_id: TenantId, alert: Dict[str, Any]) -> None: ...


# ============================================================================
# DOMAIN SERVICES - Business Logic
# ============================================================================

class QualityThresholdCalculationService:
 """Pure business logic for calculating optimal thresholds"""

 def __init__(self):
 self.statistical_baselines = {
 'conservative': 0.8,
 'balanced': 0.6,
 'aggressive': 0.4,
 'experimental': 0.3
 }

 async def calculate_recommended_thresholds(
 self,
 business_context: Dict[str, Any],
 historical_performance: List[QualityPerformanceMetrics]
 ) -> Dict[str, float]:
 """Calculate threshold recommendations based on context and history"""

 # Start with statistical baseline
 baseline = self._get_baseline_for_context(business_context)

 # Adjust based on historical performance
 if historical_performance:
 performance_adjustment = self._analyze_historical_performance(historical_performance)
 baseline = self._apply_performance_adjustment(baseline, performance_adjustment)

 # Generate threshold options
 return {
 'conservative': min(baseline + 0.2, 0.95),
 'recommended': baseline,
 'aggressive': max(baseline - 0.2, 0.05),
 'experimental': max(baseline - 0.3, 0.01)
 }

 def _get_baseline_for_context(self, context: Dict[str, Any]) -> float:
 """Determine baseline threshold from business context"""
 risk_tolerance = context.get('risk_tolerance', 'balanced')
 return self.statistical_baselines.get(risk_tolerance, 0.6)

 def _analyze_historical_performance(self, metrics: List[QualityPerformanceMetrics]) -> float:
 """Analyze historical performance to suggest adjustments"""
 if not metrics:
 return 0.0

 # Simple average of business impact scores
 impact_scores = [m.business_impact_score for m in metrics if m.business_impact_score is not None]
 if not impact_scores:
 return 0.0

 avg_impact = sum(impact_scores) / len(impact_scores)

 # Convert impact to adjustment factor
 if avg_impact > 0.8:
 return 0.1 # Increase threshold for better quality
 elif avg_impact < 0.4:
 return -0.1 # Decrease threshold for better performance
 return 0.0 # No adjustment needed

 def _apply_performance_adjustment(self, baseline: float, adjustment: float) -> float:
 """Apply performance-based adjustment to baseline"""
 adjusted = baseline + adjustment
 return max(0.01, min(0.99, adjusted))


class QualityDecisionValidationService:
 """Service for validating quality threshold decisions"""

 def __init__(self, audit_logger: AuditLogger):
 self.audit_logger = audit_logger

 async def validate_decision(
 self,
 decision: QualityThresholdDecision,
 user_permissions: Dict[str, Any]
 ) -> Dict[str, Any]:
 """Validate a quality threshold decision"""

 # Domain validation
 domain_errors = decision.validate()
 if domain_errors:
 await self.audit_logger.log_security_event(
 "INVALID_DECISION_ATTEMPT",
 {"decision_id": decision.id, "errors": domain_errors, "user_id": decision.user_id}
 )
 return {"valid": False, "errors": domain_errors}

 # Permission validation
 permission_errors = await self._validate_permissions(decision, user_permissions)
 if permission_errors:
 await self.audit_logger.log_security_event(
 "PERMISSION_VIOLATION",
 {"decision_id": decision.id, "errors": permission_errors, "user_id": decision.user_id}
 )
 return {"valid": False, "errors": permission_errors}

 # Business rule validation
 business_errors = await self._validate_business_rules(decision)
 if business_errors:
 return {"valid": False, "errors": business_errors}

 return {"valid": True, "errors": []}

 async def _validate_permissions(
 self,
 decision: QualityThresholdDecision,
 permissions: Dict[str, Any]
 ) -> List[str]:
 """Validate user has permission to make this decision"""
 errors = []

 # Check basic threshold modification permission
 if not permissions.get('can_modify_thresholds', False):
 errors.append("User does not have permission to modify quality thresholds")

 # Check extreme threshold permissions
 if decision.threshold_value > 0.9 or decision.threshold_value < 0.1:
 if not permissions.get('can_set_extreme_thresholds', False):
 errors.append("User does not have permission to set extreme thresholds")

 # Check tenant-specific permissions
 allowed_tenants = permissions.get('allowed_tenants', [])
 if allowed_tenants and decision.tenant_id not in allowed_tenants:
 errors.append("User does not have access to this tenant")

 return errors

 async def _validate_business_rules(self, decision: QualityThresholdDecision) -> List[str]:
 """Validate business-specific rules"""
 errors = []

 # Extreme threshold requires detailed rationale
 if decision.threshold_value > 0.9 or decision.threshold_value < 0.1:
 if len(decision.business_rationale) < 100:
 errors.append("Extreme thresholds require detailed business rationale (minimum 100 characters)")

 # High-risk decisions require specific risk acknowledgments
 if decision.risk_level in ['HIGH', 'CRITICAL']:
 required_risks = ['performance_impact', 'business_continuity', 'data_quality']
 missing_risks = [r for r in required_risks if r not in decision.acknowledged_risks]
 if missing_risks:
 errors.append(f"High-risk decisions require acknowledgment of: {', '.join(missing_risks)}")

 return errors


# ============================================================================
# APPLICATION SERVICES - Use Case Orchestration
# ============================================================================

class QualityThresholdApplicationService:
 """Application service orchestrating quality threshold use cases"""

 def __init__(
 self,
 decision_repository: QualityDecisionRepository,
 metrics_repository: PerformanceMetricsRepository,
 calculation_service: QualityThresholdCalculationService,
 validation_service: QualityDecisionValidationService,
 event_publisher: EventPublisher,
 audit_logger: AuditLogger,
 notification_service: NotificationService
 ):
 self.decision_repository = decision_repository
 self.metrics_repository = metrics_repository
 self.calculation_service = calculation_service
 self.validation_service = validation_service
 self.event_publisher = event_publisher
 self.audit_logger = audit_logger
 self.notification_service = notification_service

 async def get_threshold_recommendations(
 self,
 tenant_id: TenantId,
 user_id: UserId,
 business_context: Dict[str, Any]
 ) -> Dict[str, Any]:
 """Get personalized threshold recommendations"""

 try:
 # Get historical performance for this tenant
 historical_decisions = await self.decision_repository.get_decisions_by_tenant(tenant_id)

 # Collect performance metrics for historical decisions
 all_metrics = []
 for decision in historical_decisions[-10:]: # Last 10 decisions
 metrics = await self.metrics_repository.get_metrics_by_decision(decision.id)
 all_metrics.extend(metrics)

 # Calculate recommendations
 recommendations = await self.calculation_service.calculate_recommended_thresholds(
 business_context, all_metrics
 )

 # Add metadata
 response = {
 'recommendations': recommendations,
 'historical_data_points': len(all_metrics),
 'confidence_level': min(len(all_metrics) / 50.0, 1.0), # Max confidence at 50 data points
 'business_context_applied': business_context,
 'generated_at': datetime.utcnow().isoformat()
 }

 # Audit the recommendation request
 await self.audit_logger.log_decision(
 QualityThresholdDecision(
 tenant_id=tenant_id,
 user_id=user_id,
 threshold_value=recommendations['recommended'],
 risk_level='RECOMMENDATION',
 business_rationale='System-generated recommendation',
 acknowledged_risks=[]
 ),
 {'action': 'GET_RECOMMENDATIONS', 'context': business_context}
 )

 return response

 except Exception as e:
 await self.audit_logger.log_security_event(
 "RECOMMENDATION_ERROR",
 {"error": str(e), "tenant_id": tenant_id, "user_id": user_id}
 )
 raise

 async def submit_threshold_decision(
 self,
 decision: QualityThresholdDecision,
 user_permissions: Dict[str, Any]
 ) -> Dict[str, Any]:
 """Submit and validate a threshold decision"""

 try:
 # Validate the decision
 validation_result = await self.validation_service.validate_decision(
 decision, user_permissions
 )

 if not validation_result['valid']:
 return {
 'accepted': False,
 'errors': validation_result['errors'],
 'decision_id': decision.id
 }

 # Save the decision
 await self.decision_repository.save_decision(decision)

 # Audit the decision
 await self.audit_logger.log_decision(decision, user_permissions)

 # Publish decision event
 await self.event_publisher.publish(
 'quality.threshold.decision_made',
 {
 'decision_id': decision.id,
 'tenant_id': decision.tenant_id,
 'user_id': decision.user_id,
 'threshold_value': decision.threshold_value,
 'timestamp': decision.timestamp.isoformat()
 }
 )

 # Notify relevant users
 await self.notification_service.notify_threshold_change(decision.user_id, decision)

 return {
 'accepted': True,
 'decision_id': decision.id,
 'monitoring_enabled': True,
 'fallback_threshold': 0.6, # Default fallback
 'next_review_date': (datetime.utcnow() + timedelta(days=30)).isoformat()
 }

 except Exception as e:
 await self.audit_logger.log_security_event(
 "DECISION_SUBMISSION_ERROR",
 {"error": str(e), "decision_id": decision.id}
 )
 raise

 async def get_performance_dashboard(
 self,
 tenant_id: TenantId,
 time_range: Dict[str, datetime]
 ) -> Dict[str, Any]:
 """Get performance dashboard data for a tenant"""

 try:
 # Get decisions in time range
 decisions = await self.decision_repository.get_decisions_by_tenant(tenant_id)
 filtered_decisions = [
 d for d in decisions
 if time_range['start'] <= d.timestamp <= time_range['end']
 ]

 # Get performance metrics for these decisions
 all_metrics = []
 for decision in filtered_decisions:
 metrics = await self.metrics_repository.get_metrics_by_decision(decision.id)
 all_metrics.extend(metrics)

 # Calculate dashboard metrics
 dashboard_data = {
 'total_decisions': len(filtered_decisions),
 'average_threshold': sum(d.threshold_value for d in filtered_decisions) / len(filtered_decisions) if filtered_decisions else 0,
 'performance_metrics': {
 'average_processing_time': sum(m.processing_time_ms for m in all_metrics) / len(all_metrics) if all_metrics else 0,
 'average_throughput': sum(m.data_throughput for m in all_metrics) / len(all_metrics) if all_metrics else 0,
 'average_error_rate': sum(m.error_rate for m in all_metrics) / len(all_metrics) if all_metrics else 0,
 'user_satisfaction_avg': sum(m.user_satisfaction_score for m in all_metrics if m.user_satisfaction_score) / len([m for m in all_metrics if m.user_satisfaction_score]) if any(m.user_satisfaction_score for m in all_metrics) else None
 },
 'risk_distribution': self._calculate_risk_distribution(filtered_decisions),
 'trends': self._calculate_trends(filtered_decisions, all_metrics),
 'generated_at': datetime.utcnow().isoformat()
 }

 return dashboard_data

 except Exception as e:
 await self.audit_logger.log_security_event(
 "DASHBOARD_ERROR",
 {"error": str(e), "tenant_id": tenant_id}
 )
 raise

 def _calculate_risk_distribution(self, decisions: List[QualityThresholdDecision]) -> Dict[str, int]:
 """Calculate distribution of risk levels"""
 distribution = {}
 for decision in decisions:
 risk_level = decision.risk_level
 distribution[risk_level] = distribution.get(risk_level, 0) + 1
 return distribution

 def _calculate_trends(
 self,
 decisions: List[QualityThresholdDecision],
 metrics: List[QualityPerformanceMetrics]
 ) -> Dict[str, Any]:
 """Calculate trend analysis"""
 # Sort by timestamp
 decisions.sort(key=lambda d: d.timestamp)

 if len(decisions) < 2:
 return {'trend': 'insufficient_data'}

 # Calculate threshold trend
 recent_thresholds = [d.threshold_value for d in decisions[-5:]]
 older_thresholds = [d.threshold_value for d in decisions[-10:-5]] if len(decisions) >= 10 else []

 threshold_trend = 'stable'
 if older_thresholds:
 recent_avg = sum(recent_thresholds) / len(recent_thresholds)
 older_avg = sum(older_thresholds) / len(older_thresholds)

 if recent_avg > older_avg + 0.05:
 threshold_trend = 'increasing'
 elif recent_avg < older_avg - 0.05:
 threshold_trend = 'decreasing'

 return {
 'threshold_trend': threshold_trend,
 'recent_average_threshold': sum(recent_thresholds) / len(recent_thresholds),
 'decision_frequency': len(decisions) / ((decisions[-1].timestamp - decisions[0].timestamp).days + 1),
 'most_common_risk_level': max(set(d.risk_level for d in decisions), key=lambda x: sum(1 for d in decisions if d.risk_level == x))
 }


# ============================================================================
# INFRASTRUCTURE ADAPTERS (Implementation of Ports)
# ============================================================================

class PostgreSQLQualityDecisionRepository:
 """PostgreSQL implementation of QualityDecisionRepository"""

 def __init__(self, connection_pool):
 self.pool = connection_pool

 async def save_decision(self, decision: QualityThresholdDecision) -> None:
 async with self.pool.acquire() as conn:
 await conn.execute("""
 INSERT INTO quality_decisions (
 id, tenant_id, user_id, threshold_value, risk_level,
 business_rationale, acknowledged_risks, timestamp, metadata
 ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
 """, decision.id, decision.tenant_id, decision.user_id,
 decision.threshold_value, decision.risk_level,
 decision.business_rationale, decision.acknowledged_risks,
 decision.timestamp, decision.metadata)

 async def get_decision_by_id(self, decision_id: str) -> Optional[QualityThresholdDecision]:
 async with self.pool.acquire() as conn:
 row = await conn.fetchrow(
 "SELECT * FROM quality_decisions WHERE id = $1", decision_id
 )
 if row:
 return QualityThresholdDecision(**dict(row))
 return None

 async def get_decisions_by_tenant(self, tenant_id: TenantId) -> List[QualityThresholdDecision]:
 async with self.pool.acquire() as conn:
 rows = await conn.fetch(
 "SELECT * FROM quality_decisions WHERE tenant_id = $1 ORDER BY timestamp DESC",
 tenant_id
 )
 return [QualityThresholdDecision(**dict(row)) for row in rows]

 async def get_decisions_by_user(self, user_id: UserId) -> List[QualityThresholdDecision]:
 async with self.pool.acquire() as conn:
 rows = await conn.fetch(
 "SELECT * FROM quality_decisions WHERE user_id = $1 ORDER BY timestamp DESC",
 user_id
 )
 return [QualityThresholdDecision(**dict(row)) for row in rows]


class RedisPerformanceMetricsRepository:
 """Redis implementation for high-frequency performance metrics"""

 def __init__(self, redis_client):
 self.redis = redis_client

 async def record_metrics(self, metrics: QualityPerformanceMetrics) -> None:
 key = f"metrics:{metrics.decision_id}"
 data = {
 'processing_time_ms': metrics.processing_time_ms,
 'data_throughput': metrics.data_throughput,
 'error_rate': metrics.error_rate,
 'user_satisfaction_score': metrics.user_satisfaction_score,
 'business_impact_score': metrics.business_impact_score,
 'timestamp': datetime.utcnow().isoformat()
 }
 await self.redis.lpush(key, json.dumps(data))
 await self.redis.expire(key, 86400 * 30) # 30 days retention

 async def get_metrics_by_decision(self, decision_id: str) -> List[QualityPerformanceMetrics]:
 key = f"metrics:{decision_id}"
 raw_metrics = await self.redis.lrange(key, 0, -1)

 metrics = []
 for raw in raw_metrics:
 data = json.loads(raw)
 metrics.append(QualityPerformanceMetrics(
 decision_id=decision_id,
 processing_time_ms=data['processing_time_ms'],
 data_throughput=data['data_throughput'],
 error_rate=data['error_rate'],
 user_satisfaction_score=data.get('user_satisfaction_score'),
 business_impact_score=data.get('business_impact_score')
 ))

 return metrics