# Excel Upload Steps

1. **Go to Django Admin:**
   - URL: http://127.0.0.1:8000/admin/wtestapp/doctorexcelupload/

2. **Click "ADD DOCTOR EXCEL UPLOAD" button**

3. **Upload Files:**
   - Excel file: Select your Batch_8 Excel file
   - Survey JSON: Select your survey_questions JSON file
   - Click "SAVE"

4. **Process the Upload:**
   - Go back to: http://127.0.0.1:8000/admin/wtestapp/doctorexcelupload/
   - **Check the checkbox** next to your uploaded file
   - **Select action:** "Process Excel + Auto-Link Survey JSON"
   - **Click "Go" button**

5. **Verify Import:**
   - Check: http://127.0.0.1:8000/admin/wtestapp/doctor/
   - Should see 9 doctors imported

6. **Test Login:**
   - Go to: http://127.0.0.1:8000/
   - Login with mobile: 9176427860
   - Enter OTP
   - Profile should show: M R KESAVAN
   - Survey & Agreement should work

## Current Status:
- Database is empty
- You need to run the "Process Excel + Auto-Link Survey JSON" **action**
- Not just upload - you must **select the action and click Go**
