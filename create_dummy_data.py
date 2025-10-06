"""
Quick script to create dummy survey data for testing
Run: python create_dummy_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wtest.settings')
django.setup()

from wtestapp.models import Survey, Question

# Create a test survey
survey, created = Survey.objects.get_or_create(
    title="Patient Health Assessment",
    defaults={
        'description': 'A comprehensive health screening survey for new patients',
        'portal_type': 'GC'  # For Genetic Counselor
    }
)

if created:
    print(f"✅ Created survey: {survey.title}")
    
    # Add questions
    questions_data = [
        {
            'question_text': 'What is your age?',
            'question_type': 'number',
            'options': None,
            'order': 1
        },
        {
            'question_text': 'What is your gender?',
            'question_type': 'radio',
            'options': ['Male', 'Female', 'Other'],
            'order': 2
        },
        {
            'question_text': 'Do you have any chronic diseases?',
            'question_type': 'yesno',
            'options': None,
            'order': 3
        },
        {
            'question_text': 'Select all symptoms you are experiencing:',
            'question_type': 'checkbox',
            'options': ['Fever', 'Cough', 'Fatigue', 'Headache', 'Body Pain', 'None'],
            'order': 4
        },
        {
            'question_text': 'How would you rate your overall health?',
            'question_type': 'rating',
            'options': None,
            'order': 5
        },
        {
            'question_text': 'Please provide any additional medical history:',
            'question_type': 'textarea',
            'options': None,
            'order': 6
        },
        {
            'question_text': 'What is your blood group?',
            'question_type': 'radio',
            'options': ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-', 'Unknown'],
            'order': 7
        },
        {
            'question_text': 'Your email address (for follow-up):',
            'question_type': 'email',
            'options': None,
            'order': 8
        },
        {
            'question_text': 'Emergency contact number:',
            'question_type': 'phone',
            'options': None,
            'order': 9
        },
    ]
    
    for q_data in questions_data:
        Question.objects.create(
            survey=survey,
            question_text=q_data['question_text'],
            question_type=q_data['question_type'],
            options=q_data['options'],
            order=q_data['order']
        )
        print(f"  ✓ Added: {q_data['question_text']}")
    
    print(f"\n🎉 Survey created with {len(questions_data)} questions!")
    print(f"\nNext steps:")
    print(f"1. Login to admin: http://127.0.0.1:8000/admin/")
    print(f"2. Go to Surveys → {survey.title}")
    print(f"3. Assign to doctors using 'assigned_to' field")
    print(f"\nOR login as doctor and the survey will auto-appear if portal_type matches!")
else:
    print(f"ℹ️ Survey '{survey.title}' already exists")
    print(f"Questions: {survey.questions.count()}")

# Create CP survey too
survey_cp, created_cp = Survey.objects.get_or_create(
    title="Clinical Practice Assessment",
    defaults={
        'description': 'Clinical evaluation survey for medical practitioners',
        'portal_type': 'CP'  # For Clinical Practitioner
    }
)

if created_cp:
    print(f"\n✅ Created CP survey: {survey_cp.title}")
    
    cp_questions = [
        {
            'question_text': 'Years of clinical experience?',
            'question_type': 'number',
            'options': None,
            'order': 1
        },
        {
            'question_text': 'Primary area of specialization:',
            'question_type': 'text',
            'options': None,
            'order': 2
        },
        {
            'question_text': 'Do you currently practice in a hospital setting?',
            'question_type': 'yesno',
            'options': None,
            'order': 3
        },
        {
            'question_text': 'Select procedures you perform regularly:',
            'question_type': 'checkbox',
            'options': ['Surgery', 'Consultation', 'Diagnosis', 'Emergency Care', 'Follow-up'],
            'order': 4
        },
    ]
    
    for q_data in cp_questions:
        Question.objects.create(
            survey=survey_cp,
            question_text=q_data['question_text'],
            question_type=q_data['question_type'],
            options=q_data['options'],
            order=q_data['order']
        )
    
    print(f"🎉 CP Survey created with {len(cp_questions)} questions!")

print("\n" + "="*50)
print("✅ DUMMY DATA SETUP COMPLETE!")
print("="*50)
print("\n📝 Testing Instructions:")
print("1. Go to: http://127.0.0.1:8000/login/")
print("2. Enter mobile: 9999999999")
print("3. Copy OTP from green alert box")
print("4. Verify OTP")
print("5. View role display page")
print("6. Complete profile")
print("7. Sign agreement")
print("8. Take survey!")
print("\n💡 TIP: Use /gc/ or /cp/ in URL to test different portals")
print("   - GC: http://127.0.0.1:8000/gc/login/")
print("   - CP: http://127.0.0.1:8000/cp/login/")
