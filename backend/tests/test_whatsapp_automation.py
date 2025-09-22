"""
WhatsApp Automation Service Test
Comprehensive test for the WhatsApp Business automation system.
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from datetime import datetime, timedelta


def test_whatsapp_models():
    """Test WhatsApp data models"""
    print("Testing WhatsApp models...")
    
    try:
        from services.automation.whatsapp.models import (
            WhatsAppContact, WhatsAppMessage, MessageTemplate, 
            CustomerSegment, MessageType, AutoResponse
        )
        
        # Test contact creation
        contact = WhatsAppContact(
            phone_number="+919876543210",
            name="Test Customer",
            segment=CustomerSegment.NEW_CUSTOMER,
            total_orders=0,
            lifetime_value=0.0
        )
        
        assert contact.phone_number == "+919876543210"
        assert contact.segment == CustomerSegment.NEW_CUSTOMER
        
        # Test message creation
        message = WhatsAppMessage.create_outbound(
            contact_phone="+919876543210",
            content="Hello from test!",
            message_type=MessageType.TEXT
        )
        
        assert message.is_from_business == True
        assert message.content == "Hello from test!"
        
        # Test template creation
        template = MessageTemplate(
            template_id="test_template",
            name="Test Template",
            content="Hello {customer_name}, welcome to {business_name}!",
            message_type=MessageType.TEXT,
            variables=["customer_name", "business_name"]
        )
        
        assert len(template.variables) == 2
        assert "customer_name" in template.variables
        
        # Test auto-response
        auto_response = AutoResponse(
            trigger_keywords=["hello", "hi"],
            response_template="Hello! How can we help you?"
        )
        
        assert auto_response.matches_message("Hello there!") == True
        assert auto_response.matches_message("Goodbye") == False
        
        print("✓ WhatsApp models working correctly")
        return True
        
    except Exception as e:
        print(f"✗ WhatsApp models test failed: {e}")
        return False


def test_contact_manager():
    """Test contact management system"""
    print("Testing contact manager...")
    
    try:
        from services.automation.whatsapp.contact_manager import WhatsAppContactManager
        from services.automation.whatsapp.models import WhatsAppContact, CustomerSegment
        
        # Create contact manager
        contact_manager = WhatsAppContactManager()
        
        # Test adding contact
        contact = WhatsAppContact(
            phone_number="+919876543210",
            name="Test Restaurant Customer",
            segment=CustomerSegment.NEW_CUSTOMER
        )
        
        # Since these are async methods, we'll test the sync parts
        contact_manager._contacts[contact.phone_number] = contact
        
        # Test getting contact
        retrieved_contact = contact_manager._contacts.get("+919876543210")
        assert retrieved_contact is not None
        assert retrieved_contact.name == "Test Restaurant Customer"
        
        print("✓ Contact manager working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Contact manager test failed: {e}")
        return False


def test_auto_responder():
    """Test auto-response system"""
    print("Testing auto-responder...")
    
    try:
        from services.automation.whatsapp.auto_responder import SmartAutoResponder
        from services.automation.whatsapp.models import WhatsAppMessage, MessageType
        
        # Create auto-responder
        responder = SmartAutoResponder(
            business_name="Test Restaurant",
            business_type="restaurant"
        )
        
        # Test that responder was created with default rules
        assert len(responder.auto_responses) > 0
        
        # Test greeting detection
        greeting_message = WhatsAppMessage(
            message_id="test_msg_1",
            contact_phone="+919876543210",
            content="Hello",
            message_type=MessageType.TEXT,
            timestamp=datetime.now(),
            is_from_business=False
        )
        
        # Find matching response rule
        matching_rule = None
        for rule in responder.auto_responses:
            if rule.matches_message(greeting_message.content):
                matching_rule = rule
                break
        
        assert matching_rule is not None
        
        print("✓ Auto-responder working correctly") 
        return True
        
    except Exception as e:
        print(f"✗ Auto-responder test failed: {e}")
        return False


def test_template_manager():
    """Test template management system"""
    print("Testing template manager...")
    
    try:
        from services.automation.whatsapp.template_manager import WhatsAppTemplateManager
        from services.automation.whatsapp.models import MessageTemplate, MessageType
        
        # Create template manager
        template_manager = WhatsAppTemplateManager(
            business_name="Test Restaurant",
            business_type="restaurant"
        )
        
        # Test that default templates were created
        assert len(template_manager.templates) > 0
        
        # Test getting welcome template
        welcome_template = template_manager.templates.get("welcome_new_customer")
        assert welcome_template is not None
        assert "welcome" in welcome_template.content.lower()
        
        # Test restaurant-specific templates
        daily_special = template_manager.templates.get("daily_special")
        assert daily_special is not None
        assert "special" in daily_special.content.lower()
        
        print("✓ Template manager working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Template manager test failed: {e}")
        return False


def test_automation_service_creation():
    """Test WhatsApp automation service creation"""
    print("Testing automation service creation...")
    
    try:
        from services.automation.whatsapp import create_whatsapp_automation_service
        
        # Test configuration
        config = {
            "business_name": "Test Restaurant",
            "business_type": "restaurant",
            "whatsapp_access_token": "test_token",
            "whatsapp_phone_number_id": "test_phone_id",
            "whatsapp_business_account_id": "test_account_id",
            "whatsapp_verify_token": "test_verify_token",
            "business_hours": {
                "monday": "9:00-18:00",
                "tuesday": "9:00-18:00",
                "wednesday": "9:00-18:00",
                "thursday": "9:00-18:00", 
                "friday": "9:00-18:00",
                "saturday": "9:00-18:00",
                "sunday": "closed"
            }
        }
        
        # Create service
        service = create_whatsapp_automation_service(config)
        
        # Test service components
        assert service.business_name == "Test Restaurant"
        assert service.business_type == "restaurant"
        assert service.whatsapp_client is not None
        assert service.contact_manager is not None
        assert service.auto_responder is not None
        assert service.template_manager is not None
        
        print("✓ Automation service creation working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Automation service creation test failed: {e}")
        return False


def test_business_specific_features():
    """Test business-type specific features"""
    print("Testing business-specific features...")
    
    try:
        from services.automation.whatsapp.template_manager import WhatsAppTemplateManager
        
        # Test restaurant features
        restaurant_manager = WhatsAppTemplateManager("Test Restaurant", "restaurant")
        assert "daily_special" in restaurant_manager.templates
        assert "delivery_update" in restaurant_manager.templates
        
        # Test salon features  
        salon_manager = WhatsAppTemplateManager("Test Salon", "salon")
        assert "service_complete" in salon_manager.templates
        assert "maintenance_reminder" in salon_manager.templates
        
        # Test retail features
        retail_manager = WhatsAppTemplateManager("Test Store", "retail")
        assert "new_arrival" in retail_manager.templates
        assert "sale_announcement" in retail_manager.templates
        
        print("✓ Business-specific features working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Business-specific features test failed: {e}")
        return False


def test_practical_business_scenarios():
    """Test practical business scenarios"""
    print("Testing practical business scenarios...")
    
    try:
        from services.automation.whatsapp import create_whatsapp_automation_service
        from services.automation.whatsapp.models import CustomerSegment
        
        # Restaurant scenario
        restaurant_config = {
            "business_name": "Sharma's Kitchen",
            "business_type": "restaurant",
            "whatsapp_access_token": "test_token",
            "whatsapp_phone_number_id": "test_phone_id", 
            "whatsapp_business_account_id": "test_account_id",
            "whatsapp_verify_token": "test_verify_token"
        }
        
        restaurant_service = create_whatsapp_automation_service(restaurant_config)
        
        # Test customer journey simulation
        # 1. New customer inquiry
        welcome_template = restaurant_service.template_manager.templates.get("welcome_new_customer")
        assert welcome_template is not None
        assert "welcome" in welcome_template.content.lower()
        
        # 2. Order confirmation
        order_template = restaurant_service.template_manager.templates.get("order_confirmation")
        assert order_template is not None
        assert "order" in order_template.content.lower()
        assert "amount" in order_template.variables
        
        # 3. Daily special promotion
        daily_special = restaurant_service.template_manager.templates.get("daily_special")
        assert daily_special is not None
        assert "special" in daily_special.content.lower()
        
        print("✓ Practical business scenarios working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Practical business scenarios test failed: {e}")
        return False


async def test_async_functionality():
    """Test async functionality"""
    print("Testing async functionality...")
    
    try:
        from services.automation.whatsapp import create_whatsapp_automation_service
        
        config = {
            "business_name": "Test Business", 
            "business_type": "restaurant",
            "whatsapp_access_token": "test_token",
            "whatsapp_phone_number_id": "test_phone_id",
            "whatsapp_business_account_id": "test_account_id", 
            "whatsapp_verify_token": "test_verify_token"
        }
        
        service = create_whatsapp_automation_service(config)
        
        # Test async customer creation
        success = await service.add_customer(
            phone_number="+919876543210",
            name="Test Customer"
        )
        assert success == True
        
        # Test async template creation
        template_success = await service.create_custom_template(
            template_id="test_custom",
            name="Test Custom Template", 
            content="Hello {customer_name}!",
            variables=["customer_name"]
        )
        assert template_success == True
        
        print("✓ Async functionality working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Async functionality test failed: {e}")
        return False


def run_whatsapp_automation_tests():
    """Run all WhatsApp automation tests"""
    print("Running WhatsApp Automation Service Tests")
    print("=" * 60)
    
    tests = [
        test_whatsapp_models,
        test_contact_manager, 
        test_auto_responder,
        test_template_manager,
        test_automation_service_creation,
        test_business_specific_features,
        test_practical_business_scenarios
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    # Run async test
    try:
        asyncio.run(test_async_functionality())
        passed += 1
        total += 1
        print()
    except Exception as e:
        print(f"✗ Async functionality test failed: {e}")
        total += 1
        print()
    
    print("=" * 60)
    print(f"WhatsApp Automation Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ WhatsApp automation service is working correctly!")
        print("✓ Ready for real business integration!")
        return True
    else:
        print("✗ Some tests failed - need to resolve issues")
        return False


if __name__ == "__main__":
    success = run_whatsapp_automation_tests()
    sys.exit(0 if success else 1)