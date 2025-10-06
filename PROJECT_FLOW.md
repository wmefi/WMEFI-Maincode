# 🏥 WTest Portal - Complete Flow Documentation

## 📋 Overview
Django-based medical survey platform with OTP authentication, role-based access (GC/CP), agreement management, and dynamic survey system.

---

## 🔐 1. LOGIN & OTP VERIFICATION FLOW

### **User Login Flow**
```
Mobile Number Input → OTP Generation → SMS Sent → OTP Verification → Role Assignment → Login Success
```

### **Implementation Details**

#### **Models** (`wtestapp/models.py`)
```python
class OTPVerification(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    
    def generate_otp(self):
        # Generates 6-digit OTP
        
    def is_expired(self):
        # Expires after 30 seconds

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=15, unique=True)
    portal_type = models.CharField(max_length=10, choices=[('CP','CP'),('GC','GC')])
    # ... other fields
```

#### **Views** (`wtestapp/views.py`)
- **`login(request)`**: Accepts mobile number, generates OTP, sends SMS
- **`verify_otp(request)`**: Verifies OTP, creates/updates Doctor, assigns role
- **`doctor_role_display(request)`**: Shows assigned role (GC/CP) after login

#### **SMS Providers Supported**
Configure in `settings.py`:
```python
SMS_PROVIDER = 'twilio'  # or 'ssdweb', 'custom', 'debug'

# Twilio Config
TWILIO_ACCOUNT_SID = 'your_sid'
TWILIO_AUTH_TOKEN = 'your_token'
TWILIO_FROM_NUMBER = '+1234567890'

# SSDWeb Config
SMS_SSDWEB_URL = 'https://sms.ssdweb.in/user/#send_sms'
SMS_SSDWEB_PARAMS = {
    'authkey': 'your_key',
    'mobile': '{mobile}',
    'message': '{message}',
    'sender': 'SENDER_ID'
}
```

### **URLs**
```python
path('login/', views.login, name='login'),
path('verify-otp/', views.verify_otp, name='verify_otp'),
path('doctor_role/', views.doctor_role_display, name='doctor_role_display'),
```

### **Templates**
- `login.html` - Mobile number input with OTP request
- `otp.html` - OTP verification with 30s countdown timer
- `doctor_role_display.html` - Role assignment display (GC/CP)

---

## 👤 2. DOCTOR PROFILE FLOW

### **Profile Completion Flow**
```
Login → Check Profile → Complete/Edit Profile → Save → Redirect to Agreement
```

### **Required Fields**
```python
# Mandatory for profile completion
- first_name, last_name
- email, mobile
- address, state, city, pincode
- specialty, degree
- mci_registration, pan
- bank details (account_name, bank_name, account_no, ifsc)
- documents (pan_copy, prescription_file)
```

### **Views**
- **`doctor_profile(request)`**: Gateway - checks completion → agreement → surveys
- **`doctor_profile_edit(request)`**: Form to edit/create profile
- **`doctor_profile_view(request)`**: Read-only profile display

### **Features**
✅ Auto-populated state/city dropdown (India)
✅ GST optional with conditional field
✅ File uploads for PAN & prescription
✅ Profession auto-set to "Dr."
✅ Mobile auto-filled from login

---

## 📝 3. AGREEMENT PAGE FLOW

### **Agreement Flow**
```
Profile Complete → Agreement Page → Sign (Digital/Typed) → Accept → Download PDF → Surveys
```

### **Models**
```python
class Agreement(models.Model):
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE)
    agreement_text = models.TextField()
    digital_signature = models.TextField()  # Base64 or typed
    signature_type = models.CharField(choices=[('drawn','Drawn'),('typed','Typed')])
    signed_at = models.DateTimeField(auto_now_add=True)
    survey = models.ForeignKey(Survey, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
```

### **Views**
- **`agreement_page(request)`**: Display agreement with signature pad
- **`accept_agreement(request)`**: Save signature & mark accepted
- **`download_agreement_pdf(request)`**: Generate PDF with signature

