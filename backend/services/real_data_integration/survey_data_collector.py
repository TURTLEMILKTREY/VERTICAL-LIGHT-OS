"""
Real Survey Data Collection Service
Production survey and manual data collection system for Indian hospitals
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import json
import aiohttp
from aiohttp import ClientSession, ClientTimeout
import pandas as pd
from urllib.parse import urlencode, quote
import hashlib
from pathlib import Path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import xlsxwriter
from io import BytesIO

from ...models.hospital_benchmarks import (
    Hospital, CityTier, HospitalType, SpecialtyType
)
from ...config.advanced_config_manager import ConfigManager
from ...services.shared.error_handling import ApplicationError


class SurveyPlatform(Enum):
    """Supported survey platforms"""
    GOOGLE_FORMS = "google_forms"
    MICROSOFT_FORMS = "microsoft_forms"
    TYPEFORM = "typeform"
    SURVEYMONKEY = "surveymonkey"
    CUSTOM_SURVEY = "custom_survey"
    WHATSAPP_SURVEY = "whatsapp_survey"
    EMAIL_SURVEY = "email_survey"


class SurveyType(Enum):
    """Types of surveys for hospital data collection"""
    PERFORMANCE_METRICS = "performance_metrics"
    FINANCIAL_DATA = "financial_data"
    STAFF_SATISFACTION = "staff_satisfaction"
    PATIENT_SATISFACTION = "patient_satisfaction"
    GOVERNMENT_SCHEMES = "government_schemes"
    OPERATIONAL_DATA = "operational_data"
    QUALITY_INDICATORS = "quality_indicators"


@dataclass
class SurveyConfiguration:
    """Survey configuration for different data collection needs"""
    survey_type: SurveyType
    platform: SurveyPlatform
    survey_id: Optional[str] = None
    survey_url: Optional[str] = None
    questions: List[Dict[str, Any]] = None
    target_respondents: List[str] = None
    reminder_schedule: List[int] = None  # Days for reminders
    incentive_amount: Optional[Decimal] = None
    completion_deadline: Optional[datetime] = None
    
    def __post_init__(self):
        if self.questions is None:
            self.questions = []
        if self.target_respondents is None:
            self.target_respondents = []
        if self.reminder_schedule is None:
            self.reminder_schedule = [3, 7, 14]  # Default reminders


@dataclass
class HospitalContact:
    """Hospital contact information for surveys"""
    hospital_id: str
    primary_contact_name: str
    primary_contact_email: str
    primary_contact_phone: str
    admin_contact_name: Optional[str] = None
    admin_contact_email: Optional[str] = None
    finance_contact_name: Optional[str] = None
    finance_contact_email: Optional[str] = None
    ceo_contact_name: Optional[str] = None
    ceo_contact_email: Optional[str] = None
    preferred_language: str = "english"
    whatsapp_number: Optional[str] = None


class SurveyDataCollectionError(ApplicationError):
    """Survey data collection errors"""
    pass


class RealSurveyDataCollector:
    """Production Survey Data Collection Service"""
    
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Survey platform configurations
        self.platform_configs = {
            SurveyPlatform.GOOGLE_FORMS: {
                "api_base": "https://forms.googleapis.com/v1",
                "auth_required": True,
                "response_format": "json"
            },
            SurveyPlatform.MICROSOFT_FORMS: {
                "api_base": "https://graph.microsoft.com/v1.0/forms",
                "auth_required": True,
                "response_format": "json"
            },
            SurveyPlatform.TYPEFORM: {
                "api_base": "https://api.typeform.com",
                "auth_required": True,
                "response_format": "json"
            },
            SurveyPlatform.SURVEYMONKEY: {
                "api_base": "https://api.surveymonkey.com/v3",
                "auth_required": True,
                "response_format": "json"
            }
        }
        
        # Survey question templates
        self.survey_templates = self._initialize_survey_templates()
        
        # Active survey campaigns
        self.active_campaigns: Dict[str, Dict] = {}
        
        # Email configuration
        self.email_config = self._get_email_config()
        
    def _initialize_survey_templates(self) -> Dict[SurveyType, Dict[str, Any]]:
        """Initialize survey question templates for different data collection needs"""
        
        return {
            SurveyType.PERFORMANCE_METRICS: {
                "title": "Hospital Performance Metrics Survey",
                "description": "Monthly performance data collection for benchmarking",
                "questions": [
                    {
                        "id": "bed_occupancy",
                        "question": "What is your current average bed occupancy rate (%)?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 0, "max": 100}
                    },
                    {
                        "id": "average_los",
                        "question": "What is your average length of stay (days)?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 0, "max": 30}
                    },
                    {
                        "id": "patient_satisfaction",
                        "question": "What is your patient satisfaction score (1-10)?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 1, "max": 10}
                    },
                    {
                        "id": "or_utilization",
                        "question": "What is your OR utilization rate (%)?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 0, "max": 100}
                    },
                    {
                        "id": "ed_wait_time",
                        "question": "What is your average Emergency Department wait time (minutes)?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 0, "max": 300}
                    },
                    {
                        "id": "readmission_rate",
                        "question": "What is your 30-day readmission rate (%)?",
                        "type": "number",
                        "required": False,
                        "validation": {"min": 0, "max": 25}
                    },
                    {
                        "id": "infection_rate",
                        "question": "What is your hospital-acquired infection rate (%)?",
                        "type": "number",
                        "required": False,
                        "validation": {"min": 0, "max": 10}
                    }
                ]
            },
            
            SurveyType.FINANCIAL_DATA: {
                "title": "Hospital Financial Performance Survey",
                "description": "Monthly financial metrics for performance analysis",
                "questions": [
                    {
                        "id": "total_revenue",
                        "question": "What is your total monthly revenue (INR Lakhs)?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 0}
                    },
                    {
                        "id": "total_costs",
                        "question": "What are your total monthly costs (INR Lakhs)?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 0}
                    },
                    {
                        "id": "ar_days",
                        "question": "What are your Accounts Receivable days?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 0, "max": 180}
                    },
                    {
                        "id": "cash_percentage",
                        "question": "What percentage of revenue is from cash patients (%)?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 0, "max": 100}
                    },
                    {
                        "id": "insurance_percentage",
                        "question": "What percentage of revenue is from insurance (%)?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 0, "max": 100}
                    },
                    {
                        "id": "government_scheme_percentage",
                        "question": "What percentage of revenue is from government schemes (%)?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 0, "max": 100}
                    },
                    {
                        "id": "ebitda_margin",
                        "question": "What is your EBITDA margin (%)?",
                        "type": "number",
                        "required": False,
                        "validation": {"min": -50, "max": 50}
                    }
                ]
            },
            
            SurveyType.GOVERNMENT_SCHEMES: {
                "title": "Government Health Schemes Performance Survey",
                "description": "Monthly data on government health scheme performance",
                "questions": [
                    {
                        "id": "ayushman_cases",
                        "question": "How many Ayushman Bharat cases did you treat this month?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 0}
                    },
                    {
                        "id": "ayushman_revenue",
                        "question": "What was the total Ayushman Bharat revenue (INR Lakhs)?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 0}
                    },
                    {
                        "id": "ayushman_approval_rate",
                        "question": "What is your Ayushman Bharat approval rate (%)?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 0, "max": 100}
                    },
                    {
                        "id": "cghs_cases",
                        "question": "How many CGHS cases did you treat this month?",
                        "type": "number",
                        "required": False,
                        "validation": {"min": 0}
                    },
                    {
                        "id": "esi_cases",
                        "question": "How many ESI cases did you treat this month?",
                        "type": "number",
                        "required": False,
                        "validation": {"min": 0}
                    },
                    {
                        "id": "reimbursement_delay",
                        "question": "What is your average reimbursement delay in days?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 0, "max": 365}
                    },
                    {
                        "id": "scheme_challenges",
                        "question": "What are your main challenges with government schemes?",
                        "type": "multiple_choice",
                        "required": False,
                        "options": [
                            "Delayed reimbursements",
                            "Complex documentation",
                            "Low package rates",
                            "Frequent policy changes",
                            "Technology issues",
                            "Other"
                        ]
                    }
                ]
            },
            
            SurveyType.STAFF_SATISFACTION: {
                "title": "Hospital Staff Satisfaction Survey",
                "description": "Quarterly staff satisfaction and productivity assessment",
                "questions": [
                    {
                        "id": "total_doctors",
                        "question": "How many doctors are currently employed?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 0}
                    },
                    {
                        "id": "total_nurses",
                        "question": "How many nurses are currently employed?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 0}
                    },
                    {
                        "id": "staff_turnover",
                        "question": "What is your monthly staff turnover rate (%)?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 0, "max": 50}
                    },
                    {
                        "id": "staff_satisfaction_score",
                        "question": "What is your overall staff satisfaction score (1-10)?",
                        "type": "number",
                        "required": True,
                        "validation": {"min": 1, "max": 10}
                    },
                    {
                        "id": "overtime_hours",
                        "question": "Average overtime hours per staff member per month?",
                        "type": "number",
                        "required": False,
                        "validation": {"min": 0, "max": 100}
                    }
                ]
            }
        }
    
    def _get_email_config(self) -> Dict[str, Any]:
        """Get email configuration for survey distribution"""
        return {
            "smtp_server": self.config.get("email.smtp_server", "smtp.gmail.com"),
            "smtp_port": self.config.get("email.smtp_port", 587),
            "username": self.config.get("email.username"),
            "password": self.config.get("email.password"),
            "from_name": self.config.get("email.from_name", "Hospital Benchmark Survey"),
            "from_email": self.config.get("email.from_email")
        }
    
    async def create_survey_campaign(self, survey_type: SurveyType,
                                   target_hospitals: List[str],
                                   platform: SurveyPlatform = SurveyPlatform.CUSTOM_SURVEY,
                                   incentive_amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """Create a new survey campaign for data collection"""
        
        try:
            campaign_id = f"survey_{survey_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Get survey template
            survey_template = self.survey_templates.get(survey_type)
            if not survey_template:
                raise SurveyDataCollectionError(f"No template found for survey type: {survey_type.value}")
            
            # Create survey configuration
            survey_config = SurveyConfiguration(
                survey_type=survey_type,
                platform=platform,
                questions=survey_template["questions"],
                target_respondents=target_hospitals,
                incentive_amount=incentive_amount,
                completion_deadline=datetime.now() + timedelta(days=14)  # 2 weeks deadline
            )
            
            # Create survey on platform
            if platform == SurveyPlatform.GOOGLE_FORMS:
                survey_url = await self._create_google_form(survey_template, campaign_id)
            elif platform == SurveyPlatform.TYPEFORM:
                survey_url = await self._create_typeform(survey_template, campaign_id)
            elif platform == SurveyPlatform.CUSTOM_SURVEY:
                survey_url = await self._create_custom_survey(survey_template, campaign_id)
            else:
                survey_url = f"https://survey.verticallight.com/campaigns/{campaign_id}"
            
            survey_config.survey_url = survey_url
            
            # Store campaign information
            campaign_data = {
                "campaign_id": campaign_id,
                "survey_type": survey_type.value,
                "platform": platform.value,
                "survey_config": survey_config.__dict__,
                "target_hospitals": target_hospitals,
                "created_at": datetime.now().isoformat(),
                "status": "created",
                "responses_received": 0,
                "total_targets": len(target_hospitals),
                "survey_url": survey_url
            }
            
            self.active_campaigns[campaign_id] = campaign_data
            
            # Save to persistent storage
            self._save_campaign_data(campaign_id, campaign_data)
            
            self.logger.info(f"Created survey campaign {campaign_id} for {len(target_hospitals)} hospitals")
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "survey_url": survey_url,
                "target_hospitals_count": len(target_hospitals),
                "platform": platform.value,
                "survey_type": survey_type.value,
                "deadline": survey_config.completion_deadline.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create survey campaign: {str(e)}")
            raise SurveyDataCollectionError(f"Survey campaign creation failed: {str(e)}")
    
    async def distribute_survey(self, campaign_id: str, 
                              distribution_methods: List[str] = ["email"]) -> Dict[str, Any]:
        """Distribute survey to target hospitals"""
        
        try:
            campaign = self.active_campaigns.get(campaign_id)
            if not campaign:
                raise SurveyDataCollectionError(f"Campaign {campaign_id} not found")
            
            survey_url = campaign["survey_url"]
            target_hospitals = campaign["target_hospitals"]
            
            distribution_results = {
                "campaign_id": campaign_id,
                "distribution_timestamp": datetime.now().isoformat(),
                "methods_used": distribution_methods,
                "total_targets": len(target_hospitals),
                "distribution_results": {},
                "success_count": 0,
                "failure_count": 0,
                "errors": []
            }
            
            # Get hospital contact information
            hospital_contacts = await self._get_hospital_contacts(target_hospitals)
            
            # Distribute via each method
            for method in distribution_methods:
                if method == "email":
                    results = await self._distribute_via_email(campaign, hospital_contacts, survey_url)
                elif method == "whatsapp":
                    results = await self._distribute_via_whatsapp(campaign, hospital_contacts, survey_url)
                elif method == "sms":
                    results = await self._distribute_via_sms(campaign, hospital_contacts, survey_url)
                else:
                    results = {"success": 0, "failed": 0, "errors": [f"Unknown method: {method}"]}
                
                distribution_results["distribution_results"][method] = results
                distribution_results["success_count"] += results.get("success", 0)
                distribution_results["failure_count"] += results.get("failed", 0)
                distribution_results["errors"].extend(results.get("errors", []))
            
            # Update campaign status
            campaign["status"] = "distributed"
            campaign["distribution_completed"] = datetime.now().isoformat()
            self._save_campaign_data(campaign_id, campaign)
            
            # Schedule reminders
            await self._schedule_survey_reminders(campaign_id, hospital_contacts)
            
            self.logger.info(f"Distributed survey {campaign_id} to {distribution_results['success_count']} hospitals")
            
            return distribution_results
            
        except Exception as e:
            self.logger.error(f"Survey distribution failed: {str(e)}")
            raise SurveyDataCollectionError(f"Survey distribution failed: {str(e)}")
    
    async def _distribute_via_email(self, campaign: Dict[str, Any], 
                                  hospital_contacts: List[HospitalContact],
                                  survey_url: str) -> Dict[str, Any]:
        """Distribute survey via email"""
        
        success_count = 0
        failed_count = 0
        errors = []
        
        email_template = self._get_email_template(campaign["survey_type"])
        
        for contact in hospital_contacts:
            try:
                # Create personalized email
                email_content = email_template["content"].format(
                    hospital_name=contact.primary_contact_name,
                    survey_url=survey_url,
                    deadline=campaign["survey_config"]["completion_deadline"],
                    incentive=campaign["survey_config"].get("incentive_amount", ""),
                    campaign_id=campaign["campaign_id"]
                )
                
                # Send email
                await self._send_email(
                    to_email=contact.primary_contact_email,
                    to_name=contact.primary_contact_name,
                    subject=email_template["subject"],
                    content=email_content,
                    hospital_id=contact.hospital_id
                )
                
                success_count += 1
                self.logger.info(f"Survey email sent to {contact.primary_contact_email}")
                
            except Exception as e:
                failed_count += 1
                error_msg = f"Failed to send email to {contact.primary_contact_email}: {str(e)}"
                errors.append(error_msg)
                self.logger.error(error_msg)
        
        return {
            "success": success_count,
            "failed": failed_count,
            "errors": errors
        }
    
    async def _send_email(self, to_email: str, to_name: str, 
                        subject: str, content: str, hospital_id: str) -> None:
        """Send individual email"""
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.email_config['from_name']} <{self.email_config['from_email']}>"
            msg['To'] = f"{to_name} <{to_email}>"
            msg['Subject'] = subject
            
            # HTML content
            html_part = MIMEText(content, 'html')
            msg.attach(html_part)
            
            # Send via SMTP
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            
            text = msg.as_string()
            server.sendmail(self.email_config['from_email'], to_email, text)
            server.quit()
            
            # Log email sent
            self._log_email_sent(hospital_id, to_email, subject)
            
        except Exception as e:
            self.logger.error(f"SMTP email sending failed: {str(e)}")
            raise
    
    def _get_email_template(self, survey_type: str) -> Dict[str, str]:
        """Get email template for survey type"""
        
        templates = {
            "performance_metrics": {
                "subject": "Monthly Performance Metrics Survey - Hospital Benchmarking Program",
                "content": """
                <html>
                <body>
                    <h2>Hospital Performance Benchmarking Survey</h2>
                    <p>Dear {hospital_name},</p>
                    
                    <p>We invite you to participate in our monthly hospital performance benchmarking survey. Your participation helps create industry standards and improves healthcare delivery across India.</p>
                    
                    <p><strong>Survey Details:</strong></p>
                    <ul>
                        <li>Time to complete: 5-10 minutes</li>
                        <li>Data confidentiality: Assured</li>
                        <li>Deadline: {deadline}</li>
                        <li>Incentive: ₹{incentive} upon completion</li>
                    </ul>
                    
                    <p><a href="{survey_url}" style="background-color: #4CAF50; color: white; padding: 14px 20px; text-decoration: none; border-radius: 4px;">Start Survey</a></p>
                    
                    <p>Your responses will be used to create industry benchmarks and provide you with comparative insights.</p>
                    
                    <p>Thank you for your participation!</p>
                    
                    <p>Best regards,<br>Hospital Benchmarking Team<br>VerticalLight Healthcare Analytics</p>
                    
                    <p><small>Campaign ID: {campaign_id}</small></p>
                </body>
                </html>
                """
            },
            
            "financial_data": {
                "subject": "Financial Performance Survey - Confidential Benchmarking Study",
                "content": """
                <html>
                <body>
                    <h2>Hospital Financial Performance Survey</h2>
                    <p>Dear {hospital_name},</p>
                    
                    <p>We are conducting a confidential financial benchmarking study to help hospitals understand their performance relative to peers.</p>
                    
                    <p><strong>Survey Details:</strong></p>
                    <ul>
                        <li>Complete confidentiality assured</li>
                        <li>Benchmarking report provided</li>
                        <li>Deadline: {deadline}</li>
                        <li>Completion incentive: ₹{incentive}</li>
                    </ul>
                    
                    <p><a href="{survey_url}" style="background-color: #2196F3; color: white; padding: 14px 20px; text-decoration: none; border-radius: 4px;">Complete Survey</a></p>
                    
                    <p>All data will be aggregated and anonymized for benchmarking purposes.</p>
                    
                    <p>Best regards,<br>Financial Benchmarking Team</p>
                </body>
                </html>
                """
            },
            
            "government_schemes": {
                "subject": "Government Health Schemes Performance Survey",
                "content": """
                <html>
                <body>
                    <h2>Government Health Schemes Survey</h2>
                    <p>Dear {hospital_name},</p>
                    
                    <p>Help us understand the performance and challenges of government health schemes in your hospital.</p>
                    
                    <p><strong>Survey Focus:</strong></p>
                    <ul>
                        <li>Ayushman Bharat performance</li>
                        <li>CGHS and ESI experiences</li>
                        <li>Reimbursement challenges</li>
                        <li>Operational impacts</li>
                    </ul>
                    
                    <p><a href="{survey_url}" style="background-color: #FF9800; color: white; padding: 14px 20px; text-decoration: none; border-radius: 4px;">Share Your Experience</a></p>
                    
                    <p>Your insights will help improve scheme implementations and hospital experiences.</p>
                    
                    <p>Thank you!</p>
                </body>
                </html>
                """
            }
        }
        
        return templates.get(survey_type, templates["performance_metrics"])
    
    async def _distribute_via_whatsapp(self, campaign: Dict[str, Any],
                                     hospital_contacts: List[HospitalContact],
                                     survey_url: str) -> Dict[str, Any]:
        """Distribute survey via WhatsApp Business API"""
        
        success_count = 0
        failed_count = 0
        errors = []
        
        # WhatsApp Business API configuration
        whatsapp_config = self.config.get("whatsapp", {})
        
        if not whatsapp_config.get("api_token"):
            errors.append("WhatsApp API not configured")
            return {"success": 0, "failed": len(hospital_contacts), "errors": errors}
        
        for contact in hospital_contacts:
            try:
                if contact.whatsapp_number:
                    message = f"""
