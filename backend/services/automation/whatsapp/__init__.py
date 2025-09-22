"""
WhatsApp Business Automation Package
Complete WhatsApp Business automation system for small businesses.

This package provides:
- WhatsApp Business API integration
- Automated customer responses  
- Message template management
- Contact management and segmentation
- Broadcast campaign management
- Analytics and performance tracking

Usage:
    from services.automation.whatsapp import create_whatsapp_automation_service
    
    config = {
        "business_name": "My Restaurant",
        "business_type": "restaurant", 
        "whatsapp_access_token": "your_token",
        "whatsapp_phone_number_id": "your_phone_id",
        "whatsapp_business_account_id": "your_account_id",
        "whatsapp_verify_token": "your_verify_token"
    }
    
    service = create_whatsapp_automation_service(config)
    await service.start_automation()
"""

from .automation_service import WhatsAppAutomationService, create_whatsapp_automation_service
from .api import WhatsAppBusinessClient
from .contact_manager import WhatsAppContactManager
from .auto_responder import SmartAutoResponder
from .template_manager import WhatsAppTemplateManager
from .models import (
    WhatsAppMessage,
    WhatsAppContact, 
    MessageTemplate,
    BroadcastCampaign,
    WhatsAppBusinessProfile,
    WhatsAppAnalytics,
    MessageType,
    MessageStatus,
    CustomerSegment
)

__all__ = [
    # Main service
    "WhatsAppAutomationService",
    "create_whatsapp_automation_service",
    
    # Core components
    "WhatsAppBusinessClient",
    "WhatsAppContactManager", 
    "SmartAutoResponder",
    "WhatsAppTemplateManager",
    
    # Data models
    "WhatsAppMessage",
    "WhatsAppContact",
    "MessageTemplate", 
    "BroadcastCampaign",
    "WhatsAppBusinessProfile",
    "WhatsAppAnalytics",
    
    # Enums
    "MessageType",
    "MessageStatus", 
    "CustomerSegment"
]