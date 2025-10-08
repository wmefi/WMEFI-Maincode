# How to Export Survey Responses to Excel

## ✅ Step-by-Step Guide

### Step 1: Login to Admin Panel
```
URL: http://127.0.0.1:8000/admin/
```

### Step 2: Navigate to Survey Responses
```
Left sidebar → Click on "Survey responses"
```

**You'll see a list like this:**
```
┌─────────────────────────────────────────────────────────────────┐
│ Select survey response to change                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ☐ ID | Doctor Name | Contact No | Survey | Complete | Answers  │
│ ☐ 27 | Dr. Sharma  | 8554081666 | Sun... | Yes      | 8 answers│
│ ☐ 26 | Dr. Patel   | 9433263932 | Sun... | Yes      | 5 answers│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Step 3: Select Checkboxes ⚠️ IMPORTANT
```
Click on the checkbox (☐) on the LEFT SIDE of each row

Example:
☑ 27 | Dr. Sharma  | 8554081666 | Sunscreen Survey | Yes | 8 answers

Or use "Select all" checkbox at the top
```

### Step 4: Choose Export Action
```
After selecting checkboxes, you'll see:

Action: [Select an action ▼]

Click on dropdown and select:
"📊 Export Selected to Excel"
```

### Step 5: Click "Go" Button
```
After selecting action, click the "Go" button next to dropdown

Action: [📊 Export Selected to Excel ▼] [Go]
                                          ↑
                                      Click here
```

### Step 6: Excel Downloads
```
✅ File downloads: survey_responses.xlsx
✅ Check your Downloads folder
```

---

## ⚠️ Common Errors & Solutions

### Error: "Items must be selected in order to perform actions on them"

**Reason:** You forgot to select checkboxes

**Solution:**
1. ✅ First click checkboxes (☐ → ☑)
2. ✅ Then select action from dropdown
3. ✅ Then click "Go"

**Visual Guide:**
```
WRONG ❌:
1. Select action → Export
2. Click Go
❌ No checkboxes selected = Error

CORRECT ✅:
1. Click checkboxes ☑
2. Select action → Export
3. Click Go
✅ Works!
```

---

## 📊 Excel Output Format

### Columns:
1. Response ID
2. Doctor Name (actual name)
3. Contact Number
4. Email
5. Survey (title)
6. Completed (Yes/No)
7. Submitted At (date & time)
8. Q1, Q2, Q3... (all questions)

### Example:
```
┌────┬─────────────┬────────────┬───────┬─────────┬──────────┬─────────────┬────────┬────────┐
│ ID │ Doctor Name │ Contact No │ Email │ Survey  │ Complete │ Submitted   │ Q1     │ Q2     │
├────┼─────────────┼────────────┼───────┼─────────┼──────────┼─────────────┼────────┼────────┤
│ 27 │ Dr. Sharma  │ 8554081666 │ ...   │ Survey1 │ Yes      │ 2025-01-08  │ Cream  │ ghghg  │
└────┴─────────────┴────────────┴───────┴─────────┴──────────┴─────────────┴────────┴────────┘
```

---

## 🎯 Quick Checklist

Before exporting, make sure:
- [x] Logged into admin panel
- [x] On "Survey responses" page (NOT "Answers")
- [x] Checkboxes are selected (☑)
- [x] Action dropdown shows "Export Selected to Excel"
- [x] Clicked "Go" button

---

## 📱 Screenshots Reference

### Step 1: Select Checkboxes
```
Look for checkboxes on the LEFT side:

☐ 27 | Dr. Sharma  | 8554081666 | ...
↑
Click here first!
```

### Step 2: Action Dropdown
```
Action: [------------ ▼] [Go]
        ↑
        Click dropdown
        
Then select:
"📊 Export Selected to Excel"
```

### Step 3: Click Go
```
Action: [📊 Export Selected to Excel ▼] [Go]
                                         ↑
                                    Click here
```

---

## 🚀 Quick Summary

1. Admin → Survey responses
2. Select ☑ checkboxes
3. Action → Export to Excel
4. Click Go
5. Download Excel ✅

**That's it!** 🎉
