"""
Business Configuration Interface
Simple web interface for business owners to configure WhatsApp automation.
"""

from flask import Flask, render_template, request, jsonify, session
import json
import requests
import hmac
import hashlib
from typing import Dict, List, Any
from datetime import datetime

# Import our WhatsApp automation service
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.automation.whatsapp import create_whatsapp_automation_service


app = Flask(__name__)
app.secret_key = "whatsapp-automation-config-key"

# WhatsApp Business API Configuration 
WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"


class RealWhatsAppHandler:
 """Handle real WhatsApp Business API interactions"""

 def __init__(self, access_token, phone_number_id, verify_token):
 self.access_token = access_token
 self.phone_number_id = phone_number_id
 self.verify_token = verify_token

 def send_message(self, to_number, message_text):
 """Send actual WhatsApp message"""
 url = f"{WHATSAPP_API_URL}/{self.phone_number_id}/messages"

 headers = {
 "Authorization": f"Bearer {self.access_token}",
 "Content-Type": "application/json"
 }

 data = {
 "messaging_product": "whatsapp",
 "to": to_number,
 "type": "text",
 "text": {"body": message_text}
 }

 try:
 response = requests.post(url, headers=headers, json=data)
 return response.json()
 except Exception as e:
 return {"error": str(e)}

 def find_auto_response(self, message_text, business_config):
 """Find matching auto-response from configured rules"""
 message_lower = message_text.lower()

 # Check configured auto-responses
 for response_rule in business_config.get("auto_responses", []):
 if response_rule.get("active", False):
 for keyword in response_rule.get("keywords", []):
 if keyword.lower() in message_lower:
 return response_rule["response"].replace(
 "{business_name}", business_config.get("business_name", "")
 )

 return None

 def process_incoming_message(self, webhook_data, business_config):
 """Process incoming WhatsApp message and send auto-response"""
 try:
 # Extract message data
 entry = webhook_data["entry"][0]
 changes = entry["changes"][0]
 value = changes["value"]

 if "messages" in value:
 message = value["messages"][0]
 from_number = message["from"]
 message_text = message["text"]["body"]

 # Find matching auto-response
 response_text = self.find_auto_response(message_text, business_config)

 if response_text:
 # Send auto-response
 result = self.send_message(from_number, response_text)

 # Log the interaction
 self.log_message_interaction(from_number, message_text, response_text)

 return True, result

 return False, "No auto-response found"
 except Exception as e:
 return False, f"Error processing message: {e}"

 def log_message_interaction(self, from_number, message_text, response_text):
 """Log message interaction for analytics"""
 interaction = {
 "timestamp": datetime.now().isoformat(),
 "from_number": from_number,
 "message": message_text,
 "response": response_text,
 "type": "auto_response"
 }

 # TODO: Save to analytics database
 # For now, just print for debugging
 print(f"WhatsApp Interaction: {interaction}")


