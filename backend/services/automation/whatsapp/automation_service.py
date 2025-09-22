"""
WhatsApp Business Automation Service
Main service that orchestrates all WhatsApp automation features.
"""

import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging

from .api import WhatsAppBusinessClient
from .contact_manager import WhatsAppContactManager, InMemoryContactStorage
from .auto_responder import SmartAutoResponder
from .template_manager import WhatsAppTemplateManager, TemplateAnalytics
from .models import (
    WhatsAppMessage, WhatsAppContact, BroadcastCampaign,
    CustomerSegment, MessageType, WhatsAppAnalytics
)


logger = logging.getLogger(__name__)


class WhatsAppAutomationService:
    """Complete WhatsApp Business automation service"""
    
    def __init__(self, business_config: Dict[str, str]):
        """Initialize WhatsApp automation service
        
        Args:
            business_config: Dictionary containing:
                - business_name: Name of the business
                - business_type: Type of business (restaurant, salon, retail, etc.)
                - whatsapp_access_token: WhatsApp Business API access token
                - whatsapp_phone_number_id: WhatsApp phone number ID
                - whatsapp_business_account_id: WhatsApp business account ID
                - whatsapp_verify_token: Webhook verification token
                - business_hours: Business operating hours (optional)
        """
        self.business_name = business_config["business_name"]
        self.business_type = business_config["business_type"]
        
        # Initialize WhatsApp Business API client
        self.whatsapp_client = WhatsAppBusinessClient(
            access_token=business_config["whatsapp_access_token"],
            phone_number_id=business_config["whatsapp_phone_number_id"],
            business_account_id=business_config["whatsapp_business_account_id"],
            verify_token=business_config["whatsapp_verify_token"]
        )
        
        # Initialize contact management
        storage = InMemoryContactStorage()
        self.contact_manager = WhatsAppContactManager(storage)
        
        # Initialize auto-responder
        business_hours = business_config.get("business_hours")
        self.auto_responder = SmartAutoResponder(
            business_name=self.business_name,
            business_type=self.business_type,
            business_hours=business_hours
        )
        
        # Initialize template management
        self.template_manager = WhatsAppTemplateManager(
            business_name=self.business_name,
            business_type=self.business_type
        )
        
        # Initialize analytics
        self.template_analytics = TemplateAnalytics()
        
        # Message queue for processing
        self.message_queue: List[WhatsAppMessage] = []
        self.is_processing = False
    
    async def start_automation(self):
        """Start the WhatsApp automation service"""
        logger.info(f"Starting WhatsApp automation for {self.business_name}")
        
        # Start message processing
        self.is_processing = True
        asyncio.create_task(self._process_message_queue())
        
        logger.info("WhatsApp automation service started successfully")
    
    async def stop_automation(self):
        """Stop the WhatsApp automation service"""
        logger.info("Stopping WhatsApp automation service")
        self.is_processing = False
    
    # Message Handling
    async def handle_incoming_message(self, webhook_data: Dict[str, Any]) -> bool:
        """Handle incoming WhatsApp message"""
        try:
            # Parse incoming message
            message = await self.whatsapp_client.process_webhook(webhook_data)
            if not message:
                return False
            
            # Add contact if new
            await self._ensure_contact_exists(message.contact_phone)
            
            # Update contact interaction
            await self.contact_manager.update_contact(
                message.contact_phone,
                {"last_interaction": datetime.now()}
            )
            
            # Generate auto-response if applicable
            auto_response = await self.auto_responder.process_incoming_message(message)
            if auto_response:
                await self._send_message(auto_response)
            
            logger.info(f"Processed incoming message from {message.contact_phone}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle incoming message: {e}")
            return False
    
    async def send_message(self, phone_number: str, content: str) -> bool:
        """Send a message to a contact"""
        try:
            message = await self.whatsapp_client.send_message(phone_number, content)
            
            # Ensure contact exists
            await self._ensure_contact_exists(phone_number)
            
            logger.info(f"Sent message to {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    async def send_template_message(self, phone_number: str, template_id: str, 
                                  customer_data: Dict[str, str] = None) -> bool:
        """Send a personalized template message"""
        try:
            if customer_data is None:
                customer_data = {}
            
            # Get personalized content
            personalized_content = await self.template_manager.personalize_template(
                template_id, customer_data
            )
            
            if not personalized_content:
                logger.error(f"Failed to personalize template {template_id}")
                return False
            
            # Send message
            success = await self.send_message(phone_number, personalized_content)
            
            if success:
                # Record template analytics
                self.template_analytics.record_template_send(template_id)
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send template message: {e}")
            return False
    
    # Broadcast Campaigns
    async def create_broadcast_campaign(self, campaign_name: str, template_id: str,
                                      target_segment: Optional[CustomerSegment] = None) -> str:
        """Create a broadcast campaign"""
        try:
            # Get target contacts
            if target_segment:
                target_contacts = await self.contact_manager.segment_contacts(
                    {"segment": target_segment}
                )
            else:
                all_contacts = await self.contact_manager.segment_contacts({})
                target_contacts = all_contacts
            
            # Get template
            template = await self.template_manager.get_template(template_id)
            if not template:
                raise ValueError(f"Template {template_id} not found")
            
            # Create campaign
            campaign = BroadcastCampaign(
                campaign_id=f"campaign_{datetime.now().timestamp()}",
                name=campaign_name,
                template=template,
                target_contacts=[contact.phone_number for contact in target_contacts]
            )
            
            logger.info(f"Created broadcast campaign: {campaign.campaign_id}")
            return campaign.campaign_id
            
        except Exception as e:
            logger.error(f"Failed to create broadcast campaign: {e}")
            return ""
    
    async def send_broadcast_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Send a broadcast campaign"""
        # This would typically be stored in a database
        # For now, we'll simulate the campaign execution
        
        try:
            results = {
                "campaign_id": campaign_id,
                "total_sent": 0,
                "successful": 0,
                "failed": 0,
                "errors": []
            }
            
            # This is a simplified implementation
            # In production, you'd retrieve the campaign from storage
            # and send messages to all target contacts
            
            logger.info(f"Broadcast campaign {campaign_id} execution completed")
            return results
            
        except Exception as e:
            logger.error(f"Failed to send broadcast campaign: {e}")
            return {"error": str(e)}
    
    # Customer Management
    async def add_customer(self, phone_number: str, name: str = None, 
                          customer_data: Dict[str, Any] = None) -> bool:
        """Add a new customer"""
        try:
            contact = WhatsAppContact(
                phone_number=phone_number,
                name=name,
                segment=CustomerSegment.NEW_CUSTOMER
            )
            
            if customer_data:
                for key, value in customer_data.items():
                    if hasattr(contact, key):
                        setattr(contact, key, value)
            
            return await self.contact_manager.add_contact(contact)
            
        except Exception as e:
            logger.error(f"Failed to add customer: {e}")
            return False
    
    async def update_customer_order(self, phone_number: str, order_value: float) -> bool:
        """Update customer order statistics"""
        return await self.contact_manager.update_customer_stats(phone_number, order_value)
    
    async def get_customer_insights(self) -> Dict[str, Any]:
        """Get customer insights and analytics"""
        return await self.contact_manager.get_contact_insights()
    
    # Template Management
    async def create_custom_template(self, template_id: str, name: str, 
                                   content: str, variables: List[str] = None) -> bool:
        """Create a custom message template"""
        from .models import MessageTemplate, MessageType
        
        template = MessageTemplate(
            template_id=template_id,
            name=name,
            content=content,
            message_type=MessageType.TEXT,
            variables=variables or []
        )
        
        return await self.template_manager.create_template(template)
    
    async def get_template_performance(self) -> List[Dict[str, Any]]:
        """Get template performance analytics"""
        return self.template_analytics.get_top_performing_templates()
    
    # Automation Rules
    async def add_auto_response_rule(self, trigger_keywords: List[str], 
                                   response_template: str) -> bool:
        """Add custom auto-response rule"""
        return await self.auto_responder.add_auto_response_rule(
            trigger_keywords, response_template
        )
    
    async def get_auto_response_rules(self) -> List[Dict[str, Any]]:
        """Get all auto-response rules"""
        return await self.auto_responder.get_auto_response_rules()
    
    # Analytics and Reporting
    async def get_analytics(self, days: int = 30) -> WhatsAppAnalytics:
        """Get WhatsApp automation analytics"""
        # This would typically pull from a database
        # For now, return basic analytics structure
        
        return WhatsAppAnalytics(
            total_messages_sent=0,
            total_messages_received=0,
            response_rate=0.0,
            avg_response_time_minutes=0.0,
            active_conversations=0,
            new_customers_acquired=0,
            period_start=datetime.now() - timedelta(days=days),
            period_end=datetime.now()
        )
    
    # Private Helper Methods
    async def _ensure_contact_exists(self, phone_number: str):
        """Ensure contact exists in system"""
        contact = await self.contact_manager.get_contact(phone_number)
        if not contact:
            await self.add_customer(phone_number)
    
    async def _send_message(self, message: WhatsAppMessage):
        """Send message through WhatsApp API"""
        try:
            await self.whatsapp_client.send_message(
                message.contact_phone, 
                message.content
            )
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    
    async def _process_message_queue(self):
        """Process queued messages"""
        while self.is_processing:
            try:
                if self.message_queue:
                    message = self.message_queue.pop(0)
                    await self._send_message(message)
                
                # Small delay to prevent overwhelming the API
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing message queue: {e}")
                await asyncio.sleep(5)


# Factory function for easy service creation
def create_whatsapp_automation_service(business_config: Dict[str, str]) -> WhatsAppAutomationService:
    """Create and configure WhatsApp automation service"""
    return WhatsAppAutomationService(business_config)