# 📱 SMS Configuration Guide

## Overview
The platform supports multiple SMS providers for OTP delivery. Choose based on your region and requirements.

---

## 🔧 Provider Options

### **1. Debug Mode (Development)**
Shows OTP in console and Django messages. No real SMS sent.

**Configuration** (`settings.py`):
```python
SMS_PROVIDER = 'debug'
DEBUG = True
```

**Use Case**: Local development and testing

---

### **2. Twilio (International)**
Professional SMS service with global coverage.

#### **Setup Steps**

**A. Create Twilio Account**
1. Go to https://www.twilio.com/
2. Sign up for free trial ($15 credit)
3. Get phone number from console

**B. Get Credentials**
1. Dashboard → Account Info
2. Copy **Account SID**
3. Copy **Auth Token**
4. Note your **Twilio Phone Number**

**C. Configure Django** (`settings.py`):
```python
SMS_PROVIDER = 'twilio'
TWILIO_ACCOUNT_SID = 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
TWILIO_AUTH_TOKEN = 'your_auth_token_here'
TWILIO_FROM_NUMBER = '+15551234567'  # Your Twilio number
```

**D. Install Package**:
```bash
pip install twilio==9.2.4
```

#### **Testing**
```python
# Django shell
python manage.py shell

from wtestapp.views import _send_sms
_send_sms('9876543210', 'Test OTP: 123456')
# Check your phone for SMS
```

#### **Pricing**
- **US/Canada**: $0.0075 per SMS
- **India**: $0.0087 per SMS
- **Free Trial**: $15 credit (~1700 messages)

**Pros**: Reliable, global, excellent docs
**Cons**: Requires phone number verification, costs money

---

### **3. SSDWeb (India-Focused)**
Bulk SMS provider popular in India.

#### **Setup Steps**

**A. Create Account**
1. Go to https://sms.ssdweb.in/
2. Register → Complete KYC
3. Recharge account (minimum ₹500)
4. Get sender ID approved

**B. Get Credentials**
1. Login → API Settings
2. Copy **Auth Key**
3. Note your **Sender ID** (e.g., SMSDMO)

**C. Configure Django** (`settings.py`):
```python
SMS_PROVIDER = 'ssdweb'
SMS_SSDWEB_URL = 'https://api.ssdweb.in/api/v1/send'
SMS_SSDWEB_PARAMS = {
    'authkey': 'your_auth_key_here',
    'mobiles': '{mobile}',
    'message': '{message}',
    'sender': 'SMSDMO',  # Your approved sender ID
    'route': '4',  # 4 = Transactional
    'country': '91'  # India
}
```

**D. Test via cURL**:
```bash
curl "https://api.ssdweb.in/api/v1/send?authkey=YOUR_KEY&mobiles=9876543210&message=Test&sender=SMSDMO&route=4&country=91"
```

#### **Pricing**
- **Transactional SMS**: ₹0.15 - ₹0.25 per SMS
- **Promotional SMS**: ₹0.10 - ₹0.15 per SMS
- **DND Numbers**: Only transactional works

**Pros**: Cheap, India-specific, fast delivery
**Cons**: Requires KYC, sender ID approval takes 24-48 hrs

---

### **4. Custom Provider**
Configure any HTTP-based SMS API.

#### **Generic Configuration** (`settings.py`):
```python
SMS_PROVIDER = 'custom'
SMS_CUSTOM_URL = 'https://api.yourprovider.com/sms/send'
SMS_CUSTOM_METHOD = 'POST'  # or 'GET'
SMS_CUSTOM_PARAMS = {
    'api_key': 'your_api_key',
    'to': '{mobile}',
    'text': '{message}',
    'from': 'YourApp'
}
```

**Placeholders**:
- `{mobile}` → Replaced with recipient number
- `{message}` → Replaced with SMS text

#### **Example: MSG91**
```python
SMS_PROVIDER = 'custom'
SMS_CUSTOM_URL = 'https://api.msg91.com/api/v5/flow/'
SMS_CUSTOM_METHOD = 'POST'
SMS_CUSTOM_PARAMS = {
    'authkey': 'your_msg91_authkey',
    'mobile': '{mobile}',
    'message': '{message}',
    'sender': 'MSGDMO',
    'route': '4'
}
```

#### **Example: Fast2SMS**
```python
SMS_PROVIDER = 'custom'
SMS_CUSTOM_URL = 'https://www.fast2sms.com/dev/bulkV2'
SMS_CUSTOM_METHOD = 'GET'
SMS_CUSTOM_PARAMS = {
    'authorization': 'your_fast2sms_key',
    'route': 'v3',
    'sender_id': 'FSTSMS',
    'message': '{message}',
    'numbers': '{mobile}'
}
```

---

