"""
Automation Services Package
Core automation capabilities for local businesses
"""

# WhatsApp Business automation - fully implemented
from .whatsapp import (
    WhatsAppAutomationService,
    create_whatsapp_automation_service,
    WhatsAppContact,
    MessageTemplate,
    CustomerSegment
)

__all__ = [
    'WhatsAppAutomationService',
    'create_whatsapp_automation_service', 
    'WhatsAppContact',
    'MessageTemplate',
    'CustomerSegment'
]