### **Features**
✅ Canvas-based signature drawing
✅ Typed signature option
✅ Auto-populated doctor details
✅ Fixed agreement amount per doctor (rotating: 10k, 20k, 25k, 30k)
✅ PDF generation with `xhtml2pdf`
✅ Client-side date capture

### **Template**
`agreement_page.html` - Interactive signature canvas with:
- Draw signature with mouse/touch
- Type signature option
- Clear button
- Agreement text preview
- Auto-date formatting

---

## 📊 4. SURVEY SYSTEM FLOW

### **Survey Flow**
```
Surveys List → Select Survey → Answer Questions → Save Draft/Submit → Download PDF
```

### **Models**
```python
class Survey(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to = models.ManyToManyField(Doctor)
    portal_type = models.CharField(choices=[('CP','CP'),('GC','GC')])

class Question(models.Model):
    survey = models.ForeignKey(Survey)
    question_text = models.CharField(max_length=500)
    question_type = models.CharField(choices=[
        ('text','Text'), ('textarea','Long Text'),
        ('radio','MCQ'), ('checkbox','Multiple Choice'),
        ('yesno','Yes/No'), ('rating','Rating'),
        ('number','Number'), ('email','Email'), ('phone','Phone')
    ])
    options = JSONField()  # For MCQ/checkbox
    order = models.PositiveIntegerField()

class SurveyResponse(models.Model):
    doctor = models.ForeignKey(Doctor)
    survey = models.ForeignKey(Survey)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True)

class Answer(models.Model):
    survey_response = models.ForeignKey(SurveyResponse)
    question = models.ForeignKey(Question)
    answer_text = models.TextField()
```

### **Views**
- **`doctor_surveys_list(request)`**: List assigned surveys with status
- **`survey_detail(request, survey_id)`**: Display questions, save answers
- **`survey_done(request)`**: Completion confirmation
- **`download_survey_pdf(request, survey_id)`**: Generate response PDF

### **Dynamic Question Types**
| Type | Description | Example |
|------|-------------|---------|
| `text` | Short text input | Name, email |
| `textarea` | Long text area | Comments |
| `radio` | Single choice MCQ | Gender selection |
| `checkbox` | Multiple choice | Select symptoms |
| `yesno` | Yes/No radio | Consent |
| `rating` | Scale 1-5 | Satisfaction |
| `number` | Numeric input | Age, dosage |
| `email` | Email validation | Contact email |
| `phone` | 10-digit phone | Mobile number |

### **Survey Upload**
Upload surveys via JSON or Excel:

**JSON Format:**
```json
{
  "title": "Clinical Assessment",
  "description": "Patient evaluation survey",
  "questions": [
    {
      "question_text": "Patient symptoms?",
      "question_type": "checkbox",
      "options": ["Fever", "Cough", "Fatigue"]
    }
  ]
}
```

**Excel Format:**
- Row 1: Survey title (B1)
- Row 2: Description (B2)
- Row 5+: Questions (B=text, C=type, D=options)

### **PDF Generation**
- Template: `survey_pdf_template.html`
- Uses `xhtml2pdf` for rendering
- Includes doctor details, questions, answers
- Downloadable after completion

---

## 🎨 5. UI/UX DESIGN

### **Color Scheme**
```css
--teal: #64c5cb
--purple: #c0769e
--pink: #e664a2
--bg: #fdeef4
--card: #ffffff
```

### **Design Features**
✅ Modern gradient backgrounds
✅ Card-based layouts with shadows
✅ Responsive mobile-first design
✅ Custom checkbox/radio indicators
✅ Progress step indicators
✅ Success animations
✅ Font Awesome icons

### **Templates Structure**
```
base.html (extends all pages)
├── login.html
├── otp.html
├── doctor_role_display.html
├── doctor_profile.html
├── doctor_profile_view.html
├── agreement_page.html
├── doctor_surveys.html
├── survey_detail.html
└── survey_done.html
```

---

## 🔄 6. COMPLETE USER JOURNEY

