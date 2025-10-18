"""
Fix script to set portal_type for all doctors
Run with: python fix_portal_types.py
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wtest.settings')
django.setup()

from wtestapp.models import Doctor

print("=" * 50)
print("FIXING PORTAL TYPES")
print("=" * 50)

# Get all doctors with NULL portal_type
doctors_with_null = Doctor.objects.filter(portal_type__isnull=True)
print(f"\nFound {doctors_with_null.count()} doctors with NULL portal_type")

if doctors_with_null.count() == 0:
    print("No doctors to fix!")
    exit()

print("\nOptions:")
print("1. Set all to CP")
print("2. Set all to GC")
print("3. Set alternately (1st=CP, 2nd=GC, 3rd=CP, etc.)")
print("4. Set manually")

choice = input("\nEnter your choice (1-4): ").strip()

if choice == '1':
    count = doctors_with_null.update(portal_type='CP')
    print(f"\n✓ Updated {count} doctors to CP")
    
elif choice == '2':
    count = doctors_with_null.update(portal_type='GC')
    print(f"\n✓ Updated {count} doctors to GC")
    
elif choice == '3':
    for i, doc in enumerate(doctors_with_null):
        portal = 'CP' if i % 2 == 0 else 'GC'
        doc.portal_type = portal
        doc.save()
        name = f"{doc.first_name} {doc.last_name}".strip() or doc.mobile or "Unknown"
        print(f"  {i+1}. {name} → {portal}")
    print(f"\n✓ Updated {doctors_with_null.count()} doctors")
    
elif choice == '4':
    for i, doc in enumerate(doctors_with_null):
        name = f"{doc.first_name} {doc.last_name}".strip() or doc.mobile or "Unknown"
        print(f"\n{i+1}. {name}")
        print(f"   Mobile: {doc.mobile}")
        print(f"   Email: {doc.email}")
        portal = input("   Set portal_type to (CP/GC): ").strip().upper()
        if portal in ['CP', 'GC']:
            doc.portal_type = portal
            doc.save()
            print(f"   ✓ Set to {portal}")
        else:
            print(f"   ✗ Skipped (invalid input)")
    print(f"\n✓ Done!")
    
else:
    print("Invalid choice!")
    exit()

# Show final counts
print("\n" + "=" * 50)
print("FINAL COUNTS")
print("=" * 50)
cp_count = Doctor.objects.filter(portal_type='CP').count()
gc_count = Doctor.objects.filter(portal_type='GC').count()
null_count = Doctor.objects.filter(portal_type__isnull=True).count()

print(f"\nCP Doctors: {cp_count}")
print(f"GC Doctors: {gc_count}")
print(f"NULL portal_type: {null_count}")
print(f"Total: {Doctor.objects.count()}")
