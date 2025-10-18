"""
Quick fix to set portal_type for all doctors alternately
Run with: python quick_fix_portal.py
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wtest.settings')
django.setup()

from wtestapp.models import Doctor

print("Fixing portal types...")

# Get all doctors with NULL portal_type
doctors = Doctor.objects.filter(portal_type__isnull=True)

for i, doc in enumerate(doctors):
    # Alternate between CP and GC
    portal = 'CP' if i % 2 == 0 else 'GC'
    doc.portal_type = portal
    doc.save()
    name = f"{doc.first_name} {doc.last_name}".strip() or doc.mobile or "Unknown"
    print(f"  {i+1}. {name} -> {portal}")

print(f"\nDone! Updated {doctors.count()} doctors")

# Show final counts
cp_count = Doctor.objects.filter(portal_type='CP').count()
gc_count = Doctor.objects.filter(portal_type='GC').count()
print(f"\nCP Doctors: {cp_count}")
print(f"GC Doctors: {gc_count}")
