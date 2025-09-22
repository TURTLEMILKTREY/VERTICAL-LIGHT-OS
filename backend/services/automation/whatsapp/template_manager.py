"""
WhatsApp Message Template Management
Template management system for WhatsApp Business automation.
"""

import json
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

from .interfaces import MessageTemplateInterface
from .models import MessageTemplate, MessageType, CustomerSegment


logger = logging.getLogger(__name__)


class WhatsAppTemplateManager(MessageTemplateInterface):
    """Template management for WhatsApp Business messages"""
    
    def __init__(self, business_name: str, business_type: str):
        self.business_name = business_name
        self.business_type = business_type
        self.templates: Dict[str, MessageTemplate] = {}
        
        # Create default templates
        self._create_default_templates()
    
    async def create_template(self, template: MessageTemplate) -> bool:
        """Create a new message template"""
        try:
            self.templates[template.template_id] = template
            logger.info(f"Created template: {template.template_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            return False
    
    async def get_templates(self) -> List[MessageTemplate]:
        """Get all message templates"""
        return list(self.templates.values())
    
    async def get_template(self, template_id: str) -> Optional[MessageTemplate]:
        """Get specific template"""
        return self.templates.get(template_id)
    
    async def delete_template(self, template_id: str) -> bool:
        """Delete a template"""
        try:
            if template_id in self.templates:
                del self.templates[template_id]
                logger.info(f"Deleted template: {template_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete template: {e}")
            return False
    
    async def get_templates_by_segment(self, segment: CustomerSegment) -> List[MessageTemplate]:
        """Get templates for specific customer segment"""
        return [
            template for template in self.templates.values()
            if template.target_segment == segment or template.target_segment is None
        ]
    
    async def personalize_template(self, template_id: str, 
                                 customer_data: Dict[str, str]) -> Optional[str]:
        """Personalize template with customer data"""
        template = await self.get_template(template_id)
        if not template:
            return None
        
        try:
            personalized_content = template.content
            
            # Replace variables with customer data
            for variable in template.variables:
                if variable in customer_data:
                    personalized_content = personalized_content.replace(
                        f"{{{variable}}}", 
                        customer_data[variable]
                    )
            
            # Replace business name
            personalized_content = personalized_content.replace(
                "{business_name}", 
                self.business_name
            )
            
            return personalized_content
            
        except Exception as e:
            logger.error(f"Failed to personalize template: {e}")
            return None
    
    def _create_default_templates(self):
        """Create default message templates based on business type"""
        
        # Welcome message for new customers
        self.templates["welcome_new_customer"] = MessageTemplate(
            template_id="welcome_new_customer",
            name="Welcome New Customer",
            content=f"Welcome to {self.business_name}! We're excited to serve you. {{customer_name}}, thank you for choosing us!",
            message_type=MessageType.TEXT,
            variables=["customer_name"],
            target_segment=CustomerSegment.NEW_CUSTOMER
        )
        
        # Order confirmation
        self.templates["order_confirmation"] = MessageTemplate(
            template_id="order_confirmation",
            name="Order Confirmation", 
            content=f"Hi {{customer_name}}! Your order #{{order_id}} has been confirmed at {self.business_name}. Total: ₹{{amount}}. Expected ready time: {{ready_time}}.",
            message_type=MessageType.TEXT,
            variables=["customer_name", "order_id", "amount", "ready_time"]
        )
        
        # Appointment confirmation
        self.templates["appointment_confirmation"] = MessageTemplate(
            template_id="appointment_confirmation",
            name="Appointment Confirmation",
            content=f"Hi {{customer_name}}! Your appointment at {self.business_name} is confirmed for {{date}} at {{time}}. We look forward to seeing you!",
            message_type=MessageType.TEXT,
            variables=["customer_name", "date", "time"]
        )
        
        # Reminder message
        self.templates["appointment_reminder"] = MessageTemplate(
            template_id="appointment_reminder", 
            name="Appointment Reminder",
            content=f"Hi {{customer_name}}! This is a friendly reminder about your appointment at {self.business_name} tomorrow at {{time}}. See you then!",
            message_type=MessageType.TEXT,
            variables=["customer_name", "time"]
        )
        
        # Thank you message
        self.templates["thank_you"] = MessageTemplate(
            template_id="thank_you",
            name="Thank You Message",
            content=f"Thank you for visiting {self.business_name} today, {{customer_name}}! We hope you had a great experience. Please let us know if you need anything else!",
            message_type=MessageType.TEXT,
            variables=["customer_name"]
        )
        
        # Promotional message for regular customers
        self.templates["promo_regular"] = MessageTemplate(
            template_id="promo_regular",
            name="Promotion for Regular Customers",
            content=f"Hi {{customer_name}}! As a valued customer of {self.business_name}, enjoy {{discount}}% off your next visit. Valid until {{expiry_date}}!",
            message_type=MessageType.TEXT,
            variables=["customer_name", "discount", "expiry_date"],
            target_segment=CustomerSegment.REGULAR_CUSTOMER
        )
        
        # VIP customer special offer
        self.templates["vip_special"] = MessageTemplate(
            template_id="vip_special",
            name="VIP Special Offer",
            content=f"Exclusive for you, {{customer_name}}! As our VIP customer at {self.business_name}, get {{special_offer}}. Limited time offer just for you!",
            message_type=MessageType.TEXT,
            variables=["customer_name", "special_offer"],
            target_segment=CustomerSegment.VIP_CUSTOMER
        )
        
        # Win-back message for inactive customers
        self.templates["win_back"] = MessageTemplate(
            template_id="win_back",
            name="Win Back Inactive Customers",
            content=f"Hi {{customer_name}}! We miss you at {self.business_name}! Come back and enjoy {{incentive}} on your next visit. We'd love to see you again!",
            message_type=MessageType.TEXT,
            variables=["customer_name", "incentive"],
            target_segment=CustomerSegment.INACTIVE_CUSTOMER
        )
        
        # Add business-specific templates
        if self.business_type.lower() in ["restaurant", "cafe", "food"]:
            self._add_restaurant_templates()
        elif self.business_type.lower() in ["salon", "spa", "beauty"]:
            self._add_salon_templates()
        elif self.business_type.lower() in ["retail", "shop", "store"]:
            self._add_retail_templates()
    
    def _add_restaurant_templates(self):
        """Add restaurant-specific templates"""
        
        self.templates["daily_special"] = MessageTemplate(
            template_id="daily_special",
            name="Daily Special Announcement",
            content=f"Today's special at {self.business_name}: {{dish_name}} for just ₹{{price}}! {{description}}. Order now for dine-in or delivery!",
            message_type=MessageType.TEXT,
            variables=["dish_name", "price", "description"]
        )
        
        self.templates["delivery_update"] = MessageTemplate(
            template_id="delivery_update",
            name="Delivery Status Update",
            content=f"Hi {{customer_name}}! Your order from {self.business_name} is {{status}}. {{additional_info}}",
            message_type=MessageType.TEXT,
            variables=["customer_name", "status", "additional_info"]
        )
        
        self.templates["table_ready"] = MessageTemplate(
            template_id="table_ready",
            name="Table Ready Notification",
            content=f"Hi {{customer_name}}! Your table at {self.business_name} is ready. Please come in when convenient!",
            message_type=MessageType.TEXT,
            variables=["customer_name"]
        )
    
    def _add_salon_templates(self):
        """Add salon/spa-specific templates"""
        
        self.templates["service_complete"] = MessageTemplate(
            template_id="service_complete",
            name="Service Completion",
            content=f"Hi {{customer_name}}! Your {{service_name}} at {self.business_name} is complete. You look amazing! Don't forget to book your next appointment!",
            message_type=MessageType.TEXT,
            variables=["customer_name", "service_name"]
        )
        
        self.templates["maintenance_reminder"] = MessageTemplate(
            template_id="maintenance_reminder",
            name="Maintenance Reminder",
            content=f"Hi {{customer_name}}! It's time for your {{service_type}} maintenance at {self.business_name}. Book now to keep looking your best!",
            message_type=MessageType.TEXT,
            variables=["customer_name", "service_type"]
        )
        
        self.templates["new_service_launch"] = MessageTemplate(
            template_id="new_service_launch",
            name="New Service Launch",
            content=f"Exciting news {{customer_name}}! {self.business_name} now offers {{new_service}}. Book now and get {{launch_offer}}!",
            message_type=MessageType.TEXT,
            variables=["customer_name", "new_service", "launch_offer"]
        )
    
    def _add_retail_templates(self):
        """Add retail/shop-specific templates"""
        
        self.templates["new_arrival"] = MessageTemplate(
            template_id="new_arrival",
            name="New Arrival Announcement",
            content=f"New arrival at {self.business_name}! {{product_name}} now available. {{customer_name}}, come check it out!",
            message_type=MessageType.TEXT,
            variables=["customer_name", "product_name"]
        )
        
        self.templates["stock_alert"] = MessageTemplate(
            template_id="stock_alert",
            name="Stock Alert",
            content=f"Hi {{customer_name}}! The {{product_name}} you were interested in is back in stock at {self.business_name}. Limited quantity available!",
            message_type=MessageType.TEXT,
            variables=["customer_name", "product_name"]
        )
        
        self.templates["sale_announcement"] = MessageTemplate(
            template_id="sale_announcement",
            name="Sale Announcement",
            content=f"Big sale at {self.business_name}! {{sale_details}}. {{customer_name}}, don't miss out on these amazing deals!",
            message_type=MessageType.TEXT,
            variables=["customer_name", "sale_details"]
        )


class TemplateAnalytics:
    """Analytics for message template performance"""
    
    def __init__(self):
        self.template_stats: Dict[str, Dict[str, int]] = {}
    
    def record_template_send(self, template_id: str):
        """Record that a template was sent"""
        if template_id not in self.template_stats:
            self.template_stats[template_id] = {
                "sent": 0,
                "delivered": 0,
                "read": 0,
                "responded": 0
            }
        
        self.template_stats[template_id]["sent"] += 1
    
    def record_template_delivery(self, template_id: str):
        """Record that a template was delivered"""
        if template_id in self.template_stats:
            self.template_stats[template_id]["delivered"] += 1
    
    def record_template_read(self, template_id: str):
        """Record that a template was read"""
        if template_id in self.template_stats:
            self.template_stats[template_id]["read"] += 1
    
    def record_template_response(self, template_id: str):
        """Record that a template generated a response"""
        if template_id in self.template_stats:
            self.template_stats[template_id]["responded"] += 1
    
    def get_template_performance(self, template_id: str) -> Dict[str, float]:
        """Get performance metrics for a template"""
        if template_id not in self.template_stats:
            return {}
        
        stats = self.template_stats[template_id]
        sent = stats["sent"]
        
        if sent == 0:
            return {}
        
        return {
            "delivery_rate": (stats["delivered"] / sent) * 100,
            "read_rate": (stats["read"] / sent) * 100,
            "response_rate": (stats["responded"] / sent) * 100,
            "total_sent": sent
        }
    
    def get_top_performing_templates(self, metric: str = "response_rate", 
                                   limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing templates by specified metric"""
        template_performances = []
        
        for template_id in self.template_stats:
            performance = self.get_template_performance(template_id)
            if performance and metric in performance:
                template_performances.append({
                    "template_id": template_id,
                    "performance": performance[metric],
                    "stats": performance
                })
        
        # Sort by metric and return top performers
        template_performances.sort(key=lambda x: x["performance"], reverse=True)
        return template_performances[:limit]