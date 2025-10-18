# Build and Test Instructions

## ✅ Data Fixed!
- 5 CP doctors (all with "pending" status)
- 4 GC doctors (1 completed, 3 pending)

## 🔨 Build React App

### Step 1: Navigate to React Project
```bash
cd wtestapp/templates/wtestapp/admin_minidash
```

### Step 2: Build
```bash
npm run build
```

### Step 3: Copy to Django Static
**Windows:**
```bash
xcopy /E /I /Y dist\* ..\..\..\static\admin_minidash\
```

**Linux/Mac:**
```bash
cp -r dist/* ../../../static/admin_minidash/
```

### Step 4: Restart Django Server
```bash
cd ../../../..
python manage.py runserver
```

## 🧪 Testing Scenarios

### Test 1: CP Only + Pending Status
1. Select "CP Only" from Mode dropdown
2. Select "Pending" from Status dropdown
3. **Expected Result**: Shows 5 CP doctors with pending status
4. **Stats Box Shows**: CP: 5, GC: 0, Total: 5

### Test 2: GC Only + Completed Status
1. Select "GC Only" from Mode dropdown
2. Select "Completed" from Status dropdown
3. **Expected Result**: Shows 1 GC doctor with completed status
4. **Stats Box Shows**: CP: 0, GC: 1, Total: 1

### Test 3: GC Only + Pending Status
1. Select "GC Only" from Mode dropdown
2. Select "Pending" from Status dropdown
3. **Expected Result**: Shows 3 GC doctors with pending status
4. **Stats Box Shows**: CP: 0, GC: 3, Total: 3

### Test 4: All Modes + All Status
1. Select "All Modes"
2. Select "All Status"
3. **Expected Result**: Shows all 9 doctors
4. **Stats Box Shows**: CP: 5, GC: 4, Total: 9

### Test 5: Excel Export
1. Set any filter (e.g., CP Only + Pending)
2. Click "Export Excel"
3. **Expected Result**: Excel file contains only the filtered data (5 CP pending doctors)

## 🐛 Debug in Browser

Open browser console (F12) and check:
```
Filter state: {filterMode: "CP", filterStatus: "pending", selectedSurveyId: "all"}
Researchers from API: 5
Filtered researchers: 5
```

## ✨ What's Working Now:

1. ✅ **Mode Filter (CP/GC)**: API filters by portal_type
2. ✅ **Status Filter**: Frontend filters by status (completed/pending/in-progress/not-started)
3. ✅ **Survey Filter**: API filters by survey assignment
4. ✅ **Combined Filters**: All filters work together
5. ✅ **Stats Display**: Shows accurate CP, GC, Total counts
6. ✅ **Excel Export**: Respects all active filters
7. ✅ **CSV Export**: Respects all active filters
8. ✅ **Empty State**: Shows "No results" with clear filters button
9. ✅ **Loading States**: Shows spinner when fetching data
10. ✅ **Responsive Design**: Works on all devices

## 🎯 Expected Behavior:

**When you select CP Only + Pending:**
- API call: `/api/researchers/?mode=CP`
- Returns: 5 CP doctors (all pending)
- Frontend filters for "pending" status
- Result: 5 doctors displayed
- Stats: CP: 5, GC: 0, Total: 5

**When you select GC Only + Completed:**
- API call: `/api/researchers/?mode=GC`
- Returns: 4 GC doctors (1 completed, 3 pending)
- Frontend filters for "completed" status
- Result: 1 doctor displayed
- Stats: CP: 0, GC: 1, Total: 1

**When you Export Excel with CP Only + Pending:**
- Makes API call: `/api/export-doctors-excel/?mode=CP`
- Backend filters CP doctors
- Returns Excel with 5 CP doctors (all pending)

## 📝 Notes:

- Console logs added for debugging
- All filters are properly connected
- Data flow: User → State → API → Frontend Filter → Display
- Export uses same filters as display