🏥 *Hospital Performance Survey*

Dear {contact.primary_contact_name},

We invite you to participate in our hospital benchmarking survey.

📊 *Survey Details:*
• Duration: 5-10 minutes
• Confidential & Secure
• Deadline: {campaign['survey_config']['completion_deadline']}

🎁 *Incentive:* ₹{campaign['survey_config'].get('incentive_amount', 'TBD')} upon completion

👇 *Click to start:*
{survey_url}

Thank you for your participation!

_VerticalLight Healthcare Analytics_
                    """
                    
                    await self._send_whatsapp_message(contact.whatsapp_number, message)
                    success_count += 1
                else:
                    failed_count += 1
                    errors.append(f"No WhatsApp number for {contact.hospital_id}")
                    
            except Exception as e:
                failed_count += 1
                errors.append(f"WhatsApp failed for {contact.hospital_id}: {str(e)}")
        
        return {
            "success": success_count,
            "failed": failed_count,
            "errors": errors
        }
    
    async def _send_whatsapp_message(self, phone_number: str, message: str) -> None:
        """Send WhatsApp message via Business API"""
        
        whatsapp_config = self.config.get("whatsapp", {})
        
        url = "https://graph.facebook.com/v17.0/{}/messages".format(
            whatsapp_config.get("phone_number_id")
        )
        
        headers = {
            "Authorization": f"Bearer {whatsapp_config.get('api_token')}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    response_text = await response.text()
                    raise Exception(f"WhatsApp API error: {response.status} - {response_text}")
    
    async def _distribute_via_sms(self, campaign: Dict[str, Any],
                                hospital_contacts: List[HospitalContact],
                                survey_url: str) -> Dict[str, Any]:
        """Distribute survey via SMS"""
        
        # SMS implementation would use services like Twilio, AWS SNS, or Indian SMS providers
        return {
            "success": 0,
            "failed": len(hospital_contacts),
            "errors": ["SMS distribution not implemented yet"]
        }
    
    async def collect_survey_responses(self, campaign_id: str) -> Dict[str, Any]:
        """Collect and process survey responses"""
        
        try:
            campaign = self.active_campaigns.get(campaign_id)
            if not campaign:
                raise SurveyDataCollectionError(f"Campaign {campaign_id} not found")
            
            platform = SurveyPlatform(campaign["platform"])
            
            if platform == SurveyPlatform.GOOGLE_FORMS:
                responses = await self._collect_google_forms_responses(campaign)
            elif platform == SurveyPlatform.TYPEFORM:
                responses = await self._collect_typeform_responses(campaign)
            elif platform == SurveyPlatform.CUSTOM_SURVEY:
                responses = await self._collect_custom_survey_responses(campaign)
            else:
                responses = []
            
            # Process and validate responses
            processed_responses = []
            
            for response in responses:
                try:
                    processed_response = await self._process_survey_response(
                        response, campaign["survey_type"]
                    )
                    processed_responses.append(processed_response)
                except Exception as e:
                    self.logger.error(f"Failed to process response: {str(e)}")
            
            # Update campaign statistics
            campaign["responses_received"] = len(processed_responses)
            campaign["response_rate"] = (len(processed_responses) / campaign["total_targets"]) * 100
            campaign["last_collection"] = datetime.now().isoformat()
            
            self._save_campaign_data(campaign_id, campaign)
            
            return {
                "success": True,
                "campaign_id": campaign_id,
                "total_responses": len(processed_responses),
                "response_rate": campaign["response_rate"],
                "responses": processed_responses
            }
            
        except Exception as e:
            self.logger.error(f"Survey response collection failed: {str(e)}")
            raise SurveyDataCollectionError(f"Response collection failed: {str(e)}")
    
    async def _process_survey_response(self, response: Dict[str, Any], 
                                     survey_type: str) -> Dict[str, Any]:
        """Process and validate individual survey response"""
        
        processed_response = {
            "response_id": response.get("response_id"),
            "hospital_id": response.get("hospital_id"),
            "completion_time": response.get("completion_time"),
            "survey_type": survey_type,
            "data": {},
            "validation_score": 0,
            "quality_issues": []
        }
        
        # Get survey template for validation
        template = self.survey_templates.get(SurveyType(survey_type))
        if not template:
            processed_response["quality_issues"].append("No template found for validation")
            return processed_response
        
        # Process each question response
        total_questions = len(template["questions"])
        answered_questions = 0
        
        for question in template["questions"]:
            question_id = question["id"]
            answer = response.get("answers", {}).get(question_id)
            
            if answer is not None and answer != "":
                answered_questions += 1
                
                # Validate answer
                if self._validate_answer(answer, question):
                    processed_response["data"][question_id] = self._convert_answer_type(answer, question["type"])
                else:
                    processed_response["quality_issues"].append(f"Invalid answer for {question_id}: {answer}")
            elif question["required"]:
                processed_response["quality_issues"].append(f"Missing required answer for {question_id}")
        
        # Calculate validation score
        completeness_score = (answered_questions / total_questions) * 100
        quality_deduction = len(processed_response["quality_issues"]) * 10
        processed_response["validation_score"] = max(0, completeness_score - quality_deduction)
        
        return processed_response
    
    def _validate_answer(self, answer: Any, question: Dict[str, Any]) -> bool:
        """Validate survey answer against question constraints"""
        
        validation = question.get("validation", {})
        
        if question["type"] == "number":
            try:
                num_value = float(answer)
                
                if "min" in validation and num_value < validation["min"]:
                    return False
                if "max" in validation and num_value > validation["max"]:
                    return False
                    
                return True
            except (ValueError, TypeError):
                return False
        
        elif question["type"] == "multiple_choice":
            options = question.get("options", [])
            return answer in options
        
        elif question["type"] == "text":
            min_length = validation.get("min_length", 0)
            max_length = validation.get("max_length", 1000)
            
            return min_length <= len(str(answer)) <= max_length
        
        return True
    
    def _convert_answer_type(self, answer: Any, question_type: str) -> Any:
        """Convert answer to appropriate type"""
        
        if question_type == "number":
            try:
                if '.' in str(answer):
                    return Decimal(str(answer))
                else:
                    return int(answer)
            except (ValueError, TypeError):
                return answer
        
        return answer
    
    async def _get_hospital_contacts(self, hospital_ids: List[str]) -> List[HospitalContact]:
        """Get hospital contact information"""
        
        contacts = []
        
        for hospital_id in hospital_ids:
            # In production, this would query the hospital database
            # For now, using placeholder data
            
            contacts.append(HospitalContact(
                hospital_id=hospital_id,
                primary_contact_name=f"Administrator_{hospital_id[-3:]}",
                primary_contact_email=f"admin@{hospital_id.lower().replace('_', '')}.com",
                primary_contact_phone=f"+91-98765-{hospital_id[-5:]}",
                whatsapp_number=f"91-98765-{hospital_id[-5:]}",
                preferred_language="english"
            ))
        
        return contacts
    
    async def _create_custom_survey(self, survey_template: Dict[str, Any], 
                                  campaign_id: str) -> str:
        """Create custom survey form"""
        
        # Generate custom survey URL
        survey_url = f"https://survey.verticallight.com/campaigns/{campaign_id}"
        
        # In production, this would create actual survey form
        # Store survey configuration for custom form rendering
        survey_config = {
            "campaign_id": campaign_id,
            "title": survey_template["title"],
            "description": survey_template["description"],
            "questions": survey_template["questions"],
            "created_at": datetime.now().isoformat()
        }
        
        self._save_survey_config(campaign_id, survey_config)
        
        return survey_url
    
    def _save_campaign_data(self, campaign_id: str, campaign_data: Dict[str, Any]) -> None:
        """Save campaign data to persistent storage"""
        
        # In production, this would save to database
        campaigns_file = Path("data/survey_campaigns.json")
        campaigns_file.parent.mkdir(exist_ok=True)
        
        try:
            if campaigns_file.exists():
                with open(campaigns_file, 'r') as f:
                    all_campaigns = json.load(f)
            else:
                all_campaigns = {}
            
            all_campaigns[campaign_id] = campaign_data
            
            with open(campaigns_file, 'w') as f:
                json.dump(all_campaigns, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Failed to save campaign data: {str(e)}")
    
    def _save_survey_config(self, campaign_id: str, survey_config: Dict[str, Any]) -> None:
        """Save survey configuration"""
        
        config_file = Path(f"data/survey_configs/{campaign_id}.json")
        config_file.parent.mkdir(exist_ok=True, parents=True)
        
        with open(config_file, 'w') as f:
            json.dump(survey_config, f, indent=2, default=str)
    
    def _log_email_sent(self, hospital_id: str, email: str, subject: str) -> None:
        """Log email sending for tracking"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "hospital_id": hospital_id,
            "email": email,
            "subject": subject,
            "status": "sent"
        }
        
        # In production, save to database
        self.logger.info(f"Email logged: {log_entry}")
    
    async def _schedule_survey_reminders(self, campaign_id: str,
                                       hospital_contacts: List[HospitalContact]) -> None:
        """Schedule automatic survey reminders"""
        
        # In production, this would use a task scheduler
        self.logger.info(f"Scheduled reminders for campaign {campaign_id}")
        
        # Placeholder for reminder scheduling
        # Would integrate with Celery, Apache Airflow, or similar
        pass
    
    async def _collect_custom_survey_responses(self, campaign: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect responses from custom survey"""
        
        # In production, this would query the survey response database
        # For now, return placeholder responses
        return []
    
    def get_survey_analytics(self, campaign_id: str) -> Dict[str, Any]:
        """Get survey campaign analytics"""
        
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign:
            return {"error": "Campaign not found"}
        
        return {
            "campaign_id": campaign_id,
            "survey_type": campaign["survey_type"],
            "total_targets": campaign["total_targets"],
            "responses_received": campaign.get("responses_received", 0),
            "response_rate": campaign.get("response_rate", 0),
            "status": campaign["status"],
            "created_at": campaign["created_at"],
            "distribution_completed": campaign.get("distribution_completed"),
            "last_collection": campaign.get("last_collection")
        }


# Survey response processing utilities
class SurveyDataProcessor:
    """Process and standardize survey response data"""
    
    @staticmethod
    def convert_to_benchmark_format(responses: List[Dict[str, Any]], 
                                  survey_type: SurveyType) -> Dict[str, Any]:
        """Convert survey responses to benchmark database format"""
        
        if survey_type == SurveyType.PERFORMANCE_METRICS:
            return SurveyDataProcessor._process_performance_responses(responses)
        elif survey_type == SurveyType.FINANCIAL_DATA:
            return SurveyDataProcessor._process_financial_responses(responses)
        elif survey_type == SurveyType.GOVERNMENT_SCHEMES:
            return SurveyDataProcessor._process_scheme_responses(responses)
        else:
            return {"processed_responses": responses}
    
    @staticmethod
    def _process_performance_responses(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process performance metrics survey responses"""
        
        processed_data = []
        
        for response in responses:
            data = response.get("data", {})
            
            performance_metrics = {
                "hospital_id": response["hospital_id"],
                "data_period": datetime.now().strftime("%Y-%m"),
                "data_type": "monthly",
                "bed_occupancy_rate": data.get("bed_occupancy"),
                "average_length_of_stay": data.get("average_los"),
                "patient_satisfaction_score": data.get("patient_satisfaction"),
                "or_utilization_rate": data.get("or_utilization"),
                "ed_average_wait_time": data.get("ed_wait_time"),
                "readmission_rate": data.get("readmission_rate"),
                "infection_rate": data.get("infection_rate"),
                "data_source": "manual_survey",
                "quality_score": response["validation_score"] // 10  # Convert to 1-10 scale
            }
            
            processed_data.append(performance_metrics)
        
        return {
            "processed_responses": processed_data,
            "total_responses": len(processed_data),
            "data_type": "performance_metrics"
        }
    
    @staticmethod
    def _process_financial_responses(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process financial survey responses"""
        
        processed_data = []
        
        for response in responses:
            data = response.get("data", {})
            
            financial_metrics = {
                "hospital_id": response["hospital_id"],
                "data_period": datetime.now().strftime("%Y-%m"),
                "data_type": "monthly",
                "total_revenue": data.get("total_revenue"),
                "total_costs": data.get("total_costs"),
                "accounts_receivable_days": data.get("ar_days"),
                "cash_percentage": data.get("cash_percentage"),
                "insurance_percentage": data.get("insurance_percentage"),
                "government_scheme_percentage": data.get("government_scheme_percentage"),
                "ebitda_margin": data.get("ebitda_margin"),
                "data_source": "manual_survey",
                "quality_score": response["validation_score"] // 10
            }
            
            processed_data.append(financial_metrics)
        
        return {
            "processed_responses": processed_data,
            "total_responses": len(processed_data),
            "data_type": "financial_metrics"
        }
    
    @staticmethod
    def _process_scheme_responses(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process government scheme survey responses"""
        
        processed_data = []
        
        for response in responses:
            data = response.get("data", {})
            
            scheme_data = {
                "hospital_id": response["hospital_id"],
                "data_period": datetime.now().strftime("%Y-%m"),
                "scheme_type": "multiple_schemes",
                "ayushman_cases": data.get("ayushman_cases"),
                "ayushman_revenue": data.get("ayushman_revenue"),
                "ayushman_approval_rate": data.get("ayushman_approval_rate"),
                "cghs_cases": data.get("cghs_cases"),
                "esi_cases": data.get("esi_cases"),
                "average_reimbursement_days": data.get("reimbursement_delay"),
                "main_challenges": data.get("scheme_challenges"),
                "data_source": "manual_survey",
                "quality_score": response["validation_score"] // 10
            }
            
            processed_data.append(scheme_data)
        
        return {
            "processed_responses": processed_data,
            "total_responses": len(processed_data),
            "data_type": "government_schemes"
        }