"""
WhatsApp Auto-Response System
Intelligent auto-response system for WhatsApp Business automation.
"""

import re
from typing import List, Dict, Optional, Any
from datetime import datetime, time
import logging

from .interfaces import AutoResponseInterface
from .models import WhatsAppMessage, AutoResponse, MessageType


logger = logging.getLogger(__name__)


class WhatsAppAutoResponder(AutoResponseInterface):
    """Automatic response system for WhatsApp messages"""
    
    def __init__(self, business_name: str, business_hours: Dict[str, str] = None):
        self.business_name = business_name
        self.business_hours = business_hours or {
            "monday": "9:00-18:00",
            "tuesday": "9:00-18:00",
            "wednesday": "9:00-18:00", 
            "thursday": "9:00-18:00",
            "friday": "9:00-18:00",
            "saturday": "9:00-18:00",
            "sunday": "closed"
        }
        
        # Default auto-response rules
        self.auto_responses = self._create_default_responses()
    
    async def process_incoming_message(self, message: WhatsAppMessage) -> Optional[WhatsAppMessage]:
        """Process incoming message and generate auto-response if applicable"""
        try:
            # Don't auto-respond to our own messages
            if message.is_from_business:
                return None
            
            # Find matching auto-response
            for response_rule in self.auto_responses:
                if response_rule.matches_message(message.content):
                    
                    # Check business hours if required
                    if response_rule.business_hours_only and not self._is_business_hours():
                        continue
                    
                    # Generate response content
                    response_content = self._generate_response_content(
                        response_rule.response_template, 
                        message
                    )
                    
                    # Create response message
                    response = WhatsAppMessage.create_outbound(
                        contact_phone=message.contact_phone,
                        content=response_content,
                        message_type=MessageType.TEXT
                    )
                    
                    logger.info(f"Generated auto-response for {message.contact_phone}")
                    return response
            
            # No matching auto-response found
            return None
            
        except Exception as e:
            logger.error(f"Failed to process auto-response: {e}")
            return None
    
    async def add_auto_response_rule(self, trigger_keywords: List[str], 
                                   response_template: str) -> bool:
        """Add new auto-response rule"""
        try:
            new_rule = AutoResponse(
                trigger_keywords=trigger_keywords,
                response_template=response_template,
                is_active=True,
                priority=len(self.auto_responses) + 1
            )
            
            self.auto_responses.append(new_rule)
            logger.info(f"Added auto-response rule for keywords: {trigger_keywords}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add auto-response rule: {e}")
            return False
    
    async def get_auto_response_rules(self) -> List[Dict[str, Any]]:
        """Get all auto-response rules"""
        return [
            {
                "trigger_keywords": rule.trigger_keywords,
                "response_template": rule.response_template,
                "is_active": rule.is_active,
                "priority": rule.priority,
                "business_hours_only": rule.business_hours_only
            }
            for rule in self.auto_responses
        ]
    
    def _create_default_responses(self) -> List[AutoResponse]:
        """Create default auto-response rules for common queries"""
        return [
            # Greetings
            AutoResponse(
                trigger_keywords=["hello", "hi", "hey", "good morning", "good afternoon", "good evening"],
                response_template=f"Hello! Welcome to {self.business_name}. How can we help you today?",
                priority=1
            ),
            
            # Business hours inquiry
            AutoResponse(
                trigger_keywords=["hours", "open", "close", "timing", "time"],
                response_template=f"Our business hours are:\n{self._format_business_hours()}\n\nHow can we assist you?",
                priority=2
            ),
            
            # Location inquiry
            AutoResponse(
                trigger_keywords=["location", "address", "where", "directions"],
                response_template=f"You can find {self.business_name} at our location. Would you like directions or have any other questions?",
                priority=3
            ),
            
            # Menu/Services inquiry
            AutoResponse(
                trigger_keywords=["menu", "services", "what do you", "offerings", "catalog"],
                response_template=f"We offer a variety of services at {self.business_name}. Let me connect you with our team to discuss your specific needs!",
                priority=4
            ),
            
            # Pricing inquiry
            AutoResponse(
                trigger_keywords=["price", "cost", "rate", "charge", "fee"],
                response_template="Thanks for your interest in our pricing! Our rates vary based on your specific needs. Let me connect you with our team for a personalized quote.",
                priority=5
            ),
            
            # Booking/Appointment
            AutoResponse(
                trigger_keywords=["book", "appointment", "schedule", "reserve", "slot"],
                response_template="Great! We'd love to schedule an appointment for you. Our team will help you find the perfect time slot. What service are you interested in?",
                priority=6
            ),
            
            # Order inquiry
            AutoResponse(
                trigger_keywords=["order", "delivery", "pickup", "food"],
                response_template="We'd be happy to help with your order! Let me connect you with our team to process your request and provide delivery details.",
                priority=7
            ),
            
            # Out of hours response
            AutoResponse(
                trigger_keywords=["urgent", "emergency", "asap", "immediately"],
                response_template=f"Thank you for contacting {self.business_name}. We're currently outside business hours but we'll respond as soon as we're open. For urgent matters, please call us directly.",
                business_hours_only=False,
                priority=8
            ),
            
            # Thank you acknowledgment
            AutoResponse(
                trigger_keywords=["thank", "thanks", "appreciate"],
                response_template=f"You're very welcome! We're always happy to help at {self.business_name}. Is there anything else we can assist you with?",
                priority=9
            ),
            
            # Default fallback
            AutoResponse(
                trigger_keywords=[""],  # Matches any message if no other rules match
                response_template=f"Thank you for contacting {self.business_name}! We've received your message and our team will get back to you shortly. Have a great day!",
                priority=99
            )
        ]
    
    def _generate_response_content(self, template: str, original_message: WhatsAppMessage) -> str:
        """Generate response content from template with dynamic variables"""
        # Replace common variables in template
        content = template
        content = content.replace("{business_name}", self.business_name)
        content = content.replace("{current_time}", datetime.now().strftime("%I:%M %p"))
        content = content.replace("{current_date}", datetime.now().strftime("%B %d, %Y"))
        
        return content
    
    def _is_business_hours(self) -> bool:
        """Check if current time is within business hours"""
        now = datetime.now()
        current_day = now.strftime("%A").lower()
        current_time = now.time()
        
        if current_day not in self.business_hours:
            return False
        
        hours_str = self.business_hours[current_day]
        if hours_str.lower() == "closed":
            return False
        
        try:
            # Parse hours like "9:00-18:00"
            start_str, end_str = hours_str.split("-")
            start_time = time.fromisoformat(start_str)
            end_time = time.fromisoformat(end_str)
            
            return start_time <= current_time <= end_time
            
        except ValueError:
            # If parsing fails, assume open
            return True
    
    def _format_business_hours(self) -> str:
        """Format business hours for display"""
        formatted_hours = []
        
        for day, hours in self.business_hours.items():
            day_name = day.capitalize()
            if hours.lower() == "closed":
                formatted_hours.append(f"{day_name}: Closed")
            else:
                formatted_hours.append(f"{day_name}: {hours}")
        
        return "\n".join(formatted_hours)