### **First-Time User**
1. **Login**: Enter mobile → Receive OTP → Verify
2. **Role Display**: See assigned role (GC/CP)
3. **Profile**: Complete all mandatory fields → Upload documents
4. **Agreement**: Read agreement → Sign (draw/type) → Accept
5. **Surveys**: View assigned surveys → Complete → Download PDF

### **Returning User**
1. **Login**: Enter mobile → OTP → Verify
2. **Dashboard**: View profile or surveys
3. **Surveys**: Continue saved drafts or view completed

---

## ⚙️ 7. ADMIN FEATURES

### **Admin Dashboard** (`/admin-dashboard/`)
- View all doctors, surveys, agreements
- Filter by portal (CP/GC)
- Monitor survey responses
- Track completion rates

### **Django Admin**
Access via `/admin/` for full control:
- Create/Edit surveys
- Assign surveys to doctors
- Manage questions
- View responses
- Export data

---

## 🔧 8. CONFIGURATION

### **Required Settings**
```python
# settings.py
INSTALLED_APPS = [
    'wtestapp',
    'crispy_forms',
    'crispy_bootstrap5',
]

# SMS Provider
SMS_PROVIDER = 'debug'  # 'twilio', 'ssdweb', 'custom'

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

### **Dependencies** (`requirements.txt`)
```
Django==5.2.6
xhtml2pdf==0.2.16
reportlab==4.2.2
Pillow==10.4.0
pandas==2.2.3
openpyxl==3.1.5
twilio==9.2.4
requests==2.32.3
django-crispy-forms==2.3
crispy-bootstrap5==2024.2
```

---

## 🚀 9. DEPLOYMENT CHECKLIST

### **Before Production**
- [ ] Set `DEBUG = False` in settings
- [ ] Configure proper SMS provider (Twilio/SSDWeb)
- [ ] Set strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Setup PostgreSQL/MySQL database
- [ ] Run migrations: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Setup SSL/HTTPS
- [ ] Configure CORS if needed
- [ ] Setup backup system

### **Running Locally**
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

---

## 📱 10. API ENDPOINTS

### **OTP APIs** (JSON)
```
POST /api/otp/send/
Body: {"mobile": "9876543210"}
Response: {"ok": true, "sent": true, "debug_otp": "123456"}

POST /api/otp/verify/
Body: {"mobile": "9876543210", "otp": "123456"}
Response: {"ok": true, "next_url": "/doctor_profile/"}
```

### **Doctor Status API**
```
GET /doctor_status/
Response: {
  "exists": true,
  "profile_complete": true,
  "agreement_accepted": true
}
```

---

## 🐛 11. TROUBLESHOOTING

### **OTP Not Received**
- Check SMS provider configuration
- Verify mobile number format (+91 for India)
- Check SMS provider logs
- In DEBUG mode, OTP shown in messages

### **PDF Not Generating**
- Ensure `STATIC_ROOT` is set
- Run `collectstatic` command
- Check file permissions for media folder
- Verify `reportlab` and `xhtml2pdf` installed

### **Survey Questions Not Showing**
- Check question order field
- Verify survey assigned to doctor
- Check portal_type filter
- Verify JSON structure in upload

---

## 📞 12. SUPPORT

For issues or questions:
- **Email**: connect@wmefi.co.in
- **Check logs**: Debug messages in console
- **Database**: Use Django shell for queries

---

## ✅ IMPLEMENTATION STATUS

| Feature | Status | Notes |
|---------|--------|-------|
| Login/OTP | ✅ Complete | Twilio, SSDWeb, Custom SMS |
| Role Assignment | ✅ Complete | GC/CP portal types |
| Doctor Profile | ✅ Complete | Full form with validations |
| Agreement | ✅ Complete | Digital signature + PDF |
| Dynamic Surveys | ✅ Complete | 9 question types supported |
| Survey PDF | ✅ Complete | Professional template |
| Admin Dashboard | ✅ Complete | Portal filtering |
| Mobile Responsive | ✅ Complete | Bootstrap 4 |

---

**Version**: 1.0
**Last Updated**: October 2025
**Framework**: Django 5.2.6
**License**: Proprietary
