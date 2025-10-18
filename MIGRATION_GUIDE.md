# Migration Guide - Per-Survey Agreement Implementation

## ✅ All Changes Complete!

### Files Changed:
1. ✅ `wtestapp/models.py` - Agreement model
2. ✅ `wtestapp/admin.py` - Upload logic (2 places)
3. ✅ `wtestapp/views.py` - Agreement checks (3 functions)
4. ✅ `wtestapp/context_processors.py` - Profile complete check
5. ✅ `wtestapp/templates/wtestapp/doctor_surveys.html` - UI update
6. ✅ `wtestapp/templates/wtestapp/doctor_profile_view.html` - Badge added
7. ✅ Migration created and applied

---

## How It Works Now:

### Flow 1: Existing Doctor + New Survey

**Current State**:
- Doctor: VIKAS (9769890961)
- Survey 1: "Perception mapping..." (completed, agreement signed)

**Admin Action**:
```
1. Upload NEW Excel + NEW JSON
2. Survey Name: "Pediatric Care Survey"
```

**What Happens**:
```
Database:
  Survey created: ID=2, title="Pediatric Care Survey"
  Agreement created: (doctor=VIKAS, survey=2, unsigned)
  Assignment created: VIKAS → Survey 2
```

**Doctor Login**:
```
1. Login
2. Profile complete ✅ → Skip profile page
3. Check agreements:
   - Survey 1: Agreement signed ✅ → Skip
   - Survey 2: Agreement NOT signed ❌ → Redirect to /agreement/2/
4. Agreement page opens for Survey 2
5. Doctor signs
6. Agreement saved (doctor=VIKAS, survey=2, signed)
7. Redirect to "My Surveys"
```

**My Surveys Page Shows**:
```
🆕 New Surveys [1]
  📋 Pediatric Care Survey ← NEW!
  ⚠️ Action Required
  [▶️ Start Survey]

✅ Completed Surveys
  📄 Perception mapping of Indian Physicians... ← OLD!
  ✓ Completed
  [👁️ View]
```

---

## Important: Survey Title "(8)" Issue

The survey title showing "...ALL (8)" is from your database. This happens when:

### Reason 1: Survey Title in Excel
```
Excel column "Survey Name": "Perception mapping... ALL (8)"
                                                       ↑↑↑ Part of title
```

### Reason 2: Auto-Generated
When same survey uploaded multiple times, it adds number:
```
1st upload: "Perception mapping..."
2nd upload: "Perception mapping... (2)"
...
8th upload: "Perception mapping... (8)"  ← This is what you see
```

### Solution:
Either:
1. **Clean survey titles in Excel** - Remove "(8)" from Excel before upload
2. **Or manually edit** - Django Admin → Surveys → Edit title

---

## Testing Checklist:

### ✅ Test 1: Profile Navbar
- [ ] Login as existing doctor (profile complete)
- [ ] Navbar shows "Profile" (NOT "Complete Profile")
- [ ] Login as new doctor (profile incomplete)
- [ ] Navbar shows "Complete Profile"

### ✅ Test 2: Multiple Agreements
- [ ] Doctor has 1 signed agreement for Survey 1
- [ ] Admin uploads NEW survey (Survey 2)
- [ ] Doctor login → Redirects to /agreement/2/
- [ ] Sign agreement
- [ ] Check database: 2 agreement records exist

### ✅ Test 3: Survey Ordering
- [ ] "My Surveys" page
- [ ] New surveys show at TOP
- [ ] Completed surveys show at BOTTOM
- [ ] Badge shows count

### ✅ Test 4: Agreement Per Survey
- [ ] Go to /agreement/1/ → Shows "Already Signed" (old survey)
- [ ] Go to /agreement/2/ → Shows sign form (new survey)
- [ ] After signing → Can access Survey 2

---

## Database Check:

Run this to verify:
```python
python test_api.py
```

Then check:
```python
from wtestapp.models import Agreement, Survey

# Check surveys
surveys = Survey.objects.all().order_by('-created_at')
for s in surveys:
    print(f"Survey {s.id}: {s.title}")

# Check agreements
agreements = Agreement.objects.all()
for a in agreements:
    print(f"Agreement {a.id}: Doctor={a.doctor.mobile}, Survey={a.survey.title if a.survey else 'None'}, Signed={bool(a.digital_signature)}")
```

---

## Expected Database State:

### After Old Upload + Completion:
```sql
Survey: id=1, title="Perception mapping... (8)"
Agreement: id=1, doctor_id=1, survey_id=1, signed=TRUE
SurveyResponse: id=1, doctor_id=1, survey_id=1, completed=TRUE
```

### After New Upload:
```sql
Survey: id=1, title="Perception mapping... (8)"  ← OLD, unchanged
Survey: id=2, title="Pediatric Care Survey"      ← NEW!

Agreement: id=1, doctor_id=1, survey_id=1, signed=TRUE  ← OLD
Agreement: id=2, doctor_id=1, survey_id=2, signed=FALSE ← NEW, unsigned!

SurveyResponse: id=1, doctor_id=1, survey_id=1, completed=TRUE  ← OLD
```

### After Doctor Signs Agreement 2:
```sql
Agreement: id=2, doctor_id=1, survey_id=2, signed=TRUE  ← NOW SIGNED!
```

### After Doctor Completes Survey 2:
```sql
SurveyResponse: id=2, doctor_id=1, survey_id=2, completed=TRUE  ← NEW!
```

---

## Fix for "(8)" in Title:

If you want clean titles, update your database:

```python
# Django shell
python manage.py shell

from wtestapp.models import Survey

# Find survey with (8)
s = Survey.objects.get(id=1)
print(s.title)  # Shows: "Perception mapping... (8)"

# Clean the title
s.title = "Perception mapping of Indian Physicians on Role of pegaspargase in management of ALL"
s.save()
```

---

## Summary:

✅ **Agreement model**: ForeignKey (multiple per doctor)
✅ **Upload logic**: Creates new survey + new agreement
✅ **Agreement check**: Per-survey basis
✅ **Profile navbar**: Shows correct link
✅ **Survey ordering**: New TOP, Completed BOTTOM
✅ **Notification badge**: Shows pending count
✅ **All data preserved**: No overwrites

**Restart server and test!** 🚀

```bash
python manage.py runserver
```
