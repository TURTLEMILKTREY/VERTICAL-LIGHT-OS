"""
WhatsApp Contact Management
Production-ready contact management for WhatsApp Business automation.
"""

import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging

from .interfaces import ContactManagerInterface
from .models import WhatsAppContact, CustomerSegment


logger = logging.getLogger(__name__)


class WhatsAppContactManager(ContactManagerInterface):
    """Contact management for WhatsApp Business"""
    
    def __init__(self, storage_backend: Optional[Any] = None):
        """Initialize contact manager with optional storage backend"""
        self.storage = storage_backend
        self._contacts: Dict[str, WhatsAppContact] = {}
        
        # Load existing contacts if storage backend is available
        if self.storage:
            self._load_contacts()
    
    async def add_contact(self, contact: WhatsAppContact) -> bool:
        """Add a new contact"""
        try:
            self._contacts[contact.phone_number] = contact
            
            if self.storage:
                await self._save_contact(contact)
            
            logger.info(f"Added contact: {contact.phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add contact {contact.phone_number}: {e}")
            return False
    
    async def update_contact(self, phone_number: str, updates: Dict[str, Any]) -> bool:
        """Update contact information"""
        try:
            if phone_number not in self._contacts:
                return False
            
            contact = self._contacts[phone_number]
            
            # Update contact fields
            for field, value in updates.items():
                if hasattr(contact, field):
                    setattr(contact, field, value)
            
            # Update last interaction time
            contact.last_interaction = datetime.now()
            
            if self.storage:
                await self._save_contact(contact)
            
            logger.info(f"Updated contact: {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update contact {phone_number}: {e}")
            return False
    
    async def get_contact(self, phone_number: str) -> Optional[WhatsAppContact]:
        """Get contact by phone number"""
        return self._contacts.get(phone_number)
    
    async def segment_contacts(self, segment_criteria: Dict[str, Any]) -> List[WhatsAppContact]:
        """Get contacts matching segment criteria"""
        matching_contacts = []
        
        for contact in self._contacts.values():
            if self._matches_criteria(contact, segment_criteria):
                matching_contacts.append(contact)
        
        return matching_contacts
    
    async def get_inactive_customers(self, days_threshold: int = 30) -> List[WhatsAppContact]:
        """Get customers who haven't interacted in specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        
        inactive_contacts = []
        for contact in self._contacts.values():
            if (contact.last_interaction and 
                contact.last_interaction < cutoff_date):
                inactive_contacts.append(contact)
        
        return inactive_contacts
    
    async def get_vip_customers(self, min_orders: int = 10, 
                              min_value: float = 5000.0) -> List[WhatsAppContact]:
        """Get VIP customers based on order count and lifetime value"""
        vip_contacts = []
        
        for contact in self._contacts.values():
            if (contact.total_orders >= min_orders and 
                contact.lifetime_value >= min_value):
                contact.segment = CustomerSegment.VIP_CUSTOMER
                vip_contacts.append(contact)
        
        return vip_contacts
    
    async def update_customer_stats(self, phone_number: str, 
                                  order_value: float) -> bool:
        """Update customer order statistics"""
        contact = await self.get_contact(phone_number)
        if not contact:
            return False
        
        updates = {
            "total_orders": contact.total_orders + 1,
            "lifetime_value": contact.lifetime_value + order_value,
            "last_interaction": datetime.now()
        }
        
        # Update segment based on new stats
        if updates["total_orders"] >= 10 and updates["lifetime_value"] >= 5000:
            updates["segment"] = CustomerSegment.VIP_CUSTOMER
        elif updates["total_orders"] >= 3:
            updates["segment"] = CustomerSegment.REGULAR_CUSTOMER
        
        return await self.update_contact(phone_number, updates)
    
    async def get_contact_insights(self) -> Dict[str, Any]:
        """Get overall contact insights"""
        total_contacts = len(self._contacts)
        
        if total_contacts == 0:
            return {
                "total_contacts": 0,
                "segments": {},
                "avg_lifetime_value": 0,
                "avg_orders_per_customer": 0
            }
        
        # Calculate segment distribution
        segments = {}
        total_value = 0
        total_orders = 0
        
        for contact in self._contacts.values():
            segment = contact.segment.value
            segments[segment] = segments.get(segment, 0) + 1
            total_value += contact.lifetime_value
            total_orders += contact.total_orders
        
        return {
            "total_contacts": total_contacts,
            "segments": segments,
            "avg_lifetime_value": total_value / total_contacts,
            "avg_orders_per_customer": total_orders / total_contacts,
            "total_lifetime_value": total_value
        }
    
    def _matches_criteria(self, contact: WhatsAppContact, 
                         criteria: Dict[str, Any]) -> bool:
        """Check if contact matches segment criteria"""
        for field, expected_value in criteria.items():
            contact_value = getattr(contact, field, None)
            
            if contact_value != expected_value:
                return False
        
        return True
    
    def _load_contacts(self):
        """Load contacts from storage backend"""
        # Implementation depends on storage backend
        # Could be database, file system, etc.
        pass
    
    async def _save_contact(self, contact: WhatsAppContact):
        """Save contact to storage backend"""
        # Implementation depends on storage backend
        # Could be database, file system, etc.
        pass


class InMemoryContactStorage:
    """Simple in-memory contact storage for testing/development"""
    
    def __init__(self):
        self.contacts_file = "whatsapp_contacts.json"
    
    def save_contact(self, contact: WhatsAppContact):
        """Save contact to JSON file"""
        try:
            # Load existing contacts
            try:
                with open(self.contacts_file, 'r') as f:
                    contacts_data = json.load(f)
            except FileNotFoundError:
                contacts_data = {}
            
            # Add/update contact
            contacts_data[contact.phone_number] = {
                "phone_number": contact.phone_number,
                "name": contact.name,
                "segment": contact.segment.value,
                "last_interaction": contact.last_interaction.isoformat() if contact.last_interaction else None,
                "total_orders": contact.total_orders,
                "lifetime_value": contact.lifetime_value,
                "preferences": contact.preferences
            }
            
            # Save back to file
            with open(self.contacts_file, 'w') as f:
                json.dump(contacts_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save contact to file: {e}")
    
    def load_contacts(self) -> Dict[str, WhatsAppContact]:
        """Load contacts from JSON file"""
        try:
            with open(self.contacts_file, 'r') as f:
                contacts_data = json.load(f)
            
            contacts = {}
            for phone, data in contacts_data.items():
                last_interaction = None
                if data.get("last_interaction"):
                    last_interaction = datetime.fromisoformat(data["last_interaction"])
                
                contact = WhatsAppContact(
                    phone_number=data["phone_number"],
                    name=data.get("name"),
                    segment=CustomerSegment(data.get("segment", "new_customer")),
                    last_interaction=last_interaction,
                    total_orders=data.get("total_orders", 0),
                    lifetime_value=data.get("lifetime_value", 0.0),
                    preferences=data.get("preferences", {})
                )
                contacts[phone] = contact
            
            return contacts
            
        except FileNotFoundError:
            return {}
        except Exception as e:
            logger.error(f"Failed to load contacts from file: {e}")
            return {}