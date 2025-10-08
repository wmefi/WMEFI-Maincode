# Quick Start Guide - Survey System

## 🚀 For Admins

### Step 1: Access Admin Panel
```
URL: http://localhost:8000/admin/
Login with superuser credentials
```

### Step 2: View Survey Responses
```
Admin → Survey responses
```
**You'll see:**
- List of all doctor submissions
- Contact numbers
- Survey titles
- Completion status
- Answer counts

### Step 3: Export to Excel (Two Methods)

**Method A - From Survey Responses:**
```
1. Survey responses page
2. Select checkboxes (or "Select all")
3. Action dropdown → "📊 Export Selected to Excel"
4. Click "Go"
```

**Method B - From Answers (Recommended for filtering):**
```
1. Answers page
2. Filter by survey/question type/date (optional)
3. Select checkboxes (or "Select all")
4. Action dropdown → "📊 Export Selected Answers to Excel"
5. Click "Go"
6. Excel auto-groups answers by doctor
```

### Step 4: Search by Contact Number
```
Search box → Type: 9876543210
Press Enter
```

### Step 5: View Individual Answers
```
Admin → Answers
Filter by survey or search by mobile number
```

---

## 📝 For Doctors (Survey Users)

### Step 1: Login
```
URL: http://localhost:8000/login/
Enter mobile number
Enter OTP
```

### Step 2: View Available Surveys
```
After login → Automatically redirected to Surveys page
Or click "My Surveys" in menu
```

### Step 3: Fill Survey
```
1. Click "Start Survey"
2. Fill all questions (all mandatory with *)
3. Visual feedback on each answer:
   - Green checkmark appears
   - Section highlights briefly
4. Yes/No questions may show follow-up text field
5. Click "Submit Survey" when done
```

### Step 4: Features
```
✅ Auto-save: Answers save automatically every 600ms
✅ Save Draft: Save partial progress
✅ Checkbox: Only one option selectable
✅ Visual feedback: Green highlights on selection
✅ Validation: Can't submit without filling all fields
```

---

## 🔧 For Developers

### Database Models
```python
Doctor         # User who fills survey
Survey         # Survey template with JSON
Question       # Individual questions
SurveyResponse # Doctor's submission
Answer         # Individual answer to question
```

### Key Files
```
wtestapp/admin.py         # Admin panel config
wtestapp/models.py        # Database models
wtestapp/views.py         # Survey logic
templates/survey_detail.html  # Survey UI
```

### Run Server
```bash
python manage.py runserver
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 📊 Excel Export Format

### Columns in exported file:
```
| Response ID | Doctor Name | Contact Number | Email | Survey | Completed | Submitted At | Question 1 | Question 2 | ... |
```

### Example row:
```
| 1 | Dr. Sharma | 9876543210 | sharma@example.com | Sunscreen Survey | Yes | 2025-01-08 14:30:00 | Yes - Mild redness | SPF 50+ | Routine outdoor exposure |
```

---

## 🎯 Common Tasks

### Task 1: Upload new survey
```
1. Create JSON file with questions
2. Admin → Doctor excel uploads
3. Upload Excel (doctors) + JSON (survey)
4. Auto-processes and assigns
```

### Task 2: Check survey completion rate
```
Admin → Survey responses
Filter by survey
Count completed vs. total
```

### Task 3: Find specific doctor's answers
```
Method 1: Survey responses → Search by mobile
Method 2: Answers → Search by mobile
```

### Task 4: Download all responses
```
Survey responses → Select all → Export to Excel
```

---

## ⚠️ Important Notes

1. **All questions mandatory by default** - Red asterisk (*) shown
2. **Checkbox = Single-select** - Works like radio button
3. **Yes/No follow-up** - Text field appears when "Yes" selected
4. **Auto-save** - Don't worry about losing data
5. **Contact number** - Unique identifier for doctors
6. **Excel export** - Questions become column headers

---

## 🐛 Troubleshooting

### Problem: Can't export to Excel
**Solution:** 
```bash
pip install openpyxl pandas
```

### Problem: Survey not showing for doctor
**Solution:**
- Check if survey assigned in Admin → Survey assignments
- Check doctor's mobile number matches

### Problem: Answers not saving
**Solution:**
- Check browser console (F12) for errors
- Verify all required fields filled
- Try "Save Draft" first

### Problem: Follow-up field not showing
**Solution:**
- Check JSON has `"follow_up"` field
- Only works for `"type": "yesno"` questions

---

## 📞 Support

For issues or questions:
1. Check browser console (F12)
2. Check Django logs
3. Check ADMIN_SURVEY_RESPONSES_GUIDE.md
4. Check SURVEY_IMPROVEMENTS.md
