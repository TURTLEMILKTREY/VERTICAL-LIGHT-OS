"""
WhatsApp Business Automation Models
Clean data models for WhatsApp business automation service.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    """Types of WhatsApp messages"""
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    TEMPLATE = "template"
    INTERACTIVE = "interactive"


class MessageStatus(Enum):
    """Status of sent messages"""
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class CustomerSegment(Enum):
    """Customer segments for targeting"""
    NEW_CUSTOMER = "new_customer"
    REGULAR_CUSTOMER = "regular_customer"
    VIP_CUSTOMER = "vip_customer"
    INACTIVE_CUSTOMER = "inactive_customer"


@dataclass
class WhatsAppContact:
    """WhatsApp contact information"""
    phone_number: str
    name: Optional[str] = None
    segment: CustomerSegment = CustomerSegment.NEW_CUSTOMER
    last_interaction: Optional[datetime] = None
    total_orders: int = 0
    lifetime_value: float = 0.0
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}


@dataclass
class MessageTemplate:
    """WhatsApp message template"""
    template_id: str
    name: str
    content: str
    message_type: MessageType
    variables: List[str] = None
    target_segment: Optional[CustomerSegment] = None
    language: str = "en"
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = []


@dataclass
class AutoResponse:
    """Automatic response configuration"""
    trigger_keywords: List[str]
    response_template: str
    is_active: bool = True
    priority: int = 1
    business_hours_only: bool = False
    
    def matches_message(self, message_text: str) -> bool:
        """Check if message matches trigger keywords"""
        message_lower = message_text.lower()
        return any(keyword.lower() in message_lower for keyword in self.trigger_keywords)


@dataclass
class WhatsAppMessage:
    """WhatsApp message data"""
    message_id: str
    contact_phone: str
    content: str
    message_type: MessageType
    timestamp: datetime
    is_from_business: bool = False
    status: MessageStatus = MessageStatus.SENT
    template_id: Optional[str] = None
    
    @classmethod
    def create_outbound(cls, contact_phone: str, content: str, 
                       message_type: MessageType = MessageType.TEXT) -> 'WhatsAppMessage':
        """Create an outbound message"""
        return cls(
            message_id=f"msg_{datetime.now().timestamp()}",
            contact_phone=contact_phone,
            content=content,
            message_type=message_type,
            timestamp=datetime.now(),
            is_from_business=True
        )


@dataclass
class BroadcastCampaign:
    """WhatsApp broadcast campaign"""
    campaign_id: str
    name: str
    template: MessageTemplate
    target_contacts: List[str]
    scheduled_time: Optional[datetime] = None
    is_sent: bool = False
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class WhatsAppBusinessProfile:
    """WhatsApp Business profile information"""
    business_phone: str
    business_name: str
    description: str
    address: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    business_hours: Dict[str, str] = None
    
    def __post_init__(self):
        if self.business_hours is None:
            self.business_hours = {
                "monday": "9:00-18:00",
                "tuesday": "9:00-18:00", 
                "wednesday": "9:00-18:00",
                "thursday": "9:00-18:00",
                "friday": "9:00-18:00",
                "saturday": "9:00-18:00",
                "sunday": "closed"
            }


@dataclass
class WhatsAppAnalytics:
    """WhatsApp performance analytics"""
    total_messages_sent: int = 0
    total_messages_received: int = 0
    response_rate: float = 0.0
    avg_response_time_minutes: float = 0.0
    active_conversations: int = 0
    new_customers_acquired: int = 0
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None