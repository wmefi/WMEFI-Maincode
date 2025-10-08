# 📋 Checkbox Single-Select Behavior

## Important Change: Checkboxes Now Work Like Radio Buttons

### ✅ How It Works Now

#### Before (Multiple Selection):
```
☑ Routine outdoor exposure
☑ Atopic or sensitive skin  
☑ During vacations/travel
```
Multiple checkboxes could be selected at once.

#### After (Single Selection - Current):
```
☑ Routine outdoor exposure
☐ Atopic or sensitive skin  
☐ During vacations/travel
```
**Only ONE checkbox can be selected at a time!**

---

## User Experience

### Scenario 1: Selecting First Option
1. User clicks "Routine outdoor exposure"
2. ✅ It gets checked
3. ✅ Green checkmark appears
4. ✅ Section highlights briefly

### Scenario 2: Changing Selection
1. User clicks "Atopic or sensitive skin"
2. ✅ "Routine outdoor exposure" automatically UNCHECKS
3. ✅ "Atopic or sensitive skin" gets checked
4. ✅ Green checkmark moves to new option
5. ✅ Only ONE option is checked

### Scenario 3: Deselecting
1. User clicks already checked "Atopic or sensitive skin" again
2. ✅ It unchecks
3. ✅ No option is selected now
4. ✅ User can select a different one or leave blank (until submit)

---

## Technical Implementation

### Frontend (JavaScript)
```javascript
function handleCheckboxChange(element, questionIndex, otherInputId) {
  // If checking a new checkbox
  if (element.checked) {
    // Find all checkboxes with same name
    const allCheckboxes = document.querySelectorAll(`input[name="${element.name}"][type="checkbox"]`);
    
    // Uncheck all others
    allCheckboxes.forEach(checkbox => {
      if (checkbox !== element) {
        checkbox.checked = false;
        // Remove visual feedback from others
      }
    });
  }
  
  // Show visual feedback on selected one
  // ...
}
```

### Backend (Django)
```python
# Old: Multiple values saved as comma-separated
answer_value = ', '.join(selected)  # "Option1, Option2, Option3"

# New: Single value only
answer_value = selected[0] if selected else ''  # "Option1"
```

### Validation
```python
# Old: Check if any value exists in list
if not answer_value or all(not v.strip() for v in answer_value):
    errors.append("Required")

# New: Check if single value exists
if not answer_value or not answer_value[0].strip():
    errors.append("Required")
```

---

## Database Storage

### Answer Table Structure
```
id | survey_response | question | answer_text | created_at
1  | 123            | 456      | Option1     | 2025-01-08
```

**Before:** `answer_text = "Option1, Option2, Option3"`  
**Now:** `answer_text = "Option1"` (single value)

---

## Visual Feedback Timeline

```
0ms    - User clicks checkbox
10ms   - Previous checkbox unchecks (if any)
50ms   - New checkbox checks
100ms  - Green checkmark appears (fadeIn animation)
150ms  - Section background turns light green (#e8f5e9)
800ms  - Section background resets to white
1500ms - Green checkmark disappears
```

---

## Why This Change?

### Original Requirement:
> "ek pe he click ho, agar second wale pe click kr rhi hu to uske pehle wala hatna chahiye"

Translation: Only one should be clickable, if clicking on second one, the first should be removed.

### Solution:
- Changed checkbox behavior to single-select
- Keeps checkbox UI (square boxes) but works like radio buttons (single selection)
- User can still uncheck by clicking again (unlike radio buttons)
- Backend updated to save only one value

---

## Comparison: Checkbox vs Radio vs Our Implementation

| Feature | Normal Checkbox | Radio Button | Our Checkbox |
|---------|----------------|--------------|--------------|
| Multiple selection | ✅ Yes | ❌ No | ❌ No |
| Can uncheck | ✅ Yes | ❌ No | ✅ Yes |
| Visual indicator | Square | Circle | Square |
| Single value saved | ❌ No | ✅ Yes | ✅ Yes |

**Our implementation = Radio button behavior + Checkbox appearance + Ability to uncheck**

---

## Testing Checklist

- [ ] Click first checkbox → It checks ✅
- [ ] Click second checkbox → First unchecks, second checks ✅
- [ ] Click second checkbox again → It unchecks ✅
- [ ] Submit without selecting → Shows error ✅
- [ ] Submit with selection → Saves single value to database ✅
- [ ] Visual feedback (checkmark) works properly ✅
- [ ] Section highlighting works ✅
- [ ] Console logs show correct selection ✅

---

## Browser Console Output Example

```javascript
Question 3 - Selected: Routine outdoor exposure
Question 3 - Selected: Atopic or sensitive skin    // Previous one auto-unchecked
Question 3 - Deselected: Atopic or sensitive skin  // Clicked same one again
```

---

## Troubleshooting

### Issue: Multiple checkboxes getting checked
**Solution:** Clear browser cache, refresh page. JavaScript should prevent multiple selections.

### Issue: Cannot uncheck selected checkbox
**Solution:** Click the same checkbox again. Unlike radio buttons, checkboxes can be unchecked.

### Issue: Database showing multiple values
**Solution:** 
1. Check `views.py` line 287: `answer_value = selected[0] if selected else ''`
2. Verify only one checkbox is checked before submission
3. Check browser console for any JavaScript errors

---

## Future Enhancement Ideas

1. Add animation when option switches (slide effect)
2. Show "1 of N selected" counter
3. Add keyboard navigation (arrow keys to switch)
4. Add "Clear selection" button
5. Custom styling for selected state beyond checkmark
