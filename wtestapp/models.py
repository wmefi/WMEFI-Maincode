from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.json import JSONField
from django.utils import timezone
import random
import string
import requests
import json

class CustomUser(models.Model):
    username = models.CharField(max_length=15, unique=True, default='')
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, unique=True)
    role = models.CharField(max_length=10, choices=[('gc','GC'),('cp','CP')], null=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def generate_otp(self):
        self.otp = ''.join(random.choices(string.digits, k=6))
        self.otp_created_at = timezone.now()
        self.save()
        return self.otp
    
    def send_otp_sms(self):
        otp = self.generate_otp()
        message = f"Your OTP for login is: {otp}. Valid for 5 minutes."
        
        try:
            api_url = "https://sms.ssdweb.in/api/send_sms"
            payload = {
                "mobile": self.mobile,
                "message": message,
            }
            return True
        except Exception as e:
            print(f"SMS sending failed: {str(e)}")
            return False
    
    def verify_otp(self, entered_otp):
        if self.otp == entered_otp and not self.is_expired():
            self.is_verified = True
            self.save()
            return True
        return False
    
    def is_expired(self):
        if not self.otp_created_at:
            return True
        return (timezone.now() - self.otp_created_at).seconds > 300
    
    def __str__(self):
        return f"{self.name} ({self.mobile})"

class OTPVerification(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    
    def generate_otp(self):
        self.otp = ''.join(random.choices(string.digits, k=6))
        self.save()
        return self.otp
    
    def is_expired(self):
        return (timezone.now() - self.created_at).seconds > 300
    
    def __str__(self):
        return f"{self.phone_number} - {self.otp}"

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    custom_user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='doctor_profile')
    mobile = models.CharField(max_length=15, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=120, blank=True)
    last_name = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    PORTAL_CHOICES = (
        ("CP", "CP"),
        ("GC", "GC"),
    )
    portal_type = models.CharField(max_length=10, choices=PORTAL_CHOICES, blank=True, null=True)
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True)
    state = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profession = models.CharField(max_length=80, blank=True)
    specialty = models.CharField(max_length=80, blank=True, null=True)
    contact_info = models.CharField(max_length=200, blank=True, null=True)
    degree = models.CharField(max_length=80, blank=True)
    medical_degree = models.CharField(max_length=80, blank=True)
    experience = models.IntegerField(blank=True, null=True)
    registration_number = models.CharField(max_length=80, blank=True)
    diploma = models.CharField(max_length=80, blank=True)
    pg_degree = models.CharField(max_length=80, blank=True)
    diplomate = models.CharField(max_length=80, blank=True)
    superspeciality = models.CharField(max_length=80, blank=True)
    mci_registration = models.CharField(max_length=80, blank=True)
    pan = models.CharField(max_length=20, blank=True)
    pan_copy = models.FileField(upload_to='documents/', blank=True, null=True)
    cancelled_cheque = models.FileField(upload_to='documents/', blank=True, null=True)
    visiting_card = models.FileField(upload_to='documents/', blank=True, null=True)
    optional_document = models.FileField(upload_to='documents/', blank=True, null=True)
    prescription_name = models.CharField(max_length=150, blank=True)
    prescription_file = models.FileField(upload_to='documents/', blank=True, null=True)
    clinic_name = models.CharField(max_length=120, blank=True)
    qualification = models.CharField(max_length=120, blank=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    has_gst = models.BooleanField(default=False)
    gst_certificate = models.FileField(upload_to='documents/', blank=True, null=True)
    bank_account_name = models.CharField(max_length=120, blank=True, null=True)
    bank_name = models.CharField(max_length=120, blank=True, null=True)
    account_no = models.CharField(max_length=50, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    ifsc = models.CharField(max_length=20, blank=True, null=True)
    agreement_accepted = models.BooleanField(default=False)
    agreement_amount = models.PositiveIntegerField(blank=True, null=True)
    
    # Manager/Territory fields from Excel
    territory = models.CharField(max_length=200, blank=True, null=True, help_text="Territory/Location")
    emp1_name = models.CharField(max_length=150, blank=True, null=True, help_text="Manager 1 Name (ZSM/BDM/ZM)")
    emp1_mobile = models.CharField(max_length=15, blank=True, null=True, help_text="Manager 1 Mobile")
    emp2_name = models.CharField(max_length=150, blank=True, null=True, help_text="Manager 2 Name")
    emp2_mobile = models.CharField(max_length=15, blank=True, null=True, help_text="Manager 2 Mobile")
    designation = models.CharField(max_length=50, blank=True, null=True, help_text="Designation (ZSM/BDM/ZM/etc)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user and hasattr(self.user, 'username') and self.user.username:
            return self.user.username
        elif self.custom_user:
            return f"{self.custom_user.name or self.custom_user.username or self.custom_user.mobile}"
        elif self.first_name or self.last_name:
            return f"Dr. {self.first_name} {self.last_name}".strip()
        elif self.mobile:
            return self.mobile
        return f"Doctor #{self.id}"

class Agreement(models.Model):
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE, related_name='signed_agreement')
    agreement_text = models.TextField(blank=True, null=True, help_text='Optional - Leave blank to use default agreement template')
    digital_signature = models.TextField(blank=True, null=True)
    signature_type = models.CharField(max_length=20, choices=[('drawn', 'Drawn'), ('typed', 'Typed')], default='drawn')
    signed_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='agreements/', blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    survey = models.ForeignKey('Survey', on_delete=models.SET_NULL, null=True, blank=True, related_name='agreements')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        doctor_name = str(self.doctor) if self.doctor else "Unknown"
        return f"Agreement - {doctor_name} - {self.signed_at.strftime('%Y-%m-%d')}"

class Survey(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    survey_json = models.FileField(upload_to='surveys/', blank=True, null=True, help_text='Upload JSON file for survey questions')
    assigned_to = models.ManyToManyField(Doctor, related_name='surveys', blank=True)
    PORTAL_CHOICES = (
        ("CP", "CP"),
        ("GC", "GC"),
    )
    portal_type = models.CharField(max_length=10, choices=PORTAL_CHOICES, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Default amount for this survey')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPES = (
        ('text', 'Text Input'),
        ('textarea', 'Long Text'),
        ('radio', 'Multiple Choice (Single)'),
        ('checkbox', 'Multiple Choice (Multiple)'),
        ('yesno', 'Yes/No'),
        ('rating', 'Rating Scale'),
        ('number', 'Number Input'),
        ('email', 'Email'),
        ('phone', 'Phone Number'),
    )
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=15, choices=QUESTION_TYPES, default='text')
    options = JSONField(blank=True, null=True)
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    help_text = models.CharField(max_length=200, blank=True, null=True)
    
    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question_text

class SurveyResponse(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='survey_responses')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    pdf_file = models.FileField(upload_to='survey_responses/', blank=True, null=True)
    
    class Meta:
        unique_together = ['doctor', 'survey']
    
    def __str__(self):
        doctor_label = str(self.doctor) if self.doctor else "Unknown Doctor"
        survey_label = self.survey.title if self.survey else "Unknown Survey"
        return f"{doctor_label} - {survey_label}"

class Answer(models.Model):
    survey_response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='answers', null=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        doctor_label = "Unknown"
        if self.survey_response and self.survey_response.doctor:
            doctor_label = str(self.survey_response.doctor)
        question_text = self.question.question_text if self.question else "Unknown Question"
        answer_preview = (self.answer_text[:30] + '...') if self.answer_text and len(self.answer_text) > 30 else (self.answer_text or 'No answer')
        return f"{doctor_label} - {question_text}: {answer_preview}"

class SurveyAssignment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("doctor", "survey")

    def __str__(self):
        doctor_label = str(self.doctor) if self.doctor else "Unknown Doctor"
        survey_label = self.survey.title if self.survey else "Unknown Survey"
        return f"{doctor_label} -> {survey_label}"

class DoctorExcelUpload(models.Model):
    excel_file = models.FileField(upload_to="uploads/excel/")
    survey_json = models.FileField(upload_to="uploads/surveys/", blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        import os
        filename = os.path.basename(self.excel_file.name)
        return f"ID {self.id}: {filename}"