# ✅ Implementation Complete - Per-Survey Agreement Flow

## Changes Made:

### 1. Agreement Model Updated ✅
**File**: `wtestapp/models.py` (Line 152)

**Before**:
```python
doctor = models.OneToOneField(Doctor, ...)  # One agreement per doctor
```

**After**:
```python
doctor = models.ForeignKey(Doctor, ...)  # Multiple agreements per doctor
```

**Impact**: Doctor can now have multiple agreements (one per survey)

---

### 2. Database Migration Created ✅
**File**: `wtestapp/migrations/0012_change_agreement_to_foreignkey.py`

**Command**: `python manage.py migrate` (Already run)

**Result**: Database schema updated

---

### 3. Admin Upload Logic Fixed ✅
**File**: `wtestapp/admin.py`

**Lines 214-220**:
```python
# OLD: update_or_create (overwrites existing agreement)
Agreement.objects.update_or_create(
    doctor=doctor,
    defaults={"survey": survey, ...}
)

# NEW: get_or_create (creates per-survey agreement)
Agreement.objects.get_or_create(
    doctor=doctor,
    survey=survey,  # ← Key: doctor + survey combination
    defaults={"amount": survey_amount}
)
```

**Lines 400-406** (process_upload action): Same fix applied

---

### 4. Agreement Check Logic Updated ✅
**File**: `wtestapp/views.py` (Line 450-469)

**Before**:
```python
# Check if ANY agreement exists
agreement_signed = Agreement.objects.filter(doctor=doctor).exists()
```

**After**:
```python
# Check EACH survey for its agreement
for survey in assigned_surveys:
    agreement_signed = Agreement.objects.filter(
        doctor=doctor,
        survey=survey,  # ← Check THIS survey's agreement
        digital_signature__isnull=False
    ).exists()
    
    if not agreement_signed:
        # Redirect to agreement page for THIS survey
        return redirect('agreement_page', survey_id=survey.id)
```

---

### 5. Profile View Updated ✅
**File**: `wtestapp/views.py` (Line 698-714)

**Before**:
```python
agreement = Agreement.objects.filter(doctor=doctor).first()  # First agreement only
```

**After**:
```python
agreements = Agreement.objects.filter(
    doctor=doctor,
    digital_signature__isnull=False
).select_related('survey')  # All signed agreements
```

---

### 6. Survey Listing Fixed ✅
**File**: `wtestapp/views.py` (Line 45-62)

**Added**:
- Separate `pending_surveys` and `completed_surveys_objs`
- Order by `-created_at` (newest first)
- Pass `pending_count` to template

---

### 7. Survey Page UI Enhanced ✅
**File**: `wtestapp/templates/wtestapp/doctor_surveys.html`

**New Layout**:
```html
<!-- NEW SURVEYS SECTION -->
<h4>🆕 New Surveys [Badge: count]</h4>
<div class="survey-item" style="border: 2px solid pink; pulse animation">
  🆕 {{ survey.title }}
  ⚠️ Action Required
  <a href="...">▶️ Start Survey</a>
</div>

<!-- COMPLETED SURVEYS SECTION -->
<h4>✅ Completed Surveys</h4>
<div class="survey-item">
  {{ survey.title }}
  ✓ Completed
  <a href="...?view=1">👁️ View</a>
</div>
```

---

### 8. Profile View Badge Added ✅
**File**: `wtestapp/templates/wtestapp/doctor_profile_view.html` (Line 643)

**Added**:
```html
<a href="{% url 'surveys' %}" style="position: relative;">
  My Surveys
  {% if pending_surveys_count > 0 %}
    <span class="badge bounce-animation">{{ pending_surveys_count }}</span>
  {% endif %}
</a>
```

---

### 9. Context Processor Fixed ✅
**File**: `wtestapp/context_processors.py`

**Changes**:
- Removed `last_name` requirement
- Check agreement with signature fields
- Better profile_complete logic

---

## New Flow:

### Scenario 1: Existing Doctor + New Survey

**Step 1: Admin Uploads**
```
Admin uploads:
- Excel: Doctor (9769890961) 
- Survey JSON: "Pediatric Care Survey"
- Creates: Survey ID 2
- Creates: Agreement (doctor=X, survey=2, unsigned)
- Assigns: Doctor → Survey 2
```

**Step 2: Doctor Login**
```
Doctor login (9769890961)
    ↓
Profile complete? YES ✅
    ↓
Check agreements:
  - Survey 1: Agreement signed ✅
  - Survey 2: Agreement NOT signed ❌
    ↓
Redirect to: /agreement/2/ (Survey 2 agreement)
```