class BusinessConfigManager:
 """Manages business configuration for WhatsApp automation"""

 def __init__(self):
 self.configs_file = "../config/business/business_configs.json"
 self.configs = self._load_configs()

 def _load_configs(self) -> Dict[str, Any]:
 """Load existing business configurations"""
 try:
 with open(self.configs_file, 'r') as f:
 return json.load(f)
 except FileNotFoundError:
 return {}

 def _save_configs(self):
 """Save configurations to file"""
 with open(self.configs_file, 'w') as f:
 json.dump(self.configs, f, indent=2)

 def create_business_config(self, business_data: Dict[str, Any]) -> str:
 """Create a new business configuration"""
 business_id = f"business_{datetime.now().timestamp()}"

 config = {
 "business_id": business_id,
 "business_name": business_data["business_name"],
 "business_type": business_data["business_type"],
 "owner_name": business_data["owner_name"],
 "phone_number": business_data["phone_number"],
 "address": business_data.get("address", ""),
 "business_hours": business_data.get("business_hours", self._default_hours()),
 "whatsapp_config": {
 "access_token": business_data.get("whatsapp_access_token", ""),
 "phone_number_id": business_data.get("whatsapp_phone_number_id", ""),
 "business_account_id": business_data.get("whatsapp_business_account_id", ""),
 "verify_token": business_data.get("whatsapp_verify_token", "")
 },
 "auto_responses": self._default_auto_responses(business_data["business_type"]),
 "custom_templates": [],
 "created_at": datetime.now().isoformat(),
 "status": "active"
 }

 self.configs[business_id] = config
 self._save_configs()

 return business_id

 def get_business_config(self, business_id: str) -> Dict[str, Any]:
 """Get business configuration"""
 return self.configs.get(business_id, {})

 def update_auto_responses(self, business_id: str, auto_responses: List[Dict[str, Any]]):
 """Update auto-response rules"""
 if business_id in self.configs:
 self.configs[business_id]["auto_responses"] = auto_responses
 self._save_configs()

 def add_custom_template(self, business_id: str, template: Dict[str, Any]):
 """Add custom message template"""
 if business_id in self.configs:
 self.configs[business_id]["custom_templates"].append(template)
 self._save_configs()

 def _default_hours(self) -> Dict[str, str]:
 """Default business hours"""
 return {
 "monday": "9:00-18:00",
 "tuesday": "9:00-18:00",
 "wednesday": "9:00-18:00",
 "thursday": "9:00-18:00",
 "friday": "9:00-18:00",
 "saturday": "9:00-18:00",
 "sunday": "closed"
 }

 def _default_auto_responses(self, business_type: str) -> List[Dict[str, Any]]:
 """Default auto-response rules based on business type"""
 base_responses = [
 {
 "keywords": ["hello", "hi", "hey"],
 "response": "Hello! Welcome to {business_name}. How can we help you today?",
 "active": True
 },
 {
 "keywords": ["hours", "open", "timing"],
 "response": "Our business hours are Monday-Saturday 9 AM to 6 PM. We're closed on Sundays.",
 "active": True
 },
 {
 "keywords": ["location", "address", "where"],
 "response": "You can find us at our location. Would you like directions?",
 "active": True
 }
 ]

 if business_type == "restaurant":
 base_responses.extend([
 {
 "keywords": ["menu", "food", "eat"],
 "response": "We have a delicious menu! What type of cuisine are you in the mood for?",
 "active": True
 },
 {
 "keywords": ["delivery", "order"],
 "response": "Yes, we offer delivery! What would you like to order today?",
 "active": True
 }
 ])

 elif business_type == "salon":
 base_responses.extend([
 {
 "keywords": ["appointment", "book", "schedule"],
 "response": "I'd be happy to help you schedule an appointment! What service are you interested in?",
 "active": True
 },
 {
 "keywords": ["services", "treatment"],
 "response": "We offer a full range of beauty services! Which service interests you today?",
 "active": True
 }
 ])

 elif business_type == "retail":
 base_responses.extend([
 {
 "keywords": ["product", "available", "stock"],
 "response": "Let me check our current stock for you! What product are you looking for?",
 "active": True
 },
 {
 "keywords": ["price", "cost"],
 "response": "I'd be happy to help with pricing information! Which product are you interested in?",
 "active": True
 }
 ])

 return base_responses


config_manager = BusinessConfigManager()


@app.route('/')
def index():
 """Main configuration page"""
 return render_template('index.html')


@app.route('/setup', methods=['GET', 'POST'])
def business_setup():
 """Business setup form"""
 if request.method == 'POST':
 business_data = request.json

 try:
 business_id = config_manager.create_business_config(business_data)
 session['business_id'] = business_id

 return jsonify({
 "success": True,
 "business_id": business_id,
 "message": "Business configuration created successfully!"
 })

 except Exception as e:
 return jsonify({
 "success": False,
 "error": str(e)
 }), 400

 return render_template('setup.html')


@app.route('/configure/<business_id>')
def configure_automation(business_id):
 """Configure automation settings"""
 config = config_manager.get_business_config(business_id)

 if not config:
 return "Business not found", 404

 return render_template('configure.html', config=config)


@app.route('/whatsapp-setup/<business_id>')
def whatsapp_setup(business_id):
 """WhatsApp API setup page"""
 config = config_manager.get_business_config(business_id)

 if not config:
 return "Business not found", 404

 return render_template('whatsapp_setup.html', config=config)


@app.route('/api/auto-responses/<business_id>', methods=['GET', 'POST'])
def manage_auto_responses(business_id):
 """Manage auto-response rules"""

 if request.method == 'GET':
 config = config_manager.get_business_config(business_id)
 return jsonify(config.get("auto_responses", []))

 elif request.method == 'POST':
 auto_responses = request.json
 config_manager.update_auto_responses(business_id, auto_responses)

 return jsonify({
 "success": True,
 "message": "Auto-responses updated successfully!"
 })


@app.route('/api/templates/<business_id>', methods=['POST'])
def add_custom_template(business_id):
 """Add custom message template"""
 template_data = request.json

 template = {
 "template_id": f"custom_{datetime.now().timestamp()}",
 "name": template_data["name"],
 "content": template_data["content"],
 "variables": template_data.get("variables", []),
 "created_at": datetime.now().isoformat()
 }

 config_manager.add_custom_template(business_id, template)

 return jsonify({
 "success": True,
 "message": "Custom template added successfully!"
 })


