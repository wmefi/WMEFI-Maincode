# 🚀 Quick Start Guide - WTest Portal

## ⚡ 5-Minute Setup

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Run Database Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

### **3. Create Superuser (Admin)**
```bash
python manage.py createsuperuser
# Enter username, email, password when prompted
```

### **4. Configure SMS (Optional for Testing)**
In `wtest/settings.py`, add:
```python
# For testing (shows OTP in console/messages)
SMS_PROVIDER = 'debug'
DEBUG = True
```

For production, configure Twilio or SSDWeb:
```python
# Twilio
SMS_PROVIDER = 'twilio'
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_FROM_NUMBER = '+1234567890'

# OR SSDWeb
SMS_PROVIDER = 'ssdweb'
SMS_SSDWEB_URL = 'https://sms.ssdweb.in/user/#send_sms'
SMS_SSDWEB_PARAMS = {
    'authkey': 'your_auth_key',
    'mobile': '{mobile}',
    'message': '{message}',
    'sender': 'YOURID'
}
```

### **5. Run Server**
```bash
python manage.py runserver
```

Visit: **http://localhost:8000**

---

## 👥 Testing the Flow

### **Test User Login**
1. Go to `http://localhost:8000/login/`
2. Enter mobile: `9876543210` (any 10-digit number)
3. In DEBUG mode, OTP will show in green message
4. Enter OTP on verification page
5. Complete profile → Sign agreement → Take surveys

### **Admin Access**
1. Go to `http://localhost:8000/admin/`
2. Login with superuser credentials
3. Create surveys, assign to doctors
4. View responses and agreements

---

## 📊 Creating Your First Survey

### **Method 1: Django Admin**
1. Login to `/admin/`
2. Go to **Surveys** → **Add Survey**
3. Enter title, description
4. Add **Questions**:
   - Question text
   - Type (radio, checkbox, text, etc.)
   - Options (JSON format for MCQ)
   - Order
5. **Assign to Doctors** via ManyToMany field

### **Method 2: Upload JSON**
1. Login as doctor
2. Go to `/survey/upload/`
3. Upload JSON file:
```json
{
  "title": "Patient Screening Survey",
  "description": "Initial patient assessment",
  "questions": [
    {
      "question_text": "Patient Age Group?",
      "question_type": "radio",
      "options": ["0-18", "19-40", "41-60", "60+"]
    },
    {
      "question_text": "Symptoms (select all)?",
      "question_type": "checkbox",
      "options": ["Fever", "Cough", "Fatigue", "Headache"]
    },
    {
      "question_text": "Additional Notes",
      "question_type": "textarea"
    }
  ]
}
```

### **Method 3: Upload Excel**
1. Create Excel file with format:
   - **B1**: Survey Title
   - **B2**: Description
   - **Row 5+**: Questions
     - Column B: Question Text
     - Column C: Question Type (radio, checkbox, text, etc.)
     - Column D: Options (comma-separated)

Example:
```
A    | B                          | C         | D
-----|----------------------------|-----------|-------------------
1    | Survey Title               | Clinical  |
2    | Description                | Patient   |
3    |                            |           |
4    | Headers                    |           |
5    | Q1                         | What is your age? | number |
6    | Q2                         | Gender?   | radio | Male,Female,Other
7    | Q3                         | Symptoms? | checkbox | Fever,Cough,Fatigue
```

---

## 🔑 Portal Types (GC/CP)

### **Assigning Roles**
Doctors are assigned portal types (GC/CP) automatically based on URL:
- Access via `/gc/` → Portal Type = GC
- Access via `/cp/` → Portal Type = CP

Alternatively, set manually in Django Admin:
1. Go to `/admin/wtestapp/doctor/`
2. Edit doctor
3. Set **Portal Type** to GC or CP

### **Filtering by Portal**
Surveys automatically filter by doctor's portal type. To assign surveys to specific portals:
1. Edit survey in admin
2. Set **Portal Type** field
3. Only doctors with matching portal see that survey

---

## 📝 Common Tasks

### **View All Doctors**
```bash
python manage.py shell
>>> from wtestapp.models import Doctor
>>> for d in Doctor.objects.all():
...     print(f"{d.user.username} - {d.mobile} - {d.portal_type}")
```

### **Assign Survey to Doctor**
```bash
python manage.py shell
>>> from wtestapp.models import Doctor, Survey
>>> doctor = Doctor.objects.get(mobile='9876543210')
>>> survey = Survey.objects.get(title='Patient Survey')
>>> survey.assigned_to.add(doctor)
>>> survey.save()
```

### **Reset OTP**
```bash
python manage.py shell
>>> from wtestapp.models import OTPVerification
>>> otp = OTPVerification.objects.get(phone_number='9876543210')
>>> otp.generate_otp()  # Returns new OTP
```

### **Check Survey Responses**
```bash
python manage.py shell
>>> from wtestapp.models import SurveyResponse
>>> responses = SurveyResponse.objects.filter(is_completed=True)
>>> for r in responses:
...     print(f"{r.doctor.user.username} - {r.survey.title} - {r.completed_at}")
```

---

## 🎯 Testing Checklist

- [ ] Login with mobile number works
- [ ] OTP received (or shown in DEBUG)
- [ ] Role display page shows after login
- [ ] Profile form validates all required fields
- [ ] State/city dropdowns populate
- [ ] File uploads work (PAN, prescription)
- [ ] Agreement signature (draw/type) works
- [ ] Agreement PDF downloads
- [ ] Surveys list shows assigned surveys
- [ ] Questions render correctly (all types)
- [ ] Save draft works
- [ ] Submit survey marks as complete
- [ ] Survey PDF downloads after completion
- [ ] Admin dashboard accessible
- [ ] Portal filtering (GC/CP) works

---

## 🐛 Common Issues & Fixes

### **Issue**: "No such table: wtestapp_doctor"
**Fix**: Run migrations
```bash
python manage.py makemigrations wtestapp
python manage.py migrate
```

### **Issue**: Static files not loading
**Fix**: Collect static files
```bash
python manage.py collectstatic --noinput
```

### **Issue**: PDF download fails
**Fix**: Check media directory permissions
```bash
# Linux/Mac
chmod -R 755 media/

# Windows
# Ensure media folder exists and is writable
```

### **Issue**: OTP not expiring
**Fix**: Check timezone settings
```python
# settings.py
USE_TZ = True
TIME_ZONE = 'Asia/Kolkata'
```

### **Issue**: Survey questions not showing
**Fix**: Check question order and survey assignment
```bash
python manage.py shell
>>> from wtestapp.models import Survey, Question
>>> survey = Survey.objects.get(id=1)
>>> survey.questions.all()  # Should show questions
>>> survey.assigned_to.all()  # Should show assigned doctors
```

---

## 📦 Production Deployment

### **Heroku**
```bash
# Install Heroku CLI
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### **AWS/DigitalOcean**
1. Setup Ubuntu server
2. Install Python, PostgreSQL, Nginx
3. Clone repository
4. Install dependencies in virtual environment
5. Configure Gunicorn
6. Setup Nginx reverse proxy
7. Enable SSL with Let's Encrypt

### **Docker**
```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "wtest.wsgi:application", "--bind", "0.0.0.0:8000"]
```

```bash
docker build -t wtest-portal .
docker run -p 8000:8000 wtest-portal
```

---

## 📞 Support & Resources

- **Documentation**: See `PROJECT_FLOW.md` for detailed flow
- **Django Docs**: https://docs.djangoproject.com/
- **Issue Tracker**: Contact admin
- **Email**: connect@wmefi.co.in

---

**Happy Coding! 🎉**