## 🧪 Testing Your Configuration

### **1. Test in Django Shell**
```python
python manage.py shell

from wtestapp.views import _send_sms
from django.conf import settings

print(f"Current provider: {settings.SMS_PROVIDER}")
result = _send_sms('9876543210', 'Test message from WTest Portal')
print(f"Send result: {result}")
```

### **2. Test via Login Flow**
1. Go to `/login/`
2. Enter test mobile number
3. Check:
   - SMS received on phone (production)
   - OTP shown in green message (debug mode)
   - Console logs for API response

### **3. Check Logs**
```python
# views.py already has debug prints
# Check console output for:
[DEBUG SMS] To: 9876543210 | Msg: Your login OTP is 123456
Twilio SMS sid=SMxxx...
SSDWeb SMS response: 200 {"status":"success"}
```

---

## 🔐 Security Best Practices

### **1. Use Environment Variables**
Never hardcode credentials in `settings.py`!

**Install python-decouple**:
```bash
pip install python-decouple
```

**Create `.env` file** (add to `.gitignore`):
```env
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_token_here
TWILIO_FROM_NUMBER=+15551234567
```

**Update `settings.py`**:
```python
from decouple import config

SMS_PROVIDER = config('SMS_PROVIDER', default='debug')
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_FROM_NUMBER = config('TWILIO_FROM_NUMBER', default='')
```

### **2. Rate Limiting**
Prevent OTP spam:
```python
# In views.py (already implemented in OTPVerification model)
if otp_obj.attempts > 5:
    messages.error(request, 'Too many attempts. Please try after 1 hour.')
    return redirect('login')
```

### **3. OTP Expiry**
OTPs expire in 30 seconds (already implemented):
```python
def is_expired(self):
    return (timezone.now() - self.created_at).seconds > 30
```

---

## 🌍 Country-Specific Notes

### **India**
- Use SSDWeb, MSG91, or Fast2SMS
- DND numbers: Only transactional route works
- Sender ID must be 6 chars (alpha)
- KYC required by TRAI regulations

### **USA/Canada**
- Twilio recommended
- Use long code or toll-free number
- No special registration needed

### **UK/Europe**
- Twilio or Vonage
- GDPR compliance required
- Alphanumeric sender IDs supported

### **Other Regions**
- Check Twilio's coverage: https://www.twilio.com/console/sms/coverage
- Local providers often cheaper

---

## 📊 Cost Comparison

| Provider | India | USA | Global | Setup Time |
|----------|-------|-----|--------|------------|
| Debug | Free | Free | Free | 1 min |
| Twilio | ₹0.65 | $0.0075 | Varies | 10 min |
| SSDWeb | ₹0.15 | N/A | N/A | 2 days (KYC) |
| MSG91 | ₹0.20 | $0.01 | Varies | 2 days (KYC) |

**Recommendation for India**: Start with Twilio for testing, move to SSDWeb for production (cheaper).

---

## 🛠️ Troubleshooting

### **SMS Not Delivered**

**Check 1: Provider Logs**
```python
# Enable verbose logging in views.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Check 2: Number Format**
```python
# views.py auto-formats India numbers
# Ensure format matches provider requirements
# India: +919876543210 or 919876543210
# USA: +15551234567
```

**Check 3: Balance**
- Twilio: Check dashboard for credit
- SSDWeb: Check wallet balance
- Most providers: Low balance = delivery failure

**Check 4: DND (India)**
- Number on DND list?
- Use transactional route (route=4)
- Get sender ID whitelisted

**Check 5: Sender ID Issues**
- Not approved yet (SSDWeb, MSG91)
- Wrong format (must be 6 chars alpha for India)
- Using default test sender ID

### **OTP Expires Too Fast**

Increase timeout in `models.py`:
```python
def is_expired(self):
    return (timezone.now() - self.created_at).seconds > 60  # 60 seconds instead of 30
```

### **Multiple OTPs Sent**

Already prevented by `get_or_create` in views. Check logs for duplicate requests.

---

## 📞 Provider Support

- **Twilio**: https://support.twilio.com/
- **SSDWeb**: support@ssdweb.in
- **MSG91**: support@msg91.com
- **Fast2SMS**: https://www.fast2sms.com/contact

---

## ✅ Configuration Checklist

Before going live:
- [ ] SMS provider configured correctly
- [ ] Credentials stored in environment variables
- [ ] `.env` file added to `.gitignore`
- [ ] Test OTP sent successfully
- [ ] OTP received on phone
- [ ] OTP expiry working (30 seconds)
- [ ] Rate limiting tested
- [ ] Provider balance sufficient
- [ ] Logs checked for errors
- [ ] Sender ID approved (if applicable)
- [ ] DND compliance verified (India)

---

**Happy Texting! 📲**
