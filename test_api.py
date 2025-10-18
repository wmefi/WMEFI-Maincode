"""
Test script to check API data
Run with: python test_api.py
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wtest.settings')
django.setup()

from wtestapp.models import Doctor, Survey, SurveyResponse

print("=" * 50)
print("TESTING DOCTOR DATA")
print("=" * 50)

# Check total doctors
total_doctors = Doctor.objects.count()
print(f"\nTotal Doctors: {total_doctors}")

# Check CP doctors
cp_doctors = Doctor.objects.filter(portal_type='CP').count()
print(f"CP Doctors: {cp_doctors}")

# Check GC doctors
gc_doctors = Doctor.objects.filter(portal_type='GC').count()
print(f"GC Doctors: {gc_doctors}")

# Check doctors with NULL portal_type
null_portal = Doctor.objects.filter(portal_type__isnull=True).count()
print(f"Doctors with NULL portal_type: {null_portal}")

# Check doctors with empty string portal_type
empty_portal = Doctor.objects.filter(portal_type='').count()
print(f"Doctors with empty portal_type: {empty_portal}")

print("\n" + "=" * 50)
print("SAMPLE CP DOCTORS (First 5)")
print("=" * 50)

cp_sample = Doctor.objects.filter(portal_type='CP')[:5]
for i, doc in enumerate(cp_sample, 1):
    # Check survey status
    total_surveys = Survey.objects.filter(assigned_to=doc).count()
    completed = SurveyResponse.objects.filter(doctor=doc, is_completed=True).count()
    in_progress = SurveyResponse.objects.filter(doctor=doc, is_completed=False).count()
    
    # Determine status
    if completed == total_surveys and total_surveys > 0:
        status = 'completed'
    elif in_progress > 0:
        status = 'in-progress'
    elif total_surveys > 0:
        status = 'pending'
    else:
        status = 'not-started'
    
    name = f"{doc.first_name} {doc.last_name}".strip() or doc.mobile or "Unknown"
    print(f"\n{i}. {name}")
    print(f"   Portal: {doc.portal_type}")
    print(f"   Status: {status}")
    print(f"   Total Surveys: {total_surveys}")
    print(f"   Completed: {completed}")
    print(f"   In Progress: {in_progress}")

print("\n" + "=" * 50)
print("STATUS BREAKDOWN FOR CP DOCTORS")
print("=" * 50)

cp_docs = Doctor.objects.filter(portal_type='CP')
status_counts = {'completed': 0, 'in-progress': 0, 'pending': 0, 'not-started': 0}

for doc in cp_docs:
    total_surveys = Survey.objects.filter(assigned_to=doc).count()
    completed = SurveyResponse.objects.filter(doctor=doc, is_completed=True).count()
    in_progress = SurveyResponse.objects.filter(doctor=doc, is_completed=False).count()
    
    if completed == total_surveys and total_surveys > 0:
        status_counts['completed'] += 1
    elif in_progress > 0:
        status_counts['in-progress'] += 1
    elif total_surveys > 0:
        status_counts['pending'] += 1
    else:
        status_counts['not-started'] += 1

print(f"\nCompleted: {status_counts['completed']}")
print(f"In Progress: {status_counts['in-progress']}")
print(f"Pending: {status_counts['pending']}")
print(f"Not Started: {status_counts['not-started']}")

print("\n" + "=" * 50)
print("STATUS BREAKDOWN FOR GC DOCTORS")
print("=" * 50)

gc_docs = Doctor.objects.filter(portal_type='GC')
status_counts_gc = {'completed': 0, 'in-progress': 0, 'pending': 0, 'not-started': 0}

for doc in gc_docs:
    total_surveys = Survey.objects.filter(assigned_to=doc).count()
    completed = SurveyResponse.objects.filter(doctor=doc, is_completed=True).count()
    in_progress = SurveyResponse.objects.filter(doctor=doc, is_completed=False).count()
    
    if completed == total_surveys and total_surveys > 0:
        status_counts_gc['completed'] += 1
    elif in_progress > 0:
        status_counts_gc['in-progress'] += 1
    elif total_surveys > 0:
        status_counts_gc['pending'] += 1
    else:
        status_counts_gc['not-started'] += 1

print(f"\nCompleted: {status_counts_gc['completed']}")
print(f"In Progress: {status_counts_gc['in-progress']}")
print(f"Pending: {status_counts_gc['pending']}")
print(f"Not Started: {status_counts_gc['not-started']}")
