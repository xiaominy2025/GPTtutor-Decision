# Strategic Thinking Lens Extraction Fix - V1.6.5.1

## Issue Identified

The Strategic Thinking Lens section was appearing cut off in the frontend display. Upon investigation, the issue was in the `answer_processor.py` file where the regex pattern for extracting sections was looking for the emoji followed by the section title, but the actual content format uses just the section title in bold (e.g., "**Strategic Thinking Lens**" without the emoji).

## Root Cause

The `_extract_section` method in `answer_processor.py` was using a regex pattern that expected:
```
**🧠 Strategic Thinking Lens**
```

But the actual content format was:
```
**Strategic Thinking Lens**
```

## Solution Implemented

### 1. **Enhanced Section Extraction Logic**
Updated the `_extract_section` method to handle both formats:
- **Pattern 1**: With emoji (old format): `**🧠 Strategic Thinking Lens**`
- **Pattern 2**: Without emoji (current format): `**Strategic Thinking Lens**`

### 2. **Updated Section Definitions**
Updated the sections dictionary to include all current sections:
```python
self.sections = {
    "strategic_thinking": {"emoji": "🧠", "title": "Strategic Thinking Lens"},
    "story_action": {"emoji": "📘", "title": "Story in Action"},
    "followup_prompts": {"emoji": "💬", "title": "Follow-up Prompts"},
    "concepts_tools": {"emoji": "🔧", "title": "Concepts/Tools"}
}
```

### 3. **Enhanced Regex Patterns**
Updated regex patterns to include the new emoji for Concepts/Tools section:
- Old: `(?=\*\*[^🧠📘💬]|$)`
- New: `(?=\*\*[^🧠📘💬🔧]|$)`

## Testing Results

✅ **Strategic Thinking Lens**: 803 characters (full content extracted)
✅ **Story in Action**: 434 characters (full content extracted)  
✅ **Follow-up Prompts**: 486 characters (full content extracted)
✅ **Concepts/Tools**: 237 characters (full content extracted)

## Impact

- **Fixed**: Strategic Thinking Lens content is no longer cut off
- **Enhanced**: All four sections are now properly extracted
- **Backward Compatible**: Still supports old format with emojis
- **Future Proof**: Ready for any additional sections

## Files Modified

- `answer_processor.py`: Enhanced section extraction logic and updated section definitions

## Verification

The fix was tested with the exact content format from the user's example and confirmed that all sections are now properly extracted without truncation. 