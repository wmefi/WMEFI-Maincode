# Survey Testing Instructions

## Pre-requisites
1. Make sure Django server is running: `python manage.py runserver`
2. Login as a doctor
3. Have at least one survey assigned to you

## Test Cases

### ✅ Test 1: Single-Select Checkbox Behavior (Acts Like Radio Button)
**Steps:**
1. Open any survey with checkbox questions (like the sunscreen question)
2. Click on "Routine outdoor exposure"
3. **Expected:** Green checkmark (✓) appears next to the option, question section briefly turns light green
4. Click on "Atopic or sensitive skin"
5. **Expected:** 
   - "Routine outdoor exposure" automatically UNCHECKS
   - "Atopic or sensitive skin" gets checked with green checkmark
   - Only ONE checkbox is checked at a time
6. Click on "Atopic or sensitive skin" again
7. **Expected:** It unchecks, no option is selected now
8. **Result:** Checkboxes work as single-select (only one can be ticked) ✓

---

### ✅ Test 2: Visual Feedback for Yes/No Questions
**Steps:**
1. Find a Yes/No question (e.g., "Have you observed any common skin reactions...")
2. Click "Yes"
3. **Expected:** 
   - Entire question section turns green (#d4edda)
   - Green left border appears
   - Checkmark icon shows up
   - After 2 seconds, all visual feedback disappears
4. Click "No"
5. **Expected:** Same visual feedback
6. **Result:** User gets clear confirmation of their answer ✓

---

### ✅ Test 3: Visual Feedback for Radio Buttons
**Steps:**
1. Find a multiple-choice question with radio buttons
2. Click on first option
3. **Expected:**
   - Green checkmark appears next to option
   - Question section briefly turns light green
   - Feedback fades after 1.5 seconds
4. Click on another option
5. **Expected:** Same feedback, previous selection is replaced
6. **Result:** Only one option can be selected ✓

---

### ✅ Test 4: Mandatory Field Validation
**Steps:**
1. Open a survey
2. Leave the first question blank
3. Scroll to bottom and click "Submit Survey"
4. **Expected:**
   - Page stays on survey form (doesn't submit)
   - Error message appears: "Question 1 (...) is required"
   - Maximum 3 error messages shown
5. Fill all required fields
6. Click "Submit Survey"
7. **Expected:**
   - Survey submits successfully
   - Redirects to success page
   - Message: "Survey completed successfully"
8. **Result:** Cannot submit without answering all questions ✓

---

### ✅ Test 5: Save Draft Feature
**Steps:**
1. Open a survey
2. Answer only 2-3 questions (leave rest blank)
3. Click "Save Draft"
4. **Expected:**
   - Draft saves successfully (no validation errors)
   - Message: "Draft saved"
   - User stays on same page
5. Close browser and reopen
6. Open same survey
7. **Expected:** Previously filled answers are still there
8. **Result:** Can save partial progress ✓

---

### ✅ Test 6: Auto-save Feature
**Steps:**
1. Open a survey
2. Start typing in a text field
3. Wait 600ms without typing
4. Check browser console (F12 → Console)
5. **Expected:** You should see auto-save happening in background
6. Refresh the page
7. **Expected:** Your typed answer is still there
8. **Result:** Answers auto-save while user is filling the form ✓

---

### ✅ Test 7: Database Verification
**Steps:**
1. Complete and submit a survey
2. Open Django admin or database viewer
3. Navigate to `Answer` table
4. **Expected:** 
   - One row for each answered question
   - `survey_response` field links to SurveyResponse
   - `question` field links to Question
   - `answer_text` contains the actual answer
   - `created_at` has timestamp
5. **Result:** All answers are properly saved in database ✓

---

### ✅ Test 8: Browser Console Logs
**Steps:**
1. Open browser DevTools (F12)
2. Go to Console tab
3. Answer questions in the survey
4. **Expected Console Output:**
   ```
   Question 0 - Selected: Routine outdoor exposure
   Question 0 - Selected: Atopic or sensitive skin
   Question 1 answered: Yes
   Question 2 - Selected: Under 6 months
   ```
5. **Result:** All interactions are logged for debugging ✓

---

### ✅ Test 9: Mobile Responsiveness
**Steps:**
1. Open survey on mobile device or browser mobile view (F12 → Toggle Device)
2. Click on checkboxes
3. **Expected:** 
   - Touch-friendly - easy to click
   - Visual feedback works same as desktop
   - No layout issues
4. Try submitting without filling all fields
5. **Expected:** Error messages display properly on mobile
6. **Result:** Works perfectly on mobile ✓

---

### ✅ Test 10: New JSON Survey Upload
**Steps:**
1. Create a new JSON file with survey questions:
```json
{
  "title": "Test Survey",
  "description": "Testing new format",
  "questions": [
    {
      "text": "What is your name?",
      "type": "text"
    },
    {
      "text": "Do you agree?",
      "type": "yesno"
    },
    {
      "text": "Select all that apply",
      "type": "checkbox",
      "options": ["Option 1", "Option 2", "Option 3"]
    }
  ]
}
```
2. Upload via Django admin
3. Assign to a doctor
4. Open the survey
5. **Expected:**
   - All questions display with red asterisk (*)
   - All are mandatory
   - Visual feedback works for all types
6. Submit survey
7. **Expected:** Validation works, answers save properly
8. **Result:** System automatically handles new JSON formats ✓

---

## Common Issues & Solutions

### Issue: Visual feedback not working
**Solution:** 
- Clear browser cache (Ctrl+Shift+Del)
- Check browser console for errors
- Make sure Font Awesome is loaded (for checkmark icons)

### Issue: Validation not working
**Solution:**
- Check if `required` attribute is present in HTML
- Verify backend validation logic is running
- Check Django messages are displayed in template

### Issue: Auto-save not working
**Solution:**
- Check browser console for errors
- Verify CSRF token is present in form
- Check network tab (F12) to see if POST requests are being made

---

## Success Criteria
- ✅ All visual feedback animations work smoothly
- ✅ Mandatory validation prevents submission of incomplete forms
- ✅ Draft save allows partial completion
- ✅ Auto-save runs in background
- ✅ All answers save correctly to database
- ✅ Works on mobile and desktop
- ✅ New JSON surveys work automatically

---

## Performance Notes
- Auto-save has 600ms debounce to prevent excessive server requests
- Visual feedback uses CSS animations (no jQuery needed)
- Form validation happens on both frontend (HTML5) and backend (Django)
- Database uses `update_or_create()` to prevent duplicate answers
