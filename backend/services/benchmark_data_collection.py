"""
Hospital Benchmark Data Collection Service
Comprehensive service for collecting, processing, and analyzing Indian hospital performance data
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
import json
from pathlib import Path

from ..models.hospital_benchmarks import (
    Hospital, PerformanceMetrics, FinancialMetrics, 
    GovernmentSchemeData, BenchmarkStandards,
    CityTier, HospitalType, SpecialtyType, GovernmentScheme,
    HospitalCreate, PerformanceMetricsCreate, FinancialMetricsCreate,
    BenchmarkQuery, BenchmarkResult,
    INDIAN_HOSPITAL_BENCHMARK_CATEGORIES
)
from ..config.advanced_config_manager import ConfigManager
from ..services.shared.error_handling import ApplicationError, ErrorHandler


class BenchmarkDataCollectionError(ApplicationError):
    """Specific error for benchmark data collection issues"""
    pass


class HospitalDataCollector:
    """Service for collecting hospital performance data"""
    
    def __init__(self, db_session: AsyncSession, config: ConfigManager):
        self.db = db_session
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.error_handler = ErrorHandler()
        
        # Data collection sources configuration
        self.data_sources = {
            "hms_apis": config.get("data_collection.hms_apis", []),
            "government_apis": config.get("data_collection.government_apis", {}),
            "survey_platforms": config.get("data_collection.survey_platforms", []),
            "manual_upload": config.get("data_collection.manual_upload", True)
        }
        
        # Target hospital identification
        self.target_hospitals = {
            "tier_1_count": 15,  # Major metro hospitals
            "tier_2_count": 20,  # Tier 2 city hospitals  
            "tier_3_count": 10,  # Smaller city hospitals
            "tier_4_count": 5,   # Town-level hospitals
            "total_target": 50
        }

    async def identify_target_hospitals(self) -> List[Dict[str, Any]]:
        """Identify 50+ target hospitals across India for data collection"""
        
        target_hospitals = []
        
        # Tier 1 Cities - Major Corporate Hospitals
        tier_1_hospitals = [
            {
                "name": "Apollo Hospitals Enterprise",
                "city": "Mumbai",
                "state": "Maharashtra", 
                "city_tier": CityTier.TIER_1,
                "hospital_type": HospitalType.PRIVATE_CORPORATE,
                "bed_count": 500,
                "specialties": ["multispecialty", "cardiology", "oncology"],
                "contact_priority": "high",
                "data_availability": "hms_api"
            },
            {
                "name": "Fortis Healthcare",
                "city": "Delhi",
                "state": "Delhi",
                "city_tier": CityTier.TIER_1,
                "hospital_type": HospitalType.PRIVATE_CORPORATE,
                "bed_count": 400,
                "specialties": ["multispecialty", "cardiology"],
                "contact_priority": "high",
                "data_availability": "manual"
            },
            {
                "name": "Manipal Hospitals",
                "city": "Bangalore",
                "state": "Karnataka",
                "city_tier": CityTier.TIER_1,
                "hospital_type": HospitalType.PRIVATE_CORPORATE,
                "bed_count": 650,
                "specialties": ["multispecialty", "neurology"],
                "contact_priority": "high",
                "data_availability": "hms_api"
            },
            {
                "name": "Max Healthcare",
                "city": "Delhi",
                "state": "Delhi",
                "city_tier": CityTier.TIER_1,
                "hospital_type": HospitalType.PRIVATE_CORPORATE,
                "bed_count": 350,
                "specialties": ["multispecialty", "orthopedics"],
                "contact_priority": "high",
                "data_availability": "manual"
            },
            {
                "name": "Narayana Health",
                "city": "Bangalore",
                "state": "Karnataka",
                "city_tier": CityTier.TIER_1,
                "hospital_type": HospitalType.PRIVATE_CORPORATE,
                "bed_count": 450,
                "specialties": ["multispecialty", "cardiology"],
                "contact_priority": "high",
                "data_availability": "survey"
            },
            # Government Hospitals
            {
                "name": "All Institute of Medical Sciences (AIIMS)",
                "city": "Delhi",
                "state": "Delhi",
                "city_tier": CityTier.TIER_1,
                "hospital_type": HospitalType.GOVERNMENT,
                "bed_count": 2500,
                "specialties": ["multispecialty", "emergency_trauma"],
                "contact_priority": "medium",
                "data_availability": "government_api"
            },
            {
                "name": "King Edward Memorial Hospital",
                "city": "Mumbai",
                "state": "Maharashtra",
                "city_tier": CityTier.TIER_1,
                "hospital_type": HospitalType.GOVERNMENT,
                "bed_count": 1800,
                "specialties": ["multispecialty", "emergency_trauma"],
                "contact_priority": "medium",
                "data_availability": "manual"
            },
            # Medical College Hospitals
            {
                "name": "Christian Medical College",
                "city": "Chennai",
                "state": "Tamil Nadu",
                "city_tier": CityTier.TIER_1,
                "hospital_type": HospitalType.MEDICAL_COLLEGE,
                "bed_count": 2200,
                "specialties": ["multispecialty", "research"],
                "contact_priority": "high",
                "data_availability": "manual"
            },
            # Standalone Private Hospitals
            {
                "name": "Jaslok Hospital",
                "city": "Mumbai",
                "state": "Maharashtra",
                "city_tier": CityTier.TIER_1,
                "hospital_type": HospitalType.PRIVATE_STANDALONE,
                "bed_count": 350,
                "specialties": ["multispecialty"],
                "contact_priority": "medium",
                "data_availability": "manual"
            },
            {
                "name": "Ruby Hall Clinic",
                "city": "Pune",
                "state": "Maharashtra",
                "city_tier": CityTier.TIER_2,
                "hospital_type": HospitalType.PRIVATE_STANDALONE,
                "bed_count": 750,
                "specialties": ["multispecialty", "cardiology"],
                "contact_priority": "high",
                "data_availability": "hms_api"
            }
        ]
        
        # Tier 2 Cities - Regional Leaders
        tier_2_hospitals = [
            {
                "name": "Kokilaben Dhirubhai Ambani Hospital",
                "city": "Pune",
                "state": "Maharashtra",
                "city_tier": CityTier.TIER_2,
                "hospital_type": HospitalType.PRIVATE_STANDALONE,
                "bed_count": 400,
                "specialties": ["multispecialty", "oncology"],
                "contact_priority": "high",
                "data_availability": "manual"
            },
            {
                "name": "Yashoda Hospitals",
                "city": "Hyderabad",
                "state": "Telangana", 
                "city_tier": CityTier.TIER_2,
                "hospital_type": HospitalType.PRIVATE_CORPORATE,
                "bed_count": 500,
                "specialties": ["multispecialty", "gastroenterology"],
                "contact_priority": "high",
                "data_availability": "hms_api"
            },
            {
                "name": "Sterling Hospitals",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "city_tier": CityTier.TIER_2,
                "hospital_type": HospitalType.PRIVATE_STANDALONE,
                "bed_count": 300,
                "specialties": ["multispecialty"],
                "contact_priority": "medium",
                "data_availability": "survey"
            },
            # Additional Tier 2 hospitals across different states
            {
                "name": "Eternal Hospital",
                "city": "Jaipur",
                "state": "Rajasthan",
                "city_tier": CityTier.TIER_2,
                "hospital_type": HospitalType.PRIVATE_STANDALONE,
                "bed_count": 200,
                "specialties": ["multispecialty"],
                "contact_priority": "medium",
                "data_availability": "manual"
            }
        ]
        
        # Add more tier 2, 3, and 4 hospitals...
        target_hospitals.extend(tier_1_hospitals)
        target_hospitals.extend(tier_2_hospitals)
        
        # Generate additional hospitals to reach target of 50+
        additional_hospitals = await self._generate_representative_hospital_list()
        target_hospitals.extend(additional_hospitals)
        
        return target_hospitals[:55]  # Return 55 hospitals for buffer

    async def _generate_representative_hospital_list(self) -> List[Dict[str, Any]]:
        """Generate additional representative hospitals across India"""
        
        additional_hospitals = []
        
        # Tier 3 Cities
        tier_3_cities = [
            ("Indore", "Madhya Pradesh"), ("Bhopal", "Madhya Pradesh"),
            ("Patna", "Bihar"), ("Vadodara", "Gujarat"), 
            ("Agra", "Uttar Pradesh"), ("Nashik", "Maharashtra"),
            ("Coimbatore", "Tamil Nadu"), ("Kochi", "Kerala"),
            ("Mysore", "Karnataka"), ("Guwahati", "Assam")
        ]
        
        for i, (city, state) in enumerate(tier_3_cities):
            additional_hospitals.append({
                "name": f"{city} Multi Specialty Hospital",
                "city": city,
                "state": state,
                "city_tier": CityTier.TIER_3,
                "hospital_type": HospitalType.PRIVATE_STANDALONE,
                "bed_count": 150 + (i * 20),
                "specialties": ["multispecialty"],
                "contact_priority": "medium",
                "data_availability": "manual"
            })
        
        # Tier 4 Cities
        tier_4_cities = [
            ("Shimla", "Himachal Pradesh"), ("Dehradun", "Uttarakhand"),
            ("Ranchi", "Jharkhand"), ("Raipur", "Chhattisgarh"),
            ("Bhubaneswar", "Odisha")
        ]
        
        for i, (city, state) in enumerate(tier_4_cities):
            additional_hospitals.append({
                "name": f"{city} General Hospital",
                "city": city,
                "state": state,
                "city_tier": CityTier.TIER_4,
                "hospital_type": HospitalType.PRIVATE_STANDALONE,
                "bed_count": 80 + (i * 15),
                "specialties": ["multispecialty"],
                "contact_priority": "low",
                "data_availability": "manual"
            })
        
        # Government hospitals in different states
        government_hospitals = [
            {
                "name": "Government Medical College Hospital",
                "city": "Nagpur",
                "state": "Maharashtra",
                "city_tier": CityTier.TIER_2,
                "hospital_type": HospitalType.GOVERNMENT,
                "bed_count": 1000,
                "specialties": ["multispecialty", "emergency_trauma"],
                "contact_priority": "medium",
                "data_availability": "government_api"
            },
            {
                "name": "District Hospital",
                "city": "Lucknow", 
                "state": "Uttar Pradesh",
                "city_tier": CityTier.TIER_2,
                "hospital_type": HospitalType.GOVERNMENT,
                "bed_count": 800,
                "specialties": ["multispecialty"],
                "contact_priority": "low",
                "data_availability": "manual"
            }
        ]
        
        additional_hospitals.extend(government_hospitals)
        return additional_hospitals

    async def create_data_collection_campaigns(self, target_hospitals: List[Dict]) -> Dict[str, Any]:
        """Create systematic data collection campaigns for different hospital types"""
        
        campaigns = {
            "hms_api_integration": {
                "hospitals": [],
                "priority": "high",
                "timeline": "2 weeks",
                "automation_level": "high",
                "expected_data_quality": 9
            },
            "manual_survey": {
                "hospitals": [],
                "priority": "medium", 
                "timeline": "4 weeks",
                "automation_level": "low",
                "expected_data_quality": 7
            },
            "government_api": {
                "hospitals": [],
                "priority": "medium",
                "timeline": "6 weeks",
                "automation_level": "medium",
                "expected_data_quality": 8
            },
            "partner_network": {
                "hospitals": [],
                "priority": "high",
                "timeline": "3 weeks", 
                "automation_level": "medium",
                "expected_data_quality": 8
            }
        }
        
        # Categorize hospitals by data collection method
        for hospital in target_hospitals:
            data_source = hospital.get("data_availability", "manual")
            
            if data_source == "hms_api":
                campaigns["hms_api_integration"]["hospitals"].append(hospital)
            elif data_source == "government_api":
                campaigns["government_api"]["hospitals"].append(hospital)
            elif data_source == "survey":
                campaigns["manual_survey"]["hospitals"].append(hospital)
            else:
                campaigns["partner_network"]["hospitals"].append(hospital)
        
        # Create detailed collection plans
        collection_plans = {}
        
        for campaign_type, campaign_data in campaigns.items():
            collection_plans[campaign_type] = await self._create_collection_plan(
                campaign_type, campaign_data
            )
        
        return collection_plans

    async def _create_collection_plan(self, campaign_type: str, campaign_data: Dict) -> Dict:
        """Create detailed data collection plan for specific campaign type"""
        
        base_plan = {
            "campaign_name": f"Hospital Data Collection - {campaign_type.title()}",
            "target_hospitals": len(campaign_data["hospitals"]),
            "timeline": campaign_data["timeline"],
            "priority": campaign_data["priority"],
            "automation_level": campaign_data["automation_level"]
        }
        
        if campaign_type == "hms_api_integration":
            base_plan.update({
                "method": "API Integration",
                "data_points": [
                    "Real-time patient flow data",
                    "Financial transaction data", 
                    "Operational metrics",
                    "Resource utilization data",
                    "Quality indicators"
                ],
                "collection_frequency": "daily",
                "data_validation": "automated",
                "expected_completion": "95%",
                "technical_requirements": [
                    "API access credentials",
                    "Data mapping documentation",
                    "Security compliance",
                    "Rate limiting configuration"
                ],
                "success_criteria": {
                    "data_completeness": 90,
                    "data_accuracy": 95,
                    "collection_reliability": 98
                }
            })
        
        elif campaign_type == "manual_survey":
            base_plan.update({
                "method": "Digital Survey + Manual Collection",
                "data_points": [
                    "Performance metrics questionnaire",
                    "Financial summary data",
                    "Operational efficiency indicators", 
                    "Quality measures",
                    "Staff satisfaction metrics"
                ],
                "collection_frequency": "monthly",
                "data_validation": "manual_review",
                "expected_completion": "75%",
                "survey_platform": "Google Forms + Custom Portal",
                "follow_up_strategy": [
                    "Initial email invitation",
                    "Phone call follow-up after 3 days",
                    "Site visit for high-priority hospitals",
                    "Incentive program for completion"
                ],
                "success_criteria": {
                    "response_rate": 70,
                    "data_completeness": 80,
                    "data_accuracy": 85
                }
            })
        
        elif campaign_type == "government_api":
            base_plan.update({
                "method": "Government API + Public Data Sources",
                "data_points": [
                    "AYUSH portal data",
                    "National Health Mission data",
                    "State health department data",
                    "Insurance claim data",
                    "Accreditation data"
                ],
                "collection_frequency": "weekly",
                "data_validation": "cross_reference",
                "expected_completion": "60%",
                "api_sources": [
                    "National Health Portal",
                    "CGHS database",
                    "State health department APIs",
                    "NABH accreditation database"
                ],
                "success_criteria": {
                    "data_completeness": 70,
                    "data_accuracy": 90,
                    "collection_reliability": 85
                }
            })
        
        elif campaign_type == "partner_network":
            base_plan.update({
                "method": "Healthcare Partner Network",
                "data_points": [
                    "Partner-provided performance data",
                    "Benchmarking study participation",
                    "Industry association data",
                    "Consultant-collected data",
                    "Peer network sharing"
                ],
                "collection_frequency": "quarterly",
                "data_validation": "peer_review",
                "expected_completion": "80%",
                "partner_types": [
                    "Healthcare consulting firms",
                    "Hospital management companies",
                    "Medical equipment vendors",
                    "Healthcare IT providers",
                    "Industry associations"
                ],
                "success_criteria": {
                    "partner_participation": 75,
                    "data_completeness": 85,
                    "data_accuracy": 88
                }
            })
        
        return base_plan

    async def collect_performance_data(self, hospital_id: str, collection_method: str) -> Dict[str, Any]:
        """Collect performance data for a specific hospital"""
        
        try:
            collection_results = {
                "hospital_id": hospital_id,
                "collection_method": collection_method,
                "timestamp": datetime.utcnow(),
                "success": False,
                "data_collected": {},
                "quality_score": 0,
                "errors": []
            }
            
            if collection_method == "hms_api":
                results = await self._collect_via_hms_api(hospital_id)
            elif collection_method == "manual_survey":
                results = await self._collect_via_survey(hospital_id)
            elif collection_method == "government_api":
                results = await self._collect_via_government_api(hospital_id)
            elif collection_method == "partner_network":
                results = await self._collect_via_partners(hospital_id)
            else:
                raise BenchmarkDataCollectionError(f"Unknown collection method: {collection_method}")
            
            collection_results.update(results)
            
            # Store collected data
            if collection_results["success"]:
                await self._store_collected_data(hospital_id, collection_results["data_collected"])
                
            return collection_results
            
        except Exception as e:
            self.error_handler.handle_error(e, {
                "hospital_id": hospital_id,
                "collection_method": collection_method
            })
            raise BenchmarkDataCollectionError(f"Data collection failed: {str(e)}")

    async def _collect_via_hms_api(self, hospital_id: str) -> Dict[str, Any]:
        """Collect data via Hospital Management System API integration"""
        
        # Mock HMS API integration - replace with actual HMS API calls
        collected_data = {
            "performance_metrics": {
                "bed_occupancy_rate": Decimal("78.5"),
                "average_length_of_stay": Decimal("4.2"),
                "patient_satisfaction_score": Decimal("8.1"),
                "or_utilization_rate": Decimal("82.3"),
                "ed_average_wait_time": 45
            },
            "financial_metrics": {
                "total_revenue": Decimal("245.8"),  # INR Lakhs
                "total_costs": Decimal("198.2"),
                "accounts_receivable_days": 42,
                "cash_percentage": Decimal("35.2"),
                "government_scheme_percentage": Decimal("28.5")
            },
            "government_schemes": {
                "ayushman_bharat_cases": 156,
                "cghs_cases": 89,
                "average_reimbursement_days": 28,
                "approval_rate": Decimal("87.5")
            }
        }
        
        return {
            "success": True,
            "data_collected": collected_data,
            "quality_score": 9,
            "collection_timestamp": datetime.utcnow(),
            "data_source": "hms_api"
        }

    async def _collect_via_survey(self, hospital_id: str) -> Dict[str, Any]:
        """Collect data via manual surveys and questionnaires"""
        
        # Mock survey data collection
        collected_data = {
            "performance_metrics": {
                "bed_occupancy_rate": Decimal("72.1"),
                "patient_satisfaction_score": Decimal("7.8"),
                "staff_satisfaction_score": Decimal("7.2"),
                "readmission_rate": Decimal("8.5")
            },
            "financial_metrics": {
                "revenue_per_bed": Decimal("12.5"),  # INR Lakhs
                "cost_per_patient": Decimal("15420"),
                "ebitda_margin": Decimal("18.5")
            }
        }
        
        return {
            "success": True,
            "data_collected": collected_data,
            "quality_score": 7,
            "collection_timestamp": datetime.utcnow(),
            "data_source": "manual_survey"
        }

    async def _collect_via_government_api(self, hospital_id: str) -> Dict[str, Any]:
        """Collect data via government APIs and public sources"""
        
        # Mock government API data
        collected_data = {
            "government_schemes": {
                "ayushman_bharat_cases": 234,
                "total_approved_amount": Decimal("1245680"),
                "approval_rate": Decimal("91.2"),
                "average_reimbursement_days": 32
            },
            "accreditation_data": {
                "nabh_accredited": True,
                "nabh_score": Decimal("8.4"),
                "jci_accredited": False
            }
        }
        
        return {
            "success": True,
            "data_collected": collected_data,
            "quality_score": 8,
            "collection_timestamp": datetime.utcnow(),
            "data_source": "government_api"
        }

    async def _collect_via_partners(self, hospital_id: str) -> Dict[str, Any]:
        """Collect data via healthcare partner network"""
        
        # Mock partner network data
        collected_data = {
            "performance_metrics": {
                "bed_occupancy_rate": Decimal("75.8"),
                "or_utilization_rate": Decimal("79.2"),
                "staff_turnover_rate": Decimal("12.5")
            },
            "benchmarking_data": {
                "peer_ranking": 3,
                "total_peers": 12,
                "category": "tier_2_private_standalone"
            }
        }
        
        return {
            "success": True,
            "data_collected": collected_data,
            "quality_score": 8,
            "collection_timestamp": datetime.utcnow(),
            "data_source": "partner_network"
        }

    async def _store_collected_data(self, hospital_id: str, data: Dict[str, Any]) -> None:
        """Store collected data in the benchmark database"""
        
        try:
            current_period = datetime.utcnow().strftime("%Y-%m")
            
            # Store performance metrics
            if "performance_metrics" in data:
                perf_data = PerformanceMetricsCreate(
                    hospital_id=hospital_id,
                    data_period=current_period,
                    data_type="monthly",
                    **data["performance_metrics"]
                )
                
                # Convert to database model and save
                perf_record = PerformanceMetrics(**perf_data.dict())
                self.db.add(perf_record)
            
            # Store financial metrics
            if "financial_metrics" in data:
                fin_data = FinancialMetricsCreate(
                    hospital_id=hospital_id,
                    data_period=current_period,
                    data_type="monthly",
                    **data["financial_metrics"]
                )
                
                fin_record = FinancialMetrics(**fin_data.dict())
                self.db.add(fin_record)
            
            # Store government scheme data
            if "government_schemes" in data:
                scheme_record = GovernmentSchemeData(
                    hospital_id=hospital_id,
                    scheme_type=GovernmentScheme.AYUSHMAN_BHARAT.value,
                    data_period=current_period,
                    **data["government_schemes"]
                )
                self.db.add(scheme_record)
            
            await self.db.commit()
            self.logger.info(f"Successfully stored data for hospital {hospital_id}")
            
        except Exception as e:
            await self.db.rollback()
            self.logger.error(f"Failed to store data for hospital {hospital_id}: {str(e)}")
            raise

    async def execute_full_data_collection(self) -> Dict[str, Any]:
        """Execute complete data collection campaign for all target hospitals"""
        
        collection_summary = {
            "start_time": datetime.utcnow(),
            "target_hospitals": 0,
            "successful_collections": 0,
            "failed_collections": 0,
            "data_quality_average": 0,
            "collection_methods": {},
            "errors": [],
            "completion_rate": 0
        }
        
        try:
            # Get target hospitals
            target_hospitals = await self.identify_target_hospitals()
            collection_summary["target_hospitals"] = len(target_hospitals)
            
            # Create collection campaigns
            campaigns = await self.create_data_collection_campaigns(target_hospitals)
            
            # Execute collections
            quality_scores = []
            
            for campaign_type, plan in campaigns.items():
                campaign_results = {
                    "attempted": 0,
                    "successful": 0,
                    "failed": 0,
                    "quality_scores": []
                }
                
                for hospital in plan.get("hospitals", []):
                    try:
                        # Create hospital record first
                        hospital_record = await self._create_hospital_record(hospital)
                        
                        # Collect data
                        collection_method = hospital.get("data_availability", "manual")
                        results = await self.collect_performance_data(
                            hospital_record.id, collection_method
                        )
                        
                        campaign_results["attempted"] += 1
                        
                        if results["success"]:
                            campaign_results["successful"] += 1
                            campaign_results["quality_scores"].append(results["quality_score"])
                            quality_scores.append(results["quality_score"])
                        else:
                            campaign_results["failed"] += 1
                            collection_summary["errors"].extend(results.get("errors", []))
                        
                        # Add delay between collections
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        campaign_results["failed"] += 1
                        collection_summary["errors"].append(str(e))
                        self.logger.error(f"Collection failed for hospital {hospital['name']}: {str(e)}")
                
                collection_summary["collection_methods"][campaign_type] = campaign_results
            
            # Calculate summary statistics
            total_attempted = sum(r["attempted"] for r in collection_summary["collection_methods"].values())
            total_successful = sum(r["successful"] for r in collection_summary["collection_methods"].values())
            
            collection_summary["successful_collections"] = total_successful
            collection_summary["failed_collections"] = total_attempted - total_successful
            collection_summary["completion_rate"] = (total_successful / total_attempted * 100) if total_attempted > 0 else 0
            collection_summary["data_quality_average"] = np.mean(quality_scores) if quality_scores else 0
            collection_summary["end_time"] = datetime.utcnow()
            
            self.logger.info(f"Data collection completed: {total_successful}/{total_attempted} hospitals")
            
            return collection_summary
            
        except Exception as e:
            collection_summary["errors"].append(str(e))
            self.error_handler.handle_error(e, collection_summary)
            raise BenchmarkDataCollectionError(f"Full data collection failed: {str(e)}")

    async def _create_hospital_record(self, hospital_data: Dict[str, Any]) -> Hospital:
        """Create or update hospital record in database"""
        
        # Check if hospital already exists
        existing = await self.db.execute(
            text("SELECT * FROM hospitals WHERE name = :name AND city = :city"),
            {"name": hospital_data["name"], "city": hospital_data["city"]}
        )
        
        if existing.first():
            return existing.first()
        
        # Create new hospital record
        hospital_create = HospitalCreate(**hospital_data)
        hospital_record = Hospital(**hospital_create.dict())
        
        self.db.add(hospital_record)
        await self.db.commit()
        await self.db.refresh(hospital_record)
        
        return hospital_record


class BenchmarkAnalyzer:
    """Service for analyzing collected benchmark data"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.logger = logging.getLogger(__name__)

    async def create_tier_wise_benchmarks(self) -> Dict[str, Any]:
        """Create benchmarks organized by city tier"""
        
        benchmarks = {}
        
        for tier in CityTier:
            tier_data = await self._analyze_tier_performance(tier)
            benchmarks[tier.value] = tier_data
        
        return benchmarks

    async def _analyze_tier_performance(self, tier: CityTier) -> Dict[str, Any]:
        """Analyze performance metrics for specific city tier"""
        
        # Query performance data for tier
        query = """
            SELECT 
                h.city_tier,
                h.hospital_type,
                pm.*
            FROM performance_metrics pm
            JOIN hospitals h ON pm.hospital_id = h.id
            WHERE h.city_tier = :tier
            AND pm.data_period >= :start_period
        """
        
        start_period = (datetime.utcnow() - timedelta(days=365)).strftime("%Y-%m")
        
        result = await self.db.execute(
            text(query),
            {"tier": tier.value, "start_period": start_period}
        )
        
        data = result.fetchall()
        
        if not data:
            return {"sample_size": 0, "benchmarks": {}}
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame([dict(row) for row in data])
        
        # Calculate benchmark statistics
        benchmarks = {}
        
        numeric_columns = [
            "bed_occupancy_rate", "average_length_of_stay", "patient_satisfaction_score",
            "or_utilization_rate", "readmission_rate", "staff_satisfaction_score"
        ]
        
        for col in numeric_columns:
            if col in df.columns and df[col].notna().sum() > 0:
                benchmarks[col] = {
                    "percentile_25": float(df[col].quantile(0.25)),
                    "percentile_50": float(df[col].quantile(0.50)),
                    "percentile_75": float(df[col].quantile(0.75)),
                    "percentile_90": float(df[col].quantile(0.90)),
                    "mean": float(df[col].mean()),
                    "std_dev": float(df[col].std()),
                    "sample_size": int(df[col].notna().sum())
                }
        
        return {
            "sample_size": len(df),
            "hospital_count": df["hospital_id"].nunique(),
            "benchmarks": benchmarks,
            "analysis_period": start_period,
            "last_updated": datetime.utcnow().isoformat()
        }

    async def create_specialty_benchmarks(self) -> Dict[str, Any]:
        """Create specialty-wise performance benchmarks"""
        
        specialty_benchmarks = {}
        
        for specialty in SpecialtyType:
            specialty_data = await self._analyze_specialty_performance(specialty)
            specialty_benchmarks[specialty.value] = specialty_data
        
        return specialty_benchmarks

    async def _analyze_specialty_performance(self, specialty: SpecialtyType) -> Dict[str, Any]:
        """Analyze performance for specific medical specialty"""
        
        # This would involve complex queries joining hospitals, specialties, and performance data
        # For now, returning mock data structure
        
        return {
            "specialty_type": specialty.value,
            "hospital_count": 15,
            "benchmarks": {
                "bed_occupancy_rate": {"median": 75.5, "p75": 82.1, "p90": 88.2},
                "patient_satisfaction": {"median": 8.1, "p75": 8.7, "p90": 9.2},
                "average_length_of_stay": {"median": 4.2, "p75": 5.1, "p90": 6.8}
            },
            "last_updated": datetime.utcnow().isoformat()
        }

    async def analyze_government_scheme_patterns(self) -> Dict[str, Any]:
        """Analyze government scheme reimbursement patterns"""
        
        scheme_analysis = {}
        
        for scheme in GovernmentScheme:
            scheme_data = await self._analyze_scheme_performance(scheme)
            scheme_analysis[scheme.value] = scheme_data
        
        return scheme_analysis

    async def _analyze_scheme_performance(self, scheme: GovernmentScheme) -> Dict[str, Any]:
        """Analyze reimbursement patterns for specific government scheme"""
        
        query = """
            SELECT 
                h.city_tier,
                h.hospital_type,
                gsd.*
            FROM government_scheme_data gsd
            JOIN hospitals h ON gsd.hospital_id = h.id
            WHERE gsd.scheme_type = :scheme
            AND gsd.data_period >= :start_period
        """
        
        start_period = (datetime.utcnow() - timedelta(days=180)).strftime("%Y-%m")
        
        result = await self.db.execute(
            text(query),
            {"scheme": scheme.value, "start_period": start_period}
        )
        
        data = result.fetchall()
        
        if not data:
            return {"sample_size": 0, "analysis": {}}
        
        df = pd.DataFrame([dict(row) for row in data])
        
        analysis = {
            "sample_size": len(df),
            "hospital_count": df["hospital_id"].nunique(),
            "total_cases": int(df["total_cases"].sum()) if "total_cases" in df else 0,
            "average_approval_rate": float(df["approval_rate"].mean()) if "approval_rate" in df else 0,
            "average_reimbursement_days": float(df["average_reimbursement_days"].mean()) if "average_reimbursement_days" in df else 0,
            "tier_wise_performance": {},
            "hospital_type_performance": {}
        }
        
        # Tier-wise analysis
        if "city_tier" in df.columns:
            for tier in df["city_tier"].unique():
                tier_df = df[df["city_tier"] == tier]
                analysis["tier_wise_performance"][tier] = {
                    "approval_rate": float(tier_df["approval_rate"].mean()) if "approval_rate" in tier_df else 0,
                    "reimbursement_days": float(tier_df["average_reimbursement_days"].mean()) if "average_reimbursement_days" in tier_df else 0,
                    "case_count": int(tier_df["total_cases"].sum()) if "total_cases" in tier_df else 0
                }
        
        return analysis