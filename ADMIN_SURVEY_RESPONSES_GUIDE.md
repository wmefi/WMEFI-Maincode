# Admin Panel - Survey Responses Guide

## Overview
Admin panel me ab aap survey responses dekh sakte ho aur Excel me download kar sakte ho.

---

## Access Admin Panel

1. Browser me jao: `http://localhost:8000/admin/`
2. Admin credentials se login karo
3. Left sidebar me dekhoge:
   - **Survey responses** ← Survey submissions
   - **Answers** ← Individual question answers

---

## View Survey Responses

### Navigate to Survey Responses
1. Django Admin → **Survey responses**
2. Yaha aapko list milegi:
   - Doctor Name
   - Contact Number
   - Survey Title
   - Completed (Yes/No)
   - Submitted At
   - Answers count

### Filter & Search
**Filter by:**
- Survey name (dropdown)
- Completion status (Completed/Not completed)
- Date range

**Search by:**
- Doctor name
- Contact number
- Survey title

### View Individual Response
1. Click on any Response ID
2. Aapko dikhega:
   - Doctor details
   - Survey info
   - All answers inline (in table format)

---

## Export to Excel

### Method 1: Export from Survey Responses Page
1. Django Admin → **Survey responses**
2. Select checkboxes of responses you want to export
3. From "Action" dropdown, select: **📊 Export Selected to Excel**
4. Click "Go"
5. Excel file download hogi: `survey_responses.xlsx`

### Method 2: Export from Answers Page ⭐ NEW
1. Django Admin → **Answers**
2. Select checkboxes of answers you want to export
3. From "Action" dropdown, select: **📊 Export Selected Answers to Excel**
4. Click "Go"
5. Excel file download hogi: `survey_answers_export.xlsx`

**Benefit:** 
- Can filter by survey first, then export only those answers
- Can filter by question type (text, radio, yesno, etc.)
- Can filter by date range
- Groups answers by doctor/response automatically

### Method 3: Export All Responses
1. Django Admin → **Survey responses** or **Answers**
2. Check top checkbox (selects all)
3. Action → **📊 Export to Excel**
4. Click "Go"

### Excel File Format
```
| Response ID | Doctor Name | Contact Number | Email | Survey | Completed | Submitted At | Q1: Question text... | Q2: Question text... | ... |
|------------|-------------|----------------|-------|--------|-----------|--------------|---------------------|---------------------|-----|
| 1          | Dr. Sharma  | 9876543210    | ...   | Survey1| Yes       | 2025-01-08   | Yes - Mild redness  | Option A            | ... |
```

**Excel Columns:**
- Response ID
- Doctor Name
- Contact Number
- Email
- Survey (title)
- Completed (Yes/No)
- Submitted At (date & time)
- **Each question as separate column**
- Answer values in cells

---

## View Individual Answers

### Navigate to Answers
1. Django Admin → **Answers**
2. Yaha har question ka answer separately dikhega:
   - Doctor name
   - Contact number
   - Survey name
   - Question text (truncated)
   - Answer text

### Filter Answers
**Filter by:**
- Survey name
- Question type (text, radio, checkbox, yesno, etc.)
- Date created

**Search by:**
- Doctor mobile number
- Doctor name
- Question text
- Answer text

### Visual Highlights
- **Yes answers**: Green & bold
- **No answers**: Red & bold
- **Other answers**: Normal text
- **Empty answers**: Gray "No answer"

---

## Search by Contact Number