**Step 3: Sign Agreement**
```
Doctor signs agreement for Survey 2
    ↓
Agreement (doctor=X, survey=2) updated:
  - digital_signature: "..."
  - signed_at: now()
    ↓
Redirect to: "My Surveys"
```

**Step 4: My Surveys Page**
```
Shows:
  🆕 New Surveys [1]
    - Pediatric Care Survey (NEW!) ← Survey 2
    - [▶️ Start Survey]
  
  ✅ Completed Surveys
    - Pegaspargase Survey ← Survey 1
    - [👁️ View]
```

**Step 5: Complete Survey 2**
```
Doctor fills Survey 2
    ↓
Submit
    ↓
SurveyResponse created (survey=2, is_completed=True)
    ↓
Redirect to success page
```

**Step 6: Back to My Surveys**
```
Shows:
  ✅ Completed Surveys
    - Pediatric Care Survey ← NOW completed!
    - Pegaspargase Survey
```

---

## Database After Flow:

### Doctor Table:
```sql
id | first_name  | mobile      | email                    | profile_complete
1  | VIKAS       | 9769890961  | email@gmail.com          | TRUE
```

### Survey Table:
```sql
id | title                  | json_file      | created_at
1  | Pegaspargase Survey    | survey1.json   | 2025-01-10
2  | Pediatric Care Survey  | survey2.json   | 2025-01-17  ← NEW!
```

### Agreement Table (NEW STRUCTURE):
```sql
id | doctor_id | survey_id | digital_signature | signed_at           | amount
1  | 1         | 1         | "data:image..."   | 2025-01-11 10:00:00 | 5000
2  | 1         | 2         | "data:image..."   | 2025-01-17 14:30:00 | 6000  ← NEW!
```

### SurveyResponse Table:
```sql
id | doctor_id | survey_id | is_completed | answers_json | completed_at
1  | 1         | 1         | TRUE         | {...}        | 2025-01-12 15:00:00
2  | 1         | 2         | TRUE         | {...}        | 2025-01-17 16:00:00  ← NEW!
```

---

## Navbar Logic:

### Profile Complete Check:
```python
profile_complete = all([
    doctor.first_name,     # Required
    doctor.mobile,         # Required
    doctor.email,          # Required
    doctor.specialty       # Required
])

# last_name is OPTIONAL now!
```

### Navbar Display:
```html
{% if profile_complete %}
  <li><a href="/profile/view/">Profile</a></li>  ← Existing doctors
{% else %}
  <li><a href="/profile/">Complete Profile</a></li>  ← New doctors
{% endif %}
```

---

## Key Points:

### ✅ Multiple Surveys per Doctor:
- Doctor 1 can have Survey 1, 2, 3, 4...
- All separate in database
- All responses saved separately

### ✅ Multiple Agreements per Doctor:
- Agreement 1 for Survey 1
- Agreement 2 for Survey 2
- Agreement 3 for Survey 3
- Each linked to its survey

### ✅ Profile Data Safe:
- Profile saved once
- Never overwritten
- Reused for all surveys

### ✅ Survey Data Safe:
- Each survey separate
- Responses saved separately
- Old surveys never change

### ✅ Agreement Per Survey:
- Doctor must sign for each survey
- Can't skip agreement
- Each survey's agreement tracked

---

## Testing:

### Test 1: Fresh Doctor + First Survey
1. Upload Excel + JSON (Survey 1)
2. Doctor login
3. Complete profile
4. Sign agreement (Survey 1)
5. Fill survey
6. Submit
7. Download PDF

### Test 2: Existing Doctor + New Survey
1. Upload NEW Excel + JSON (Survey 2) for SAME doctor
2. Doctor login
3. ✅ Profile already complete → Skip profile page
4. ❌ Agreement not signed for Survey 2 → Show agreement page
5. Doctor signs → Save Agreement (survey=2)
6. "My Surveys" shows:
   - 🆕 New: Survey 2 (TOP)
   - ✅ Completed: Survey 1 (BOTTOM)
7. Doctor fills Survey 2
8. Both surveys downloadable

### Test 3: Profile Navbar
1. Login as NEW doctor (profile incomplete)
2. Navbar shows: "Complete Profile" ✅
3. Complete profile
4. Navbar changes to: "Profile" ✅

---

## Summary:

🎉 **ALL DONE!**

✅ **Agreement per survey** implemented
✅ **Profile navbar** shows correct link
✅ **Survey ordering** - New TOP, Completed BOTTOM
✅ **Multiple surveys** supported
✅ **All data preserved**
✅ **Clean separation**

**Restart server aur test karo!** 🚀

```bash
python manage.py runserver
```
