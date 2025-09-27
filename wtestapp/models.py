from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.json import JSONField
from django.utils import timezone
import random
import string

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
        return (timezone.now() - self.created_at).seconds > 300  # 5 minutes
    
    def __str__(self):
        return f"{self.phone_number} - {self.otp}"

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=15, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=120, blank=True)
    last_name = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    # Portal separation
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
    profession = models.CharField(max_length=80, blank=True)
    specialty = models.CharField(max_length=80, blank=False, null=False)
    contact_info = models.CharField(max_length=200, blank=False, null=False)
    degree = models.CharField(max_length=80, blank=True)
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
    # New: Prescription details
    prescription_name = models.CharField(max_length=150, blank=True)
    prescription_file = models.FileField(upload_to='documents/', blank=True, null=True)
    clinic_name = models.CharField(max_length=120, blank=True)
    qualification = models.CharField(max_length=120, blank=True)
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    has_gst = models.BooleanField(default=False)
    bank_account_name = models.CharField(max_length=120, blank=True, null=True)
    bank_name = models.CharField(max_length=120, blank=True, null=True)
    account_no = models.CharField(max_length=50, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    ifsc = models.CharField(max_length=20, blank=True, null=True)
    agreement_accepted = models.BooleanField(default=False)
    # Per-doctor compensation amount to display and print on Agreement (in INR)
    agreement_amount = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class Agreement(models.Model):
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE, related_name='signed_agreement')
    agreement_text = models.TextField()
    digital_signature = models.TextField(blank=True, null=True)  # Base64 encoded signature
    signature_type = models.CharField(max_length=20, choices=[('drawn', 'Drawn'), ('typed', 'Typed')], default='drawn')
    signed_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='agreements/', blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Agreement - {self.doctor.user.username} - {self.signed_at}"

class Survey(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ManyToManyField(Doctor, related_name='surveys', blank=True)
    # Portal separation for surveys
    PORTAL_CHOICES = (
        ("CP", "CP"),
        ("GC", "GC"),
    )
    portal_type = models.CharField(max_length=10, choices=PORTAL_CHOICES, blank=True, null=True)
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
    options = JSONField(blank=True, null=True)  # For radio/checkbox options
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
        return f"{self.doctor.user.username} - {self.survey.title}"

class Answer(models.Model):
    survey_response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='answers', null=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.survey_response.doctor.user.username} - {self.question.question_text}: {self.answer_text}"

# New model to explicitly track assignments (kept alongside Survey.assigned_to for backward compatibility)
class SurveyAssignment(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("doctor", "survey")

    def __str__(self):
        return f"{self.doctor.user.username} -> {self.survey.title}"
