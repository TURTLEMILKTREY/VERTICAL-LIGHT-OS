# Real WhatsApp Business API Setup Guide

## Get Your WhatsApp Automation Working with Real Messages

This guide will connect your dashboard to actual WhatsApp messages so customers get real auto-responses.

---

## **What You Need to Set Up**

### **Requirements:**
- Facebook Business account
- Meta Developer account 
- WhatsApp Business phone number
- Valid business documentation
- SSL-enabled webhook URL (we'll set this up)

### **Time Required:** 2-3 hours setup + Meta verification time
### **Cost:** Free for small business volume (1000+ messages/month)

---

## **Step-by-Step Real API Setup**

### **Phase 1: Meta Developer Account Setup (30 minutes)**

#### **Step 1: Create Facebook Business Account**
1. **Go to**: `https://business.facebook.com`
2. **Click "Create Account"**
3. **Enter your business details**:
 - Business name: [Your business name]
 - Your name: [Your real name]
 - Business email: [Your business email]
4. **Verify email** and complete setup

#### **Step 2: Create Meta Developer Account**
1. **Go to**: `https://developers.facebook.com`
2. **Click "Get Started"**
3. **Use same Facebook account** as business account
4. **Accept terms** and complete verification

#### **Step 3: Create WhatsApp Business App**
1. **In Meta Developer Console**, click "Create App"
2. **Select "Business"** as app type
3. **Enter app details**:
 - App name: "[Your Business] WhatsApp Automation"
 - Contact email: [Your email]
 - Business account: [Select your business]
4. **Add WhatsApp Business** product to your app

---

### **Phase 2: WhatsApp Business API Configuration (45 minutes)**

#### **Step 1: Get API Credentials**
```
In your Meta Developer app:
1. Go to WhatsApp > API Setup
2. Note these credentials:
 - App ID: [Copy this]
 - App Secret: [Copy this] 
 - Access Token: [Copy this]
 - Phone Number ID: [Copy this]
 - Business Account ID: [Copy this]
```

#### **Step 2: Set Up Webhook**
We need a public URL for Meta to send messages to your system.

**Option A: Use ngrok (Quick Setup)**
```bash
# Install ngrok
# Download from: https://ngrok.com/download

# In new terminal window:
ngrok http 5000

# Copy the HTTPS URL (like: https://abc123.ngrok.io)
```

**Option B: Use Cloud Service**
- Deploy to Heroku, Railway, or similar
- Get public HTTPS URL for your Flask app

#### **Step 3: Configure Webhook in Meta**
1. **In Meta Developer Console** > WhatsApp > Configuration
2. **Set Webhook URL**: `https://your-ngrok-url.com/webhook`
3. **Set Verify Token**: `your_verify_token_123`
4. **Subscribe to**: `messages` events
5. **Test webhook** connection

---

### **Phase 3: Update Your Flask App for Real API (30 minutes)**

<function_calls>
<invoke name="create_file">
<parameter name="content"># Real WhatsApp API Integration Code

```python
# Add this to your business_config_app.py

import requests
import hmac
import hashlib
from flask import request

# WhatsApp Business API Configuration
WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"

class RealWhatsAppHandler:
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

 response = requests.post(url, headers=headers, json=data)
 return response.json()

 def process_incoming_message(self, webhook_data):
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
 response_text = self.find_auto_response(message_text)

 if response_text:
 # Send auto-response
 self.send_message(from_number, response_text)

 # Log the interaction
 self.log_message_interaction(from_number, message_text, response_text)

 return True
 except Exception as e:
 print(f"Error processing message: {e}")
 return False

 def find_auto_response(self, message_text):
 """Find matching auto-response from configured rules"""
 # Get current business configuration
 # This would integrate with your existing business config

 # Example auto-response logic
 message_lower = message_text.lower()

 if any(keyword in message_lower for keyword in ["hi", "hello", "hey"]):
 return "Hi! Welcome to our business. How can we help you today?"

 elif any(keyword in message_lower for keyword in ["menu", "food", "eat"]):
 return "Here's our menu: Biryani ₹200, Dal Rice ₹120, Tea ₹30. To order call: 9876543210"

 elif any(keyword in message_lower for keyword in ["hours", "time", "open"]):
 return "We're open Monday-Sunday, 9 AM to 9 PM. Currently OPEN!"

 elif any(keyword in message_lower for keyword in ["location", "address", "where"]):
 return "We're located at [Your Address]. Google Maps: [Your Maps Link]"

 return None # No auto-response found

 def log_message_interaction(self, from_number, message_text, response_text):
 """Log message interaction for analytics"""
 interaction = {
 "timestamp": datetime.now().isoformat(),
 "from_number": from_number,
 "message": message_text,
 "response": response_text,
 "type": "auto_response"
 }

 # Save to your analytics system
 # This integrates with your existing dashboard analytics


# Add these routes to your Flask app

@app.route('/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
 """Handle WhatsApp webhook"""

 if request.method == 'GET':
 # Webhook verification
 verify_token = request.args.get('hub.verify_token')
 challenge = request.args.get('hub.challenge')

 if verify_token == "your_verify_token_123":
 return challenge
 else:
 return "Forbidden", 403

 elif request.method == 'POST':
 # Process incoming message
 webhook_data = request.get_json()

 # Initialize WhatsApp handler with your credentials
 whatsapp_handler = RealWhatsAppHandler(
 access_token="YOUR_ACCESS_TOKEN",
 phone_number_id="YOUR_PHONE_NUMBER_ID", 
 verify_token="your_verify_token_123"
 )

 # Process the message
 whatsapp_handler.process_incoming_message(webhook_data)

 return "OK", 200


@app.route('/api/send-test-message', methods=['POST'])
def send_test_message():
 """Send test message via WhatsApp API"""
 data = request.get_json()

 whatsapp_handler = RealWhatsAppHandler(
 access_token="YOUR_ACCESS_TOKEN",
 phone_number_id="YOUR_PHONE_NUMBER_ID",
 verify_token="your_verify_token_123"
 )

 result = whatsapp_handler.send_message(
 to_number=data["to_number"],
 message_text=data["message"]
 )

 return jsonify(result)
```