### Scenario: Find all responses from specific doctor
1. Django Admin → **Survey responses**
2. Search box me type karo: `9876543210` (doctor's mobile)
3. Enter press karo
4. Sabhi responses of that doctor dikhengi

### Scenario: Find specific answer by contact number
1. Django Admin → **Answers**
2. Search box me type karo: `9876543210`
3. Enter press karo
4. Sabhi answers of that doctor dikhengi

---

## Example Use Cases

### Use Case 1: Export all sunscreen survey responses
**Steps:**
1. Go to **Survey responses**
2. Filter by survey: "Sunscreen for Babies"
3. Click "Select all" checkbox
4. Action → Export to Excel
5. Download Excel file

### Use Case 2: Check Dr. Sharma's responses
**Steps:**
1. Go to **Survey responses**
2. Search: "Dr. Sharma" or "9876543210"
3. Click on Response ID
4. View all answers inline

### Use Case 3: Find all "Yes" answers with follow-ups
**Steps:**
1. Go to **Answers**
2. Search: "Yes -" (this finds Yes answers with follow-up text)
3. View all matching answers

### Use Case 4: Export responses submitted today
**Steps:**
1. Go to **Survey responses**
2. Filter by: "Completed at" → Today
3. Select all
4. Export to Excel

### Use Case 5: Export only Yes/No question answers
**Steps:**
1. Go to **Answers**
2. Filter by: "Question type" → "Yes/No"
3. Select all visible answers
4. Action → Export Selected Answers to Excel
5. Excel will group by doctor automatically

### Use Case 6: Export specific survey answers (e.g., 8-10 questions)
**Steps:**
1. Go to **Answers**
2. Filter by: "Survey" → Select your survey
3. All answers for that survey will show
4. Select all (even if 100+ answers)
5. Action → Export to Excel
6. Excel automatically creates:
   - One row per doctor
   - One column per question (all 8-10 questions)
   - Proper grouping and formatting

---

## Data Analysis Tips

### In Excel (after export):
1. **Sort by Contact Number** - Group all responses by doctor
2. **Filter by Survey** - Analyze specific survey results
3. **Pivot Table** - Create summary reports
4. **Charts** - Visualize Yes/No questions
5. **Find duplicates** - Check if any doctor submitted twice

### Common Analysis Queries:
```sql
-- In Django shell or database
# Total responses per survey
SurveyResponse.objects.filter(is_completed=True).values('survey__title').annotate(count=Count('id'))

# Responses by doctor
SurveyResponse.objects.filter(doctor__mobile='9876543210')

# All Yes answers
Answer.objects.filter(answer_text__istartswith='Yes')

# Completed surveys this week
from datetime import timedelta
from django.utils import timezone
week_ago = timezone.now() - timedelta(days=7)
SurveyResponse.objects.filter(completed_at__gte=week_ago, is_completed=True)
```

---

## Troubleshooting

### Issue: Can't see Survey responses menu
**Solution:** Register SurveyResponse in admin.py (already done in code)

### Issue: Excel export shows error
**Solution:** 
- Check if `openpyxl` is installed: `pip install openpyxl`
- Make sure pandas is installed: `pip install pandas`

### Issue: Column width too small in Excel
**Solution:** Code already auto-adjusts width (max 50 chars)

### Issue: Question text truncated in Excel
**Solution:** Questions longer than 50 chars are auto-truncated with "..."
- Hover over cell in Excel to see full text
- Or manually adjust column width

---

## Admin Panel Features Summary

| Feature | Location | Purpose |
|---------|----------|---------|
| View all responses | Survey responses | See all submissions |
| Filter by survey | Survey responses → Filter | Narrow down results |
| Search by mobile | Search box | Find specific doctor |
| View inline answers | Response detail | See all Q&A |
| Export to Excel | Action dropdown | Download data |
| View individual answers | Answers section | Detailed answer view |
| Highlight Yes/No | Answers list | Visual feedback |

---

## Permissions

**Who can access:**
- Superusers (full access)
- Staff users with permissions:
  - Can view survey response
  - Can change survey response
  - Can export survey response

**To grant access:**
1. Django Admin → Users
2. Select user
3. Check: "Staff status"
4. Add permissions: survey response (view, change)
5. Save

---

## Quick Reference

### URLs:
- Admin Panel: `/admin/`
- Survey Responses: `/admin/wtestapp/surveyresponse/`
- Answers: `/admin/wtestapp/answer/`

### Key Models:
- `SurveyResponse` - Overall submission
- `Answer` - Individual question answer
- `Doctor` - User who submitted
- `Survey` - Survey template
- `Question` - Survey questions

### Export Format:
- File type: `.xlsx` (Excel)
- Encoding: UTF-8
- Date format: `YYYY-MM-DD HH:MM:SS`
- Empty cells: Blank (not "N/A")
