# 🔄 Database Migration Guide

## Model Changes Applied

### **1. Doctor Model Updates**
- Made `specialty` and `contact_info` nullable (blank=True, null=True)
- Already has `portal_type` field for GC/CP role assignment

### **2. Agreement Model Enhancements**
- Added `survey` ForeignKey to link agreements with surveys
- Added `amount` DecimalField to track agreement compensation

---

## 🚀 Running Migrations

### **Step 1: Generate Migration Files**
```bash
python manage.py makemigrations wtestapp
```

**Expected Output:**
```
Migrations for 'wtestapp':
  wtestapp/migrations/0XXX_auto.py
    - Alter field specialty on doctor
    - Alter field contact_info on doctor
    - Add field survey to agreement
    - Add field amount to agreement
```

### **Step 2: Review Migration File**
```bash
# View the generated migration
cat wtestapp/migrations/0XXX_auto.py
```

### **Step 3: Apply Migrations**
```bash
python manage.py migrate wtestapp
```

**Expected Output:**
```
Running migrations:
  Applying wtestapp.0XXX_auto... OK
```

### **Step 4: Verify Changes**
```bash
python manage.py shell
```
```python
from wtestapp.models import Doctor, Agreement

# Check Doctor fields
doctor = Doctor.objects.first()
print(f"Specialty required: {Doctor._meta.get_field('specialty').null}")  # Should be True
print(f"Contact Info required: {Doctor._meta.get_field('contact_info').null}")  # Should be True

# Check Agreement new fields
agreement = Agreement.objects.first()
if agreement:
    print(f"Survey: {agreement.survey}")
    print(f"Amount: {agreement.amount}")
```

---

## 🔧 Troubleshooting Migrations

### **Issue: Migration Conflicts**
```bash
# If you have unapplied migrations
python manage.py showmigrations wtestapp

# If conflicts exist, merge migrations
python manage.py makemigrations --merge wtestapp
```

### **Issue: Fake Migration Needed**
If models already match database:
```bash
python manage.py migrate wtestapp --fake
```

### **Issue: Start Fresh (Development Only)**
⚠️ **WARNING: This deletes all data!**
```bash
# Delete database
rm db.sqlite3

# Delete migration files (keep __init__.py)
rm wtestapp/migrations/0*.py

# Recreate everything
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

---

## 📊 Data Migration (Populate Existing Data)

If you have existing agreements without amount/survey:
```python
# Python shell
python manage.py shell

from wtestapp.models import Agreement
from decimal import Decimal

# Set default amount for existing agreements
for agreement in Agreement.objects.filter(amount=0):
    agreement.amount = Decimal('10000.00')
    agreement.save()
    print(f"Updated agreement for {agreement.doctor.user.username}")
```

---

## ✅ Verification Checklist

After migration:
- [ ] No errors in migration output
- [ ] `python manage.py check` returns no issues
- [ ] Doctor profile form loads without errors
- [ ] Agreement page displays correctly
- [ ] Existing data remains intact
- [ ] New agreements save successfully

---

## 🔙 Rollback (If Needed)

To revert to previous migration:
```bash
# List migrations
python manage.py showmigrations wtestapp

# Rollback to specific migration
python manage.py migrate wtestapp 0XXX_previous_migration

# Then delete the problematic migration file
rm wtestapp/migrations/0YYY_problematic.py
```

---

## 📝 Best Practices

1. **Always backup database before migrating**
   ```bash
   # SQLite
   cp db.sqlite3 db.sqlite3.backup
   
   # PostgreSQL
   pg_dump dbname > backup.sql
   ```

2. **Test migrations on development first**
   - Never run untested migrations on production
   - Use staging environment

3. **Keep migration files in version control**
   - Commit migration files to Git
   - Team members apply same migrations

4. **Review migration SQL (optional)**
   ```bash
   python manage.py sqlmigrate wtestapp 0XXX
   ```

---

## 🔐 Production Migration Steps

1. **Backup database**
2. **Put site in maintenance mode**
3. **Pull latest code**
4. **Activate virtual environment**
5. **Run migrations**
   ```bash
   python manage.py migrate --no-input
   ```
6. **Collect static files**
   ```bash
   python manage.py collectstatic --no-input
   ```
7. **Restart application server**
   ```bash
   # Gunicorn
   sudo systemctl restart gunicorn
   
   # uWSGI
   sudo systemctl restart uwsgi
   ```
8. **Remove maintenance mode**
9. **Test critical functionality**

---

**Safe migrations! 🛡️**
