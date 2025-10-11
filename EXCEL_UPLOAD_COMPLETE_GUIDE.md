# ✅ Excel Upload to Dashboard - Complete Guide

## 📋 What's Been Done:

### 1. **Database Updated** ✅
Added new fields to `Doctor` model:
- `territory` - Territory/Location from Excel
- `emp1_name` - Manager 1 Name (ZSM/BDM/ZM)
- `emp1_mobile` - Manager 1 Mobile
- `emp2_name` - Manager 2 Name
- `emp2_mobile` - Manager 2 Mobile
- `designation` - Designation (ZSM/BDM/ZM/etc)

**Migration created and applied!**

### 2. **Excel Upload Logic Updated** ✅
Now captures these columns from Excel:
- Dr name as per PAN → `first_name`
- Dr email ID → `email`
- Dr Contact number → `mobile`
- speciality → `specialty`
- Territory To Which Doctor Is Associated → `territory`
- Emp1 Name → `emp1_name`
- Emp1 Mobile → `emp1_mobile`
- Emp2 Name → `emp2_name`
- emp2 Mobile → `emp2_mobile`
- Desig → `designation`
- Amount → `agreement_amount` (in Agreement)
- Survey Name → `survey.title`

### 3. **API Updated** ✅
API endpoint `/api/researchers/` now returns:
- ZSM/BDM names from `emp1_name`/`emp2_name`
- Territory from `territory` field
- Manager mobile numbers
- Designation

### 4. **React Dashboard Enhanced** ✅
- Search now works for: name, specialty, **ZSM, BDM, territory, mobile**
- Flexible search - finds "ZM", "BDM", "ZSM" - any manager name
- Shows real data from Excel upload

---

## 🚀 How to Use:

### Step 1: Prepare Your Excel File

**Required Columns:**
```
| Final | Dr name as per PAN | Dr email ID | Dr Contact number | speciality | Territory To Which Doctor Is Associated | Emp1 Name | Emp1 Mobile | Emp2 Name | emp2 Mobile | Territory | Desig | Amount | Survey Name |
```

**Example Row:**
```
BATCH 1 | M R KESAVAN | kesavan.mr7@gmail.com | 9176427860 | PAEDIATRIC ONCOLOGIST | COCHIN PST 2 | RAJESH MAHAVAN | 9535895544 | VIVEK TRIPATHI | 9811491309 | BANGALORE BDM | BDM | 50000 | Mapping of Indian Physicians...
```

### Step 2: Upload in Django Admin

1. **Login to Django Admin:**
   ```
   http://127.0.0.1:8000/admin/
   ```

2. **Go to "Doctor excel uploads"**

3. **Click "Add Doctor Excel Upload"**

4. **Upload:**
   - Excel file (.xlsx)
   - Survey JSON (optional - if you have questions)

5. **Save** - Auto-processes immediately!

### Step 3: View in React Dashboard

1. **Open Dashboard:**
   ```
   http://localhost:5173
   or
   http://127.0.0.1:8000/admin_dashboard/
   ```

2. **Data Shows:**
   - Doctor name from Excel
   - Email, Mobile, Specialty
   - Territory/Location
   - ZSM/BDM names from Emp1/Emp2
   - Survey assignment
   - Amount

3. **Search Works For:**
   - Doctor name: "KESAVAN"
   - Manager: "RAJESH" or "VIVEK"
   - Territory: "BANGALORE" or "BDM"
   - Designation: "ZM", "BDM", "ZSM"
   - Mobile: "9176427860"

---

## 🔍 Dashboard Features:

### **Flexible Search:**
```
✅ Search "BANGALORE" → Shows all doctors in Bangalore
✅ Search "RAJESH" → Shows all doctors under manager Rajesh
✅ Search "BDM" → Shows all doctors with BDM designation
✅ Search "9176427860" → Finds by mobile number
```

### **Filters:**
- **Mode:** All / CP / GC
- **Status:** All / Completed / In Progress / Pending / Not Started

### **Displays:**
- Total Researchers
- Completion Rate
- Survey Progress
- Manager Names (ZSM/BDM/ZM - whatever is in Excel)
- Territory
- Export to CSV

---

## 📊 Excel Column Mapping:

| Excel Column | Database Field | Dashboard Shows |
|-------------|---------------|-----------------|
| Dr name as per PAN | `first_name` | Name |
| Dr email ID | `email` | Email |
| Dr Contact number | `mobile` | Mobile |
| speciality | `specialty` | Specialty/Unit |
| Territory To Which Doctor Is Associated | `territory` | Location/Territory |
| Emp1 Name | `emp1_name` | ZSM |
| Emp1 Mobile | `emp1_mobile` | Manager Contact |
| Emp2 Name | `emp2_name` | BDM |
| emp2 Mobile | `emp2_mobile` | Manager 2 Contact |
| Desig | `designation` | Designation |
| Amount | Agreement `amount` | Agreement Amount |
| Survey Name | Survey `title` | Assigned Survey |

---

## ✨ Key Features:

### 1. **No Fixed Manager Names**
- Excel can have "ZSM", "BDM", "ZM", "Regional Manager" - anything!
- Dashboard shows exactly what's in Excel
- Search works for any manager name

### 2. **Auto-Assignment**
- Upload Excel → Automatically creates:
  - Doctor profile
  - Survey assignment
  - Agreement with amount

### 3. **Flexible Search**
- Searches across ALL fields:
  - Name, Email, Mobile
  - Specialty, Territory
  - Manager names (Emp1/Emp2)
  - Location

### 4. **Real-Time Dashboard**
- Upload Excel → Refresh dashboard → Data appears
- No manual mapping needed
- All fields from Excel show up

---

## 🎯 Example Workflow:

1. **Upload Excel with 100 doctors**
   - Each has territory: "BANGALORE BDM", "KOLKATA BDM", etc.
   - Manager names: different ZSMs/BDMs per region

2. **Dashboard automatically shows:**
   - 100 researchers
   - Grouped by territory
   - Manager names from Excel

3. **Admin can search:**
   - "BANGALORE" → All Bangalore doctors
   - "VIVEK TRIPATHI" → All doctors under Vivek
   - "ZM" → All doctors with ZM designation

4. **Export CSV** with all details

---

## 🔧 Technical Details:

### Files Modified:
1. `wtestapp/models.py` - Added 6 new fields to Doctor
2. `wtestapp/admin.py` - Updated Excel upload logic (2 functions)
3. `wtestapp/api_views.py` - API returns new fields
4. `wtestapp/templates/wtestapp/admin_minidash/src/App.tsx` - Enhanced search

### Migration:
```bash
python manage.py makemigrations
python manage.py migrate
```

### API Response Example:
```json
{
  "success": true,
  "researchers": [
    {
      "id": "108",
      "name": "M R KESAVAN",
      "mobile": "9176427860",
      "email": "kesavan.mr7@gmail.com",
      "specialty": "PAEDIATRIC ONCOLOGIST",
      "territory": "COCHIN PST 2",
      "zsm": "RAJESH MAHAVAN",
      "bdm": "VIVEK TRIPATHI",
      "designation": "BDM",
      "status": "not-started",
      "surveyProgress": 0
    }
  ]
}
```

---

## 🎉 Summary:

**Upload Excel → Dashboard Shows Everything Automatically!**

✅ No hardcoded ZSM/BDM names  
✅ Flexible search across all fields  
✅ Territory/location from Excel  
✅ Manager names dynamic  
✅ Works with any designation (ZM, BDM, ZSM, etc.)  
✅ Real-time updates  

**Your Excel data is now your dashboard data!** 🚀
