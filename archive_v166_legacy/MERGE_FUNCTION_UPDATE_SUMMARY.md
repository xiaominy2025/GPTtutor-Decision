# Merge Function Update Summary

## Overview
Successfully updated the `merge_and_extend_with_story()` function in `query_engine.py` to generate more cohesive strategic narratives instead of fragmented formatting.

## Changes Made

### **Location**: `query_engine.py` (lines 1100-1180)

### **Key Updates**:

1. **Replaced the entire prompt block** with the new cohesive narrative prompt
2. **Updated variable name** from `merge_prompt` to `prompt` to match the new structure
3. **Maintained all existing functionality** while improving output quality

### **New Prompt Features**:

✅ **Unified Narrative**: Merges strategic thinking and story into one cohesive flow  
✅ **No Section Headers**: Eliminates fragmented "Strategic Reasoning" or "Concrete Example" headers  
✅ **Flexible Story Placement**: Embeds story wherever it best supports the narrative flow  
✅ **Graduate-Level Tone**: Maintains professional, academic writing style  
✅ **Concise Format**: Targets two well-developed paragraphs  
✅ **No Repetition**: Avoids superficial elaboration and redundant content  

### **Before vs After**:

**Before**: Fragmented structure with separate sections
```
**Strategic Thinking Lens**
**Strategic Reasoning:**
[Analytical content]

**Concrete Example:**
[Story content]
```

**After**: Unified cohesive narrative
```
**Strategic Thinking Lens**
[Integrated narrative with story embedded naturally]
```

## Technical Implementation

### **Function Signature**: Unchanged
```python
def merge_and_extend_with_story(lens_text: str, story_text: str, domain_count: int) -> str:
```

### **Error Handling**: Maintained
- Fallback to concatenation if GPT-3.5 merge fails
- Exception handling with graceful degradation
- Token usage and response time logging

### **Integration**: Seamless
- No changes to calling functions
- Maintains existing API contract
- Preserves all error handling and logging

## Expected Benefits

1. **Improved Readability**: Single cohesive narrative instead of fragmented sections
2. **Better Flow**: Story integrated naturally into the strategic reasoning
3. **Professional Presentation**: Clean, graduate-level writing style
4. **Reduced Redundancy**: Eliminates repetitive section headers
5. **Enhanced Learning**: More natural integration of theory and practice

## Verification

The update has been applied successfully and the function should now generate more cohesive strategic narratives that flow naturally from analytical reasoning to practical examples without the fragmented formatting issues.

## Files Modified

1. **`query_engine.py`**: Updated `merge_and_extend_with_story()` function with new prompt
2. **`MERGE_FUNCTION_UPDATE_SUMMARY.md`**: This summary document

The enhanced merge function should now produce more polished, cohesive responses that better serve the educational objectives of the decision-making course. 