class SmartAutoResponder(WhatsAppAutoResponder):
    """Enhanced auto-responder with intent recognition"""
    
    def __init__(self, business_name: str, business_type: str, 
                 business_hours: Dict[str, str] = None):
        super().__init__(business_name, business_hours)
        self.business_type = business_type
        self.intent_patterns = self._create_intent_patterns()
    
    async def process_incoming_message(self, message: WhatsAppMessage) -> Optional[WhatsAppMessage]:
        """Process message with enhanced intent recognition"""
        # First try intent-based responses
        intent_response = await self._process_intent_based_response(message)
        if intent_response:
            return intent_response
        
        # Fall back to keyword-based responses
        return await super().process_incoming_message(message)
    
    async def _process_intent_based_response(self, message: WhatsAppMessage) -> Optional[WhatsAppMessage]:
        """Generate response based on detected intent"""
        message_text = message.content.lower()
        
        for intent, pattern_data in self.intent_patterns.items():
            for pattern in pattern_data["patterns"]:
                if re.search(pattern, message_text):
                    response_template = pattern_data["response"]
                    
                    response_content = self._generate_response_content(
                        response_template, 
                        message
                    )
                    
                    return WhatsAppMessage.create_outbound(
                        contact_phone=message.contact_phone,
                        content=response_content,
                        message_type=MessageType.TEXT
                    )
        
        return None
    
    def _create_intent_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Create intent patterns based on business type"""
        base_patterns = {
            "booking_intent": {
                "patterns": [
                    r"(book|schedule|appointment|reserve).*(today|tomorrow|next week|monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
                    r"(available|free).*(slot|time|appointment)",
                    r"(can i|could i).*(book|schedule|get)"
                ],
                "response": f"I'd be happy to help you schedule an appointment with {self.business_name}! What day and time works best for you?"
            },
            
            "pricing_intent": {
                "patterns": [
                    r"how much.*(cost|price|charge)",
                    r"what.*(rate|price|cost)",
                    r"(affordable|cheap|expensive|budget)"
                ],
                "response": "Our pricing varies based on your specific needs. Let me connect you with our team for accurate pricing information!"
            }
        }
        
        # Add business-type specific patterns
        if self.business_type.lower() in ["restaurant", "cafe", "food"]:
            base_patterns.update({
                "menu_intent": {
                    "patterns": [
                        r"(menu|food|eat|dish|cuisine)",
                        r"what.*(serve|offer|have)",
                        r"(vegetarian|vegan|spicy|mild)"
                    ],
                    "response": f"We have a delicious menu at {self.business_name}! Let me share our offerings with you. What type of cuisine are you in the mood for?"
                },
                
                "delivery_intent": {
                    "patterns": [
                        r"(deliver|delivery|order online)",
                        r"(takeaway|pickup|take away)",
                        r"(hungry|order food)"
                    ],
                    "response": "Yes, we offer both delivery and pickup! What would you like to order today?"
                }
            })
        
        elif self.business_type.lower() in ["salon", "spa", "beauty"]:
            base_patterns.update({
                "service_intent": {
                    "patterns": [
                        r"(haircut|hair|facial|massage|manicure|pedicure)",
                        r"(beauty|treatment|service)",
                        r"(appointment|book|schedule)"
                    ],
                    "response": f"We offer a full range of beauty services at {self.business_name}! Which service are you interested in today?"
                }
            })
        
        return base_patterns