"""
WhatsApp Business API Interface
Clean interface for WhatsApp Business API integration.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from .models import (
    WhatsAppMessage, WhatsAppContact, MessageTemplate, 
    BroadcastCampaign, WhatsAppBusinessProfile, WhatsAppAnalytics
)


class WhatsAppAPIInterface(ABC):
    """Abstract interface for WhatsApp Business API"""
    
    @abstractmethod
    async def send_message(self, contact_phone: str, content: str, 
                          message_type: str = "text") -> WhatsAppMessage:
        """Send a message to a contact"""
        pass
    
    @abstractmethod
    async def send_template_message(self, contact_phone: str, 
                                  template_id: str, variables: Dict[str, str]) -> WhatsAppMessage:
        """Send a template message"""
        pass
    
    @abstractmethod
    async def get_message_status(self, message_id: str) -> str:
        """Get status of a sent message"""
        pass
    
    @abstractmethod
    async def get_contacts(self) -> List[WhatsAppContact]:
        """Get all contacts"""
        pass
    
    @abstractmethod
    async def get_business_profile(self) -> WhatsAppBusinessProfile:
        """Get business profile information"""
        pass
    
    @abstractmethod
    async def update_business_profile(self, profile: WhatsAppBusinessProfile) -> bool:
        """Update business profile"""
        pass


class WhatsAppWebhookInterface(ABC):
    """Abstract interface for WhatsApp webhook handling"""
    
    @abstractmethod
    async def handle_incoming_message(self, webhook_data: Dict[str, Any]) -> Optional[WhatsAppMessage]:
        """Handle incoming message webhook"""
        pass
    
    @abstractmethod
    async def handle_message_status_update(self, webhook_data: Dict[str, Any]) -> bool:
        """Handle message status update webhook"""
        pass
    
    @abstractmethod
    async def verify_webhook(self, verify_token: str, challenge: str) -> Optional[str]:
        """Verify webhook setup"""
        pass


class ContactManagerInterface(ABC):
    """Abstract interface for contact management"""
    
    @abstractmethod
    async def add_contact(self, contact: WhatsAppContact) -> bool:
        """Add a new contact"""
        pass
    
    @abstractmethod
    async def update_contact(self, phone_number: str, updates: Dict[str, Any]) -> bool:
        """Update contact information"""
        pass
    
    @abstractmethod
    async def get_contact(self, phone_number: str) -> Optional[WhatsAppContact]:
        """Get contact by phone number"""
        pass
    
    @abstractmethod
    async def segment_contacts(self, segment_criteria: Dict[str, Any]) -> List[WhatsAppContact]:
        """Get contacts matching segment criteria"""
        pass


class MessageTemplateInterface(ABC):
    """Abstract interface for message template management"""
    
    @abstractmethod
    async def create_template(self, template: MessageTemplate) -> bool:
        """Create a new message template"""
        pass
    
    @abstractmethod
    async def get_templates(self) -> List[MessageTemplate]:
        """Get all message templates"""
        pass
    
    @abstractmethod
    async def get_template(self, template_id: str) -> Optional[MessageTemplate]:
        """Get specific template"""
        pass
    
    @abstractmethod
    async def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        pass


class AutoResponseInterface(ABC):
    """Abstract interface for automatic responses"""
    
    @abstractmethod
    async def process_incoming_message(self, message: WhatsAppMessage) -> Optional[WhatsAppMessage]:
        """Process incoming message and generate auto-response if applicable"""
        pass
    
    @abstractmethod
    async def add_auto_response_rule(self, trigger_keywords: List[str], 
                                   response_template: str) -> bool:
        """Add new auto-response rule"""
        pass
    
    @abstractmethod
    async def get_auto_response_rules(self) -> List[Dict[str, Any]]:
        """Get all auto-response rules"""
        pass


class BroadcastInterface(ABC):
    """Abstract interface for broadcast campaigns"""
    
    @abstractmethod
    async def create_broadcast_campaign(self, campaign: BroadcastCampaign) -> bool:
        """Create a new broadcast campaign"""
        pass
    
    @abstractmethod
    async def send_broadcast(self, campaign_id: str) -> Dict[str, Any]:
        """Send broadcast campaign"""
        pass
    
    @abstractmethod
    async def schedule_broadcast(self, campaign_id: str, scheduled_time: str) -> bool:
        """Schedule broadcast for later"""
        pass
    
    @abstractmethod
    async def get_broadcast_status(self, campaign_id: str) -> Dict[str, Any]:
        """Get broadcast campaign status"""
        pass


class AnalyticsInterface(ABC):
    """Abstract interface for WhatsApp analytics"""
    
    @abstractmethod
    async def get_message_analytics(self, start_date: str, end_date: str) -> WhatsAppAnalytics:
        """Get message analytics for date range"""
        pass
    
    @abstractmethod
    async def get_conversation_analytics(self) -> Dict[str, Any]:
        """Get conversation analytics"""
        pass
    
    @abstractmethod
    async def get_customer_insights(self) -> Dict[str, Any]:
        """Get customer behavior insights"""
        pass