@app.route('/api/test-automation/<business_id>', methods=['POST'])
def test_automation(business_id):
 """Test the WhatsApp automation setup"""
 try:
 config = config_manager.get_business_config(business_id)

 if not config:
 return jsonify({"success": False, "error": "Business not found"}), 404

 # Create test configuration
 test_config = {
 "business_name": config["business_name"],
 "business_type": config["business_type"],
 "whatsapp_access_token": "test_token",
 "whatsapp_phone_number_id": "test_phone_id",
 "whatsapp_business_account_id": "test_account_id",
 "whatsapp_verify_token": "test_verify_token",
 "business_hours": config["business_hours"]
 }

 # Create automation service (in test mode)
 automation_service = create_whatsapp_automation_service(test_config)

 # Test auto-responses
 test_messages = ["Hello", "What are your hours?", "Do you deliver?"]
 test_results = []

 for msg in test_messages:
 # Simulate how the auto-responder would handle the message
 matching_response = None
 for response_rule in config["auto_responses"]:
 if response_rule["active"]:
 for keyword in response_rule["keywords"]:
 if keyword.lower() in msg.lower():
 matching_response = response_rule["response"].replace(
 "{business_name}", config["business_name"]
 )
 break
 if matching_response:
 break

 test_results.append({
 "input": msg,
 "response": matching_response or "No automatic response configured"
 })

 return jsonify({
 "success": True,
 "test_results": test_results,
 "message": "Automation test completed successfully!"
 })

 except Exception as e:
 return jsonify({
 "success": False,
 "error": str(e)
 }), 500


@app.route('/dashboard/<business_id>')
def business_dashboard(business_id):
 """Business dashboard with analytics"""
 config = config_manager.get_business_config(business_id)

 if not config:
 return "Business not found", 404

 # Mock analytics data for demo
 analytics = {
 "messages_today": 42,
 "auto_responses_sent": 34,
 "response_rate": "81%",
 "customers_served": 28,
 "time_saved_hours": 2.3
 }

 return render_template('dashboard.html', config=config, analytics=analytics)


@app.route('/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
 """Handle WhatsApp webhook for real message processing"""

 if request.method == 'GET':
 # Webhook verification
 verify_token = request.args.get('hub.verify_token')
 challenge = request.args.get('hub.challenge')

 if verify_token == "whatsapp_verify_token_2025":
 return challenge
 else:
 return "Forbidden", 403

 elif request.method == 'POST':
 # Process incoming message
 webhook_data = request.get_json()

 # For now, get the first business config (later: match by phone number)
 all_configs = config_manager.configs
 if not all_configs:
 return "No business configured", 400

 business_config = list(all_configs.values())[0]

 # Check if WhatsApp API is configured for this business
 if not business_config.get("whatsapp_api_configured"):
 return "WhatsApp API not configured", 400

 # Initialize WhatsApp handler with business credentials
 whatsapp_handler = RealWhatsAppHandler(
 access_token=business_config.get("whatsapp_access_token", ""),
 phone_number_id=business_config.get("whatsapp_phone_number_id", ""),
 verify_token="whatsapp_verify_token_2025"
 )

 # Process the message
 success, result = whatsapp_handler.process_incoming_message(webhook_data, business_config)

 if success:
 return "OK", 200
 else:
 print(f"Message processing failed: {result}")
 return "OK", 200 # Still return OK to Meta


@app.route('/api/setup-whatsapp-api/<business_id>', methods=['POST'])
def setup_whatsapp_api(business_id):
 """Configure WhatsApp Business API credentials"""
 try:
 data = request.get_json()

 config = config_manager.get_business_config(business_id)
 if not config:
 return jsonify({"success": False, "error": "Business not found"}), 404

 # Update business config with WhatsApp API credentials
 config.update({
 "whatsapp_access_token": data.get("access_token"),
 "whatsapp_phone_number_id": data.get("phone_number_id"),
 "whatsapp_business_account_id": data.get("business_account_id"),
 "whatsapp_app_id": data.get("app_id"),
 "whatsapp_api_configured": True,
 "webhook_url": data.get("webhook_url", ""),
 })

 config_manager.configs[business_id] = config
 config_manager._save_configs()

 return jsonify({
 "success": True,
 "message": "WhatsApp API configured successfully!",
 "webhook_url": f"{data.get('webhook_url', '')}/webhook"
 })

 except Exception as e:
 return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/test-whatsapp-send/<business_id>', methods=['POST'])
def test_whatsapp_send(business_id):
 """Test sending a WhatsApp message via API"""
 try:
 data = request.get_json()
 config = config_manager.get_business_config(business_id)

 if not config or not config.get("whatsapp_api_configured"):
 return jsonify({"success": False, "error": "WhatsApp API not configured"}), 400

 whatsapp_handler = RealWhatsAppHandler(
 access_token=config.get("whatsapp_access_token"),
 phone_number_id=config.get("whatsapp_phone_number_id"),
 verify_token="whatsapp_verify_token_2025"
 )

 result = whatsapp_handler.send_message(
 to_number=data.get("to_number"),
 message_text=data.get("message")
 )

 return jsonify({
 "success": True,
 "result": result,
 "message": "Test message sent successfully!"
 })

 except Exception as e:
 return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
 app.run(debug=True, host='0.0.0.0', port=5000)